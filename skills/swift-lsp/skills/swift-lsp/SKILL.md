---
name: swift-lsp
description: Bridges Apple SourceKit-LSP (xcrun sourcekit-lsp) and Xcode .swiftinterface SDK headers into Antigravity App, Antigravity CLI (agy), Claude Code, and Gemini Spark for Swift 6, macOS 27.2+, and iOS 27.2+ development. Provides symbol-anchored hover, definition, typeDefinition, implementation, references, document/workspace symbols, sandbox-free incremental diagnostics across both macOS 27.2 and iOS 27.2 simulator targets, and direct .swiftinterface signature lookup. Use when user says "swift lsp", "sourcekit-lsp", "check swift types", "swift diagnostics", "verify macos and ios targets", "lookup swiftinterface", "macos 27.2 api", "ios 27.2 api", "resolve swift concurrency error", or writes/refactors Swift 6, SwiftUI, AppKit, UIKit, or SwiftPM code.
---

# Swift LSP & macOS / iOS 27.2+ SDK Inspector (`swift-lsp`)

You have access to **SourceKit-LSP (`xcrun sourcekit-lsp`)** and the local **Xcode `.swiftinterface` SDK headers** via the `swift-lsp-sourcekit` MCP server and its standalone CLI (`scripts/sourcekit_mcp.py`).

When working in a Swift workspace targeting **macOS 27.2+** and **iOS 27.2+** (Swift 6 language mode), follow these operational rules to replace slow cold `swift build` / `xcodebuild` loops and training-cutoff guesses with compiler-verified truth.

---

## Core Operational Rules

### Rule 1 — Assume the 27.2+ & Swift 6 Baseline
- Unless `Package.swift` or `.xcodeproj` explicitly targets an older OS, treat **macOS 27.2** and **iOS 27.2** with **Swift 6 strict concurrency** as the unconditional minimum deployment baseline.
- Do **not** emit legacy `#available(macOS 14.0, iOS 17.0, *)` or `#available(macOS 15.0, iOS 18.0, *)` availability guards, and do **not** use legacy `ObservableObject` / `@Published` / `@StateObject` when `@Observable` (`Observation`) applies.

### Rule 2 — Symbol-Anchored LSP Queries Over Regex `grep`
- Never guess raw 0-indexed UTF-16 character column numbers when calling `swift_hover`, `swift_definition`, or `swift_references`.
- Always pass **`file` + 1-based `line` + `symbol`** (e.g., `{"file": "Sources/App/HUDPanel.swift", "line": 48, "symbol": "NSPanel"}` or `symbol: ".borderedProminent"`).
- `sourcekit_mcp.py` automatically searches `line ± 3`, strips leading dots or trailing argument parens, and computes the exact UTF-16 character offset (even across emoji/Unicode literals) before querying `sourcekit-lsp`.

### Rule 3 — Ground-Truth `.swiftinterface` Lookup Before Guessing 27.2 APIs
- Model training weights lag behind **macOS 27.2** and **iOS 27.2** SDK additions and updated `@MainActor` / `Sendable` annotations.
- Whenever you are unsure of a modifier signature, initializer label, or platform availability in `SwiftUI`, `AppKit`, `UIKit`, `Observation`, `FoundationModels`, `SwiftData`, or `Metal`, call **`swift_sdk_interface`** to read the exact declaration from the installed Xcode `.swiftinterface` on disk.

### Rule 4 — Dual-Platform (`macos` + `ios`) Diagnostics Before `swift build`
- On macOS, a default `swift build` or single-target `sourcekit-lsp` session only compiles the host platform (`arm64-apple-macosx27.2`), leaving `#if os(iOS)` blocks and UIKit/iOS-specific SwiftUI modifiers unchecked.
- After editing `.swift` files that share code between macOS and iOS (or before running a full build), call **`swift_diagnostics`** with `platform: "both"` (or `"macos"` / `"ios"` as appropriate) to type-check against both `arm64-apple-macosx27.2` and `arm64-apple-ios27.2-simulator` at zero `run_command` sandbox cost.

---

## Tool Selection Matrix

| Task | MCP Tool | CLI Subcommand (`scripts/sourcekit_mcp.py`) | Key Arguments |
| :--- | :--- | :--- | :--- |
| Check Xcode toolchain, `sourcekit-lsp`, `IndexStoreDB`, and 27.2+ SDKs | `swift_toolchain_probe` | `probe` | `workspace?`, `min_version="27.2"` |
| Incremental typecheck across macOS 27.2, iOS 27.2 simulator, or both | `swift_diagnostics` | `diagnostics` | `files: [...]`, `platform: "macos" \| "ios" \| "both"` |
| Inspect inferred type, `@MainActor`/`Sendable` isolation, or docstrings | `swift_hover` | `hover` | `file`, `line`, `symbol` |
| Jump to symbol declaration, type definition, or protocol witness | `swift_definition` | `definition` | `file`, `line`, `symbol`, `kind: "definition" \| "typeDefinition" \| "implementation"` |
| Find all semantic callers across the Swift workspace | `swift_references` | `references` | `file`, `line`, `symbol`, `include_declaration: false` |
| Get file outline (`Struct`/`Actor`/`Protocol`/`Method`) or search workspace | `swift_symbols` | `symbols` | `file?`, `query?` |
| Inspect real Xcode `MacOSX27.2.sdk` / `iPhoneSimulator27.2.sdk` headers | `swift_sdk_interface` | `sdk` | `module`, `symbol?`, `platform: "macos" \| "ios"`, `availability_filter?` |

---

## Standard 4-Step Swift Development Loop

1. **Preflight Probe (Once per Workspace)**:
   Call `swift_toolchain_probe` to verify the workspace type (`swiftpm` via `Package.swift`, `xcode-bsp` via `buildServer.json`, or `xcodeproj-unconfigured`), confirm whether `.build/*/index/store` is populated, and verify the installed `macosx` and `iphonesimulator` SDK versions.
2. **Navigate & Ground Against 27.2 SDKs**:
   - Use `swift_symbols` (`file`) to inspect file structure without reading entire large files.
   - Use `swift_definition` and `swift_references` (`file`, `line`, `symbol`) before changing protocol requirements or method signatures.
   - Use `swift_sdk_interface` (`module: "SwiftUI"`, `symbol: "..."`, `platform: "macos"` or `"ios"`) to verify exact 27.2+ framework declarations.
3. **Edit & Run Fast LSP / Dual-SDK Diagnostics**:
   - After modifying `.swift` files with `edit_file` / `write_file`, run `swift_diagnostics` (`files: [...]`, `platform: "macos"` or `"both"`).
   - `sourcekit_mcp.py` automatically sends `textDocument/didOpen` or `textDocument/didChange` with the latest disk contents before querying diagnostics.
   - If a Swift 6 concurrency or generic inference error appears, call `swift_hover` on the offending expression's symbol to see the exact compiler-inferred actor isolation and type.
4. **Final Build/Test Verification**:
   - Only after `swift_diagnostics` reports `error_count: 0`, run a single `swift test` or `xcodebuild` if full linker/runtime test verification is required.

---

## Standalone CLI Fallback

When running in environments without MCP or from a terminal shell:

```bash
SWIFT_LSP_PY="$HOME/.gemini/config/plugins/swift-lsp/skills/swift-lsp/scripts/sourcekit_mcp.py"
# Or from a local repo checkout:
# SWIFT_LSP_PY="skills/swift-lsp/skills/swift-lsp/scripts/sourcekit_mcp.py"

# 1. Probe toolchain, SDKs, and IndexStoreDB readiness
python3 "$SWIFT_LSP_PY" probe --workspace .

# 2. Check diagnostics across both macOS 27.2 and iOS 27.2 simulator
python3 "$SWIFT_LSP_PY" diagnostics Sources/App/ContentView.swift --platform both --min-version 27.2

# 3. Symbol-anchored hover, definition, and references
python3 "$SWIFT_LSP_PY" hover Sources/App/ContentView.swift --line 42 --symbol fetchModels
python3 "$SWIFT_LSP_PY" definition Sources/App/ContentView.swift --line 42 --symbol fetchModels
python3 "$SWIFT_LSP_PY" references Sources/App/ContentView.swift --line 42 --symbol fetchModels

# 4. Search installed Xcode SDK .swiftinterface headers
python3 "$SWIFT_LSP_PY" sdk SwiftUI --symbol NavigationSplitView --platform macos
python3 "$SWIFT_LSP_PY" sdk SwiftUI --available 27.2 --platform ios
```

---

## Progressive-Disclosure Reference Guides

Load the relevant reference guide when deeper troubleshooting is needed:

- **[`references/sourcekit-lsp-and-indexing.md`](references/sourcekit-lsp-and-indexing.md)**: Configuring `Package.swift` vs. `.xcodeproj` / `.xcworkspace` (`buildServer.json` via `xcode-build-server`), `IndexStoreDB` lifecycle, and optional `.agents/hooks.json` auto-diagnostics.
- **[`references/dual-sdk-macos-ios-27.md`](references/dual-sdk-macos-ios-27.md)**: Dual-platform (`macOS 27.2+` and `iOS 27.2+`) architecture, preventing iOS-on-macOS API hallucinations (`AppKit` vs. `UIKit` bridges), and querying `.swiftinterface` modules.
- **[`references/swift6-concurrency-diagnostics.md`](references/swift6-concurrency-diagnostics.md)**: Using `swift_hover` and `swift_definition` to resolve Swift 6 strict concurrency errors (`@MainActor`, `Sendable`, `sending`, region-based isolation, and `AsyncSequence` streaming).
