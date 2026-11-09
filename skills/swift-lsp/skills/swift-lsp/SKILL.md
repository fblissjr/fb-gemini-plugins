---
name: swift-lsp
description: Bridges Apple SourceKit-LSP (xcrun sourcekit-lsp), Xcode 27.2+ .swiftinterface SDK headers, and bundled Xcode 27 Agent Skills & AdditionalDocumentation into Antigravity App, Antigravity CLI (agy), Claude Code, and Gemini Spark for Swift 6.4+, macOS 27.2+ ("Golden Gate"), and iOS 27.2+ development. Provides symbol-anchored hover, definition, typeDefinition, implementation, references, document/workspace symbols, sandbox-safe macro-capable incremental diagnostics across both macOS 27.2 and iOS 27.2 simulator targets, and direct .swiftinterface & Apple guide lookup. Use when user says "swift lsp", "sourcekit-lsp", "check swift types", "swift diagnostics", "verify macos and ios targets", "lookup swiftinterface", "macos 27.2 api", "golden gate swiftui", "ios 27.2 api", "resolve swift concurrency error", or writes/refactors Swift 6.4, SwiftUI, AppKit, UIKit, CoreAI, FoundationModels, or SwiftPM code.
---

# Swift LSP & macOS / iOS 27.2+ ("Golden Gate") SDK Inspector (`swift-lsp`)

You have access to **SourceKit-LSP (`xcrun sourcekit-lsp`)**, the local **Xcode 27.2+ `.swiftinterface` SDK headers** (`MacOSX27.2.sdk` and `iPhoneSimulator27.2.sdk`), and **Apple's bundled Xcode 27 Agent Skills, `AdditionalDocumentation`, and Swift 6.4 diagnostic guides** via the `swift-lsp-sourcekit` MCP server and its standalone CLI (`scripts/sourcekit_mcp.py`).

When working in a Swift workspace targeting **macOS 27.2+ ("Golden Gate")** and **iOS 27.2+** (Swift 6.4+ language mode), follow these operational rules to replace slow cold `swift build` / `xcodebuild` loops and training-cutoff guesses with compiler-verified truth.

---

## Core Operational Rules

### Rule 1 — Enforce the macOS 27.2+ ("Golden Gate"), iOS 27.2+ & Swift 6.4 Baseline
- Unless `Package.swift` or `.xcodeproj` explicitly targets an older OS, treat **macOS 27.2** and **iOS 27.2** with **Swift 6.4** as the unconditional minimum deployment baseline.
- Prefer `@available(anyAppleOS 27.0, *)` (or `27.2`) when marking cross-platform Apple OS availability rather than verbose 5-platform availability lists.
- Never emit legacy `#available(macOS 14.0, iOS 17.0, *)` or `#available(macOS 15.0, iOS 18.0, *)` guards, and never use legacy `ObservableObject` / `@Published` / `@StateObject` (`@Observable` + `@State` macro is universal).
- Respect **SDK 27 SwiftUI & Concurrency contracts**:
  - **`@State` is a macro in SDK 27**: Always mark `@State private var` when initializing an `@Observable` class inline; never combine a declaration-site default with an `init` assignment (`error: Variable 'self.x' used before being initialized`—fix by removing the declaration default, never by reordering `init`).
  - **`@ContentBuilder` unifies builders**: Use trailing-closure `.overlay { ... }` / `.background { ... }` when passing views so the compiler does not pick the `ShapeStyle` overload; use `@ContentBuilder` (emitting `TupleContent` / `EmptyContent`) for custom generic containers.
  - **Approachable Concurrency (`SE-0461`, `SE-0466`, `SE-0470`)**: Check whether the target enables `.defaultIsolation(MainActor.self)` in `Package.swift`. `sourcekit_mcp.py` automatically extracts per-target `swiftSettings` (`-default-isolation MainActor`, `-strict-memory-safety`, `-enable-upcoming-feature ...`) and passes `-disable-sandbox` to `swiftc` so `@State`, `@Observable`, `@Generable`, and `#Preview` macros expand cleanly inside Seatbelt sandboxes.

### Rule 2 — Symbol-Anchored LSP Queries Over Regex `grep`
- Never guess raw 0-indexed UTF-16 character column numbers when calling `swift_hover`, `swift_definition`, or `swift_references`.
- Always pass **`file` + 1-based `line` + `symbol`** (e.g., `{"file": "Sources/App/HUDPanel.swift", "line": 48, "symbol": "NSPanel"}` or `symbol: ".glassProminent"`), plus `workspace` (or an absolute `file` path) on the first call in a session so the MCP server binds to the active Swift repository root.
- `sourcekit_mcp.py` automatically resolves relative `file` paths against `workspace` (or the session's active Swift workspace), searches `line ± 3`, strips leading dots or trailing argument parens, and computes the exact UTF-16 character offset (even across emoji/Unicode literals) before querying `sourcekit-lsp`.

### Rule 3 — Ground-Truth `.swiftinterface` & Bundled Apple Skill Lookup Before Guessing 27.2 APIs
- Model training weights lag behind **macOS 27.2 ("Golden Gate")**, **iOS 27.2**, and **Swift 6.4.2** SDK additions, SubFrameworks, and `@available(macOS, unavailable)` annotations.
- Whenever you are unsure of a modifier signature, initializer label, or platform availability in `SwiftUI`, `AppKit`, `UIKit`, `Observation`, `FoundationModels` (including `_Vision_FoundationModels`), `CoreAI` (`CoreAIRuntime`, `CoreAIDelegates`), `SwiftData`, `Testing`, `Evaluations`, or `AppIntentsTesting`, call **`swift_sdk_interface`** to read the exact declaration from the installed Xcode `.swiftinterface` on disk.
- Set `include_guides: true` or query virtual modules `module: "XcodeSkills"`, `"XcodeDocs"`, or `"SwiftDiagnostics"` in `swift_sdk_interface` to search Apple's bundled Xcode 27 Agent Skills (`swiftui-whats-new-27`, `swiftui-specialist`, `building-document-based-swiftui-applications`, etc.), `AdditionalDocumentation` guides (Liquid Glass, New Toolbar Features, `Span`/`InlineArray`, `FoundationModels`), and Swift 6.4 compiler diagnostic docs—100% headlessly without needing Xcode GUI open.

### Rule 4 — Dual-Platform (`macos` + `ios`) Diagnostics Before `swift build`
- On macOS, a default `swift build` or single-target `sourcekit-lsp` session only compiles the host platform (`arm64-apple-macosx27.2`), leaving `#if os(iOS)` blocks and platform-exclusive SwiftUI modifiers (such as iOS/visionOS-only `ToolbarOverflowMenu` and `.topBarPinnedTrailing`, or macOS-only `Settings` and `NSHostingMenu`) unchecked.
- After editing `.swift` files, call **`swift_diagnostics`** with `platform: "both"` (or `"macos"` / `"ios"` as appropriate) to type-check against both `arm64-apple-macosx27.2` and `arm64-apple-ios27.2-simulator` at zero `run_command` sandbox cost.

---

## Tool Selection Matrix

| Task | MCP Tool | CLI Subcommand (`scripts/sourcekit_mcp.py`) | Key Arguments |
| :--- | :--- | :--- | :--- |
| Check Xcode toolchain, `sourcekit-lsp`, `IndexStoreDB`, 27.2+ SDKs, and bundled Apple skills/docs | `swift_toolchain_probe` | `probe` | `workspace?`, `min_version="27.2"` |
| Incremental macro-capable typecheck across macOS 27.2, iOS 27.2 simulator, or both | `swift_diagnostics` | `diagnostics` | `files: [...]`, `platform: "macos" \| "ios" \| "both"` |
| Inspect inferred type, `@MainActor`/`Sendable` isolation, or docstrings | `swift_hover` | `hover` | `file`, `line`, `symbol` |
| Jump to symbol declaration, type definition, or protocol witness | `swift_definition` | `definition` | `file`, `line`, `symbol`, `kind: "definition" \| "typeDefinition" \| "implementation"` |
| Find all semantic callers across the Swift workspace | `swift_references` | `references` | `file`, `line`, `symbol`, `include_declaration: false` |
| Get file outline (`Struct`/`Actor`/`Protocol`/`Method`) or search workspace | `swift_symbols` | `symbols` | `file?`, `query?` |
| Inspect Xcode 27.2 `.swiftinterface` headers or bundled Apple Agent Skills / Guides | `swift_sdk_interface` | `sdk` | `module`, `symbol?`, `platform: "macos" \| "ios"`, `availability_filter?`, `include_guides?` |

---

## Standard 4-Step Swift Development Loop

1. **Preflight Probe (Once per Workspace)**:
   Call `swift_toolchain_probe` with `workspace` set to the active Swift repository path to verify the workspace type (`swiftpm` via `Package.swift`, `xcode-bsp` via `buildServer.json`, or `xcodeproj-unconfigured`), confirm whether `.build/*/index/store` is populated, and verify the installed `macosx` and `iphonesimulator` 27.2+ SDKs and bundled Apple intelligence docs.
2. **Navigate & Ground Against 27.2 SDKs & Bundled Apple Skills**:
   - Use `swift_symbols` (`file`) to inspect file structure without reading entire large files.
   - Use `swift_definition` and `swift_references` (`file`, `line`, `symbol`) before changing protocol requirements or method signatures.
   - Use `swift_sdk_interface` (`module: "SwiftUI"` / `"CoreAI"` / `"FoundationModels"` / `"XcodeSkills"`, `symbol: "..."`, `platform: "macos"` or `"ios"`, `include_guides: true`) to verify exact 27.2+ framework declarations and Apple's official migration guidance.
3. **Edit & Run Fast LSP / Dual-SDK Diagnostics**:
   - After modifying `.swift` files with `edit_file` / `write_file`, run `swift_diagnostics` (`files: [...]`, `platform: "macos"` or `"both"`).
   - `sourcekit_mcp.py` automatically syncs the latest disk contents, infers per-target Swift 6.4 flags from `Package.swift`, and expands Swift macros (`-disable-sandbox`) cleanly.
   - If a Swift 6.4 concurrency or generic inference error appears, call `swift_hover` on the offending expression's symbol to see the exact compiler-inferred actor isolation and type.
4. **Final Build/Test Verification**:
   - Only after `swift_diagnostics` reports `error_count: 0`, run a single `swift test` or `xcodebuild` if full linker/runtime test verification is required.

---

## Standalone CLI Fallback

When running in environments without MCP or from a terminal shell:

```bash
SWIFT_LSP_PY="<HOME>/.gemini/config/plugins/swift-lsp/skills/swift-lsp/scripts/sourcekit_mcp.py"
# Or from a local repo checkout:
# SWIFT_LSP_PY="skills/swift-lsp/skills/swift-lsp/scripts/sourcekit_mcp.py"

# 1. Probe toolchain, SDKs, IndexStoreDB, and bundled Xcode 27 skills/docs
python3 "$SWIFT_LSP_PY" probe --workspace .

# 2. Check diagnostics across both macOS 27.2 and iOS 27.2 simulator
python3 "$SWIFT_LSP_PY" diagnostics Sources/App/ContentView.swift --platform both --min-version 27.2

# 3. Symbol-anchored hover, definition, and references
python3 "$SWIFT_LSP_PY" hover Sources/App/ContentView.swift --line 42 --symbol fetchModels
python3 "$SWIFT_LSP_PY" definition Sources/App/ContentView.swift --line 42 --symbol fetchModels
python3 "$SWIFT_LSP_PY" references Sources/App/ContentView.swift --line 42 --symbol fetchModels

# 4. Search installed Xcode SDK .swiftinterface headers & bundled Xcode 27 guides
python3 "$SWIFT_LSP_PY" sdk SwiftUI --symbol glassEffect --platform macos --guides
python3 "$SWIFT_LSP_PY" sdk CoreAI --symbol NDArray --platform macos
python3 "$SWIFT_LSP_PY" sdk XcodeSkills --symbol "State macro"
```

---

## Progressive-Disclosure Reference Guides

Load the relevant reference guide when deeper architectural or diagnostic rules are needed:

- **[`references/sourcekit-lsp-and-indexing.md`](references/sourcekit-lsp-and-indexing.md)**: Configuring `Package.swift` (`swift-tools-version: 6.4`) vs. `.xcodeproj` / `.xcworkspace` (`buildServer.json` via `xcode-build-server`), `IndexStoreDB` lifecycle, Xcode 27 linker/module rules (`ld-27106.1` `-Wl,-ld64` removal, unique Clang modules, avoiding the `27.1` macOS deployment target), and companion `xcrun mcpbridge` / `xcrun agent skills` workflows.
- **[`references/dual-sdk-macos-ios-27.md`](references/dual-sdk-macos-ios-27.md)**: macOS 27.x ("Golden Gate") & iOS 27.x architecture, the 4-layer Liquid Glass material hierarchy, `@State` macro & `@ContentBuilder` unification, SwiftUI view invalidation & soft-deprecation rules, asynchronous `@Observable` `Document` protocol, AppKit 27.0 interop (`NSHostingSceneRepresentation`, `NSHostingMenu`, Touch on Mac, 13 SDK-27 runtime behavior changes), and `FoundationModels` / `CoreAI` / `SwiftData` 27.0 patterns.
- **[`references/swift6-concurrency-diagnostics.md`](references/swift6-concurrency-diagnostics.md)**: Swift 6.4.2 Approachable Concurrency (`.defaultIsolation(MainActor.self)`, `nonisolated(nonsending)`, `@concurrent`, isolated conformances), resource lifetime safety (`~Sendable`, `await` inside `defer`, `withTaskCancellationShield`, move-only `Continuation`), `Observation` 27.0 (`withContinuousObservation`), and memory-safe stdlib types (`InlineArray`, `Span`, `UniqueArray`).
