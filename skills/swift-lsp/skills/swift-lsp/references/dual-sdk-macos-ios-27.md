# Dual-SDK Development for macOS 27.2+ ("Golden Gate") & iOS 27.2+

This reference covers building and verifying Swift 6.4+ and SwiftUI 27.2+ codebases targeting **macOS 27.2+ ("Golden Gate")** (`arm64-apple-macosx27.2`) and **iOS 27.2+** (`arm64-apple-ios27.2-simulator` / `arm64-apple-ios27.2`), avoiding cross-platform API hallucinations, and inspecting real Xcode `.swiftinterface` files and bundled Apple Agent Skills.

---

## 1. Why Dual-SDK Verification Matters on macOS

When running on a Mac host, `swift build` and default `sourcekit-lsp` sessions evaluate the package graph for the **host triple (`arm64-apple-macosx27.2`)** only:
- Code inside `#if os(iOS) ... #endif` is stripped at the conditional-compilation stage and **never type-checked** during a host macOS build.
- Conversely, unguarded `AppKit` or macOS-only `SwiftUI` modifiers break as soon as the target is compiled for iOS, and iOS/visionOS-only toolbar APIs (such as `ToolbarOverflowMenu` or `.topBarPinnedTrailing`) break on macOS.

Use `swift_diagnostics` with `platform: "both"` (or `"ios"`) to run `xcrun --sdk iphonesimulator swiftc -typecheck -disable-sandbox -target arm64-apple-ios27.2-simulator` alongside `arm64-apple-macosx27.2` in under a second.

---

## 2. Common macOS vs. iOS SwiftUI / Framework Divergences (SDK 27.2)

Before using any of the APIs below in shared views, either guard with `#if os(macOS)` / `#if os(iOS)` or inspect the signature via `swift_sdk_interface`:

| Capability | macOS 27.2+ (`AppKit` / `SwiftUI`) | iOS 27.2+ (`UIKit` / `SwiftUI`) |
| :--- | :--- | :--- |
| **Universal Availability Attribute** | `@available(anyAppleOS 27.0, *)` or `@available(anyAppleOS 27.2, *)` | `@available(anyAppleOS 27.0, *)` or `@available(anyAppleOS 27.2, *)` |
| **Navigation Bar Title Mode** | `.toolbarTitleDisplayMode(...)` *(Note: `.navigationBarTitleDisplayMode` is `@available(macOS, unavailable)`)* | `.toolbarTitleDisplayMode(...)` or `.navigationBarTitleDisplayMode(...)` |
| **Toolbar Title Alignment (27.2)** | `EnvironmentValues.toolbarTitleAlignment` (`ToolbarTitleAlignment`) *(Note: `.toolbarTitleAlignment(_:)` view modifier is `@available(iOS 27.2, *) @available(macOS, unavailable)`)* | `.toolbarTitleAlignment(.leading / .center)` |
| **Toolbar Overflow & Pinned Items (27.0)** | Use `.visibilityPriority(.high / .low)` (`ToolbarItemVisibilityPriority(higherThan:)`) & `ToolbarSpacer(.fixed / .flexible)` *(Note: `ToolbarOverflowMenu` and `.topBarPinnedTrailing` are `@available(macOS, unavailable)`)* | `ToolbarOverflowMenu { ... }`, `ToolbarItem(placement: .topBarPinnedTrailing)`, `ToolbarSpacer`, `.visibilityPriority` |
| **Text Input Modifiers** | `.textContentType(...)`, `.autocorrectionDisabled()` *(Note: `.keyboardType(...)` and `.textInputAutocapitalization(...)` are unavailable on macOS)* | `.keyboardType(...)`, `.textInputAutocapitalization(...)` |
| **Floating / Utility Windows & Menus** | `Window`, `UtilityWindow`, `MenuBarExtra`, `Settings`, `NSPanel`, `NSHostingSceneRepresentation`, `NSHostingMenu` | `WindowGroup`, `.sheet`, `.fullScreenCover`, `UIWindowScene` |
| **System Colors & Materials** | `Color(nsColor: .windowBackgroundColor)`, `.regularMaterial`, `.glassEffect(...)`, `NSGlassEffectView` | `Color(uiColor: .systemBackground)`, `.regularMaterial`, `.glassEffect(...)` |
| **Pasteboard / Clipboard** | `NSPasteboard.general` | `UIPasteboard.general` |
| **Image Representation** | `NSImage` (`Image(nsImage:)`) | `UIImage` (`Image(uiImage:)`) |

---

## 3. Golden Gate Design Contract & 4-Layer Liquid Glass Hierarchy

macOS 27 ("Golden Gate") enforces visual consolidation, edge-to-edge full-height sidebars (`NSWindow.StyleMask.fullSizeContentView`), and a strict **4-layer material hierarchy**:

| Layer | Role | Native SwiftUI / AppKit Surface | Anti-Pattern to Reject |
| :--- | :--- | :--- | :--- |
| **1. Content Layer** | Primary canvas, editors, tables, lists, dense text | Opaque window background (`Color(nsColor: .windowBackgroundColor)`), `.regularMaterial`, `.thickMaterial`, `Form { Section { ... } }.formStyle(.grouped)` | **Never** place `.glassEffect()` behind dense body text, tables, or scrolling lists (destroys contrast and saturates GPU backdrop sampling). |
| **2. Navigation Layer** | Full-height sidebars & inspector columns | `NavigationSplitView` + `.backgroundExtensionEffect()` | Never stack nested `.background(.ultraThinMaterial)` cards inside a sidebar; `NavigationSplitView` already provides native translucent chrome. |
| **3. Commands Layer** | Unified window toolbar & grouped controls | `.toolbar { ToolbarItem / ToolbarItemGroup / ToolbarSpacer }` + `.contentMarginsRemoved()` | Never build custom `HStack` fake titlebars above the canvas or pass views inside `NSGlassEffectView` into `NSToolbarItem.view` (breaks `NSToolbarView` hit-testing). |
| **4. Transient Overlay Layer** | Floating HUDs, badges, morphing action bars, popovers | `.glassEffect(_:in:isEnabled:)`, `GlassEffectContainer(spacing:)`, `.glassEffectID(_:in:)`, `.buttonStyle(.glass)` / `.buttonStyle(.glassProminent)` | **Zero structural card budget**: do not wrap regular sections in custom `RoundedRectangle` + `.fill(.ultraThinMaterial)` + `.strokeBorder(...)` + `.shadow(...)` cards. |

### Verified Liquid Glass & Workspace Pattern (`MacOSX27.2.sdk` & `iPhoneSimulator27.2.sdk`)

```swift
import SwiftUI

struct GoldenGateWorkspaceView: View {
    @State private var columnVisibility: NavigationSplitViewVisibility = .all
    @State private var isInspectorPresented: Bool = true
    @Namespace private var glassNamespace

    var body: some View {
        NavigationSplitView(columnVisibility: $columnVisibility) {
            List(0..<20, id: \.self) { index in
                Label("Item \(index)", systemImage: "folder")
            }
            .navigationSplitViewColumnWidth(min: 200, ideal: 240, max: 320)
            .backgroundExtensionEffect()
        } detail: {
            ZStack(alignment: .bottom) {
                ScrollView {
                    Text("Primary Content Canvas")
                        .frame(maxWidth: .infinity, minHeight: 600)
                }
                .contentMarginsRemoved()

                // Layer 4: Transient floating bar using GlassEffectContainer
                GlassEffectContainer(spacing: 16) {
                    HStack(spacing: 12) {
                        Button("Run", systemImage: "play.fill") {}
                            .buttonStyle(.glassProminent)
                            .glassEffectID("runButton", in: glassNamespace)

                        Button("Inspect", systemImage: "sidebar.right") {
                            isInspectorPresented.toggle()
                        }
                        .buttonStyle(.glass)
                        .glassEffectID("inspectButton", in: glassNamespace)
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .glassEffect(.regular.interactive(), in: .capsule)
                }
                .padding(.bottom, 20)
            }
            .inspector(isPresented: $isInspectorPresented) {
                Form {
                    Section("Properties") {
                        LabeledContent("Target", value: "macOS 27.2")
                    }
                }
                .formStyle(.grouped)
                .inspectorColumnWidth(min: 240, ideal: 280, max: 360)
            }
        }
        .toolbar {
            ToolbarItemGroup(placement: .primaryAction) {
                Button("Share", systemImage: "square.and.arrow.up") {}
                    .visibilityPriority(.high)
            }
            ToolbarSpacer(.flexible)
            #if os(iOS) || os(visionOS)
            ToolbarOverflowMenu {
                Button("Export Diagnostics", systemImage: "waveform.path.ecg") {}
            }
            #endif
        }
    }
}
```

---

## 4. `@State` as a Macro & `@ContentBuilder` Unification (SDK 27.0+)

### A. `@State` Macro Migration (`SwiftUIMacros.StateMacro`)
In SDK 27.0+, `@State` is a **Swift macro** rather than a legacy property wrapper. Three strict compiler rules apply:

1. **Always mark `@State` properties `private` when initializing `@Observable` classes inline**:
   ```swift
   @Observable final class ViewModel {}

   struct DashboardView: View {
       @State private var viewModel = ViewModel() // `private` enables lazy autoclosure init
       var body: some View { EmptyView() }
   }
   ```
   Without `private`, `@State` generates a memberwise initializer parameter whose default value allocates a new `ViewModel()` on **every** parent view re-evaluation.
2. **Never combine a declaration-site default value with an `init` assignment**:
   ```swift
   // ❌ FAILS in SDK 27 with: `error: Variable 'self.title' used before being initialized`
   struct BadEditorView: View {
       @State private var title: String = "Untitled"
       let id: UUID
       init(id: UUID, initialTitle: String) {
           self.title = initialTitle // Calls macro setter before `self.id` is initialized!
           self.id = id
       }
       var body: some View { Text(title) }
   }
   ```
   > [!CAUTION]
   > **Never "fix" this error by reordering `self.id = id` above `self.title = initialTitle`!** If `self.title` keeps its declaration default (`= "Untitled"`), the `@State` macro synthesizes `var _title = State(initialValue: "Untitled")` and subsequent assignments inside `init` become no-ops when SwiftUI updates the view.
   > **Correct fix**: Remove the declaration-site default value (`@State private var title: String`).
3. **Trailing-closure `.overlay { ... }` / `.background { ... }` for overload disambiguation**:
   Because `@State` is now a macro, the compiler changes overload ranking on `.overlay(_:alignment:)`. Always use the trailing-closure view builder `.overlay(alignment: .center) { ProgressView() }` instead of `.overlay(ProgressView())` (which fails with `Instance method 'overlay(_:ignoresSafeAreaEdges:)' requires that 'ProgressView<...>' conform to 'ShapeStyle'`).

### B. `@ContentBuilder` Unification (`TupleContent`, `EmptyContent`)
- In SDK 27.0+, `@ViewBuilder`, `@SceneBuilder`, `@ToolbarContentBuilder`, `@CommandsBuilder`, and `@TableRowBuilder` are unified as typealiases to **`@ContentBuilder`**.
- Multi-statement closures inside `@ContentBuilder` emit **`TupleContent<...>`** and empty closures emit **`EmptyContent`** (rather than `TupleView` / `EmptyView`).
- **Exception**: Swift Charts (`@ChartContentBuilder`) does **not** use `@ContentBuilder`. Extract helper properties returning `some ChartContent` with `@ChartContentBuilder`, not `@ViewBuilder`.

---

## 5. SwiftUI Specialist Invalidation, Data-Flow & Soft-Deprecation Rules

From Apple's bundled `swiftui-specialist` skill for SDK 27:

1. **Isolate invalidation Domains (`@Observable` Identity vs. Closures)**:
   - Extract distinct visual regions (header, filter bar, row item, inspector) into separate `View` structs.
   - Pass **narrow value inputs** (`String`, `Int`, `Bool`, `Identifiable` value struct) when the child only reads a few primitives.
   - When a child view mutates or reads an `@Observable` model, **pass the `@Observable` object reference directly** rather than passing per-row closures (`onTap: () -> Void` or `isSelected: () -> Bool`). SwiftUI compares `@Observable` references in $O(1)$ by pointer identity (`===`) and tracks only the specific properties read in `body`, whereas closures cannot be compared for equality and force **every** row to re-evaluate on parent state changes.
2. **Never filter or sort inline inside `ForEach` / `List`**:
   - Computing `ForEach(items.filter { ... }.sorted { ... })` inside `body` runs $O(N \log N)$ work on every unrelated view update. Cache filtered/sorted arrays in a stored property on your `@Observable` model updated via `didSet` on the inputs.
3. **Never construct inline `Binding(get:set:)` in `body`**:
   - Use `@Bindable var model = model` and pass KeyPath or subscript projections (`$model.name`, `$model.itemsByID[id]`), which now support custom `subscript` declarations in SDK 27.
4. **Never store closures in `@Entry` `EnvironmentValues`**:
   - Closures in `EnvironmentValues` fail equality checks and invalidate the entire subtree on every environment update. Define an `Equatable` struct with `func callAsFunction(...)` instead.
5. **Use `@Animatable` macro (`SwiftUIMacros.AnimatableMacro`)**:
   - Annotate custom `View` or `Shape` types with `@Animatable` (which synthesizes `animatableData: AnimatableValues<...>` for all numeric stored properties) and mark non-interpolated properties (`String`, `Color`, `Bool`, closures) with `@AnimatableIgnored`.
6. **Avoid `deprecated: 100000.0` Soft-Deprecated APIs**:
   - In `.swiftinterface`, `deprecated: 100000.0` marks soft-deprecated APIs that should never be emitted in new code:
     - `NavigationView` $\rightarrow$ `NavigationStack` / `NavigationSplitView`
     - `foregroundColor(_:)` $\rightarrow$ `foregroundStyle(_:)`
     - `cornerRadius(_:)` $\rightarrow$ `clipShape(.rect(cornerRadius:))`
     - `onChange(of:perform:)` (1-arg closure) $\rightarrow$ `onChange(of:) { oldValue, newValue in ... }` or `onChange(of:) { ... }`
     - `.tabItem { ... }` $\rightarrow$ `Tab("Title", systemImage: "icon", value: id) { ... }`
     - `FileDocument` / `ReferenceFileDocument` $\rightarrow$ `Document` (`ReadableDocument` / `WritableDocument`)

---

## 6. Overhauled `Document` Protocol (`ReadableDocument` / `WritableDocument`) & SDK 27 Modifiers

### A. Asynchronous Reference-Type `Document` Protocol (SDK 27.0+)
`FileDocument` and `ReferenceFileDocument` are soft-deprecated (`100000.0`). In SDK 27.0+, documents are `@Observable final class` reference types conforming to `Document` (`ReadableDocument` + `WritableDocument`), backed by `FileWrapperDocumentReader` / `FileWrapperDocumentWriter` and `Foundation.Subprogress`:

```swift
import SwiftUI
import UniformTypeIdentifiers

extension UTType {
    static let canvasDoc = UTType(exportedAs: "com.example.canvas-doc")
}

struct CanvasSnapshot: Codable, Sendable {
    var title: String
}

struct CanvasDocumentReader: FileWrapperDocumentReader {
    let snapshot: CanvasSnapshot

    @concurrent
    init(file: FileWrapper, contentType: UTType, progress: consuming Subprogress) async throws {
        let reporter = progress.start(totalCount: 100)
        guard let data = file.regularFileContents else {
            throw CocoaError(.fileReadCorruptFile)
        }
        self.snapshot = try JSONDecoder().decode(CanvasSnapshot.self, from: data)
        reporter.complete(count: 100)
    }
}

struct CanvasDocumentWriter: FileWrapperDocumentWriter {
    let snapshot: CanvasSnapshot

    @concurrent
    func write(contentType: UTType, progress: consuming Subprogress) async throws -> FileWrapper {
        let reporter = progress.start(totalCount: 100)
        let data = try JSONEncoder().encode(snapshot)
        reporter.complete(count: 100)
        return FileWrapper(regularFileWithContents: data)
    }
}

@MainActor
@Observable
final class CanvasDocument: Document {
    static var readableContentTypes: [UTType] { [.canvasDoc] }
    var title: String = "Untitled"

    init(context: DocumentCreationContext) async throws {
        if context.creationSource == .importedImage {
            self.title = "Imported Image"
        }
    }

    init(With reader: CanvasDocumentReader) async throws {
        self.title = reader.snapshot.title
    }

    func writer(for contentType: UTType) throws -> CanvasDocumentWriter {
        CanvasDocumentWriter(snapshot: CanvasSnapshot(title: title))
    }

    /// CRITICAL: Autosave will NOT fire on `Document` unless mutations register with `UndoManager`!
    func rename(to newTitle: String, undoManager: UndoManager?) {
        let oldTitle = title
        title = newTitle
        undoManager?.registerUndo(withTarget: self) { doc in
            doc.rename(to: oldTitle, undoManager: undoManager)
        }
    }
}
```

### B. Reordering, Swipe Actions, Item-Bound Alerts & `AsyncImage(request:)` (SDK 27.0+)
- **Reordering across `List`, `ForEach`, and `LazyVGrid`**:
  Apply `.reorderable(isEnabled)` to item views and `.reorderContainer(for: Item.self) { items, destination in ... }` on the container. Add `.reorderTrigger(by: .dragGesture)` on custom layouts.
- **Swipe Actions Outside `List`**:
  Apply `.swipeActions { ... }` to rows inside a custom `ScrollView` / `LazyVStack` and attach `.swipeActionsContainer()` to the parent scroll container so opening one row's swipe actions automatically closes others.
- **Item-Bound & Error-Bound Alerts**:
  Use `.alert("Delete?", item: $selectedItem) { item in ... } message: { item in ... }`, `.confirmationDialog("Options", item: $selectedItem) { ... }`, or `.alert(error: $lastError)` (accepts any `LocalizedError` binding without manual boolean state).
- **AsyncImage(`request: URLRequest`)**:
  Pass custom `URLRequest` headers directly via `AsyncImage(request: request)` and configure the hierarchy's session via `.asyncImageURLSession(customSession)`.
- **Xcode 27.3 (`MacOSX27.3.sdk` / `iPhoneSimulator27.3.sdk`) Additions**:
  - **`ToolbarContainerBehavior` & `.toolbarContainerBehavior(_:)` (`27.3+`)**: Controls whether a descendant view hierarchy uses the global window toolbar or a local container toolbar. **Dual-SDK caveat**: `ToolbarContainerBehavior.local` is `@available(iOS 27.3, *) @available(macOS, unavailable)`—guard `.toolbarContainerBehavior(.local)` with `#if os(iOS)`.
  - **`draggable(_:containerNamespace:preview:)` (`27.3+`)**: Drag an `Identifiable & Transferable` item directly within a `@Namespace` container (`@available(iOS 27.3, macOS 27.3, visionOS 27.3, *)`).

---

## 7. AppKit 27.0 Interop, Touch on Mac (`macos-touch-gestures`) & 13 SDK-27 Runtime Behavior Changes

### A. AppKit $\leftrightarrow$ SwiftUI Bridging in macOS 27
1. **`NSHostingSceneRepresentation` (`NSApp.addSceneRepresentation`)**:
   Host SwiftUI `Window`, `UtilityWindow`, or `Settings` scenes inside an `NSApplicationDelegate` lifecycle without rewriting the app root:
   ```swift
   import AppKit
   import SwiftUI

   @MainActor
   func registerSwiftUIScenes() {
       NSApp.addSceneRepresentation(
           NSHostingSceneRepresentation {
               Settings {
                   Text("App Settings")
                       .frame(width: 480, height: 320)
               }
           }
       )
   }
   ```
2. **`NSHostingMenu`**: Render SwiftUI menu hierarchies (`Menu`, `Button`, `Picker`, `Toggle`, `Divider`, `Section`) natively inside an `NSMenu` for context menus, status-bar items, and dock menus.
3. **`NSGestureRecognizerRepresentable`**: Bridge custom `NSGestureRecognizer` subclasses directly into SwiftUI (`makeNSGestureRecognizer`, `updateNSGestureRecognizer`, `handleNSGestureRecognizerAction`) with `CoordinateSpaceConverter`.
4. **Automatic `@Observable` Tracking in AppKit**: When linked against SDK 27, reading `@Observable` properties inside `NSView.layout()`, `NSView.updateConstraints()`, `NSView.draw(_:)`, or `NSViewController.updateProperties()` automatically invalidates only the affected pass.
5. **Typed Concurrency-Safe Notifications (`NotificationCenter.MainActorMessage`)**:
   Use `NotificationCenter.default.addObserver(of: subject, for: NSWindow.DidBecomeKeyMessage.self) { message in ... }` to receive `@MainActor`-isolated notifications without `Sendable` warnings.

### B. Touch on Mac (`macos-touch-gestures` in Xcode 27.3 & `GestureInputKinds`)
Verified from Apple's bundled `macos-touch-gestures` skill (12 task guides in Xcode 27.3):
- **AppKit's 16pt Touch Forgiveness Radius & 24pt `NSControl` Auto-Growth**:
  - When a direct touch begins on macOS, AppKit hit-testing automatically searches within a **16pt forgiveness radius** and grows enabled `NSControl` instances whose width or height is smaller than **24pt** up to **24pt** around their center.
  - **Custom `NSView` caveat**: Plain `NSView` subclasses (that do not inherit from `NSControl`) do **not** get automatic 24pt touch target expansion! Either subclass `NSControl`, ensure the view's frame is $\ge 24\times 24\text{pt}$ (ideally $36\times 36\text{pt}$ in toolbars), or override `hitTest(_:)`.
- **Replace `event.clickCount == 2` with `NSClickGestureRecognizer`**:
  - On touch displays, double-taps have wider spatial tolerance than mouse double-clicks; manually checking `NSEvent.clickCount == 2` in `mouseDown(with:)` misses valid double-taps. Attach an `NSClickGestureRecognizer` with `numberOfClicksRequired = 2`.
- **Never Rely on `NSEvent.addLocalMonitorForEvents(matching: .leftMouseDown)` for Outside-Tap Dismissal**:
  - Touch taps outside a custom floating view or popover do **not** always emit `.leftMouseDown` events to local mouse monitors. Present transient popups with `NSPopover` (`popover.behavior = .transient`) so AppKit dismisses them on both pointer clicks and outside touch taps.
- **Keep `NSView.menu(for:)` Side-Effect-Free**:
  - On touch input, AppKit may call `menu(for:)` early during touch-down to probe for context-menu support without actually displaying the menu. Mutating selection or model state inside `menu(for:)` corrupts state on normal taps—move side effects into `NSMenuDelegate.menuWillOpen(_:)`.
- **Never Gate Actions Behind Hover Alone**: `.onHover` / `NSTrackingArea` (`mouseEntered`/`mouseExited`) must only provide visual enhancement; every action must be reachable via direct tap, context menu, or swipe.
- **Differentiating Pointer vs. Touch in SwiftUI**: Check `GestureInputKinds` (`.pointer`, `.touch`) when customizing gesture feedback.

### C. 13 SDK-27 Runtime Behavior Changes Checklist
Recompiling an app with `-sdk macosx27.2` activates runtime behavior gates checking the binary's `LC_BUILD_VERSION` SDK version:
1. **Menu Item Icons Hidden by Default (`NSMenuItem.preferredImageVisibility`)**: Standard app menu items hide their icons by default in macOS 27. To show an icon on a specific menu item, set `menuItem.preferredImageVisibility = .visible` (or `.labelStyle(.titleAndIcon)` in SwiftUI `Menu` / `.commands`).
2. **SwiftUI `Spacer` Minimum Length**: `Spacer()` inside `HStack`/`VStack` now defaults to `minLength: 0` when linked on SDK 27. Use `Spacer(minLength: 8)` when non-zero separation is required.
3. **`NSGlassEffectView` Inside `NSToolbarItem.view` Forbidden**: Never wrap custom toolbar views in `NSGlassEffectView`; `NSToolbarView` already manages the Liquid Glass bar and double-wrapping breaks hit testing.
4. **Full-Height Sidebar Safe Areas**: `NavigationSplitView` and `NSSplitViewController` sidebar items automatically extend edge-to-edge under the window toolbar; rely on safe-area insets rather than hardcoded top offsets.
5. **`@Observable` Automatic `NSView` Invalidation**: Enabled by default on SDK 27 (can be toggled via `NSObservationTrackingEnabled` in `Info.plist`).
6. **`NSMenu` Header & Section Spacing**: `NSMenuItem.sectionHeader(title:)` uses updated Golden Gate typography and compact group inset padding.
7. **`NSScrollView` Pocket & Edge Effect Propagation**: Scroll views automatically propagate content under translucent toolbars and `.backgroundExtensionEffect()` sidebars unless `.contentMargins` or `.scrollEdgeEffectHidden()` is set.
8. **`NSWindow.ToolbarStyle` Default**: Windows with a split view default to `.unified` with automatic Liquid Glass item grouping.
9. **`NSAlert` & Sheet Presentation**: Alerts and sheets anchor to the active document/inspector column when presented from a scoped hierarchy.
10. **`NSTextField` / `TextField` Focus Ring**: Uses high-contrast continuous capsule/rounded-rect focus rings matching the control's clip shape.
11. **`NSColor.controlAccentColor` Adaptation**: Dynamically shifts luminance over Liquid Glass surfaces.
12. **`FileDocument` / `ReferenceFileDocument` Soft Deprecation**: New document groups should adopt `Document` (`ReadableDocument` / `WritableDocument`) + `URLDocumentConfiguration`.
13. **`Table` Column Customization & Alignment**: `TableColumn` headers respect `.toolbarTitleAlignment` and Golden Gate row density metrics.

---

## 8. macOS 27 Intelligence Stack (`FoundationModels`, `CoreAI`, `SwiftData`, `Evaluations`)

### A. `FoundationModels` 27.0 (On-Device, Private Cloud Compute & Vision Tools)
Verified against `FoundationModels.swiftinterface` and `_Vision_FoundationModels.swiftinterface`:
- **Models**: `SystemLanguageModel.default` (on-device) and `PrivateCloudComputeLanguageModel()` (opt-in PCC; note: it is an initializer `PrivateCloudComputeLanguageModel()`, **not** `.default`).
- **Tool Calling Mode**: `GenerationOptions.ToolCallingMode` has `.allowed`, `.required`, and `.disallowed` (**not** `.automatic`).
- **Multimodal Attachments**: Construct `Attachment(imageURL: url)` (or pass `CGImage` / `CIImage` / `CVPixelBuffer`; **not** `Attachment(contentsOf:)` and **not** `NSImage`).
- **Vision Tools**: `import _Vision_FoundationModels` provides `OCRTool()` and `BarcodeReaderTool()` for `LanguageModelSession(model:tools:)`.
- **Headless CLI**: `/usr/bin/fm` runs quick terminal smoke tests against `SystemLanguageModel`.

```swift
import Foundation
import FoundationModels
import _Vision_FoundationModels

@Generable
struct DocumentExtraction: Sendable {
    @Guide(description: "Concise document summary")
    var summary: String
    @Guide(description: "Detected invoice or reference codes", .count(1...10))
    var codes: [String]
}

func extractFromImage(imageURL: URL) async throws -> DocumentExtraction {
    let model = SystemLanguageModel.default
    guard model.isAvailable else {
        throw CocoaError(.featureUnsupported)
    }
    let session = LanguageModelSession(
        model: model,
        tools: [OCRTool(), BarcodeReaderTool()]
    )
    let attachment = try Attachment(imageURL: imageURL)
    var options = GenerationOptions(temperature: 0.2)
    options.toolCallingMode = .allowed

    let response = try await session.respond(
        to: Prompt {
            "Extract the summary and reference codes from this image."
            attachment
        },
        generating: DocumentExtraction.self,
        options: options
    )
    return response.content
}
```

### B. `CoreAI` 27.0 (`AIModel`, `SpecializationOptions`, `NDArray`, `Span`)
Verified against `CoreAI.swiftinterface`, `CoreAIDelegates.swiftinterface`, and `CoreAIRuntime.swiftinterface`:
- **Import only `CoreAI`** (never `import CoreAIRuntime` directly, which fails with `module 'CoreAIRuntime' is an implementation detail of 'CoreAI'`).
- **`SpecializationOptions`**: Use `.default`, `.cpuOnly`, or `SpecializationOptions(preferredComputeUnitKind: .neuralEngine)` (**not** `computeUnits: .all`).
- **`InferenceFunction.run`**: Takes `inputs: [String: NDArray]` directly (`InferenceValue` is `~Copyable`).
- **`NDArray.View<Scalar>`**: Non-escapable (`~Escapable`) and does **not** conform to `Sequence`; read elements via `view.contiguousElements` (`Span<Scalar>?`).

```swift
import Foundation
import CoreAI

func runEmbeddingModel(compiledBundleURL: URL, inputFloats: [Float]) throws -> [Float] {
    let aiModel = try AIModel(contentsOf: compiledBundleURL)
    let specialized = try aiModel.specialize(options: .default)
    let fn = specialized.defaultFunction

    let inputTensor = try NDArray(shape: [1, inputFloats.count], scalars: inputFloats)
    let outputs = try fn.run(inputs: ["input": inputTensor])
    guard let outputTensor = outputs["embedding"] else { return [] }

    let view = try outputTensor.readOnlyView(of: Float.self)
    guard let span = view.contiguousElements else { return [] }
    var result: [Float] = []
    result.reserveCapacity(span.count)
    for i in 0..<span.count {
        result.append(span[i])
    }
    return result
}
```

### C. `SwiftData` 27.0 (`ResultsObserver`, `HistoryObserver`, `fetchCount`, `fetchIdentifiers`)
- Outside SwiftUI views (e.g., in `@Observable` services or background actors), observe live query diffs using `ResultsObserver<Model>` and transaction history using `HistoryObserver` instead of polling `ModelContext.fetch`.
- Use `try modelContext.fetchCount(descriptor)` and `try modelContext.fetchIdentifiers(descriptor)` to count or paginate large datasets without fault-instantiating full `@Model` objects.

### D. `Testing` (`_Testing_AppKit` / `_Testing_UIKit`), `Evaluations` (`SiriEvaluations`), and Siri Tool Intents (`27.3+`)
- `swift_sdk_interface` indexes `Developer/Library/Frameworks/` automatically:
  - Query `module: "Testing"` for Swift Testing (`@Test`, `#expect`, `#require`, `Confirmation`, `@Test(arguments:)`), plus Xcode 27.3's visual attachment companion modules (`_Testing_AppKit`, `_Testing_UIKit`, `_Testing_CoreGraphics`, `_Testing_CoreImage` providing `AttachableImageFormat` to attach `NSImage`/`NSView`/`UIView` snapshots directly to `@Test` results).
  - Query `module: "Evaluations"` for LLM/generative evaluation suites (`Evaluation`, `Judge`, `KeywordMatchJudge`) and Xcode 27.3's `SiriEvaluations` (`SiriScenario`, `SiriExpectationEvaluator`).
  - Query `module: "AppIntentsTesting"` for deterministic unit tests of `AppIntent` and `AppEntity` implementations.
- **Siri Tool Intents & `Skills.skillsbundle` (`siri-app-integration` in 27.3+)**:
  - Annotate intents exposed as LLM tools to Siri with `@AppIntent(.tool)` (or `@AppIntent(.tool, schema:)`), entities with `@AppEntity(.generable)` and `@Property(description:, visibility: .internal)`, package app-specific agent skills in `Skills.skillsbundle` containing `SKILL.md` files, and validate metadata with `xcrun sirimetadataanalyzer`.

---

## 9. Ground-Truth `.swiftinterface` & Bundled Apple Guide Queries (`swift_sdk_interface`)

`sourcekit_mcp.py` indexes **four** local ground-truth sources inside `/Applications/Xcode.app`:
1. **`System/Library/Frameworks/`**: `SwiftUI`, `SwiftUICore`, `DeveloperToolsSupport`, `AppKit`, `UIKit`, `Foundation`, `Observation`, `FoundationModels`, `_Vision_FoundationModels`, `CoreAI`, `SwiftData`, `StateReporting`, `MetricKit`, `WebKit`, `Metal`.
2. **`System/Library/SubFrameworks/`**: `CoreAIRuntime`, `CoreAIDelegates`, `CoreAIAsset`, `CoreAICache`, `CoreAICompiler`, `CoreAICommon` (automatically searched when querying `module: "CoreAI"`).
3. **`Developer/Library/Frameworks/` & `ManifestAPI`**: `Testing`, `Evaluations`, `AppIntentsTesting`, `XCUIAutomation`, `PackageDescription`.
4. **Virtual Documentation Modules (`XcodeSkills`, `XcodeDocs`, `SwiftDiagnostics`)**:
   - `{"module": "XcodeSkills", "symbol": "State macro"}` $\rightarrow$ searches Apple's bundled Xcode 27 Agent Skills (`swiftui-whats-new-27`, `swiftui-specialist`, `building-document-based-swiftui-applications`, `app-resizability`, `app-intents-whats-new-27`, `modernize-tests`, etc.).
   - `{"module": "XcodeDocs", "symbol": "Liquid Glass"}` $\rightarrow$ searches Xcode's 20+ `AdditionalDocumentation` guides (`SwiftUI-Implementing-Liquid-Glass-Design.md`, `AppKit-Implementing-Liquid-Glass-Design.md`, `SwiftUI-New-Toolbar-Features.md`, `Swift-Concurrency-Updates.md`, `Swift-InlineArray-Span.md`, `FoundationModels-Using-on-device-LLM-in-your-app.md`).
   - `{"module": "SwiftDiagnostics", "symbol": "nonisolated-nonsending"}` $\rightarrow$ searches all 76 Swift 6.4 compiler diagnostic explanations.
   - Or pass `"include_guides": true` on any framework query (e.g. `{"module": "SwiftUI", "symbol": "ToolbarSpacer", "include_guides": true}`).
