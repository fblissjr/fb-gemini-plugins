# Resolving Swift 6.4+ Concurrency, Observation 27.0 & Memory-Safe Stdlib Diagnostics

Swift 6.4 (`-swift-version 6`) enforces compile-time data-race safety while introducing **Approachable Concurrency (`SE-0461`, `SE-0466`, `SE-0470`)**, **Resource & Lifetime Safety (`SE-0493`, `SE-0504`, `SE-0518`)**, **`Observation` 27.0 (`withContinuousObservation`)**, and **memory-safe contiguous containers (`InlineArray`, `Span`, `UniqueArray`)**. Use `swift_hover`, `swift_definition`, `swift_sdk_interface`, and `swift_diagnostics` to inspect compiler-inferred isolation rather than guessing annotations.

---

## 1. Swift 6.4 Approachable Concurrency (`SE-0461`, `SE-0466`, `SE-0470`)

### A. Per-Target Default MainActor Isolation (`SE-0466`)
In Swift 6.4 (`swift-tools-version: 6.4`), targets can opt into `.defaultIsolation(MainActor.self)` in `Package.swift` (or `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` in Xcode):
- **UI / App targets**: All declarations in the target default to `@MainActor` unless explicitly marked `nonisolated` or `@concurrent`.
- **Compute / Server / Parser targets**: Typically remain `nonisolated` by default.
- `sourcekit_mcp.py` automatically parses per-target `swiftSettings` in `Package.swift` so `swift_diagnostics` passes `-default-isolation MainActor` only for files belonging to `@MainActor`-default targets.

### B. `nonisolated(nonsending)` by Default vs. `@concurrent` (`SE-0461`)
- **`nonisolated(nonsending)` (`NonisolatedNonsendingByDefault`)**: `nonisolated async` functions inherit the caller's actor executor instead of automatically hopping to the global concurrent executor. If called from `@MainActor`, they execute on the main actor without requiring non-`Sendable` arguments to cross an isolation boundary.
- **`@concurrent`**: When a function performs CPU-heavy work (e.g., JSON/SSE parsing, image resizing, `CoreAI` tensor prep, or `DocumentReader`/`DocumentWriter` I/O) and **must** hop off the caller's actor onto the global concurrent pool, annotate it with `@concurrent`:
  ```swift
  @concurrent
  func decodeLargePayload(_ data: Data) async throws -> ParsedDocument {
      try JSONDecoder().decode(ParsedDocument.self, from: data)
  }
  ```

### C. Global-Actor Isolated Protocol Conformances (`SE-0470`)
When a `@MainActor` class conforms to a protocol (`Equatable`, `Hashable`, `Codable`, or a custom protocol):
- Use **isolated conformances** (`structOrClass: @MainActor Equatable`) when equality/hashing reads `@MainActor`-isolated stored properties:
  ```swift
  @MainActor
  @Observable
  final class LayerModel: @MainActor Equatable {
      var id: UUID
      var name: String
      init(id: UUID = UUID(), name: String) {
          self.id = id
          self.name = name
      }
      static func == (lhs: LayerModel, rhs: LayerModel) -> Bool {
          lhs.id == rhs.id && lhs.name == rhs.name
      }
  }
  ```
- Conversely, if a type inside a `.defaultIsolation(MainActor.self)` target is a pure wire DTO that needs background `Codable` synthesis, mark its conformance **`nonisolated Codable, Sendable`**.

---

## 2. Resource & Lifetime Safety (`SE-0493`, `SE-0504`, `SE-0518`)

### A. `await` Inside `defer` (`SE-0493`) + `withTaskCancellationShield` (`SE-0504`)
In Swift 6.4, standard `defer { ... }` blocks inside `async` functions can contain `await` expressions. When an `async` function is cancelled, any `await` inside `defer` would immediately fail if the cleanup call checks `Task.isCancelled`. Pair `defer` with **`await withTaskCancellationShield { ... }`**:

> [!IMPORTANT]
> - There is **no** `async defer` keyword (`async defer` is a syntax error). Write a standard `defer { ... }` block containing `await`.
> - Always **`await` `withTaskCancellationShield`** inside an async cleanup block; omitting `await` selects the synchronous overload and fails with `error: 'async' call in a function that does not support concurrency`.

```swift
actor TelemetryBuffer {
    func flushToDisk() async throws {}
    func closeFileDescriptor() async {}
}

func processStream(buffer: TelemetryBuffer) async throws {
    defer {
        await withTaskCancellationShield {
            try? await buffer.flushToDisk()
            await buffer.closeFileDescriptor()
        }
    }
    try await Task.sleep(for: .milliseconds(50))
}
```

### B.Explicit `@MainActor` State Lockout (`~Sendable`, `SE-0518`)
To guarantee at compile time that an `@MainActor` state container can **never** be sent across actor boundaries (even if all its stored fields are value types), suppress `Sendable` synthesis with `~Sendable`:

```swift
@MainActor
@Observable
final class WindowWorkspaceState: ~Sendable {
    var selectedTabID: String = "home"
    var isInspectorOpen: Bool = true
}
```

### C. Move-Only `Continuation<Success, Failure>: ~Copyable` (Stdlib 27.0)
In SDK 27.0 (`_Concurrency`), `withContinuation` / `withThrowingContinuation` provide a move-only `Continuation<T, E>: ~Copyable` whose `resume(returning:)` is a `consuming` method—turning double-resumption or forgotten-resumption bugs from runtime crashes into compile-time ownership errors.

---

## 3. `Observation` 27.0 (`withContinuousObservation`)

In macOS 27.0 / iOS 27.0 (`@available(anyAppleOS 27.0, *)`), `Observation` replaces one-shot `withObservationTracking` loops with **`withContinuousObservation`**, returning a move-only `ObservationTracking.Token: ~Copyable` that automatically cancels observation when deinitialized:

```swift
import Observation

@MainActor
@Observable
final class AudioMeterModel {
    var peakDecibels: Float = -60.0
}

@MainActor
final class StatusBarBridge {
    private var observationToken: ObservationTracking.Token?

    func bind(to meter: AudioMeterModel) {
        observationToken = withContinuousObservation(options: [.didSet]) {
            _ = meter.peakDecibels
        } onChange: { event in
            // React to `.willSet`, `.didSet`, or `.deinit` events
            _ = event
        }
    }
}
```

---

## 4. Memory-Safe Contiguous Stdlib Types (`InlineArray`, `Span`, `UniqueArray`)

Swift 6.4 (`@available(anyAppleOS 27.0, *)`) ships safe stack/inline and non-escapable contiguous memory primitives (`--strict-memory-safety`):

| Type | Characteristics | Primary Use Case |
| :--- | :--- | :--- |
| **`InlineArray<let count: Int, Element>`** | Fixed-size, stack/inline value buffer (`~Copyable` / `~Escapable` compatible); zero heap allocation | Small lookup tables, fixed-dimension vectors, audio/DSP filter state, shader uniforms (`var weights: InlineArray<4, Float> = [0.25, 0.25, 0.25, 0.25]`). |
| **`Span<Element>` / `RawSpan`** | Non-escapable (`~Escapable`) bounds-checked read-only view over contiguous memory | Zero-copy parsing, reading `CoreAI.NDArray.View.contiguousElements`, and replacing `UnsafeBufferPointer` under `.strictMemorySafety()`. |
| **`MutableSpan<Element>` / `OutputSpan<Element>`** | Non-escapable (`~Escapable`) mutable or uninitialized output buffer view | Filling buffers safely in-place without `UnsafeMutableBufferPointer`. |
| **`UniqueArray<Element>: ~Copyable`** | Move-only heap array with guaranteed unique ownership (zero COW refcount overhead) | High-throughput buffers transferred across pipeline stages without accidental copy-on-write cloning. |

---

## 5. Diagnosing Actor Isolation & `Sendable` Mismatches via `swift-lsp`

1. **Inspect Compiler-Inferred Isolation**:
   Call `swift_hover` on both the **caller** and **callee** symbols (`file`, `line`, `symbol`) to see whether the symbol is `@MainActor`, `nonisolated(nonsending)`, or `@concurrent`.
2. **Lookup Official Swift 6.4 Compiler Diagnostic Guides**:
   Call `swift_sdk_interface` with `module: "SwiftDiagnostics"` and `symbol` set to the diagnostic topic (e.g., `"conformance-isolation"`, `"isolated-conformances"`, `"nonisolated-nonsending-by-default"`, `"strict-memory-safety"`, `"sending-risks-data-race"`, `"use-any-apple-os-availability"`).
3. **Check Delegate Witness Isolation in SDK 27.2**:
   Call `swift_sdk_interface` (`module: "AppKit"`, `symbol: "NSWindowDelegate"`) before implementing `AppKit` / `UIKit` delegates to check whether the method is already `@MainActor` in `MacOSX27.2.sdk`.
