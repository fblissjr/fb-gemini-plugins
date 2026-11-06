# Dual-SDK Development for macOS 27.2+ & iOS 27.2+

This reference covers building and verifying Swift 6 codebases targeting **macOS 27.2+** (`arm64-apple-macosx27.2`) and **iOS 27.2+** (`arm64-apple-ios27.2-simulator` / `arm64-apple-ios27.2`), avoiding cross-platform API hallucinations, and inspecting real Xcode `.swiftinterface` files.

---

## 1. Why Dual-SDK Verification Matters on macOS

When running on a Mac host, `swift build` and default `sourcekit-lsp` sessions evaluate the package graph for the **host triple (`arm64-apple-macosx27.2`)** only:
- Code inside `#if os(iOS) ... #endif` is stripped at the conditional-compilation stage and **never type-checked** during a host macOS build.
- Conversely, unguarded `AppKit` or macOS-only `SwiftUI` modifiers break as soon as the target is compiled for iOS.

Use `swift_diagnostics` with `platform: "both"` (or `"ios"`) to run `xcrun --sdk iphonesimulator swiftc -typecheck -target arm64-apple-ios27.2-simulator` alongside `arm64-apple-macosx27.2` in under a second.

---

## 2. Common macOS vs. iOS SwiftUI / Framework Divergences to Check via LSP

Before using any of the APIs below in shared views, either guard with `#if os(macOS)` / `#if os(iOS)` or inspect the signature via `swift_sdk_interface`:

| Capability | macOS 27.2+ (`AppKit` / `SwiftUI`) | iOS 27.2+ (`UIKit` / `SwiftUI`) |
| :--- | :--- | :--- |
| **Navigation Bar Title Mode** | `.toolbarTitleDisplayMode(...)` *(Note: `.navigationBarTitleDisplayMode` is unavailable on macOS)* | `.toolbarTitleDisplayMode(...)` or `.navigationBarTitleDisplayMode(...)` |
| **Text Input Modifiers** | Standard `.textContentType(...)`, `.autocorrectionDisabled()` *(Note: `.keyboardType(...)` and `.textInputAutocapitalization(...)` are unavailable on macOS)* | `.keyboardType(...)`, `.textInputAutocapitalization(...)` |
| **Floating / Utility Windows** | `Window`, `UtilityWindow`, `MenuBarExtra`, `Settings`, `NSPanel`, `NSWindow` | `WindowGroup`, `.sheet`, `.fullScreenCover`, `UIWindowScene` |
| **System Colors & Materials** | `Color(nsColor: .windowBackgroundColor)`, `.ultraThinMaterial`, `NSVisualEffectView` | `Color(uiColor: .systemBackground)`, `.ultraThinMaterial` |
| **Pasteboard / Clipboard** | `NSPasteboard.general` | `UIPasteboard.general` |
| **Image Representation** | `NSImage` (`Image(nsImage:)`) | `UIImage` (`Image(uiImage:)`) |

---

## 3. Ground-Truth `.swiftinterface` Queries (`swift_sdk_interface`)

Every public framework in your installed Xcode SDK ships human-readable `.swiftinterface` files at:
- **macOS SDK**: `<MacOSX.sdk>/System/Library/Frameworks/<Framework>.framework/Modules/<Framework>.swiftmodule/arm64e-apple-macos.swiftinterface` (`sourcekit_mcp.py` automatically excludes `arm64e-apple-ios-macabi.swiftinterface` Mac Catalyst headers when `platform="macos"`)
- **iOS Simulator SDK**: `<iPhoneSimulator.sdk>/System/Library/Frameworks/<Framework>.framework/Modules/<Framework>.swiftmodule/arm64-apple-ios-simulator.swiftinterface`
- **Re-Exported Companion Modules (27.2+ SDKs)**: When querying `SwiftUI`, `Foundation`, or `Swift`, `swift_sdk_interface` automatically includes companion modules (`SwiftUICore`, `FoundationEssentials`, `FoundationInternationalization`, `_Concurrency`, `Synchronization`) where core types (`View`, `State`, `Binding`) live in modern Xcode SDKs.
- **Swift Standard / Core Modules (`Observation`, `Synchronization`, `_Concurrency`)**: `<SDK>/usr/lib/swift/<Module>.swiftmodule/*.swiftinterface`

### High-Value `swift_sdk_interface` Queries

1. **Discovering New 27.x APIs in a Framework**:
   ```json
   {
     "module": "SwiftUI",
     "availability_filter": "27.",
     "platform": "macos",
     "max_results": 30
   }
   ```
2. **Checking Whether a Modifier Exists on macOS vs. iOS**:
   - Query `{"module": "SwiftUI", "symbol": "navigationBarTitleDisplayMode", "platform": "macos"}` $\rightarrow$ immediately reveals `@available(macOS, unavailable)`.
3. **Inspecting Exact `@MainActor` / `Sendable` Conformance on System Types**:
   - Query `{"module": "AppKit", "symbol": "class NSPanel", "platform": "macos"}` or `{"module": "Observation", "symbol": "protocol Observable", "platform": "macos"}`.
