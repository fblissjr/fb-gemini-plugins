# SourceKit-LSP Architecture, Workspace Layouts & Indexing (`IndexStoreDB`)

This reference covers how `xcrun sourcekit-lsp` discovers build settings and maintains its semantic index across **Swift Package Manager (`Package.swift`)**, **Xcode projects (`.xcodeproj` / `.xcworkspace`)**, and hybrid macOS/iOS desktop/mobile repositories.

---

## 1. How `sourcekit-lsp` Resolves Compiler Flags

`sourcekit-lsp` combines two distinct subsystems:
1. **In-Memory AST & Typechecker (`swift-frontend` / SourceKitD)**:
   - Operates on open documents registered via `textDocument/didOpen` and `textDocument/didChange`.
   - Powers **`swift_hover`**, **`swift_diagnostics`**, **`swift_symbols` (`documentSymbol`)**, and same-file **`swift_definition`** immediately—even before a full build completes.
2. **Global Semantic Index (`IndexStoreDB`)**:
   - Reads unit and record files emitted by `swiftc -index-store-path <path>` during compilation (or background indexing).
   - Powers cross-file **`swift_references`**, cross-module **`swift_definition` / `implementation`**, and **`swift_symbols` (`workspaceSymbol`)**.
3. **Tier-2 `sandbox-exec` Fallback (`xcrun swiftc -dump-ast`)**:
   - Inside a Mach-restricted `sandbox-exec` where `com.apple.SourceKitService` XPC is blocked, `sourcekit-lsp` emits `SOURCEKITD FATAL ERROR: Service is invalid` on `stderr` without exiting.
   - `sourcekit_mcp.py` detects that `stderr` banner in `< 5ms` and automatically falls back to multi-file `xcrun swiftc -dump-ast -module-cache-path /tmp/swift-lsp-module-cache` across the enclosing SwiftPM target (`Sources/<Target>/` or `Tests/<Target>/`), preserving cross-file hover, docstring extraction, definition, SDK jump, and reference resolution.

---

## 2. Project Layouts: `Package.swift` vs. `.xcodeproj`

### A. Swift Package Manager (`Package.swift`) — Zero-Config
When `Package.swift` is at the workspace root:
- `xcrun sourcekit-lsp` natively loads the SwiftPM package graph.
- Index store path: `.build/arm64-apple-macosx/debug/index/store` (symlinked at `.build/debug/index/store`).
- Modern Swift 6+ `sourcekit-lsp` automatically runs background indexing; you can also populate the index explicitly with a single `swift build --build-tests`.

Example `Package.swift` baseline for **macOS 27.2+ and iOS 27.2+** (Swift 6):

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "AppCore",
    platforms: [
        .macOS("27.2"),
        .iOS("27.2")
    ],
    products: [
        .library(name: "AppCore", targets: ["AppCore"])
    ],
    targets: [
        .target(
            name: "AppCore",
            swiftSettings: [
                .swiftLanguageMode(.v6)
            ]
        ),
        .testTarget(
            name: "AppCoreTests",
            dependencies: ["AppCore"]
        )
    ]
)
```

### B. Pure `.xcodeproj` / `.xcworkspace` — Build Server Protocol (`buildServer.json`)
When a project uses `.xcodeproj` or `.xcworkspace` without a root `Package.swift`, `sourcekit-lsp` needs a **Build Server Protocol (`buildServer.json`)** manifest at the repository root so it knows which Xcode scheme, SDK, and DerivedData `Index.noindex/DataStore` to query.

Generate `buildServer.json` once at the workspace root using `xcode-build-server`:

```bash
# For an .xcodeproj workspace:
xcode-build-server config -project MyApp.xcodeproj -scheme MyApp

# For an .xcworkspace workspace:
xcode-build-server config -workspace MyApp.xcworkspace -scheme MyApp
```

`swift_toolchain_probe` automatically detects whether `buildServer.json` is present (`project_kind: "xcode-bsp"`) or missing (`project_kind: "xcodeproj-unconfigured"`).

### C. Hybrid Architecture (Recommended for Standalone macOS + iOS 27.2+ Apps)
For standalone macOS desktop apps (`NSPanel`, `MenuBarExtra`, local LLM/SSE clients, Metal/MLX tools) and companion iOS 27.2+ apps:
- Place 90%+ of application logic, models, networking, and SwiftUI views inside a root **`Package.swift`** (or `Packages/AppCore/Package.swift`).
- Keep the `.xcodeproj` as a thin signing/entitlements wrapper that imports `AppCore`.
- This gives `sourcekit-lsp` instant, zero-configuration SwiftPM indexing while preserving full `.app` bundle signing and Xcode Previews.

---

## 3. Optional Workspace Auto-Diagnostics Hook (`.agents/hooks.json`)

If you want Antigravity App and `agy` CLI to automatically run `swift_diagnostics` whenever a `.swift` file exists in a dedicated Swift repository, you can add a workspace-scoped `.agents/hooks.json` inside that Swift project:

```json
{
  "swift-lsp-session": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 \"$HOME/.gemini/config/plugins/swift-lsp/skills/swift-lsp/scripts/sourcekit_mcp.py\" probe --workspace . >/dev/null 2>&1 && echo '{\"injectSteps\":[{\"systemMessage\":{\"systemMessage\":\"[swift-lsp] Active target baseline: macOS 27.2+ / iOS 27.2+ (Swift 6). Prefer swift_hover, swift_definition, swift_references, swift_diagnostics, and swift_sdk_interface over regex grep.\"}}]}' || echo '{}'",
        "timeout": 5
      }
    ]
  }
}
```
