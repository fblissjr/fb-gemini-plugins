#!/usr/bin/env python3
"""Unit and live-toolchain integration tests for skills/swift-lsp/skills/swift-lsp/scripts/sourcekit_mcp.py."""

from __future__ import annotations

import importlib.util
import io
import pathlib
import sys
import tempfile
import time
import unittest

SCRIPT_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "skills"
    / "swift-lsp"
    / "scripts"
    / "sourcekit_mcp.py"
)
SPEC = importlib.util.spec_from_file_location("sourcekit_mcp", SCRIPT_PATH)
assert SPEC and SPEC.loader
sourcekit_mcp = importlib.util.module_from_spec(SPEC)
sys.modules["sourcekit_mcp"] = sourcekit_mcp
SPEC.loader.exec_module(sourcekit_mcp)


class TestSourceKitMcp(unittest.TestCase):
    def test_utf16_and_symbol_resolution(self) -> None:
        code = "\n".join(
            [
                "import SwiftUI",
                "@MainActor",
                "struct WindowHUD: View {",
                '    var title = "🔥 Local LLM"',
                "    var body: some View {",
                "        Text(title).font(.headline)",
                "    }",
                "}",
            ]
        )
        line4 = code.splitlines()[3]
        idx_local = line4.index("Local")
        utf16_col = sourcekit_mcp.char_index_to_utf16_col(line4, idx_local)
        self.assertEqual(utf16_col, idx_local + 1)
        self.assertEqual(
            sourcekit_mcp.utf16_col_to_char_index(line4, utf16_col),
            idx_local,
        )

        pos = sourcekit_mcp.resolve_symbol_position(
            code, line_1based=4, symbol=".headline"
        )
        self.assertEqual(pos.line_1based, 6)
        self.assertEqual(pos.matched_symbol, "headline")

    def test_lsp_framing_round_trip(self) -> None:
        payload = {"jsonrpc": "2.0", "id": 42, "result": {"status": "ready"}}
        encoded = sourcekit_mcp.encode_lsp_message(payload)
        decoded = sourcekit_mcp.read_lsp_message(io.BufferedReader(io.BytesIO(encoded)))
        self.assertEqual(decoded, payload)

    def test_dual_platform_target_triples_27_2(self) -> None:
        macos_cmd = sourcekit_mcp.build_swiftc_typecheck_command(
            ["HUD.swift"],
            platform="macos",
            sdk_path="/Xcode/MacOSX27.2.sdk",
            min_version="27.2",
        )
        ios_cmd = sourcekit_mcp.build_swiftc_typecheck_command(
            ["HUD.swift"],
            platform="ios",
            sdk_path="/Xcode/iPhoneSimulator27.2.sdk",
            min_version="27.2",
        )
        self.assertIn("arm64-apple-macosx27.2", macos_cmd)
        self.assertIn("arm64-apple-ios27.2-simulator", ios_cmd)
        self.assertIn(sourcekit_mcp.DEFAULT_MODULE_CACHE_DIR, macos_cmd)

    def test_swiftinterface_declaration_parser_and_ranking(self) -> None:
        sample = "\n".join(
            [
                "@available(macOS 15.0, *)",
                "nonisolated public func meshFloatingPanelStyle(_ s: Int) -> some View",
                "@available(macOS 27.2, iOS 27.2, *)",
                "@MainActor @preconcurrency public struct MeshFloatingPanel : SwiftUI.Scene {",
                "  public init(id: Swift.String)",
                "}",
            ]
        )
        matches = sourcekit_mcp.parse_swiftinterface_declarations(
            sample,
            symbol_query="MeshFloatingPanel",
        )
        self.assertGreaterEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "MeshFloatingPanel")
        self.assertEqual(matches[0]["kind"], "struct")
        self.assertIn("@available(macOS 27.2, iOS 27.2, *)", matches[0]["declaration"])

    def test_instant_xpc_fatal_error_detection_no_timeout_hang(self) -> None:
        """Verify that if sourcekit-lsp emits `SOURCEKITD FATAL ERROR: Service is invalid` without exiting,
        SourceKitLspSession aborts in <1s instead of hanging for the full request timeout."""
        broken_lsp_script = """
import json, sys, time
line = sys.stdin.buffer.readline()
while sys.stdin.buffer.readline() not in (b"\\r\\n", b"\\n", b""):
    pass
cl = int(line.decode().split(":")[1].strip())
msg = json.loads(sys.stdin.buffer.read(cl).decode())
b = json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": {"capabilities": {}}}).encode()
sys.stdout.buffer.write(f"Content-Length: {len(b)}\\r\\n\\r\\n".encode() + b)
sys.stdout.buffer.flush()
sys.stderr.write("SOURCEKITD FATAL ERROR: Service is invalid\\n")
sys.stderr.flush()
time.sleep(30)
"""
        with tempfile.TemporaryDirectory(dir="/tmp") as tmpdir:
            tmp = pathlib.Path(tmpdir)
            srv = tmp / "broken_lsp.py"
            srv.write_text(broken_lsp_script, encoding="utf-8")
            f = tmp / "Sample.swift"
            f.write_text("public struct Sample {}\n", encoding="utf-8")

            session = sourcekit_mcp.SourceKitLspSession(
                workspace_root=tmp,
                command=[sys.executable, str(srv)],
            )
            t0 = time.monotonic()
            try:
                with self.assertRaises(sourcekit_mcp.SourceKitUnavailableError):
                    session.sync_file(f)
                    session.request(
                        "textDocument/documentSymbol",
                        {"textDocument": {"uri": sourcekit_mcp.path_to_file_uri(f)}},
                        timeout=8.0,
                    )
                elapsed = time.monotonic() - t0
                self.assertLess(elapsed, 2.0, f"Expected fast abort (<2s), took {elapsed:.2f}s")
            finally:
                session.close()

    def test_live_swiftc_multi_file_and_sdk_integration(self) -> None:
        probe = sourcekit_mcp.probe_toolchain_and_workspace()
        if not probe["sdks"]["macosx"]["available"]:
            self.skipTest("macOS SDK not available on this host")

        # 1. Test live SDK .swiftinterface search & exact-type ranking on SwiftUI
        sdk_res = sourcekit_mcp.search_sdk_interface(
            module_name="SwiftUI",
            symbol_query="NavigationSplitView",
            platform="macos",
            max_results=3,
        )
        self.assertGreaterEqual(sdk_res["count"], 1)
        self.assertEqual(sdk_res["matches"][0]["name"], "NavigationSplitView")
        self.assertEqual(sdk_res["matches"][0]["kind"], "struct")

        # 2. Test multi-file SwiftPM target symbols, hover (with cross-file docstring), definition, references, and dual-SDK diagnostics
        with tempfile.TemporaryDirectory(dir="/tmp") as tmpdir:
            root = pathlib.Path(tmpdir)
            (root / "Package.swift").write_text(
                "// swift-tools-version: 6.2\nimport PackageDescription\n"
                'let package = Package(name: "Demo", platforms: [.macOS("27.2"), .iOS("27.2")], targets: [.target(name: "Demo")])\n',
                encoding="utf-8",
            )
            src = root / "Sources" / "Demo"
            src.mkdir(parents=True)
            f_models = src / "Models.swift"
            f_models.write_text(
                "import Foundation\n\n"
                "@MainActor\n"
                "public struct ModelService: Sendable {\n"
                "    public let endpoint: String\n"
                "    public init(endpoint: String) { self.endpoint = endpoint }\n"
                "    /// Fetch served model IDs from /v1/models.\n"
                "    public func fetchModels(limit: Int) -> [String] { [endpoint] }\n"
                "}\n",
                encoding="utf-8",
            )
            f_runner = src / "Runner.swift"
            f_runner.write_text(
                "import Foundation\n\n"
                "@MainActor\n"
                "public func runDemo() -> [String] {\n"
                '    let svc = ModelService(endpoint: "http://localhost:8080")\n'
                "    return svc.fetchModels(limit: 5)\n"
                "}\n",
                encoding="utf-8",
            )

            pool = sourcekit_mcp.LspSessionPool()
            try:
                syms = sourcekit_mcp.query_symbols(pool, file_path=str(f_models))
                sym_names = [s["name"] for s in syms["symbols"]]
                self.assertIn("ModelService", sym_names)
                self.assertIn("ModelService.fetchModels(limit:)", sym_names)

                hov = sourcekit_mcp.query_hover(
                    pool, file_path=str(f_runner), line=6, symbol="fetchModels"
                )
                self.assertIn("(ModelService) -> (Int) -> [String]", hov["hover"] or "")
                self.assertIn("Fetch served model IDs", hov["hover"] or "")

                defn = sourcekit_mcp.query_definition(
                    pool, file_path=str(f_runner), line=6, symbol="fetchModels"
                )
                self.assertEqual(len(defn["locations"]), 1)
                self.assertEqual(defn["locations"][0]["line"], 8)

                refs = sourcekit_mcp.query_references(
                    pool, file_path=str(f_models), line=8, symbol="fetchModels"
                )
                self.assertEqual(refs["count"], 1)
                self.assertEqual(refs["references"][0]["line"], 6)

                diags = sourcekit_mcp.query_diagnostics(
                    pool, files=[str(f_runner)], platform="both"
                )
                self.assertEqual(diags["error_count"], 0)

                # Verify relative file paths resolve via pool.last_workspace even when cwd is outside the workspace
                rel_hov = sourcekit_mcp.query_hover(
                    pool,
                    file_path="Sources/Demo/Runner.swift",
                    line=6,
                    symbol="fetchModels",
                )
                self.assertIn("(ModelService) -> (Int) -> [String]", rel_hov["hover"] or "")
            finally:
                pool.close_all()

    def test_mcp_config_declares_eager_tools(self) -> None:
        import json

        mcp_cfg_path = SCRIPT_PATH.parent.parent.parent.parent / "mcp_config.json"
        cfg = json.loads(mcp_cfg_path.read_text(encoding="utf-8"))
        tools_cfg = cfg["mcpServers"]["swift-lsp-sourcekit"]["tools"]
        expected_tools = {t["name"] for t in sourcekit_mcp.MCP_TOOLS_SCHEMA}
        self.assertEqual(set(tools_cfg.keys()), expected_tools)
        for tool_name, meta in tools_cfg.items():
            self.assertTrue(meta.get("eager"), f"Expected eager=True for {tool_name}")

    def test_full_self_test_suite(self) -> None:
        self.assertEqual(sourcekit_mcp._run_self_tests(), 0)


if __name__ == "__main__":
    unittest.main()
