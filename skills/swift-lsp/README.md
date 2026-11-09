# swift-lsp

last updated: 2026-11-09

A **SourceKit-LSP (`xcrun sourcekit-lsp`) MCP Bridge, Xcode 27.2+ SDK `.swiftinterface` Inspector & Bundled Apple Agent Skills Search Plugin** (`v0.2.0`) for **Swift 6.4+, macOS 27.2+ ("Golden Gate"), and iOS 27.2+** development across **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+), **Claude Code**, **Gemini CLI**, and **Gemini Spark** (`Customize > Skills` and Gemini Enterprise).

---

## Why `swift-lsp`?

Building standalone macOS 27.2+ ("Golden Gate") desktop apps and iOS 27.2+ apps in **Antigravity App** and **Antigravity CLI (`agy`)** without a Language Server exposes five recurring failure modes:

1. **Model Training-Cutoff Blindness on 27.2+ SDKs & Golden Gate Rules**:
   - Pre-trained weights lag behind **macOS 27.2 ("Golden Gate")**, **iOS 27.2**, and **Swift 6.4.2** SDK additions, causing agents to emit legacy `#available(macOS 15, *)` boilerplate, misuse iOS-only toolbar APIs (`ToolbarOverflowMenu`, `.topBarPinnedTrailing`, `.navigationBarTitleDisplayMode`) on macOS, miss `@State` macro initialization rules, or hallucinate `CoreAI` / `FoundationModels` signatures.
   - `swift-lsp` queries your **local Xcode `MacOSX27.2.sdk` and `iPhoneSimulator27.2.sdk` `.swiftinterface` headers** (`System/Library/Frameworks/`, `System/Library/SubFrameworks/`, and `Developer/Library/Frameworks/`), **Apple's bundled Xcode 27 Agent Skills (`*.md.packaged`)**, **`AdditionalDocumentation` guides**, and **Swift 6.4 compiler diagnostic docs** directly on disk.
2. **LLM Column-Counting Errors on Raw LSP Coordinates**:
   - Standard LSP requires 0-indexed UTF-16 `(line, character)` offsets; LLMs frequently miscount character columns by 2–5 characters (especially around Unicode/emoji literals or indented chains).
   - Every navigation tool in `swift-lsp` (`swift_hover`, `swift_definition`, `swift_references`) accepts **`(file, line, symbol)`** and automatically resolves the exact UTF-16 character column across `line ± 3`.
3. **Host-Only Conditional Compilation Blind Spots (`#if os(iOS)` on macOS)**:
   - On a Mac, default `swift build` and `sourcekit-lsp` runs only type-check `arm64-apple-macosx27.2`, ignoring `#if os(iOS)` blocks completely.
   - `swift_diagnostics` supports `platform: "both"` to type-check against both `arm64-apple-macosx27.2` and `arm64-apple-ios27.2-simulator` in under a second while automatically inferring per-target Swift 6.4 flags (`.defaultIsolation(MainActor.self)`, `.strictMemorySafety()`, `.enableUpcomingFeature(...)`) from `Package.swift`.
4. **Two-Tier Execution (`sourcekit-lsp` + Macro-Safe `swiftc -dump-ast -disable-sandbox` Fallback)**:
   - **Tier 1 (MCP Host)**: When spawned via `mcp_config.json`, `swift-lsp` keeps `xcrun sourcekit-lsp` warm in the background (`--scratch-path /tmp/swift-lsp-scratch -Xswiftc -module-cache-path -Xswiftc /tmp/swift-lsp-module-cache`) for sub-second `IndexStoreDB` navigation and incremental diagnostics.
   - **Tier 2 (`sandbox-exec` Fallback)**: When invoked from a Mach-restricted terminal sandbox where `com.apple.SourceKitService` XPC is blocked (`SOURCEKITD FATAL ERROR: Service is invalid`), `sourcekit_mcp.py` detects the XPC failure on `stderr` in `<5ms` and falls back automatically to multi-file `xcrun swiftc -dump-ast` / `-typecheck` with `-disable-sandbox` (so `swift-plugin-server` expands `@State`, `@Observable`, `@Generable`, and `#Preview` macros without nested Seatbelt failures) and a sandbox-writable module cache (`/tmp/swift-lsp-module-cache`).

This plugin is fully self-contained; it can be used alone or chained with other skills in conversation.

---

## Seven MCP Tools & CLI Subcommands

| MCP Tool | CLI Subcommand | Purpose | Reference Guide |
| :--- | :--- | :--- | :--- |
| **`swift_toolchain_probe`** | `probe` | Inspects active Xcode toolchain, `sourcekit-lsp`, `Package.swift` vs. `buildServer.json` layout, `IndexStoreDB` health, installed `macosx` / `iphonesimulator` SDKs, and bundled Apple intelligence skills/docs. | [`references/sourcekit-lsp-and-indexing.md`](skills/swift-lsp/references/sourcekit-lsp-and-indexing.md) |
| **`swift_diagnostics`** | `diagnostics` | Pulls live diagnostics from warm `sourcekit-lsp` and/or runs macro-capable dual-platform (`macos`, `ios`, `both`) type-checking for macOS 27.2+ and iOS 27.2+ simulator targets with per-target `Package.swift` flags. | [`references/dual-sdk-macos-ios-27.md`](skills/swift-lsp/references/dual-sdk-macos-ios-27.md) |
| **`swift_hover`** | `hover` | Symbol-anchored `textDocument/hover`: returns compiler-inferred Swift types, `@MainActor` / `Sendable` isolation, generic constraints, and docstrings. | [`references/swift6-concurrency-diagnostics.md`](skills/swift-lsp/references/swift6-concurrency-diagnostics.md) |
| **`swift_definition`** | `definition` | Symbol-anchored `textDocument/definition`, `typeDefinition`, or `implementation` with inline `±4` line target source snippets. | [`references/sourcekit-lsp-and-indexing.md`](skills/swift-lsp/references/sourcekit-lsp-and-indexing.md) |
| **`swift_references`** | `references` | Finds all semantic call sites across the indexed Swift workspace (`IndexStoreDB`) with 1-line previews. | [`references/sourcekit-lsp-and-indexing.md`](skills/swift-lsp/references/sourcekit-lsp-and-indexing.md) |
| **`swift_symbols`** | `symbols` | Extracts hierarchical file outlines (`Struct`, `Class`, `Actor`, `Protocol`, `Method`, `Property`) or searches workspace-wide symbols. | [`references/sourcekit-lsp-and-indexing.md`](skills/swift-lsp/references/sourcekit-lsp-and-indexing.md) |
| **`swift_sdk_interface`** | `sdk` | Searches installed Xcode `MacOSX` and `iPhoneSimulator` `.swiftinterface` modules (`SwiftUI`, `AppKit`, `UIKit`, `Observation`, `FoundationModels`, `CoreAI`, `SwiftData`, `Testing`, `Evaluations`) and bundled Xcode 27 guides (`XcodeSkills`, `XcodeDocs`, `SwiftDiagnostics`). | [`references/dual-sdk-macos-ios-27.md`](skills/swift-lsp/references/dual-sdk-macos-ios-27.md) |

---

## Quick Start Examples

Define `SWIFT_LSP_PY` pointing to the installed plugin script (or local checkout):

```bash
SWIFT_LSP_PY="<HOME>/.gemini/config/plugins/swift-lsp/skills/swift-lsp/scripts/sourcekit_mcp.py"
# Or from a local fb-gemini-plugins checkout:
# SWIFT_LSP_PY="skills/swift-lsp/skills/swift-lsp/scripts/sourcekit_mcp.py"
```

### 1. Probe Active Xcode Toolchain, 27.2+ SDKs, and Bundled Apple Docs

```bash
python3 "$SWIFT_LSP_PY" probe --workspace .
```

### 2. Run Dual-Platform (`macOS 27.2` + `iOS 27.2` Simulator) Typechecking

```bash
python3 "$SWIFT_LSP_PY" diagnostics Sources/App/ContentView.swift --platform both --min-version 27.2
```

### 3. Symbol-Anchored Hover, Definition, and References

```bash
python3 "$SWIFT_LSP_PY" hover Sources/App/ContentView.swift --line 42 --symbol fetchModels
python3 "$SWIFT_LSP_PY" definition Sources/App/ContentView.swift --line 42 --symbol fetchModels
python3 "$SWIFT_LSP_PY" references Sources/App/ContentView.swift --line 42 --symbol fetchModels
```

### 4. Search Installed Xcode `.swiftinterface` Headers & Bundled Xcode 27 Guides

```bash
python3 "$SWIFT_LSP_PY" sdk SwiftUI --symbol glassEffect --platform macos --guides
python3 "$SWIFT_LSP_PY" sdk CoreAI --symbol NDArray --platform macos
python3 "$SWIFT_LSP_PY" sdk XcodeSkills --symbol "State macro"
```

### 5. Run the Offline Self-Test & Unit Test Suite

```bash
python3 "$SWIFT_LSP_PY" --self-test
python3 -m unittest discover -s skills/swift-lsp/tests
```

---

## Installation & Setup

### 1. Google Antigravity (`agy` CLI v1.4.0+ & Antigravity App v2.24.0+)

Plugins installed in **Antigravity CLI (`agy`)** and **Antigravity App** share `<HOME>/.gemini/config/plugins/` and synchronize automatically across both surfaces ([Marketplace docs](https://antigravity.google/docs/marketplace/)).

- **From your shell (`agy plugin`)**:
  ```bash
  # Install directly from GitHub
  agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/swift-lsp

  # Or install from a local checkout of fb-gemini-plugins
  agy plugin install ./skills/swift-lsp

  # List, toggle, uninstall, or validate
  agy plugin list
  agy plugin enable swift-lsp
  agy plugin disable swift-lsp
  agy plugin validate ./skills/swift-lsp --strict
  ```
- **Inside the `agy` interactive CLI (`/plugin` / `/plugins`)**:
  - Run `/plugin install ./skills/swift-lsp` inline, or run `/plugin` (alias `/plugins`), press `Tab` to switch to **Discover**, and select **`+ Install from local directory...`** (`Space` toggles enable/disable in **Installed**; `Ctrl+S` installs/uninstalls).
- **In the Antigravity App**:
  - Open **Customizations** in the left sidebar $\rightarrow$ **Marketplace** (to browse and click **Add** / **`+`**) or **Installed** (where plugins installed via `agy` appear automatically; use the **`⋮`** menu or detail card to enable/disable, run suggested starter prompt chips, or uninstall).

### 2. Gemini Spark & Gemini App (`Customize > Skills`)

- **Option A — Single-File Upload or Paste**:
  Upload or paste `skills/swift-lsp/skills/swift-lsp/SKILL.md` in **Customize $\rightarrow$ Skills**.
- **Option B — Full Skill Package ZIP Upload (Includes `references/` and `scripts/`)**:
  ```bash
  (cd skills/swift-lsp/skills/swift-lsp && zip -r ../../../../swift-lsp-skill.zip SKILL.md references/ scripts/)
  ```
  Upload `swift-lsp-skill.zip` via **Skills $\rightarrow$ + $\rightarrow$ Upload skill**.

---

## Directory Structure

```text
skills/swift-lsp/
├── plugin.json                                         # Native Antigravity plugin manifest (v0.2.0)
├── .claude-plugin/
│   └── plugin.json                                     # Claude Code plugin manifest (v0.2.0)
├── mcp_config.json                                     # Stdio MCP server configuration (swift-lsp-sourcekit)
├── assets/
│   └── logo.svg                                        # 128x128 square SVG icon for App/Marketplace cards
├── tests/
│   └── test_sourcekit_mcp.py                           # Unit & mock-LSP round-trip test suite
├── README.md                                           # Plugin & multi-platform documentation (this file)
└── skills/
    └── swift-lsp/
        ├── SKILL.md                                    # Self-contained skill (Antigravity + Gemini Spark)
        ├── references/
        │   ├── sourcekit-lsp-and-indexing.md           # Package.swift (6.4), buildServer.json & Xcode 27 linker rules
        │   ├── dual-sdk-macos-ios-27.md                # Golden Gate Liquid Glass, @State macro, Document, AppKit & CoreAI
        │   └── swift6-concurrency-diagnostics.md       # Approachable Concurrency, ~Sendable, Observation 27 & Span
        └── scripts/
            └── sourcekit_mcp.py                        # Zero-dependency stdlib MCP stdio server & CLI bridge
```
