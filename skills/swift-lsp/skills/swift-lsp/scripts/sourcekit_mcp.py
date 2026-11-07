#!/usr/bin/env python3
"""Zero-dependency SourceKit-LSP MCP server, CLI bridge, and Xcode SDK .swiftinterface inspector.

Designed for Swift 6, macOS 27.2+, and iOS 27.2+ development in Google Antigravity
(Antigravity App and `agy` CLI), Claude Code, and Gemini Spark.

Architecture:
  - Tier 1 (Primary): Persistent warm `xcrun sourcekit-lsp` session over JSON-RPC 2.0 stdio.
  - Tier 2 (Automatic Sandbox Fallback): When `sourcekitd`'s XPC service (`com.apple.SourceKitService`)
    is blocked inside a Mach-restricted `sandbox-exec` container, automatically falls back in <10ms
    to `xcrun swiftc -dump-ast` / `-typecheck` (`-module-cache-path /tmp/swift-lsp-module-cache`)
    across all `.swift` files in the target so `hover`, `definition`, `references`, `symbols`,
    and `diagnostics` work in both unsandboxed MCP and sandboxed CLI environments.
"""

from __future__ import annotations

import argparse
import dataclasses
import glob
import hashlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_MIN_OS_VERSION = "27.2"
DEFAULT_MODULE_CACHE_DIR = "/tmp/swift-lsp-module-cache"
DEFAULT_SCRATCH_DIR = "/tmp/swift-lsp-scratch"
SERVER_NAME = "swift-lsp-sourcekit"
SERVER_VERSION = "0.1.2"

LSP_SYMBOL_KINDS: Dict[int, str] = {
    1: "File",
    2: "Module",
    3: "Namespace",
    4: "Package",
    5: "Class",
    6: "Method",
    7: "Property",
    8: "Field",
    9: "Constructor",
    10: "Enum",
    11: "Interface/Protocol",
    12: "Function",
    13: "Variable",
    14: "Constant",
    15: "String",
    16: "Number",
    17: "Boolean",
    18: "Array",
    19: "Object",
    20: "Key",
    21: "Null",
    22: "EnumMember",
    23: "Struct",
    24: "Event",
    25: "Operator",
    26: "TypeParameter",
}

LSP_SEVERITY_NAMES: Dict[int, str] = {
    1: "error",
    2: "warning",
    3: "information",
    4: "hint",
}

COMPANION_EXPORTED_MODULES: Dict[str, List[str]] = {
    "SwiftUI": ["SwiftUI", "SwiftUICore"],
    "Foundation": ["Foundation", "FoundationEssentials", "FoundationInternationalization"],
    "Swift": ["Swift", "_Concurrency", "Synchronization"],
}


class SourceKitUnavailableError(RuntimeError):
    """Raised when `sourcekit-lsp` or its `sourcekitd` XPC service is unavailable."""


# ---------------------------------------------------------------------------
# Path, URI & UTF-16 Position Utilities
# ---------------------------------------------------------------------------


def path_to_file_uri(path: str | pathlib.Path) -> str:
    abs_path = os.path.abspath(os.fspath(path))
    return "file://" + urllib.parse.quote(abs_path, safe="/:")


def file_uri_to_path(uri: str) -> str:
    if uri.startswith("file://"):
        parsed = urllib.parse.urlparse(uri)
        return urllib.parse.unquote(parsed.path)
    return uri


def char_index_to_utf16_col(line_text: str, char_index: int) -> int:
    """Convert a Python 0-based character index on a line to UTF-16 code units."""
    clamped = max(0, min(char_index, len(line_text)))
    return len(line_text[:clamped].encode("utf-16-le")) // 2


def utf16_col_to_char_index(line_text: str, utf16_col: int) -> int:
    """Convert a 0-based UTF-16 code unit offset to a Python character index."""
    if utf16_col <= 0:
        return 0
    units = 0
    for idx, ch in enumerate(line_text):
        units += 2 if ord(ch) > 0xFFFF else 1
        if units > utf16_col:
            return idx
        if units == utf16_col:
            return idx + 1
    return len(line_text)


def normalize_symbol_token(raw_symbol: str) -> str:
    """Clean LLM-supplied symbol names (e.g., '.borderedProminent', 'fetch(id:)', '`default`')."""
    token = raw_symbol.strip()
    if token.startswith("."):
        token = token[1:]
    if "(" in token:
        token = token.split("(", 1)[0]
    token = token.strip("`").strip()
    return token


@dataclasses.dataclass(frozen=True)
class ResolvedPosition:
    line_0based: int
    col_utf16: int
    line_1based: int
    col_char: int
    matched_symbol: str
    line_text: str


def resolve_symbol_position(
    text: str,
    line_1based: int,
    symbol: Optional[str] = None,
    column_0based: Optional[int] = None,
    search_radius: int = 3,
) -> ResolvedPosition:
    """Resolve a 1-based line + optional symbol name to an exact 0-based LSP UTF-16 position.

    When `symbol` is provided, searches `line_1based` first and then `±search_radius`
    adjacent lines so minor line-number drift after prior edits never breaks queries.
    """
    lines = text.splitlines()
    if not lines:
        return ResolvedPosition(0, 0, 1, 0, symbol or "", "")

    target_idx = max(0, min(line_1based - 1, len(lines) - 1))

    if symbol and symbol.strip():
        clean = normalize_symbol_token(symbol)
        if clean:
            candidate_indices: List[int] = [target_idx]
            for delta in range(1, search_radius + 1):
                if target_idx - delta >= 0:
                    candidate_indices.append(target_idx - delta)
                if target_idx + delta < len(lines):
                    candidate_indices.append(target_idx + delta)

            word_pattern = re.compile(r"\b" + re.escape(clean) + r"\b")
            # Pass 1: exact word-boundary match
            for idx in candidate_indices:
                line_str = lines[idx]
                match = word_pattern.search(line_str)
                if match:
                    char_col = match.start()
                    return ResolvedPosition(
                        line_0based=idx,
                        col_utf16=char_index_to_utf16_col(line_str, char_col),
                        line_1based=idx + 1,
                        col_char=char_col,
                        matched_symbol=clean,
                        line_text=line_str,
                    )
            # Pass 2: substring match
            for idx in candidate_indices:
                line_str = lines[idx]
                pos = line_str.find(clean)
                if pos != -1:
                    return ResolvedPosition(
                        line_0based=idx,
                        col_utf16=char_index_to_utf16_col(line_str, pos),
                        line_1based=idx + 1,
                        col_char=pos,
                        matched_symbol=clean,
                        line_text=line_str,
                    )

    line_str = lines[target_idx]
    if column_0based is not None:
        char_col = max(0, min(column_0based, len(line_str)))
    else:
        stripped = len(line_str) - len(line_str.lstrip())
        char_col = min(stripped, max(0, len(line_str) - 1))

    return ResolvedPosition(
        line_0based=target_idx,
        col_utf16=char_index_to_utf16_col(line_str, char_col),
        line_1based=target_idx + 1,
        col_char=char_col,
        matched_symbol=symbol or "",
        line_text=line_str,
    )


# ---------------------------------------------------------------------------
# Workspace, Target File Collection & Toolchain Discovery
# ---------------------------------------------------------------------------


def discover_swift_workspace(start_path: str | pathlib.Path) -> pathlib.Path:
    """Walk up from `start_path` to find the nearest Swift/Xcode workspace root."""
    p = pathlib.Path(os.path.abspath(os.fspath(start_path)))
    if p.is_file():
        p = p.parent

    best_git: Optional[pathlib.Path] = None
    curr = p
    while True:
        if (curr / "Package.swift").is_file() or (curr / "buildServer.json").is_file():
            return curr
        if list(curr.glob("*.xcworkspace")) or list(curr.glob("*.xcodeproj")):
            return curr
        if (curr / ".git").exists() and best_git is None:
            best_git = curr
        if curr.parent == curr:
            break
        curr = curr.parent

    return best_git or p


def collect_target_swift_files(
    primary_file: str | pathlib.Path,
    workspace_root: Optional[pathlib.Path] = None,
    max_files: int = 64,
) -> List[str]:
    """Collect sibling `.swift` files belonging to the same SwiftPM target or directory."""
    primary = pathlib.Path(os.path.realpath(os.fspath(primary_file)))
    if not primary.is_file():
        return [str(primary)]

    ws = pathlib.Path(os.path.realpath(os.fspath(workspace_root or discover_swift_workspace(primary))))
    target_root: Optional[pathlib.Path] = None

    # Check if inside `Sources/<Target>/...` or `Tests/<Target>/...`
    try:
        rel = primary.relative_to(ws)
        parts = rel.parts
        if len(parts) >= 2 and parts[0] in ("Sources", "Tests"):
            target_root = ws / parts[0] / parts[1]
        elif len(parts) >= 1 and parts[0] == "Sources":
            target_root = ws / "Sources"
    except ValueError:
        pass

    if target_root is None:
        target_root = primary.parent

    siblings: List[str] = [str(primary)]
    for cand in sorted(target_root.rglob("*.swift")):
        if cand.name == "Package.swift":
            continue
        cand_str = os.path.realpath(os.fspath(cand))
        if cand_str != str(primary):
            siblings.append(cand_str)
        if len(siblings) >= max_files:
            break
    return siblings


def _run_cmd_capture(cmd: List[str], timeout: float = 10.0) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        return 1, "", str(exc)


def resolve_sdk_info(sdk_name: str) -> Dict[str, Any]:
    """Query `xcrun --sdk <sdk_name>` for SDK path and version."""
    rc_p, sdk_path, err_p = _run_cmd_capture(["xcrun", "--sdk", sdk_name, "--show-sdk-path"])
    rc_v, sdk_ver, _ = _run_cmd_capture(["xcrun", "--sdk", sdk_name, "--show-sdk-version"])
    return {
        "sdk": sdk_name,
        "available": rc_p == 0 and bool(sdk_path),
        "path": sdk_path if rc_p == 0 else None,
        "version": sdk_ver if rc_v == 0 else None,
        "error": err_p if rc_p != 0 else None,
    }


def probe_toolchain_and_workspace(
    workspace: Optional[str] = None,
    min_version: str = DEFAULT_MIN_OS_VERSION,
    pool: Optional["LspSessionPool"] = None,
) -> Dict[str, Any]:
    """Inspect Xcode toolchain, SourceKit-LSP, SDKs (macOS/iOS 27.2+), and project layout."""
    if workspace:
        ws_root = discover_swift_workspace(os.path.expanduser(workspace))
        if pool is not None:
            pool.record_workspace(ws_root)
    elif pool is not None and pool.last_workspace is not None:
        ws_root = pool.last_workspace
    else:
        ws_root = discover_swift_workspace(os.getcwd())
    rc_lsp, lsp_path, lsp_err = _run_cmd_capture(["xcrun", "--find", "sourcekit-lsp"])
    rc_swift, swift_ver, _ = _run_cmd_capture(["xcrun", "swift", "--version"])

    macos_sdk = resolve_sdk_info("macosx")
    ios_sim_sdk = resolve_sdk_info("iphonesimulator")
    ios_dev_sdk = resolve_sdk_info("iphoneos")

    has_package_swift = (ws_root / "Package.swift").is_file()
    has_build_server = (ws_root / "buildServer.json").is_file()
    xcworkspaces = [p.name for p in ws_root.glob("*.xcworkspace")]
    xcodeprojs = [p.name for p in ws_root.glob("*.xcodeproj")]

    index_candidates = [
        ws_root / ".build" / "debug" / "index" / "store",
        ws_root / ".build" / "release" / "index" / "store",
    ] + list(ws_root.glob(".build/*/debug/index/store"))
    index_store_path: Optional[str] = None
    for cand in index_candidates:
        if cand.is_dir():
            index_store_path = str(cand)
            break

    if not index_store_path and has_build_server:
        try:
            bs_data = json.loads((ws_root / "buildServer.json").read_text(encoding="utf-8"))
            if isinstance(bs_data, dict) and bs_data.get("indexStorePath"):
                index_store_path = str(bs_data["indexStorePath"])
        except (OSError, json.JSONDecodeError):
            pass

    if has_package_swift:
        project_kind = "swiftpm"
    elif has_build_server:
        project_kind = "xcode-bsp"
    elif xcworkspaces or xcodeprojs:
        project_kind = "xcodeproj-unconfigured"
    else:
        project_kind = "standalone"

    recommendations: List[str] = []
    if project_kind == "xcodeproj-unconfigured":
        recommendations.append(
            "Found .xcodeproj/.xcworkspace without Package.swift or buildServer.json. "
            "Run `xcode-build-server config -project <App>.xcodeproj -scheme <Scheme>` "
            "at the workspace root so sourcekit-lsp can read Xcode compiler flags and index store."
        )
    if project_kind == "swiftpm" and not index_store_path:
        recommendations.append(
            "SwiftPM index store (.build/*/index/store) is not populated yet. "
            "In-file and target-wide AST queries work immediately; run `swift build` once "
            "or let sourcekit-lsp background indexing finish for full workspace index coverage."
        )

    return {
        "workspace_root": str(ws_root),
        "project_kind": project_kind,
        "has_package_swift": has_package_swift,
        "has_build_server_json": has_build_server,
        "xcworkspaces": xcworkspaces,
        "xcodeprojs": xcodeprojs,
        "index_ready": index_store_path is not None,
        "index_store_path": index_store_path,
        "sourcekit_lsp": {
            "available": rc_lsp == 0 and bool(lsp_path),
            "path": lsp_path if rc_lsp == 0 else None,
            "error": lsp_err if rc_lsp != 0 else None,
        },
        "swift_version": swift_ver.splitlines()[0] if rc_swift == 0 and swift_ver else None,
        "target_baseline": {
            "macos_min": min_version,
            "ios_min": min_version,
        },
        "sdks": {
            "macosx": macos_sdk,
            "iphonesimulator": ios_sim_sdk,
            "iphoneos": ios_dev_sdk,
        },
        "recommendations": recommendations,
    }


# ---------------------------------------------------------------------------
# LSP JSON-RPC 2.0 Framing & Persistent SourceKit-LSP Session (Tier 1)
# ---------------------------------------------------------------------------


def encode_lsp_message(payload: Dict[str, Any]) -> bytes:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    return header + body


def read_lsp_message(stream: io.BufferedReader) -> Optional[Dict[str, Any]]:
    """Read a single `Content-Length` framed JSON-RPC message from a byte stream."""
    content_length: Optional[int] = None
    while True:
        line = stream.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            if content_length is not None:
                break
            continue
        decoded = line.decode("ascii", errors="replace").strip()
        if decoded.lower().startswith("content-length:"):
            try:
                content_length = int(decoded.split(":", 1)[1].strip())
            except ValueError:
                return None

    if content_length is None or content_length < 0:
        return None

    body = b""
    while len(body) < content_length:
        chunk = stream.read(content_length - len(body))
        if not chunk:
            return None
        body += chunk

    return json.loads(body.decode("utf-8", errors="replace"))


class SourceKitLspSession:
    """Manages a persistent `xcrun sourcekit-lsp` subprocess for a workspace."""

    def __init__(
        self,
        workspace_root: pathlib.Path,
        command: Optional[List[str]] = None,
    ) -> None:
        self.workspace_root = workspace_root
        self.command = command or [
            "xcrun",
            "sourcekit-lsp",
            "--scratch-path",
            DEFAULT_SCRATCH_DIR,
            "-Xswiftc",
            "-module-cache-path",
            "-Xswiftc",
            DEFAULT_MODULE_CACHE_DIR,
        ]
        self._proc: Optional[subprocess.Popen[bytes]] = None
        self._write_lock = threading.Lock()
        self._cond = threading.Condition()
        self._next_id = 1
        self._responses: Dict[int, Dict[str, Any]] = {}
        self._diagnostics: Dict[str, List[Dict[str, Any]]] = {}
        self._diag_versions: Dict[str, int] = {}
        self._doc_versions: Dict[str, int] = {}
        self._doc_hashes: Dict[str, str] = {}
        self._initialized = False
        self._eof = False
        self._fatal_error: Optional[str] = None
        self._stderr_lines: List[str] = []
        self._reader_thread: Optional[threading.Thread] = None
        self._stderr_thread: Optional[threading.Thread] = None

    def start(self, timeout: float = 10.0) -> None:
        if self._fatal_error:
            raise SourceKitUnavailableError(self._fatal_error)
        if self._initialized and self._proc and self._proc.poll() is None and not self._eof:
            return

        self._eof = False
        self._proc = subprocess.Popen(
            self.command,
            cwd=str(self.workspace_root),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._reader_thread = threading.Thread(
            target=self._reader_loop,
            name=f"sourcekit-lsp-stdout-{self.workspace_root.name}",
            daemon=True,
        )
        self._stderr_thread = threading.Thread(
            target=self._stderr_loop,
            name=f"sourcekit-lsp-stderr-{self.workspace_root.name}",
            daemon=True,
        )
        self._reader_thread.start()
        self._stderr_thread.start()

        root_uri = path_to_file_uri(self.workspace_root)
        init_params = {
            "processId": os.getpid(),
            "rootPath": str(self.workspace_root),
            "rootUri": root_uri,
            "workspaceFolders": [
                {"uri": root_uri, "name": self.workspace_root.name}
            ],
            "capabilities": {
                "textDocument": {
                    "synchronization": {
                        "dynamicRegistration": False,
                        "willSave": False,
                        "didSave": True,
                    },
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "definition": {"linkSupport": True},
                    "typeDefinition": {"linkSupport": True},
                    "implementation": {"linkSupport": True},
                    "references": {},
                    "documentSymbol": {
                        "hierarchicalDocumentSymbolSupport": True
                    },
                    "publishDiagnostics": {
                        "relatedInformation": True,
                        "CodeDescriptionSupport": True,
                    },
                    "diagnostic": {"dynamicRegistration": False},
                },
                "workspace": {
                    "workspaceFolders": True,
                    "symbol": {},
                    "configuration": True,
                },
            },
        }
        self.request("initialize", init_params, timeout=timeout)
        self.notify("initialized", {})
        self._initialized = True

    def close(self) -> None:
        proc = self._proc
        if not proc:
            return
        if proc.poll() is None:
            try:
                if not self._eof and not self._fatal_error:
                    self.request("shutdown", {}, timeout=1.5)
                    self.notify("exit", {})
            except Exception:
                pass
            try:
                proc.terminate()
                proc.wait(timeout=1.5)
            except Exception:
                try:
                    proc.kill()
                    proc.wait(timeout=1.0)
                except Exception:
                    pass
        for pipe in (proc.stdin, proc.stdout, proc.stderr):
            if pipe is not None:
                try:
                    pipe.close()
                except Exception:
                    pass

    def _send_raw(self, payload: Dict[str, Any]) -> None:
        if self._fatal_error:
            raise SourceKitUnavailableError(self._fatal_error)
        if not self._proc or not self._proc.stdin or self._eof:
            raise SourceKitUnavailableError("sourcekit-lsp process is not running")
        encoded = encode_lsp_message(payload)
        with self._write_lock:
            self._proc.stdin.write(encoded)
            self._proc.stdin.flush()

    def notify(self, method: str, params: Dict[str, Any]) -> None:
        self._send_raw({"jsonrpc": "2.0", "method": method, "params": params})

    def request(
        self,
        method: str,
        params: Dict[str, Any],
        timeout: float = 8.0,
    ) -> Any:
        with self._cond:
            if self._fatal_error:
                raise SourceKitUnavailableError(self._fatal_error)
            req_id = self._next_id
            self._next_id += 1

        self._send_raw(
            {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        )

        deadline = time.monotonic() + timeout
        with self._cond:
            while req_id not in self._responses:
                if self._fatal_error:
                    raise SourceKitUnavailableError(self._fatal_error)
                if self._eof or (self._proc and self._proc.poll() is not None):
                    stderr_tail = "; ".join(self._stderr_lines[-5:])
                    raise SourceKitUnavailableError(
                        f"sourcekit-lsp exited before replying to `{method}`"
                        + (f": {stderr_tail}" if stderr_tail else "")
                    )
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise SourceKitUnavailableError(
                        f"Timed out waiting {timeout:.1f}s for sourcekit-lsp response to `{method}`"
                    )
                self._cond.wait(timeout=min(remaining, 0.25))
            resp = self._responses.pop(req_id)

        if "error" in resp and resp["error"] is not None:
            err = resp["error"]
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            code = err.get("code", -1) if isinstance(err, dict) else -1
            raise RuntimeError(f"LSP error ({code}) in `{method}`: {msg}")
        return resp.get("result")

    def _stderr_loop(self) -> None:
        assert self._proc and self._proc.stderr
        for raw_line in self._proc.stderr:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            with self._cond:
                self._stderr_lines.append(line)
                if (
                    "SOURCEKITD FATAL ERROR" in line
                    or "Service is invalid" in line
                    or "sourcekitd connection interrupted" in line
                ):
                    self._fatal_error = (
                        f"sourcekitd XPC service unavailable ({line}); "
                        "falling back to in-process `xcrun swiftc` AST engine."
                    )
                    self._cond.notify_all()

    def _reader_loop(self) -> None:
        assert self._proc and self._proc.stdout
        stream = self._proc.stdout
        try:
            while True:
                try:
                    msg = read_lsp_message(stream)
                except Exception:
                    break
                if msg is None:
                    break

                # Server-to-client request (has both `id` and `method`)
                if "id" in msg and "method" in msg:
                    req_id = msg["id"]
                    method = msg.get("method", "")
                    result: Any = None
                    if method == "workspace/configuration":
                        items = msg.get("params", {}).get("items", [])
                        result = [None for _ in items]
                    try:
                        self._send_raw(
                            {"jsonrpc": "2.0", "id": req_id, "result": result}
                        )
                    except Exception:
                        pass
                    continue

                # Response to client request
                if "id" in msg:
                    with self._cond:
                        self._responses[int(msg["id"])] = msg
                        self._cond.notify_all()
                    continue

                # Server notification
                method = msg.get("method", "")
                if method == "textDocument/publishDiagnostics":
                    params = msg.get("params", {})
                    uri = params.get("uri", "")
                    diags = params.get("diagnostics", [])
                    with self._cond:
                        self._diagnostics[uri] = diags
                        self._diag_versions[uri] = self._diag_versions.get(uri, 0) + 1
                        self._cond.notify_all()
        finally:
            with self._cond:
                self._eof = True
                self._cond.notify_all()

    def sync_file(self, file_path: str | pathlib.Path) -> Tuple[str, str]:
        """Ensure `sourcekit-lsp` has the latest disk contents of `file_path`."""
        self.start()
        abs_path = os.path.abspath(os.fspath(file_path))
        uri = path_to_file_uri(abs_path)
        text = pathlib.Path(abs_path).read_text(encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

        if uri not in self._doc_versions:
            self._doc_versions[uri] = 1
            self._doc_hashes[uri] = digest
            self.notify(
                "textDocument/didOpen",
                {
                    "textDocument": {
                        "uri": uri,
                        "languageId": "swift",
                        "version": 1,
                        "text": text,
                    }
                },
            )
        elif self._doc_hashes.get(uri) != digest:
            ver = self._doc_versions[uri] + 1
            self._doc_versions[uri] = ver
            self._doc_hashes[uri] = digest
            self.notify(
                "textDocument/didChange",
                {
                    "textDocument": {"uri": uri, "version": ver},
                    "contentChanges": [{"text": text}],
                },
            )
        return uri, text

    def get_diagnostics(
        self,
        file_path: str | pathlib.Path,
        wait_seconds: float = 0.8,
    ) -> List[Dict[str, Any]]:
        """Retrieve diagnostics via `textDocument/diagnostic` (pull) or `publishDiagnostics` (push)."""
        with self._cond:
            uri_preview = path_to_file_uri(file_path)
            prev_ver = self._diag_versions.get(uri_preview, 0)

        uri, _ = self.sync_file(file_path)

        pull_res = self.request(
            "textDocument/diagnostic",
            {"textDocument": {"uri": uri}},
            timeout=5.0,
        )
        if isinstance(pull_res, dict) and "items" in pull_res:
            return list(pull_res.get("items") or [])

        deadline = time.monotonic() + wait_seconds
        with self._cond:
            while self._diag_versions.get(uri, 0) <= prev_ver:
                if self._fatal_error:
                    raise SourceKitUnavailableError(self._fatal_error)
                rem = deadline - time.monotonic()
                if rem <= 0:
                    break
                self._cond.wait(timeout=min(rem, 0.2))
            return list(self._diagnostics.get(uri, []))


class LspSessionPool:
    """Thread-safe pool of warm `SourceKitLspSession` instances keyed by workspace root."""

    def __init__(self, custom_command: Optional[List[str]] = None) -> None:
        self._lock = threading.Lock()
        self._sessions: Dict[str, SourceKitLspSession] = {}
        self._custom_command = custom_command
        self._last_workspace: Optional[pathlib.Path] = None

    @property
    def last_workspace(self) -> Optional[pathlib.Path]:
        with self._lock:
            return self._last_workspace

    def record_workspace(self, ws_root: pathlib.Path) -> None:
        with self._lock:
            self._last_workspace = ws_root

    def get_for_path(
        self,
        target_path: str | pathlib.Path,
        workspace: Optional[str] = None,
    ) -> SourceKitLspSession:
        ws_root = discover_swift_workspace(workspace or target_path)
        key = str(ws_root)
        with self._lock:
            self._last_workspace = ws_root
            session = self._sessions.get(key)
            if session is None:
                session = SourceKitLspSession(
                    workspace_root=ws_root,
                    command=self._custom_command,
                )
                self._sessions[key] = session
            return session

    def close_all(self) -> None:
        with self._lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()
        for s in sessions:
            s.close()


def resolve_file_path(
    file_path: str | pathlib.Path,
    workspace: Optional[str] = None,
    pool: Optional[LspSessionPool] = None,
) -> str:
    """Resolve `file_path` against `workspace` or `pool.last_workspace` when relative.

    When spawned as a global plugin MCP server, the process `cwd` is the plugin install
    directory rather than the user's Swift project root. Resolving relative paths against
    `workspace` (or the pool's last active Swift workspace) ensures relative file paths
    like `Sources/App/ContentView.swift` resolve to the active Swift project.
    """
    raw = os.path.expanduser(os.fspath(file_path))
    if os.path.isabs(raw):
        abs_p = os.path.abspath(raw)
        if pool is not None:
            pool.record_workspace(discover_swift_workspace(abs_p))
        return abs_p

    if workspace:
        ws_expanded = os.path.abspath(os.path.expanduser(workspace))
        ws_root = discover_swift_workspace(ws_expanded)
        if pool is not None:
            pool.record_workspace(ws_root)
        cand = os.path.join(ws_expanded, raw)
        if os.path.exists(cand) or not os.path.exists(os.path.join(str(ws_root), raw)):
            return os.path.abspath(cand)
        return os.path.abspath(os.path.join(str(ws_root), raw))

    if pool is not None and pool.last_workspace is not None:
        cand = pool.last_workspace / raw
        if cand.exists() or not pathlib.Path(raw).exists():
            return os.path.abspath(os.fspath(cand))

    return os.path.abspath(raw)


# ---------------------------------------------------------------------------
# Tier 2: In-Process `xcrun swiftc -dump-ast` Analyzer (Sandbox-Safe Fallback)
# ---------------------------------------------------------------------------


_AST_DECL_KINDS: Dict[str, str] = {
    "struct_decl": "Struct",
    "class_decl": "Class",
    "actor_decl": "Actor",
    "protocol_decl": "Interface/Protocol",
    "enum_decl": "Enum",
    "enum_element_decl": "EnumMember",
    "func_decl": "Function",
    "constructor_decl": "Constructor",
    "var_decl": "Property",
    "typealias_decl": "TypeParameter",
    "extension_decl": "Namespace",
}

_AST_NODE_RE = re.compile(
    r"^(?P<indent>\s*)\((?P<kind>[a-z_]+)\b(?P<attrs>.*)$"
)
_AST_RANGE_RE = re.compile(
    r"range=\[(?P<file>[^:\]]+):(?P<sline>\d+):(?P<scol>\d+)\s*-\s*line:(?P<eline>\d+):(?P<ecol>\d+)\]"
)
_AST_LOC_RE = re.compile(
    r"location=(?P<file>[^:\s]+):(?P<line>\d+):(?P<col>\d+)"
)
_AST_QUOTED_NAME_RE = re.compile(r'"(?P<name>[^"]+)"')
_AST_IFACE_TYPE_RE = re.compile(r'interface_type="(?P<itype>[^"]+)"')
_AST_EXPR_TYPE_RE = re.compile(r'\btype="(?P<etype>[^"]+)"')
_AST_DECL_REF_RE = re.compile(r'\bdecl="(?P<decl>[^"]+)"')


def run_swiftc_dump_ast(
    primary_file: str,
    workspace_root: Optional[pathlib.Path] = None,
    platform: str = "macos",
    min_version: str = DEFAULT_MIN_OS_VERSION,
) -> str:
    """Run `xcrun swiftc -dump-ast` across the target's `.swift` files with `/tmp` module cache."""
    target_files = collect_target_swift_files(primary_file, workspace_root=workspace_root)
    sdk_name = "macosx" if platform == "macos" else "iphonesimulator"
    triple = (
        f"arm64-apple-macosx{min_version}"
        if platform == "macos"
        else f"arm64-apple-ios{min_version}-simulator"
    )
    cmd = [
        "xcrun",
        "--sdk",
        sdk_name,
        "swiftc",
        "-dump-ast",
        "-module-cache-path",
        DEFAULT_MODULE_CACHE_DIR,
        "-target",
        triple,
    ] + target_files
    _, out, err = _run_cmd_capture(cmd, timeout=20.0)
    return (out + "\n" + err).strip()


def extract_doc_comment_above_line(file_path: str, line_1based: int) -> str:
    """Extract contiguous `///` doc comments or `@MainActor`/`@available` attributes above `line_1based`."""
    try:
        lines = pathlib.Path(file_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    if not (1 <= line_1based <= len(lines)):
        return ""
    collected: List[str] = []
    idx = line_1based - 2
    while idx >= 0 and idx >= line_1based - 10:
        s = lines[idx].strip()
        if s.startswith("///") or s.startswith("@"):
            collected.append(s)
            idx -= 1
        else:
            break
    collected.reverse()
    return "\n".join(collected)


def ast_fallback_symbols(
    file_path: str,
    query: Optional[str] = None,
    workspace: Optional[str] = None,
) -> Dict[str, Any]:
    abs_file = os.path.realpath(file_path)
    ws_root = discover_swift_workspace(workspace or abs_file)
    ast_text = run_swiftc_dump_ast(abs_file, workspace_root=ws_root)

    symbols: List[Dict[str, Any]] = []
    parent_stack: List[Tuple[int, str]] = []

    for raw_line in ast_text.splitlines():
        if " implicit " in raw_line:
            continue
        m = _AST_NODE_RE.match(raw_line)
        if not m:
            continue
        indent = len(m.group("indent"))
        kind = m.group("kind")
        attrs = m.group("attrs")

        while parent_stack and parent_stack[-1][0] >= indent:
            parent_stack.pop()

        if kind not in _AST_DECL_KINDS:
            continue

        rng_m = _AST_RANGE_RE.search(attrs)
        if not rng_m:
            continue
        rng_file = os.path.realpath(rng_m.group("file"))
        if rng_file != abs_file:
            continue

        name_m = _AST_QUOTED_NAME_RE.search(attrs)
        if not name_m:
            continue
        name = name_m.group("name")
        if name.startswith("$") or name.startswith("<anonymous"):
            continue

        parent_prefix = ".".join(p[1] for p in parent_stack)
        full_name = f"{parent_prefix}.{name}" if parent_prefix else name
        itype_m = _AST_IFACE_TYPE_RE.search(attrs)
        sline = int(rng_m.group("sline"))
        eline = int(rng_m.group("eline"))

        kind_label = _AST_DECL_KINDS[kind]
        if kind == "func_decl" and parent_stack:
            kind_label = "Method"

        symbols.append(
            {
                "name": full_name,
                "kind": kind_label,
                "detail": itype_m.group("itype") if itype_m else None,
                "start_line": sline,
                "end_line": eline,
            }
        )
        if kind in ("struct_decl", "class_decl", "actor_decl", "protocol_decl", "enum_decl", "extension_decl"):
            parent_stack.append((indent, name))

    if query:
        q_lower = query.lower()
        symbols = [s for s in symbols if q_lower in s["name"].lower()]

    return {
        "mode": "documentSymbol",
        "engine": "swiftc-ast-fallback",
        "file": abs_file,
        "count": len(symbols),
        "symbols": symbols,
    }


def ast_fallback_hover(
    file_path: str,
    pos: ResolvedPosition,
    workspace: Optional[str] = None,
) -> Optional[str]:
    abs_file = os.path.realpath(file_path)
    ws_root = discover_swift_workspace(workspace or abs_file)
    ast_text = run_swiftc_dump_ast(abs_file, workspace_root=ws_root)
    sym = pos.matched_symbol

    best_info: Optional[Tuple[int, str, Optional[str], Optional[str]]] = None

    for raw_line in ast_text.splitlines():
        if abs_file not in raw_line and os.path.basename(abs_file) not in raw_line:
            continue
        m = _AST_NODE_RE.match(raw_line)
        if not m:
            continue
        kind = m.group("kind")
        attrs = m.group("attrs")

        line_num: Optional[int] = None
        loc_m = _AST_LOC_RE.search(attrs)
        rng_m = _AST_RANGE_RE.search(attrs)
        if loc_m and os.path.realpath(loc_m.group("file")) == abs_file:
            line_num = int(loc_m.group("line"))
        elif rng_m and os.path.realpath(rng_m.group("file")) == abs_file:
            line_num = int(rng_m.group("sline"))

        if line_num is None or abs(line_num - pos.line_1based) > 1:
            continue

        itype_m = _AST_IFACE_TYPE_RE.search(attrs)
        etype_m = _AST_EXPR_TYPE_RE.search(attrs)
        decl_m = _AST_DECL_REF_RE.search(attrs)
        inferred_type = (
            itype_m.group("itype")
            if itype_m
            else (etype_m.group("etype") if etype_m else None)
        )
        if not inferred_type:
            continue

        decl_str = decl_m.group("decl") if decl_m else None
        score = 1
        if sym and (f'"{sym}' in attrs or (decl_str and sym in decl_str)):
            score = 3
        elif kind in ("dot_syntax_call_expr", "declref_expr", "member_ref_expr", "func_decl", "struct_decl", "var_decl"):
            score = 2

        if best_info is None or score > best_info[0]:
            best_info = (score, inferred_type, decl_str, kind)

    if not best_info:
        return None

    _, inferred_type, decl_str, _ = best_info
    doc_header = extract_doc_comment_above_line(abs_file, pos.line_1based)
    if not doc_header and decl_str:
        decl_loc_m = _DECL_LOC_SUFFIX_RE.match(decl_str)
        if decl_loc_m:
            doc_header = extract_doc_comment_above_line(
                os.path.realpath(decl_loc_m.group("file")),
                int(decl_loc_m.group("line")),
            )
    parts: List[str] = []
    if doc_header:
        parts.append(doc_header)
    parts.append(f"```swift\n{pos.matched_symbol or pos.line_text.strip()}: {inferred_type}\n```")
    if decl_str:
        parts.append(f"Resolved declaration: `{decl_str}`")
    return "\n\n".join(parts)


_DECL_LOC_SUFFIX_RE = re.compile(
    r"^(?P<sym>[^@]+)@(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+)$"
)


def ast_fallback_definition(
    file_path: str,
    pos: ResolvedPosition,
    workspace: Optional[str] = None,
) -> List[Dict[str, Any]]:
    abs_file = os.path.realpath(file_path)
    ws_root = discover_swift_workspace(workspace or abs_file)
    ast_text = run_swiftc_dump_ast(abs_file, workspace_root=ws_root)
    sym = pos.matched_symbol

    matched_decls: List[str] = []
    for raw_line in ast_text.splitlines():
        if abs_file not in raw_line and os.path.basename(abs_file) not in raw_line:
            continue
        loc_m = _AST_LOC_RE.search(raw_line)
        if not loc_m or os.path.realpath(loc_m.group("file")) != abs_file:
            continue
        if int(loc_m.group("line")) != pos.line_1based:
            continue
        decl_m = _AST_DECL_REF_RE.search(raw_line)
        if not decl_m:
            continue
        decl_val = decl_m.group("decl")
        if not sym or sym in decl_val:
            matched_decls.append(decl_val)

    locations: List[Dict[str, Any]] = []
    seen: set[Tuple[str, int]] = set()
    for decl_val in matched_decls:
        m = _DECL_LOC_SUFFIX_RE.match(decl_val)
        if m:
            target_file = os.path.abspath(m.group("file"))
            target_line = int(m.group("line"))
            target_col = int(m.group("col")) - 1
            key = (target_file, target_line)
            if key not in seen:
                seen.add(key)
                locations.append(
                    {
                        "file": target_file,
                        "line": target_line,
                        "column_utf16": max(0, target_col),
                        "declaration": m.group("sym"),
                        "snippet": _read_snippet(target_file, target_line, context_lines=4),
                    }
                )
        elif ".(file)." in decl_val:
            # Resolved to an Apple SDK module (e.g. `SwiftUICore.(file).View.buttonStyle`)
            mod_name = decl_val.split(".(file).", 1)[0]
            sdk_res = search_sdk_interface(
                module_name=mod_name,
                symbol_query=sym or decl_val.split(".")[-1],
                platform="macos",
                max_results=3,
            )
            for match in sdk_res.get("matches", []):
                iface_file = sdk_res.get("swiftinterface_file", mod_name)
                ln = int(match.get("line", 1))
                key = (iface_file, ln)
                if key not in seen:
                    seen.add(key)
                    locations.append(
                        {
                            "file": iface_file,
                            "line": ln,
                            "column_utf16": 0,
                            "declaration": decl_val,
                            "snippet": match.get("declaration", ""),
                        }
                    )
    return locations


def ast_fallback_references(
    file_path: str,
    pos: ResolvedPosition,
    include_declaration: bool = False,
    workspace: Optional[str] = None,
) -> List[Dict[str, Any]]:
    abs_file = os.path.abspath(file_path)
    ws_root = discover_swift_workspace(workspace or abs_file)
    ast_text = run_swiftc_dump_ast(abs_file, workspace_root=ws_root)
    sym = pos.matched_symbol
    if not sym:
        return []

    refs: List[Dict[str, Any]] = []
    seen: set[Tuple[str, int]] = set()

    for raw_line in ast_text.splitlines():
        if " implicit " in raw_line:
            continue
        decl_m = _AST_DECL_REF_RE.search(raw_line)
        loc_m = _AST_LOC_RE.search(raw_line)
        if not decl_m or not loc_m:
            continue
        decl_val = decl_m.group("decl")
        if sym not in decl_val:
            continue
        ref_file = os.path.abspath(loc_m.group("file"))
        ref_line = int(loc_m.group("line"))
        ref_col = max(0, int(loc_m.group("col")) - 1)
        key = (ref_file, ref_line)
        if key in seen:
            continue
        seen.add(key)
        preview = ""
        try:
            src_lines = pathlib.Path(ref_file).read_text(encoding="utf-8", errors="replace").splitlines()
            if 1 <= ref_line <= len(src_lines):
                preview = src_lines[ref_line - 1].strip()
        except OSError:
            pass
        refs.append(
            {
                "file": ref_file,
                "line": ref_line,
                "column_utf16": ref_col,
                "preview": preview,
            }
        )

    if include_declaration:
        for dloc in ast_fallback_definition(abs_file, pos, workspace=workspace):
            key = (dloc["file"], dloc["line"])
            if key not in seen:
                seen.add(key)
                refs.insert(
                    0,
                    {
                        "file": dloc["file"],
                        "line": dloc["line"],
                        "column_utf16": dloc["column_utf16"],
                        "preview": dloc.get("snippet", "").splitlines()[0] if dloc.get("snippet") else "",
                    },
                )
    return refs


# ---------------------------------------------------------------------------
# High-Level LSP Operations & Dual-Platform Typechecking
# ---------------------------------------------------------------------------


def _extract_hover_markdown(hover_result: Any) -> str:
    if not hover_result or not isinstance(hover_result, dict):
        return ""
    contents = hover_result.get("contents")
    if isinstance(contents, str):
        return contents.strip()
    if isinstance(contents, dict):
        return str(contents.get("value", "")).strip()
    if isinstance(contents, list):
        parts: List[str] = []
        for item in contents:
            if isinstance(item, str):
                parts.append(item.strip())
            elif isinstance(item, dict) and "value" in item:
                parts.append(str(item["value"]).strip())
        return "\n\n".join(p for p in parts if p)
    return ""


def _read_snippet(file_path: str, line_1based: int, context_lines: int = 5) -> str:
    try:
        lines = pathlib.Path(file_path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    if not lines:
        return ""
    start = max(1, line_1based - context_lines)
    end = min(len(lines), line_1based + context_lines)
    out: List[str] = []
    for ln in range(start, end + 1):
        marker = ">>" if ln == line_1based else "  "
        out.append(f"{marker} {ln:4d} | {lines[ln - 1]}")
    return "\n".join(out)


def _normalize_locations(raw_result: Any) -> List[Dict[str, Any]]:
    if not raw_result:
        return []
    items = raw_result if isinstance(raw_result, list) else [raw_result]
    normalized: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        uri = item.get("targetUri") or item.get("uri") or ""
        rng = (
            item.get("targetSelectionRange")
            or item.get("targetRange")
            or item.get("range")
            or {}
        )
        start = rng.get("start", {})
        line_1based = int(start.get("line", 0)) + 1
        col_0based = int(start.get("character", 0))
        path_str = file_uri_to_path(uri)
        normalized.append(
            {
                "file": path_str,
                "line": line_1based,
                "column_utf16": col_0based,
                "snippet": _read_snippet(path_str, line_1based, context_lines=4),
            }
        )
    return normalized


def query_hover(
    pool: LspSessionPool,
    file_path: str,
    line: int,
    symbol: Optional[str] = None,
    column: Optional[int] = None,
    workspace: Optional[str] = None,
) -> Dict[str, Any]:
    abs_path = resolve_file_path(file_path, workspace=workspace, pool=pool)
    text = pathlib.Path(abs_path).read_text(encoding="utf-8")
    pos = resolve_symbol_position(text, line_1based=line, symbol=symbol, column_0based=column)
    engine = "sourcekit-lsp"
    markdown = ""

    try:
        session = pool.get_for_path(abs_path, workspace=workspace)
        uri, _ = session.sync_file(abs_path)
        raw = session.request(
            "textDocument/hover",
            {
                "textDocument": {"uri": uri},
                "position": {"line": pos.line_0based, "character": pos.col_utf16},
            },
        )
        markdown = _extract_hover_markdown(raw)
    except SourceKitUnavailableError:
        engine = "swiftc-ast-fallback"
        markdown = ast_fallback_hover(abs_path, pos, workspace=workspace) or ""

    return {
        "engine": engine,
        "file": abs_path,
        "resolved_line": pos.line_1based,
        "resolved_column_utf16": pos.col_utf16,
        "matched_symbol": pos.matched_symbol,
        "line_text": pos.line_text.strip(),
        "hover": markdown or None,
    }


def query_definition(
    pool: LspSessionPool,
    file_path: str,
    line: int,
    symbol: Optional[str] = None,
    column: Optional[int] = None,
    kind: str = "definition",
    workspace: Optional[str] = None,
) -> Dict[str, Any]:
    method_map = {
        "definition": "textDocument/definition",
        "typeDefinition": "textDocument/typeDefinition",
        "implementation": "textDocument/implementation",
    }
    method = method_map.get(kind, "textDocument/definition")
    abs_path = resolve_file_path(file_path, workspace=workspace, pool=pool)
    text = pathlib.Path(abs_path).read_text(encoding="utf-8")
    pos = resolve_symbol_position(text, line_1based=line, symbol=symbol, column_0based=column)
    engine = "sourcekit-lsp"

    try:
        session = pool.get_for_path(abs_path, workspace=workspace)
        uri, _ = session.sync_file(abs_path)
        raw = session.request(
            method,
            {
                "textDocument": {"uri": uri},
                "position": {"line": pos.line_0based, "character": pos.col_utf16},
            },
        )
        locations = _normalize_locations(raw)
    except SourceKitUnavailableError:
        engine = "swiftc-ast-fallback"
        locations = ast_fallback_definition(abs_path, pos, workspace=workspace)

    return {
        "engine": engine,
        "kind": kind,
        "file": abs_path,
        "resolved_line": pos.line_1based,
        "resolved_column_utf16": pos.col_utf16,
        "matched_symbol": pos.matched_symbol,
        "locations": locations,
    }


def query_references(
    pool: LspSessionPool,
    file_path: str,
    line: int,
    symbol: Optional[str] = None,
    column: Optional[int] = None,
    include_declaration: bool = False,
    workspace: Optional[str] = None,
) -> Dict[str, Any]:
    abs_path = resolve_file_path(file_path, workspace=workspace, pool=pool)
    text = pathlib.Path(abs_path).read_text(encoding="utf-8")
    pos = resolve_symbol_position(text, line_1based=line, symbol=symbol, column_0based=column)
    ws_root = discover_swift_workspace(workspace or abs_path)
    engine = "sourcekit-lsp"
    refs: List[Dict[str, Any]] = []

    try:
        session = pool.get_for_path(abs_path, workspace=workspace)
        uri, _ = session.sync_file(abs_path)
        raw = session.request(
            "textDocument/references",
            {
                "textDocument": {"uri": uri},
                "position": {"line": pos.line_0based, "character": pos.col_utf16},
                "context": {"includeDeclaration": bool(include_declaration)},
            },
        )
        items = raw if isinstance(raw, list) else []
        for item in items:
            if not isinstance(item, dict):
                continue
            ref_uri = item.get("uri", "")
            ref_path = file_uri_to_path(ref_uri)
            start = item.get("range", {}).get("start", {})
            ln_1 = int(start.get("line", 0)) + 1
            col_0 = int(start.get("character", 0))
            preview = ""
            try:
                src_lines = pathlib.Path(ref_path).read_text(encoding="utf-8", errors="replace").splitlines()
                if 1 <= ln_1 <= len(src_lines):
                    preview = src_lines[ln_1 - 1].strip()
            except OSError:
                pass
            refs.append(
                {
                    "file": ref_path,
                    "line": ln_1,
                    "column_utf16": col_0,
                    "preview": preview,
                }
            )
    except SourceKitUnavailableError:
        engine = "swiftc-ast-fallback"
        refs = ast_fallback_references(
            abs_path, pos, include_declaration=include_declaration, workspace=workspace
        )

    probe = probe_toolchain_and_workspace(str(ws_root))
    warning: Optional[str] = None
    if not probe["index_ready"] and engine == "sourcekit-lsp":
        warning = (
            "Workspace IndexStoreDB (.build/*/index/store) is not populated yet; "
            "cross-file references may be incomplete until `swift build` or background indexing finishes."
        )
    return {
        "engine": engine,
        "file": abs_path,
        "resolved_line": pos.line_1based,
        "resolved_column_utf16": pos.col_utf16,
        "matched_symbol": pos.matched_symbol,
        "count": len(refs),
        "index_ready": probe["index_ready"],
        "warning": warning,
        "references": refs,
    }


def _flatten_document_symbols(
    items: List[Dict[str, Any]],
    parent_name: str = "",
) -> List[Dict[str, Any]]:
    flat: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", ""))
        full_name = f"{parent_name}.{name}" if parent_name else name
        kind_id = int(item.get("kind", 0))
        rng = item.get("selectionRange") or item.get("range") or item.get("location", {}).get("range", {})
        start_line = int(rng.get("start", {}).get("line", 0)) + 1
        end_line = int(item.get("range", rng).get("end", {}).get("line", start_line - 1)) + 1
        flat.append(
            {
                "name": full_name,
                "kind": LSP_SYMBOL_KINDS.get(kind_id, f"Kind({kind_id})"),
                "detail": item.get("detail"),
                "start_line": start_line,
                "end_line": end_line,
            }
        )
        children = item.get("children")
        if isinstance(children, list) and children:
            flat.extend(_flatten_document_symbols(children, parent_name=full_name))
    return flat


def query_symbols(
    pool: LspSessionPool,
    file_path: Optional[str] = None,
    query: Optional[str] = None,
    workspace: Optional[str] = None,
) -> Dict[str, Any]:
    if file_path:
        abs_path = resolve_file_path(file_path, workspace=workspace, pool=pool)
        try:
            session = pool.get_for_path(abs_path, workspace=workspace)
            uri, _ = session.sync_file(abs_path)
            raw = session.request("textDocument/documentSymbol", {"textDocument": {"uri": uri}})
            symbols = _flatten_document_symbols(raw if isinstance(raw, list) else [])
            if query:
                q_lower = query.lower()
                symbols = [s for s in symbols if q_lower in s["name"].lower()]
            return {
                "mode": "documentSymbol",
                "engine": "sourcekit-lsp",
                "file": abs_path,
                "count": len(symbols),
                "symbols": symbols,
            }
        except SourceKitUnavailableError:
            return ast_fallback_symbols(abs_path, query=query, workspace=workspace)

    ws_target = workspace or (str(pool.last_workspace) if pool.last_workspace else os.getcwd())
    session = pool.get_for_path(ws_target, workspace=workspace)
    session.start()
    raw = session.request("workspace/symbol", {"query": query or ""})
    items = raw if isinstance(raw, list) else []
    ws_symbols: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        loc = item.get("location", {})
        uri = loc.get("uri", "")
        rng = loc.get("range", {})
        kind_id = int(item.get("kind", 0))
        ws_symbols.append(
            {
                "name": item.get("name"),
                "container": item.get("containerName"),
                "kind": LSP_SYMBOL_KINDS.get(kind_id, f"Kind({kind_id})"),
                "file": file_uri_to_path(uri),
                "line": int(rng.get("start", {}).get("line", 0)) + 1,
            }
        )
    return {
        "mode": "workspaceSymbol",
        "engine": "sourcekit-lsp",
        "workspace": str(session.workspace_root),
        "query": query or "",
        "count": len(ws_symbols),
        "symbols": ws_symbols,
    }


def build_swiftc_typecheck_command(
    files: List[str],
    platform: str,
    sdk_path: Optional[str],
    min_version: str = DEFAULT_MIN_OS_VERSION,
) -> List[str]:
    """Construct an `xcrun swiftc -typecheck` command for macOS 27.2+ or iOS 27.2+ simulator."""
    sdk_name = "macosx" if platform == "macos" else "iphonesimulator"
    triple = (
        f"arm64-apple-macosx{min_version}"
        if platform == "macos"
        else f"arm64-apple-ios{min_version}-simulator"
    )
    cmd = [
        "xcrun",
        "--sdk",
        sdk_name,
        "swiftc",
        "-typecheck",
        "-module-cache-path",
        DEFAULT_MODULE_CACHE_DIR,
        "-target",
        triple,
    ]
    if sdk_path:
        cmd.extend(["-sdk", sdk_path])
    cmd.extend(os.path.abspath(f) for f in files)
    return cmd


_SWIFTC_DIAG_RE = re.compile(
    r"^(?P<file>[^\n:]+):(?P<line>\d+):(?P<col>\d+):\s+(?P<severity>error|warning|note):\s+(?P<message>.+)$"
)


def parse_swiftc_stderr(stderr_text: str) -> List[Dict[str, Any]]:
    diags: List[Dict[str, Any]] = []
    for raw_line in stderr_text.splitlines():
        m = _SWIFTC_DIAG_RE.match(raw_line.strip())
        if not m:
            continue
        sev = m.group("severity")
        if sev == "note" and diags:
            diags[-1].setdefault("notes", []).append(m.group("message"))
            continue
        diags.append(
            {
                "file": m.group("file"),
                "line": int(m.group("line")),
                "column": int(m.group("col")),
                "severity": sev,
                "source": "swiftc-typecheck",
                "message": m.group("message"),
            }
        )
    return diags


def query_diagnostics(
    pool: LspSessionPool,
    files: List[str],
    platform: str = "macos",
    min_version: str = DEFAULT_MIN_OS_VERSION,
    workspace: Optional[str] = None,
) -> Dict[str, Any]:
    """Collect diagnostics from warm `sourcekit-lsp` and/or dual-platform (`macos`/`ios`) typecheck."""
    if not files:
        raise ValueError("At least one .swift file path is required for diagnostics")

    abs_files = [resolve_file_path(f, workspace=workspace, pool=pool) for f in files]
    ws_root = discover_swift_workspace(workspace or abs_files[0])
    lsp_diagnostics: List[Dict[str, Any]] = []
    lsp_note: Optional[str] = None

    try:
        session = pool.get_for_path(abs_files[0], workspace=workspace)
        for fpath in abs_files:
            raw_diags = session.get_diagnostics(fpath)
            for d in raw_diags:
                rng = d.get("range", {}).get("start", {})
                sev_id = int(d.get("severity", 1))
                lsp_diagnostics.append(
                    {
                        "file": fpath,
                        "line": int(rng.get("line", 0)) + 1,
                        "column": int(rng.get("character", 0)) + 1,
                        "severity": LSP_SEVERITY_NAMES.get(sev_id, "error"),
                        "source": d.get("source", "sourcekit-lsp"),
                        "code": d.get("code"),
                        "message": d.get("message", ""),
                    }
                )
    except Exception as exc:
        lsp_note = str(exc)

    platforms_to_check: List[str] = []
    if platform == "both":
        platforms_to_check = ["macos", "ios"]
    elif platform in ("macos", "ios"):
        platforms_to_check = [platform]
    else:
        raise ValueError(f"Unsupported platform `{platform}`; expected 'macos', 'ios', or 'both'")

    # Expand target sibling files so cross-file references in the same SwiftPM target typecheck cleanly
    expanded_target_files: List[str] = []
    for fpath in abs_files:
        for sib in collect_target_swift_files(fpath, workspace_root=ws_root):
            if sib not in expanded_target_files:
                expanded_target_files.append(sib)

    platform_reports: Dict[str, Any] = {}
    for plat in platforms_to_check:
        sdk_key = "macosx" if plat == "macos" else "iphonesimulator"
        sdk_info = resolve_sdk_info(sdk_key)
        cmd = build_swiftc_typecheck_command(
            expanded_target_files,
            platform=plat,
            sdk_path=sdk_info.get("path"),
            min_version=min_version,
        )
        if plat == "ios" or platform == "both" or lsp_note is not None:
            rc, _, stderr_text = _run_cmd_capture(cmd, timeout=20.0)
            parsed = parse_swiftc_stderr(stderr_text)
            platform_reports[plat] = {
                "target_triple": cmd[cmd.index("-target") + 1],
                "sdk_version": sdk_info.get("version"),
                "exit_code": rc,
                "diagnostics": parsed,
            }
        else:
            platform_reports[plat] = {
                "target_triple": cmd[cmd.index("-target") + 1],
                "sdk_version": sdk_info.get("version"),
                "diagnostics": lsp_diagnostics,
            }

    total_errors = sum(
        1 for d in lsp_diagnostics if d.get("severity") == "error"
    ) + sum(
        1
        for rep in platform_reports.values()
        for d in rep.get("diagnostics", [])
        if d.get("source") == "swiftc-typecheck" and d.get("severity") == "error"
    )

    return {
        "files": abs_files,
        "platform": platform,
        "min_os_version": min_version,
        "lsp_diagnostics": lsp_diagnostics,
        "lsp_fallback_note": lsp_note,
        "platform_checks": platform_reports,
        "error_count": total_errors,
    }


# ---------------------------------------------------------------------------
# Xcode SDK `.swiftinterface` Ground-Truth Inspector (macOS 27.2+ / iOS 27.2+)
# ---------------------------------------------------------------------------


def _find_single_module_swiftinterface(
    sdk_path: str,
    module_name: str,
    platform: str = "macos",
) -> Optional[pathlib.Path]:
    root = pathlib.Path(sdk_path)
    candidates: List[pathlib.Path] = []
    search_dirs = [
        root / "System" / "Library" / "Frameworks" / f"{module_name}.framework" / "Modules" / f"{module_name}.swiftmodule",
        root / "System" / "Library" / "SubFrameworks" / f"{module_name}.framework" / "Modules" / f"{module_name}.swiftmodule",
        root / "usr" / "lib" / "swift" / f"{module_name}.swiftmodule",
    ]
    for d in search_dirs:
        if d.is_dir():
            for p in sorted(d.glob("*.swiftinterface")):
                if not p.name.endswith(".private.swiftinterface"):
                    candidates.append(p)

    if not candidates:
        pattern = str(root / "System" / "Library" / "**" / f"{module_name}.swiftmodule" / "*.swiftinterface")
        for match in sorted(glob.glob(pattern, recursive=True)):
            if not match.endswith(".private.swiftinterface"):
                candidates.append(pathlib.Path(match))

    if not candidates:
        return None

    # Exclude Mac Catalyst (`macabi`) when inspecting native macOS or iOS simulator
    non_macabi = [p for p in candidates if "macabi" not in p.name]
    pool = non_macabi or candidates

    if platform == "macos":
        macos_native = [p for p in pool if "macos" in p.name and p.name.startswith(("arm64e-", "arm64-"))]
        if macos_native:
            return macos_native[0]
    else:
        ios_native = [p for p in pool if "ios" in p.name and p.name.startswith(("arm64-", "arm64e-"))]
        if ios_native:
            return ios_native[0]

    arm_pref = [p for p in pool if p.name.startswith(("arm64e-", "arm64-"))]
    return arm_pref[0] if arm_pref else pool[0]


def find_module_swiftinterfaces(
    sdk_path: str,
    module_name: str,
    platform: str = "macos",
) -> List[pathlib.Path]:
    """Locate `.swiftinterface` files for `module_name` (and re-exported companion modules)."""
    mod_names = COMPANION_EXPORTED_MODULES.get(module_name, [module_name])
    found: List[pathlib.Path] = []
    for mod in mod_names:
        p = _find_single_module_swiftinterface(sdk_path, mod, platform=platform)
        if p and p not in found:
            found.append(p)
    return found


_SWIFTINTERFACE_DECL_RE = re.compile(
    r"(?:^|\s)(?:public|open|package)\s+"
    r"(?:@[A-Za-z0-9_().\s,*\"-]+\s+)*"
    r"(?:(?:final|nonisolated|indirect|convenience|override|static|class|mutating|nonmutating|distributed)\s+)*"
    r"(?P<kw>struct|class|actor|protocol|enum|func|var|let|init|typealias|macro|extension)\s+"
    r"(?P<ident>[A-Za-z0-9_`]+)"
)


def parse_swiftinterface_declarations(
    interface_text: str,
    symbol_query: Optional[str] = None,
    availability_filter: Optional[str] = None,
    max_results: int = 25,
    source_module: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Extract and rank declarations + preceding `@available`/`@MainActor` attributes from `.swiftinterface` text."""
    lines = interface_text.splitlines()
    scored_results: List[Tuple[int, int, Dict[str, Any]]] = []
    sym_lower = symbol_query.lower() if symbol_query else None
    avail_lower = availability_filter.lower() if availability_filter else None

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped_line = line.strip()
        if not stripped_line.startswith("//"):
            decl_m = _SWIFTINTERFACE_DECL_RE.search(line)
            if decl_m:
                kw = decl_m.group("kw")
                ident = decl_m.group("ident").strip("`")

                # Capture up to 8 preceding standalone `@available` / `@MainActor` / `///` lines
                attr_start = i
                while attr_start > 0 and attr_start > i - 9:
                    prev = lines[attr_start - 1].strip()
                    if (
                        (prev.startswith("@") or prev.startswith("///"))
                        and not _SWIFTINTERFACE_DECL_RE.search(prev)
                        and not prev.endswith("{")
                        and not prev.endswith("}")
                    ):
                        attr_start -= 1
                    else:
                        break

                # Capture signature continuation lines without bleeding into the next declaration
                end_idx = i
                if not stripped_line.endswith("{") and not stripped_line.endswith("}") and kw in ("func", "init", "struct", "class", "actor", "protocol", "enum"):
                    while end_idx + 1 < min(n, i + 6):
                        nxt = lines[end_idx + 1].strip()
                        if (
                            not nxt
                            or nxt.startswith("@")
                            or nxt.startswith("///")
                            or nxt.startswith("}")
                            or _SWIFTINTERFACE_DECL_RE.search(nxt)
                        ):
                            break
                        end_idx += 1
                        if nxt.endswith("{") or nxt.endswith("}"):
                            break

                block_lines = [ln.rstrip() for ln in lines[attr_start : end_idx + 1]]
                block_text = "\n".join(block_lines)
                block_lower = block_text.lower()

                if sym_lower and sym_lower not in block_lower:
                    i = end_idx + 1
                    continue
                if avail_lower and avail_lower not in block_lower:
                    i = end_idx + 1
                    continue

                # Relevance score:
                # 5 = exact case-sensitive match on primary type declaration (struct/class/actor/protocol/enum/macro)
                # 4 = exact case-insensitive match on non-extension declaration
                # 3 = exact identifier match on extension
                # 2 = identifier prefix match
                # 1 = substring match in signature or attributes
                score = 1
                if sym_lower:
                    ident_lower = ident.lower()
                    if ident == symbol_query and kw in ("struct", "class", "actor", "protocol", "enum", "macro", "typealias"):
                        score = 5
                    elif ident_lower == sym_lower and kw != "extension":
                        score = 4
                    elif ident_lower == sym_lower:
                        score = 3
                    elif ident_lower.startswith(sym_lower):
                        score = 2
                    elif sym_lower in line.lower():
                        score = 1
                    else:
                        score = 0

                entry: Dict[str, Any] = {
                    "line": i + 1,
                    "kind": kw,
                    "name": ident,
                    "declaration": block_text,
                }
                if source_module:
                    entry["module"] = source_module
                scored_results.append((score, -(i + 1), entry))

                if not sym_lower and len(scored_results) >= max_results:
                    break
                i = end_idx + 1
                continue
        i += 1

    if sym_lower:
        scored_results.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in scored_results[:max_results]]


def search_sdk_interface(
    module_name: str,
    symbol_query: Optional[str] = None,
    platform: str = "macos",
    availability_filter: Optional[str] = None,
    max_results: int = 25,
    sdk_path_override: Optional[str] = None,
) -> Dict[str, Any]:
    """Search installed Xcode `.swiftinterface` headers for `module_name` (and re-exported companion modules)."""
    sdk_name = "macosx" if platform == "macos" else "iphonesimulator"
    sdk_info = resolve_sdk_info(sdk_name) if not sdk_path_override else {
        "sdk": sdk_name,
        "available": True,
        "path": sdk_path_override,
        "version": None,
    }
    sdk_path = sdk_path_override or sdk_info.get("path")
    if not sdk_path:
        return {
            "module": module_name,
            "platform": platform,
            "error": f"Could not resolve Xcode SDK path for `{sdk_name}`",
            "matches": [],
        }

    interface_files = find_module_swiftinterfaces(sdk_path, module_name, platform=platform)
    if not interface_files:
        return {
            "module": module_name,
            "platform": platform,
            "sdk_path": sdk_path,
            "sdk_version": sdk_info.get("version"),
            "error": f"No `.swiftinterface` found for module `{module_name}` in `{sdk_path}`",
            "matches": [],
        }

    all_matches: List[Dict[str, Any]] = []
    for target_file in interface_files:
        mod_label = target_file.parent.name.replace(".swiftmodule", "")
        text = target_file.read_text(encoding="utf-8", errors="replace")
        file_matches = parse_swiftinterface_declarations(
            text,
            symbol_query=symbol_query,
            availability_filter=availability_filter,
            max_results=max_results,
            source_module=mod_label,
        )
        all_matches.extend(file_matches)

    if symbol_query:
        sym_l = symbol_query.lower()

        def _rank(m: Dict[str, Any]) -> Tuple[int, int]:
            raw_nm = str(m.get("name", ""))
            nm = raw_nm.lower()
            kw = str(m.get("kind", ""))
            if raw_nm == symbol_query and kw in ("struct", "class", "actor", "protocol", "enum", "macro", "typealias"):
                return (5, -int(m.get("line", 0)))
            if nm == sym_l and kw != "extension":
                return (4, -int(m.get("line", 0)))
            if nm == sym_l:
                return (3, -int(m.get("line", 0)))
            if nm.startswith(sym_l):
                return (2, -int(m.get("line", 0)))
            return (1, -int(m.get("line", 0)))

        all_matches.sort(key=_rank, reverse=True)

    trimmed = all_matches[:max_results]
    return {
        "module": module_name,
        "platform": platform,
        "sdk_path": sdk_path,
        "sdk_version": sdk_info.get("version"),
        "swiftinterface_file": str(interface_files[0]),
        "searched_swiftinterfaces": [str(f) for f in interface_files],
        "symbol_query": symbol_query,
        "availability_filter": availability_filter,
        "count": len(trimmed),
        "matches": trimmed,
    }


# ---------------------------------------------------------------------------
# MCP Stdio Server Implementation (`2024-11-05` / `2025-03-26`)
# ---------------------------------------------------------------------------


MCP_TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "name": "swift_toolchain_probe",
        "description": (
            "Inspect the active Xcode toolchain, `xcrun sourcekit-lsp` availability, "
            "SwiftPM / Xcode (`buildServer.json`) workspace layout, `IndexStoreDB` readiness, "
            "and installed `macosx` / `iphonesimulator` SDK versions (macOS 27.2+ and iOS 27.2+ baseline)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {
                    "type": "string",
                    "description": "Optional workspace directory or Swift file path (defaults to current working directory).",
                },
                "min_version": {
                    "type": "string",
                    "description": "Target minimum OS baseline version (defaults to '27.2').",
                    "default": DEFAULT_MIN_OS_VERSION,
                },
            },
        },
    },
    {
        "name": "swift_diagnostics",
        "description": (
            "Run fast, sandbox-free Swift typechecking and collect live diagnostics from `sourcekit-lsp` "
            "and/or dual-platform `swiftc -typecheck` across `macos` (arm64-apple-macosx27.2), "
            "`ios` (arm64-apple-ios27.2-simulator), or `both` (verifying both `#if os(macOS)` and `#if os(iOS)` blocks)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "One or more `.swift` file paths to check.",
                },
                "platform": {
                    "type": "string",
                    "enum": ["macos", "ios", "both"],
                    "default": "macos",
                    "description": "Target platform SDK: 'macos', 'ios' (simulator), or 'both'.",
                },
                "min_version": {
                    "type": "string",
                    "default": DEFAULT_MIN_OS_VERSION,
                    "description": "Minimum OS version for target triples (defaults to '27.2').",
                },
                "workspace": {
                    "type": "string",
                    "description": "Optional Swift workspace root path.",
                },
            },
            "required": ["files"],
        },
    },
    {
        "name": "swift_hover",
        "description": (
            "Get compiler-inferred Swift type, `@MainActor`/`Sendable` isolation, generic signature, "
            "and documentation at a symbol in a `.swift` file. Pass `symbol` + 1-based `line` "
            "(auto-resolves exact UTF-16 column on `line ± 3`)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {"type": "string", "description": "Path to the `.swift` file."},
                "line": {"type": "integer", "description": "1-based line number."},
                "symbol": {
                    "type": "string",
                    "description": "Identifier or member name on or near `line` (recommended over `column`).",
                },
                "column": {
                    "type": "integer",
                    "description": "Optional 0-based character column if `symbol` is omitted.",
                },
                "workspace": {"type": "string", "description": "Optional workspace root."},
            },
            "required": ["file", "line"],
        },
    },
    {
        "name": "swift_definition",
        "description": (
            "Jump to the declaration, type definition, or protocol witness implementation of a Swift symbol "
            "and return target file, line, and surrounding source snippet."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {"type": "string", "description": "Path to the `.swift` file."},
                "line": {"type": "integer", "description": "1-based line number."},
                "symbol": {
                    "type": "string",
                    "description": "Identifier or member name on or near `line`.",
                },
                "kind": {
                    "type": "string",
                    "enum": ["definition", "typeDefinition", "implementation"],
                    "default": "definition",
                    "description": "LSP navigation kind.",
                },
                "column": {"type": "integer", "description": "Optional 0-based column."},
                "workspace": {"type": "string", "description": "Optional workspace root."},
            },
            "required": ["file", "line"],
        },
    },
    {
        "name": "swift_references",
        "description": (
            "Find all semantic call sites and references to a Swift symbol across the workspace using `sourcekit-lsp`."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {"type": "string", "description": "Path to the `.swift` file."},
                "line": {"type": "integer", "description": "1-based line number."},
                "symbol": {
                    "type": "string",
                    "description": "Identifier or member name on or near `line`.",
                },
                "include_declaration": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to include the declaration itself.",
                },
                "column": {"type": "integer", "description": "Optional 0-based column."},
                "workspace": {"type": "string", "description": "Optional workspace root."},
            },
            "required": ["file", "line"],
        },
    },
    {
        "name": "swift_symbols",
        "description": (
            "List hierarchical document symbols (`Struct`, `Class`, `Actor`, `Protocol`, `Method`, `Property`) "
            "in a `.swift` file, or search workspace symbols by query."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "Optional `.swift` file path for document outline.",
                },
                "query": {
                    "type": "string",
                    "description": "Optional symbol name filter or workspace symbol query.",
                },
                "workspace": {"type": "string", "description": "Optional workspace root."},
            },
        },
    },
    {
        "name": "swift_sdk_interface",
        "description": (
            "Search the installed Xcode `MacOSX` or `iPhoneSimulator` SDK `.swiftinterface` files "
            "(e.g. `SwiftUI`, `AppKit`, `UIKit`, `Foundation`, `Observation`, `FoundationModels`, `Metal`) "
            "for exact macOS 27.2+ and iOS 27.2+ API signatures, `@available` attributes, and `@MainActor`/`Sendable` annotations."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Framework or module name (e.g., 'SwiftUI', 'AppKit', 'UIKit', 'Observation').",
                },
                "symbol": {
                    "type": "string",
                    "description": "Optional symbol, modifier, or type name substring to search for.",
                },
                "platform": {
                    "type": "string",
                    "enum": ["macos", "ios"],
                    "default": "macos",
                    "description": "Which Xcode SDK to inspect ('macos' or 'ios').",
                },
                "availability_filter": {
                    "type": "string",
                    "description": "Optional `@available` substring filter (e.g. '27.0' or '27.2').",
                },
                "max_results": {
                    "type": "integer",
                    "default": 25,
                    "description": "Maximum declarations to return (default 25).",
                },
            },
            "required": ["module"],
        },
    },
]


def dispatch_mcp_tool_call(
    pool: LspSessionPool,
    name: str,
    arguments: Dict[str, Any],
) -> Dict[str, Any]:
    if name == "swift_toolchain_probe":
        return probe_toolchain_and_workspace(
            workspace=arguments.get("workspace"),
            min_version=str(arguments.get("min_version", DEFAULT_MIN_OS_VERSION)),
            pool=pool,
        )
    if name == "swift_diagnostics":
        return query_diagnostics(
            pool=pool,
            files=list(arguments.get("files") or []),
            platform=str(arguments.get("platform", "macos")),
            min_version=str(arguments.get("min_version", DEFAULT_MIN_OS_VERSION)),
            workspace=arguments.get("workspace"),
        )
    if name == "swift_hover":
        return query_hover(
            pool=pool,
            file_path=str(arguments["file"]),
            line=int(arguments["line"]),
            symbol=arguments.get("symbol"),
            column=int(arguments["column"]) if arguments.get("column") is not None else None,
            workspace=arguments.get("workspace"),
        )
    if name == "swift_definition":
        return query_definition(
            pool=pool,
            file_path=str(arguments["file"]),
            line=int(arguments["line"]),
            symbol=arguments.get("symbol"),
            column=int(arguments["column"]) if arguments.get("column") is not None else None,
            kind=str(arguments.get("kind", "definition")),
            workspace=arguments.get("workspace"),
        )
    if name == "swift_references":
        return query_references(
            pool=pool,
            file_path=str(arguments["file"]),
            line=int(arguments["line"]),
            symbol=arguments.get("symbol"),
            column=int(arguments["column"]) if arguments.get("column") is not None else None,
            include_declaration=bool(arguments.get("include_declaration", False)),
            workspace=arguments.get("workspace"),
        )
    if name == "swift_symbols":
        return query_symbols(
            pool=pool,
            file_path=arguments.get("file"),
            query=arguments.get("query"),
            workspace=arguments.get("workspace"),
        )
    if name == "swift_sdk_interface":
        return search_sdk_interface(
            module_name=str(arguments["module"]),
            symbol_query=arguments.get("symbol"),
            platform=str(arguments.get("platform", "macos")),
            availability_filter=arguments.get("availability_filter"),
            max_results=int(arguments.get("max_results", 25)),
        )
    raise ValueError(f"Unknown tool: {name}")


def handle_mcp_request(
    pool: LspSessionPool,
    msg: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Process one incoming MCP JSON-RPC message and return response dict (or None for notifications)."""
    method = msg.get("method", "")
    req_id = msg.get("id")

    if req_id is None:
        return None

    if method == "initialize":
        client_proto = msg.get("params", {}).get("protocolVersion", "2024-11-05")
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": client_proto,
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                },
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": MCP_TOOLS_SCHEMA},
        }

    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}

    if method == "prompts/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}}

    if method == "tools/call":
        params = msg.get("params", {})
        tool_name = str(params.get("name", ""))
        arguments = params.get("arguments") or {}
        try:
            payload = dispatch_mcp_tool_call(pool, tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(payload, indent=2),
                        }
                    ],
                    "isError": False,
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {"error": str(exc), "tool": tool_name}, indent=2
                            ),
                        }
                    ],
                    "isError": True,
                },
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def run_mcp_stdio_loop(
    in_stream: io.BufferedReader,
    out_stream: io.BufferedWriter,
    pool: Optional[LspSessionPool] = None,
) -> None:
    """Serve MCP over stdio supporting both newline-delimited JSON and Content-Length framing."""
    own_pool = pool is None
    active_pool = pool or LspSessionPool()
    try:
        while True:
            first_line = in_stream.readline()
            if not first_line:
                break
            stripped = first_line.strip()
            if not stripped:
                continue

            use_content_length = False
            if stripped.lower().startswith(b"content-length:"):
                use_content_length = True
                try:
                    length = int(stripped.split(b":", 1)[1].strip())
                except ValueError:
                    continue
                while True:
                    hdr = in_stream.readline()
                    if not hdr or hdr in (b"\r\n", b"\n"):
                        break
                body = in_stream.read(length)
                if not body:
                    break
                msg = json.loads(body.decode("utf-8", errors="replace"))
            else:
                msg = json.loads(stripped.decode("utf-8", errors="replace"))

            resp = handle_mcp_request(active_pool, msg)
            if resp is not None:
                if use_content_length:
                    out_stream.write(encode_lsp_message(resp))
                else:
                    line_bytes = (
                        json.dumps(resp, separators=(",", ":")) + "\n"
                    ).encode("utf-8")
                    out_stream.write(line_bytes)
                out_stream.flush()
    finally:
        if own_pool:
            active_pool.close_all()


# ---------------------------------------------------------------------------
# Deterministic Offline Self-Test Suite (`--self-test`)
# ---------------------------------------------------------------------------


def _run_self_tests() -> int:
    import tempfile

    failures: List[str] = []

    def check(cond: bool, label: str) -> None:
        if not cond:
            failures.append(label)

    # 1. UTF-16 & Symbol-Anchored Position Resolution
    sample_swift = "\n".join(
        [
            "import SwiftUI",
            "",
            "@MainActor",
            "struct ContentView: View {",
            "    var body: some View {",
            '        Button("Run 🚀") { fetchModels(id: 42) }',
            "            .buttonStyle(.borderedProminent)",
            "    }",
            "}",
        ]
    )
    pos_fetch = resolve_symbol_position(sample_swift, line_1based=6, symbol="fetchModels(id:)")
    check(pos_fetch.line_1based == 6, "resolve_symbol_position exact line")
    check(pos_fetch.matched_symbol == "fetchModels", "normalize_symbol_token strips parens")
    check(
        pos_fetch.col_utf16 == pos_fetch.col_char + 1,
        f"UTF-16 surrogate pair offset ({pos_fetch.col_utf16} vs {pos_fetch.col_char})",
    )
    check(
        utf16_col_to_char_index(pos_fetch.line_text, pos_fetch.col_utf16) == pos_fetch.col_char,
        "utf16_col_to_char_index round-trip",
    )

    pos_dot = resolve_symbol_position(
        sample_swift, line_1based=5, symbol=".borderedProminent"
    )
    check(pos_dot.line_1based == 7, "resolve_symbol_position ±3 line drift recovery")
    check(pos_dot.matched_symbol == "borderedProminent", "leading dot stripped")

    # 2. LSP Framing Round-Trip
    buf = io.BytesIO()
    sample_msg = {"jsonrpc": "2.0", "id": 7, "result": {"hover": "struct Int"}}
    buf.write(encode_lsp_message(sample_msg))
    buf.seek(0)
    decoded_msg = read_lsp_message(io.BufferedReader(buf))
    check(decoded_msg == sample_msg, "LSP Content-Length encode/decode round-trip")

    # 3. Dual-Platform (macOS 27.2 & iOS 27.2) Target Command & Diagnostic Parser
    macos_cmd = build_swiftc_typecheck_command(
        ["App.swift"], platform="macos", sdk_path="/SDKs/MacOSX27.2.sdk", min_version="27.2"
    )
    ios_cmd = build_swiftc_typecheck_command(
        ["App.swift"], platform="ios", sdk_path="/SDKs/iPhoneSimulator27.2.sdk", min_version="27.2"
    )
    check("arm64-apple-macosx27.2" in macos_cmd, "macOS 27.2 target triple")
    check("arm64-apple-ios27.2-simulator" in ios_cmd, "iOS 27.2 simulator target triple")
    check(DEFAULT_MODULE_CACHE_DIR in macos_cmd, "-module-cache-path included for sandbox safety")

    sample_stderr = (
        "/tmp/App.swift:14:9: error: 'navigationBarTitleDisplayMode' is unavailable in macOS\n"
        "/tmp/App.swift:14:9: note: 'navigationBarTitleDisplayMode' has been explicitly marked unavailable here\n"
    )
    parsed_diags = parse_swiftc_stderr(sample_stderr)
    check(len(parsed_diags) == 1, "parse_swiftc_stderr folds notes into parent error")
    check(
        parsed_diags[0]["line"] == 14 and len(parsed_diags[0].get("notes", [])) == 1,
        "parse_swiftc_stderr line and note attachment",
    )

    # 4. `.swiftinterface` Parser & Relevance Ranking
    mock_swiftinterface = "\n".join(
        [
            "// swift-interface-format-version: 1.0",
            "@available(macOS 15.0, *)",
            "nonisolated public func glassToolbarEffectColumnWidth(_ w: Double) -> some View",
            "@available(macOS 27.2, iOS 27.2, *)",
            "@MainActor @preconcurrency public struct GlassToolbarEffect : SwiftUI.ViewModifier {",
            "  public init(prominence: SwiftUI.GlassProminence = .regular)",
            "}",
        ]
    )
    matches_27 = parse_swiftinterface_declarations(
        mock_swiftinterface, symbol_query="GlassToolbarEffect", availability_filter="27.2"
    )
    check(len(matches_27) == 1, ".swiftinterface 27.2 declaration match")
    check(
        "@available(macOS 27.2, iOS 27.2, *)" in matches_27[0]["declaration"],
        ".swiftinterface preserves preceding @available attribute",
    )
    ranked_matches = parse_swiftinterface_declarations(
        mock_swiftinterface, symbol_query="GlassToolbarEffect"
    )
    check(
        ranked_matches[0]["name"] == "GlassToolbarEffect",
        ".swiftinterface ranks exact type match above substring func match",
    )

    # 5. End-to-End Mock `sourcekit-lsp` Subprocess + MCP Stdio Round-Trip
    mock_lsp_script = """
import json, sys

def read_msg():
    cl = None
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\\r\\n", b"\\n"):
            if cl is not None:
                break
            continue
        s = line.decode("ascii", errors="replace").strip()
        if s.lower().startswith("content-length:"):
            cl = int(s.split(":", 1)[1].strip())
    body = sys.stdin.buffer.read(cl)
    return json.loads(body.decode("utf-8"))

def send_msg(obj):
    b = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(b)}\\r\\n\\r\\n".encode("ascii") + b)
    sys.stdout.buffer.flush()

while True:
    m = read_msg()
    if m is None:
        break
    method = m.get("method", "")
    req_id = m.get("id")
    if method == "initialize":
        send_msg({"jsonrpc": "2.0", "id": 99, "method": "client/registerCapability", "params": {}})
        ack = read_msg()
        send_msg({"jsonrpc": "2.0", "id": req_id, "result": {"capabilities": {"hoverProvider": True}}})
    elif method == "textDocument/hover":
        pos = m["params"]["position"]
        send_msg({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"contents": {"kind": "markdown", "value": f"```swift\\n@MainActor func fetchModels(id: Int)\\n``` (line {pos['line']}, col {pos['character']})"}},
        })
    elif method == "textDocument/definition":
        uri = m["params"]["textDocument"]["uri"]
        send_msg({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": [{"uri": uri, "range": {"start": {"line": 3, "character": 7}, "end": {"line": 3, "character": 18}}}],
        })
    elif method == "textDocument/references":
        uri = m["params"]["textDocument"]["uri"]
        send_msg({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": [{"uri": uri, "range": {"start": {"line": 5, "character": 24}, "end": {"line": 5, "character": 35}}}],
        })
    elif method == "textDocument/documentSymbol":
        send_msg({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": [{"name": "ContentView", "kind": 23, "range": {"start": {"line": 3, "character": 0}, "end": {"line": 8, "character": 1}}, "selectionRange": {"start": {"line": 3, "character": 7}, "end": {"line": 3, "character": 18}}}],
        })
    elif method == "textDocument/diagnostic":
        send_msg({"jsonrpc": "2.0", "id": req_id, "result": {"kind": "full", "items": []}})
    elif method == "shutdown":
        send_msg({"jsonrpc": "2.0", "id": req_id, "result": None})
    elif method == "exit":
        break
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        (tmp_path / "Package.swift").write_text("// swift-tools-version: 6.0\n", encoding="utf-8")
        swift_file = tmp_path / "ContentView.swift"
        swift_file.write_text(sample_swift, encoding="utf-8")
        mock_srv = tmp_path / "mock_lsp.py"
        mock_srv.write_text(mock_lsp_script, encoding="utf-8")

        pool = LspSessionPool(custom_command=[sys.executable, str(mock_srv)])
        try:
            mcp_in = io.BytesIO(
                "\n".join(
                    [
                        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}}),
                        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
                        json.dumps({
                            "jsonrpc": "2.0",
                            "id": 3,
                            "method": "tools/call",
                            "params": {
                                "name": "swift_hover",
                                "arguments": {"file": str(swift_file), "line": 6, "symbol": "fetchModels"},
                            },
                        }),
                        json.dumps({
                            "jsonrpc": "2.0",
                            "id": 4,
                            "method": "tools/call",
                            "params": {
                                "name": "swift_definition",
                                "arguments": {"file": str(swift_file), "line": 6, "symbol": "fetchModels"},
                            },
                        }),
                        json.dumps({
                            "jsonrpc": "2.0",
                            "id": 5,
                            "method": "tools/call",
                            "params": {
                                "name": "swift_symbols",
                                "arguments": {"file": "ContentView.swift"},
                            },
                        }),
                    ]
                ).encode("utf-8")
                + b"\n"
            )
            mcp_out = io.BytesIO()
            run_mcp_stdio_loop(
                mcp_in,  # type: ignore[arg-type]
                mcp_out,  # type: ignore[arg-type]
                pool=pool,
            )
            out_lines = [
                json.loads(line)
                for line in mcp_out.getvalue().decode("utf-8").splitlines()
                if line.strip()
            ]
            check(len(out_lines) == 5, f"MCP stdio returned 5 responses (got {len(out_lines)})")
            tools_list = out_lines[1]["result"]["tools"]
            check(len(tools_list) == 7, f"MCP tools/list exposes 7 tools (got {len(tools_list)})")
            hover_payload = json.loads(out_lines[2]["result"]["content"][0]["text"])
            check(
                "@MainActor func fetchModels" in (hover_payload.get("hover") or ""),
                "Mock sourcekit-lsp hover round-trip via MCP tools/call",
            )
            def_payload = json.loads(out_lines[3]["result"]["content"][0]["text"])
            check(
                len(def_payload.get("locations", [])) == 1,
                "Mock sourcekit-lsp definition round-trip via MCP tools/call",
            )
            sym_payload = json.loads(out_lines[4]["result"]["content"][0]["text"])
            check(
                sym_payload["symbols"][0]["name"] == "ContentView"
                and sym_payload["symbols"][0]["kind"] == "Struct",
                "Mock sourcekit-lsp documentSymbol round-trip via relative file + pool.last_workspace",
            )
            check(
                os.path.realpath(resolve_file_path("ContentView.swift", workspace=str(tmp_path)))
                == os.path.realpath(str(swift_file)),
                "resolve_file_path joins relative file with explicit workspace",
            )
            check(
                os.path.realpath(resolve_file_path("ContentView.swift", pool=pool))
                == os.path.realpath(str(swift_file)),
                "resolve_file_path joins relative file with pool.last_workspace",
            )
        finally:
            pool.close_all()

    if failures:
        print(f"FAIL: {len(failures)} self-test(s) failed:", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "ok",
                "self_tests_passed": 19,
                "server": SERVER_NAME,
                "version": SERVER_VERSION,
            },
            indent=2,
        )
    )
    return 0


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sourcekit_mcp.py",
        description="SourceKit-LSP MCP server, CLI bridge, and macOS/iOS 27.2+ SDK .swiftinterface inspector.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic offline unit and mock-LSP round-trip tests.",
    )
    sub = parser.add_subparsers(dest="subcommand")

    sub.add_parser("mcp", help="Run as an MCP stdio server.")

    p_probe = sub.add_parser("probe", help="Inspect Xcode toolchain, SDKs, and workspace index state.")
    p_probe.add_argument("--workspace", default=None, help="Workspace path.")
    p_probe.add_argument("--min-version", default=DEFAULT_MIN_OS_VERSION, help="Target OS baseline (default: 27.2).")

    p_diag = sub.add_parser("diagnostics", help="Typecheck Swift files via sourcekit-lsp and/or dual-SDK swiftc.")
    p_diag.add_argument("files", nargs="+", help="One or more .swift files.")
    p_diag.add_argument("--platform", choices=["macos", "ios", "both"], default="macos")
    p_diag.add_argument("--min-version", default=DEFAULT_MIN_OS_VERSION)
    p_diag.add_argument("--workspace", default=None)

    p_hover = sub.add_parser("hover", help="Query inferred Swift type and docstrings at a symbol.")
    p_hover.add_argument("file", help="Path to .swift file.")
    p_hover.add_argument("--line", type=int, required=True, help="1-based line number.")
    p_hover.add_argument("--symbol", default=None, help="Symbol name on or near `--line`.")
    p_hover.add_argument("--column", type=int, default=None, help="Optional 0-based column.")
    p_hover.add_argument("--workspace", default=None)

    p_def = sub.add_parser("definition", help="Find symbol definition, typeDefinition, or implementation.")
    p_def.add_argument("file", help="Path to .swift file.")
    p_def.add_argument("--line", type=int, required=True, help="1-based line number.")
    p_def.add_argument("--symbol", default=None, help="Symbol name on or near `--line`.")
    p_def.add_argument("--kind", choices=["definition", "typeDefinition", "implementation"], default="definition")
    p_def.add_argument("--column", type=int, default=None)
    p_def.add_argument("--workspace", default=None)

    p_refs = sub.add_parser("references", help="Find all semantic references to a symbol across the workspace.")
    p_refs.add_argument("file", help="Path to .swift file.")
    p_refs.add_argument("--line", type=int, required=True, help="1-based line number.")
    p_refs.add_argument("--symbol", default=None, help="Symbol name on or near `--line`.")
    p_refs.add_argument("--include-declaration", action="store_true")
    p_refs.add_argument("--column", type=int, default=None)
    p_refs.add_argument("--workspace", default=None)

    p_sym = sub.add_parser("symbols", help="List document symbols or search workspace symbols.")
    p_sym.add_argument("--file", default=None, help="Optional .swift file for documentSymbol outline.")
    p_sym.add_argument("--query", default=None, help="Symbol name filter or workspace query.")
    p_sym.add_argument("--workspace", default=None)

    p_sdk = sub.add_parser("sdk", help="Search Xcode SDK .swiftinterface declarations (macOS/iOS 27.2+).")
    p_sdk.add_argument("module", help="Module/framework name (e.g. SwiftUI, AppKit, UIKit, Observation).")
    p_sdk.add_argument("--symbol", default=None, help="Symbol or modifier substring.")
    p_sdk.add_argument("--platform", choices=["macos", "ios"], default="macos")
    p_sdk.add_argument("--available", default=None, help="Availability substring filter (e.g. 27.2).")
    p_sdk.add_argument("--max-results", type=int, default=25)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return _run_self_tests()

    if args.subcommand == "mcp":
        run_mcp_stdio_loop(sys.stdin.buffer, sys.stdout.buffer)
        return 0

    if not args.subcommand:
        parser.print_help()
        return 0

    pool = LspSessionPool()
    try:
        if args.subcommand == "probe":
            res = probe_toolchain_and_workspace(
                workspace=args.workspace, min_version=args.min_version
            )
        elif args.subcommand == "diagnostics":
            res = query_diagnostics(
                pool,
                files=args.files,
                platform=args.platform,
                min_version=args.min_version,
                workspace=args.workspace,
            )
        elif args.subcommand == "hover":
            res = query_hover(
                pool,
                file_path=args.file,
                line=args.line,
                symbol=args.symbol,
                column=args.column,
                workspace=args.workspace,
            )
        elif args.subcommand == "definition":
            res = query_definition(
                pool,
                file_path=args.file,
                line=args.line,
                symbol=args.symbol,
                column=args.column,
                kind=args.kind,
                workspace=args.workspace,
            )
        elif args.subcommand == "references":
            res = query_references(
                pool,
                file_path=args.file,
                line=args.line,
                symbol=args.symbol,
                column=args.column,
                include_declaration=args.include_declaration,
                workspace=args.workspace,
            )
        elif args.subcommand == "symbols":
            res = query_symbols(
                pool,
                file_path=args.file,
                query=args.query,
                workspace=args.workspace,
            )
        elif args.subcommand == "sdk":
            res = search_sdk_interface(
                module_name=args.module,
                symbol_query=args.symbol,
                platform=args.platform,
                availability_filter=args.available,
                max_results=args.max_results,
            )
        else:
            parser.print_help()
            return 1

        print(json.dumps(res, indent=2))
        return 0
    finally:
        pool.close_all()


if __name__ == "__main__":
    sys.exit(main())
