# SourceKit-LSP Architecture, Workspace Layouts & Xcode 27.2+ Toolchain Rules

This reference covers how `xcrun sourcekit-lsp` and `sourcekit_mcp.py` resolve compiler settings across **Swift Package Manager (`Package.swift`)**, **Xcode projects (`.xcodeproj` / `.xcworkspace`)**, and hybrid macOS/iOS 27.2+ ("Golden Gate") repositories, along with critical Xcode 27.2 linker, macro-sandbox, and deployment-target rules.

---

## 1. How `sourcekit-lsp` & `sourcekit_mcp.py` Resolve Compiler Flags

`swift-lsp` combines three complementary engines:
1. **In-Memory AST & Typechecker (`xcrun sourcekit-lsp` / SourceKitD)**:
   - Operates on open documents registered via `textDocument/didOpen` and `textDocument/didChange`.
   - Powers **`swift_hover`**, **`swift_diagnostics`**, **`swift_symbols` (`documentSymbol`)**, and same-file **`swift_definition`** immediately—even before a full build completes.
2. **Global Semantic Index (`IndexStoreDB`)**:
   - Reads unit and record files emitted by `swiftc -index-store-path <path>` during compilation (or background indexing).
   - Powers cross-file **`swift_references`**, cross-module **`swift_definition` / `implementation`**, and **`swift_symbols` (`workspaceSymbol`)**.
3. **Tier-2 Seatbelt Sandbox & Dual-SDK Engine (`xcrun swiftc -typecheck` / `-dump-ast -disable-sandbox`)**:
   - Inside a Mach-restricted `sandbox-exec` where `com.apple.SourceKitService` XPC is blocked, `sourcekit-lsp` emits `SOURCEKITD FATAL ERROR: Service is invalid` on `stderr`.
   - `sourcekit_mcp.py` detects that banner in `< 5ms` and automatically falls back to multi-file `xcrun swiftc -dump-ast -disable-sandbox -module-cache-path /tmp/swift-lsp-module-cache` across the enclosing SwiftPM target (`Sources/<Target>/` or `Tests/<Target>/`).
   - **Why `-disable-sandbox` is passed to `swiftc`**: In SDK 27, `@State`, `@Observable`, `@Generable`, `@Model`, and `#Preview` are all Swift macros expanded via `swift-plugin-server`. When `sourcekit_mcp.py` already runs inside an outer Seatbelt sandbox, `swiftc`'s attempt to wrap `swift-plugin-server` in a *nested* `sandbox-exec` fails with `sandbox-exec: sandbox_apply: Operation not permitted`. Passing `-disable-sandbox` to `swiftc` disables only the redundant inner macro sandbox so all Swift 6.4 macros expand cleanly (`rc=0`).
   - **Per-target `Package.swift` flag inference**: `sourcekit_mcp.py` parses `Package.swift` target blocks so UI targets with `.defaultIsolation(MainActor.self)` receive `-default-isolation MainActor`, while nonisolated compute/server targets in the same package do not.

---

## 2. Project Layouts: `Package.swift` (Swift 6.4) vs. `.xcodeproj`

### A. Swift Package Manager (`Package.swift`) — Swift 6.4 & macOS/iOS 27.0+ Baseline
When `Package.swift` is at the workspace root:
- `xcrun sourcekit-lsp` natively loads the SwiftPM package graph.
- Index store path: `.build/arm64-apple-macosx/debug/index/store` (symlinked at `.build/debug/index/store`).
- Modern Swift 6.4 `sourcekit-lsp` automatically runs background indexing; you can also populate the index explicitly with a single `swift build --build-tests`.

Recommended `Package.swift` template for **macOS 27.2+ ("Golden Gate") and iOS 27.2+** (`swift-tools-version: 6.4`):

```swift
// swift-tools-version: 6.4
import PackageDescription

let package = Package(
    name: "GoldenGateApp",
    platforms: [
        .macOS(.v27),
        .iOS(.v27)
    ],
    products: [
        .library(name: "AppUI", targets: ["AppUI"]),
        .library(name: "ComputeEngine", targets: ["ComputeEngine"])
    ],
    targets: [
        .target(
            name: "AppUI",
            dependencies: ["ComputeEngine"],
            swiftSettings: [
                .defaultIsolation(MainActor.self),
                .strictMemorySafety(),
                .enableUpcomingFeature("NonisolatedNonsendingByDefault")
            ]
        ),
        .target(
            name: "ComputeEngine",
            swiftSettings: [
                .strictMemorySafety(),
                .enableUpcomingFeature("NonisolatedNonsendingByDefault")
            ]
        ),
        .testTarget(
            name: "AppUITests",
            dependencies: ["AppUI"]
        )
    ]
)
```

### B. Pure `.xcodeproj` / `.xcworkspace` — Build Server Protocol (`buildServer.json`)
When a project uses `.xcodeproj` or `.xcworkspace` without a root `Package.swift`, `sourcekit-lsp` needs a **Build Server Protocol (`buildServer.json`)** manifest at the repository root so it knows which Xcode scheme, SDK, and DerivedData `Index.noindex/DataStore` to query:

```bash
# For an .xcodeproj workspace:
xcode-build-server config -project MyApp.xcodeproj -scheme MyApp

# For an .xcworkspace workspace:
xcode-build-server config -workspace MyApp.xcworkspace -scheme MyApp
```

### C. Hybrid Architecture (Recommended for Standalone macOS + iOS 27.2+ Apps)
For standalone macOS desktop apps (`NavigationSplitView`, `NSPanel`, `MenuBarExtra`, `CoreAI`, `FoundationModels`, Metal/MLX tools) and companion iOS 27.2+ apps:
- Place 90%+ of application logic, models, networking, and SwiftUI views inside a root **`Package.swift`**.
- Keep the `.xcodeproj` as a thin signing/entitlements wrapper that imports your package library.
- This gives `sourcekit-lsp` instant, zero-configuration SwiftPM indexing while preserving full `.app` bundle signing, entitlements, and Xcode Previews.

---

## 3. Critical Xcode 27.2 Toolchain, Linker & Build System Rules

1. **Purge `-Wl,-ld64` and `-Wl,-ld_classic` Linker Flags**:
   - Xcode 27 (`ld-27106.1`) completely removed the classic `ld64` linker implementation.
   - Passing `-Wl,-ld64` in `OTHER_LDFLAGS` or `LinkerSetting.unsafeFlags` is misinterpreted by the new linker driver as `-l d64` and fails with **`library 'd64' not found`**. Remove all `-Wl,-ld64` and `-Wl,-ld_classic` flags.
2. **Unique Clang Module Names Across Dependency Scans**:
   - Xcode 27's explicit module dependency scanner rejects targets or xcframeworks that define duplicate Clang module names (`module.modulemap`) anywhere in the dependency graph. Ensure every C/Objective-C target has a globally unique `MODULEMAP_FILE` module identifier.
3. **Avoid the `27.1` macOS Deployment Target Dropdown Bug**:
   - In `MacOSX27.2.sdk/SDKSettings.plist`, `ValidDeploymentTargets` lists `["26.6", "27.0", "27.2"]` (skipping `27.1`). Setting `MACOSX_DEPLOYMENT_TARGET = 27.1` triggers build-setting validation warnings in Xcode 27.2; always use **`27.0`** (in `Package.swift` `.macOS(.v27)`) or **`27.2`** (for `-target arm64-apple-macosx27.2`).
4. **Module Selector Syntax (`Module::Symbol`) for Ambiguous Type Names**:
   - Swift 6.4 obsoletes legacy workarounds when two imported modules define the same type name (e.g., a custom `Tab` struct colliding with `SwiftUI.Tab`). Use Swift 6.4 module selector syntax **`SwiftUI::Tab`** or **`AppKit::NSView`** (`option-obsoleted-by-module-selectors`).

---

## 4. How `swift-lsp` Complements `xcrun mcpbridge` and `xcrun agent skills`

Xcode 27.2 ships two additional CLI tools inside `/Applications/Xcode.app/Contents/Developer/usr/bin/` (reported by `swift_toolchain_probe` under `apple_intelligence_and_docs`):

| Tool | When It Works | How `swift-lsp` Complements It |
| :--- | :--- | :--- |
| **`swift-lsp` (`sourcekit_mcp.py`)** | **Always works (100% headless & sandboxed)** — requires only `/Applications/Xcode.app` on disk; no running Xcode GUI needed. | Provides persistent `sourcekit-lsp`, dual-SDK (`macos` + `ios`) macro-capable `swiftc -typecheck`, `.swiftinterface` inspection, and headless search over Xcode's bundled `*.md.packaged` skills and `AdditionalDocumentation/*.md`. |
| **`xcrun mcpbridge`** | **Only when Xcode GUI is open** with the workspace loaded and Xcode Settings $\rightarrow$ Intelligence MCP enabled. | Exposes Xcode's internal GUI tools (`XcodePreview`, `ExecuteSnippet`, `DocumentationSearch`). Use alongside `swift-lsp` when interactive canvas previews are needed. |
| **`xcrun agent skills export <dir>`** | Exports Xcode 27.2's 11 bundled Apple skills (`swiftui-whats-new-27`, `swiftui-specialist`, `building-document-based-swiftui-applications`, `modernize-tests`, etc.) to a directory. | `swift_sdk_interface` (`module: "XcodeSkills"` or `include_guides: true`) already indexes these exact `.md.packaged` files directly from `Xcode.app` without polluting global `~/.agents/skills/` prompts. |

---

## 5. Optional Workspace Auto-Diagnostics Hook (`.agents/hooks.json`)

If you want Antigravity App and `agy` CLI to automatically probe `swift-lsp` when opening a dedicated Swift repository, you can add a workspace-scoped `.agents/hooks.json` inside that Swift project:

```json
{
  "swift-lsp-session": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 \"<HOME>/.gemini/config/plugins/swift-lsp/skills/swift-lsp/scripts/sourcekit_mcp.py\" probe --workspace . >/dev/null 2>&1 && echo '{\"injectSteps\":[{\"systemMessage\":{\"systemMessage\":\"[swift-lsp] Active target baseline: macOS 27.2+ / iOS 27.2+ (Swift 6.4). Prefer swift_hover, swift_definition, swift_references, swift_diagnostics, and swift_sdk_interface over regex grep.\"}}]}' || echo '{}'",
        "timeout": 5
      }
    ]
  }
}
```
