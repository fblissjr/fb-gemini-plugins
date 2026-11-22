#!/usr/bin/env python3
"""Print a capability matrix for a running heylook server.

Model ids are install-local -- heylook's registry is override-only, so the
roster reflects whatever the operator has downloaded. This resolves what is
actually served, so a client never ships a literal id.

Usage:
    python3 probe.py [--base http://localhost:8000] [--api-key KEY] [--json] [--need vision]

Exit codes:
    0  read the server, and every --need is served
    1  could not read the server: unreachable, refused, auth required, or not
       answering heylook's shapes. The message says which
    2  read the server, but no served model has every --need. An empty
       roster counts

The code is derived once and both renderers return it, because the two used
to disagree: `--need vision` against an empty roster exited 0 in text mode
and 2 in --json.

Auth: when heylook's server-wide access gate is enabled (2.0.263+:
HEYLOOK_API_KEY or mode-600 <HOME>/.heylook/api_key), every route requires a
key. `probe.py` resolves --api-key, HEYLOOK_API_KEY, or <HOME>/.heylook/api_key
($HEYLOOK_API_KEY_FILE), sends it as `Authorization: Bearer <key>` only to the
requested origin, and never prints it. A 403 on GET is heylook's Host check
(DNS-rebinding guard), not auth.

Standard library only; no install step.
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

EXIT_OK = 0
EXIT_UNREADABLE = 1
EXIT_UNMATCHED = 2


def _origin(url: str) -> tuple:
    p = urllib.parse.urlsplit(url)
    return (p.scheme, p.hostname, p.port or (443 if p.scheme == "https" else 80))


class _StripAuthAcrossOrigins(urllib.request.HTTPRedirectHandler):
    """Drop auth credentials when a redirect leaves the origin they were for.

    urllib copies every header onto the redirected request, so without this a
    302 hands the key to whatever host the Location names. Same-origin
    redirects keep it: an http path rewrite on the same server is a real
    deployment and breaking it would push people back to no auth at all.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and _origin(newurl) != _origin(req.full_url):
            for store in (new.headers, new.unredirected_hdrs):
                for k in [k for k in store if k.lower() in ("authorization", "x-api-key")]:
                    del store[k]
        return new


_OPENER = urllib.request.build_opener(_StripAuthAcrossOrigins)


def resolve_api_key(explicit: str | None = None) -> str | None:
    """Resolve API key from --api-key, HEYLOOK_API_KEY, or HEYLOOK_API_KEY_FILE / <HOME>/.heylook/api_key."""
    for candidate in (explicit, os.environ.get("HEYLOOK_API_KEY")):
        if candidate and candidate.strip():
            return candidate.strip()
    if "HEYLOOK_API_KEY_FILE" in os.environ:
        raw_path = os.environ["HEYLOOK_API_KEY_FILE"].strip()
        key_paths = [(Path(raw_path).expanduser(), 0o027)] if raw_path else []
    else:
        key_paths = [(Path.home() / ".heylook" / "api_key", 0o077)]
    for p, forbidden_mask in key_paths:
        try:
            st = p.stat()
            if p.is_file() and (st.st_mode & forbidden_mask) == 0:
                val = p.read_text(encoding="utf-8").strip()
                if val:
                    return val
        except OSError:
            pass
    return None


class Unreadable(Exception):
    """A server we could not read. `hint` is the operator's next move.

    Distinct from "no model matched": that is an answer, this is the absence
    of one, and they send the operator to different places.
    """

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.hint = hint


def _error_payload(e: urllib.error.HTTPError) -> dict:
    try:
        raw = e.read()
        parsed = json.loads(raw.decode("utf-8", errors="replace")) if raw else {}
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def fetch(base: str, path: str, timeout: float, api_key: str | None = None) -> dict:
    url = f"{base.rstrip('/')}{path}"
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        with _OPENER.open(
            urllib.request.Request(url, headers=headers), timeout=timeout
        ) as r:
            body = r.read()
            ctype = r.headers.get("Content-Type", "unknown")
    except urllib.error.HTTPError as e:
        # HTTPError subclasses URLError subclasses OSError, so it must be
        # caught FIRST -- a 401 from a running server is not a dead server.
        if e.code == 403:
            # heylook's Host check (2.0.137) answers 403 to a Host header it
            # does not know -- a LAN client using a DNS name. Not a credential.
            raise Unreadable(
                f"{base} answered HTTP 403 for {path}.",
                "heylook refuses a Host it does not know. Address it by IP or "
                "localhost, or add this hostname to `allowed_hosts` in the "
                "server's heylook.toml.",
            ) from e
        if e.code == 401:
            # From 2.0.263, heylook's own AccessGateMiddleware gates every
            # route when HEYLOOK_API_KEY or <HOME>/.heylook/api_key is set (or
            # a proxy in front of it may gate discovery). Branch on whether a
            # key was already sent so the hint never tells someone to pass a
            # flag they just passed.
            hint = (
                "that credential was rejected by heylook's access gate (or a "
                "proxy in front of it). Check --api-key / HEYLOOK_API_KEY and "
                "the target URL."
                if api_key else
                "this server requires authentication (heylook's access gate or "
                "a proxy in front of it). Pass --api-key, set HEYLOOK_API_KEY, "
                "or create a mode-600 <HOME>/.heylook/api_key."
            )
            raise Unreadable(f"{base} answered HTTP 401 for {path}.", hint) from e
        if e.code == 503:
            err_body = _error_payload(e)
            err_obj = err_body.get("error") if isinstance(err_body.get("error"), dict) else {}
            if err_obj.get("code") == "auth_misconfigured":
                detail = err_body.get("detail") or err_obj.get("message") or "access key file is misconfigured."
                raise Unreadable(
                    f"{base} answered HTTP 503 (auth_misconfigured) for {path}.",
                    str(detail),
                ) from e
        raise Unreadable(
            f"{base} answered HTTP {e.code} for {path}.",
            f"a heylook server serves {path}. Check the base URL and port.",
        ) from e
    except http.client.HTTPException as e:
        # NOT an OSError: BadStatusLine when something that is not an HTTP
        # server answers, IncompleteRead when a body is cut off mid-load.
        raise Unreadable(
            f"{base} did not speak HTTP for {path} ({type(e).__name__}: {e}).",
            "is that a heylook server?",
        ) from e
    except (urllib.error.URLError, OSError) as e:
        raise Unreadable(
            f"cannot reach {base}: {e}",
            "start the server with `heylookllm` on the host machine.",
        ) from e

    try:
        payload = json.loads(body.decode())
    except (ValueError, UnicodeDecodeError) as e:
        # JSONDecodeError is a ValueError, so the OSError arm above never
        # sees it. The realistic trigger is another service already on :8000.
        raise Unreadable(
            f"{base} returned a non-JSON body for {path} (content-type: {ctype}).",
            "is that a heylook server?",
        ) from e

    if not isinstance(payload, dict):
        raise Unreadable(
            f"{base} returned {type(payload).__name__}, not an object, for {path}.",
            "is that a heylook server?",
        )
    return payload


def models_from(payload: dict, base: str) -> tuple[list[dict], int]:
    """Usable rows plus the count skipped.

    One malformed row is not an unreadable server: the rest of the roster is
    still the answer to "what can this machine serve". Exit 1 is reserved for
    a roster with nothing usable in it, because that is the only case where
    the operator has no model to pick.
    """
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise Unreadable(
            f"{base} returned /v1/models with no `data` list.",
            "is that a heylook server?",
        )
    usable = [r for r in rows if isinstance(r, dict) and r.get("id")]
    skipped = len(rows) - len(usable)
    if rows and not usable:
        raise Unreadable(
            f"{base} returned {len(rows)} /v1/models row(s), none with an `id`.",
            "the roster is unusable: an id is what a client would send.",
        )
    return usable, skipped


def _dig(row: dict, *keys):
    """Walk nested dicts; None as soon as a level is missing or not a dict."""
    node = row
    for k in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(k)
    return node


def _context(row: dict) -> str:
    """engine.context.length is a fact, {value, provenance, source}."""
    value = _dig(row, "engine", "context", "length", "value")
    return str(value) if isinstance(value, int) else "-"


def _depth(row: dict) -> str:
    """The model's own reasoning_effort words, shown untranslated."""
    values = _dig(row, "engine", "thinking", "depth", "values")
    if not isinstance(values, list):
        return "-"
    return ",".join(str(v) for v in values) or "-"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--base", default="http://localhost:8000")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument(
        "--api-key",
        default=None,
        help="API key for heylook's access gate (defaults to HEYLOOK_API_KEY or <HOME>/.heylook/api_key); never printed",
    )
    ap.add_argument("--need", action="append", default=[], metavar="CAP",
                    help="require this capability; repeatable. Exit 2 if unmatched")
    args = ap.parse_args(argv)

    api_key = resolve_api_key(args.api_key)

    try:
        models, skipped = models_from(
            fetch(args.base, "/v1/models", args.timeout, api_key), args.base
        )
    except Unreadable as e:
        print(str(e), file=sys.stderr)
        if e.hint:
            print(e.hint, file=sys.stderr)
        return EXIT_UNREADABLE

    if skipped:
        print(f"note: skipped {skipped} /v1/models row(s) with no `id`.", file=sys.stderr)

    # Capabilities are best-effort extra context; a server that answers
    # /v1/models but not this is still usable. Deliberately broad: the roster
    # is already in hand, so NOTHING here is worth failing the probe over.
    try:
        caps = fetch(args.base, "/v1/capabilities", args.timeout, api_key)
    except Exception:
        caps = {}

    need = set(args.need)
    matched = [m for m in models if need <= set(m.get("capabilities") or [])]

    # Derived once. Both renderers return this; they used to disagree.
    status = EXIT_OK if matched or not need else EXIT_UNMATCHED

    if args.json:
        json.dump({"base": args.base,
                   "server_version": caps.get("server_version"),
                   "models": models,
                   "matched": [m["id"] for m in matched]},
                  sys.stdout, indent=2)
        sys.stdout.write("\n")
        return status

    print(f"heylook {caps.get('server_version', 'unknown')} at {args.base}")
    print()

    if not models:
        print("no models served. check the [scan] folders in heylook.toml.")
    else:
        matched_ids = {m["id"] for m in matched}
        width = max(len(m["id"]) for m in models)
        # Sized to the data: a vocabulary is as long as the template says.
        dwidth = max([len("DEPTH")] + [len(_depth(m)) for m in models])
        print(f"{'MODEL'.ljust(width)}  {'PROVIDER':<8}  {'CONTEXT':>8}  "
              f"{'DEPTH'.ljust(dwidth)}  CAPABILITIES")
        print(f"{'-' * width}  {'-' * 8}  {'-' * 8}  {'-' * dwidth}  {'-' * 40}")
        for m in sorted(models, key=lambda r: r["id"]):
            cap = ",".join(m.get("capabilities") or []) or "-"
            mark = "*" if need and m["id"] in matched_ids else ""
            print(f"{m['id'].ljust(width)}  {(m.get('provider') or '-'):<8}  "
                  f"{_context(m):>8}  {_depth(m).ljust(dwidth)}  {cap}{mark}".rstrip())

    if need:
        print()
        if matched:
            print(f"* serves {sorted(need)}: {', '.join(m['id'] for m in matched)}")
        else:
            print(f"no served model has {sorted(need)}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
