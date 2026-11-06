# Resolving Swift 6 Strict Concurrency Diagnostics with `swift-lsp`

Swift 6 strict concurrency (`-swift-version 6`) enforces data-race safety at compile time. When building standalone macOS 27.2+ and iOS 27.2+ apps (e.g., streaming SSE `/v1/messages` responses on background tasks while driving `@MainActor` `@Observable` state and `SwiftUI` / `AppKit` views), use `swift_hover`, `swift_definition`, and `swift_diagnostics` to inspect compiler-inferred isolation rather than guessing annotations.

---

## 1. Diagnosing Actor Isolation Mismatches via `swift_hover`

When `swift_diagnostics` reports:
- `Main actor-isolated property '...' can not be referenced from a nonisolated context`
- `Main actor-isolated instance method '...' cannot be called from outside of the actor`
- `Call to main actor-isolated initializer '...' in a synchronous nonisolated context`

### Resolution Protocol
1. **Do not blindly slap `@unchecked Sendable` or `nonisolated(unsafe)` on types.**
2. Call **`swift_hover`** on:
   - The **caller** function or closure symbol (`file`, `line`, `symbol`), and
   - The **callee** property, method, or protocol requirement.
3. Inspect the hover signature returned by `sourcekit-lsp`:
   - `SwiftUI.View` (`macOS 27.2+` / `iOS 27.2+`), `NSView`, `NSViewController`, `NSWindowController`, `NSPanel`, and `UIViewController` are **`@MainActor`-isolated as a whole**.
   - If a view model or store drives UI state (`@Observable final class ChatStore`), mark the class **`@MainActor`** at the declaration level so all its properties and methods share `@MainActor` isolation with the views that observe it.

---

## 2. Diagnosing `Sendable` & Region-Based Isolation (`sending`) Errors

When `swift_diagnostics` reports:
- `Sending 'self.stream' risks causing data races`
- `Capture of '...' with non-sendable type '...' in a '@Sendable' closure`
- `Non-sendable type '...' returned by implicitly asynchronous call to nonisolated function cannot cross actor boundary`

### Resolution Protocol
1. Call **`swift_hover`** on the captured variable or return value to check its inferred type and whether it is a reference type (`class`), closure, or value type (`struct`/`enum`) containing a non-`Sendable` field.
2. Call **`swift_definition`** (`kind: "typeDefinition"`) to inspect the type's stored properties:
   - **Wire DTOs, SSE events, and configuration structs**: Make them immutable `struct` or `enum` values conforming to `Sendable` (`public struct MessageChunk: Sendable, Codable`).
   - **Streaming network / local LLM clients (`URLSession.AsyncBytes`)**: Keep the raw `URLSession` byte parsing inside a `nonisolated` `async` function or dedicated `actor`, and yield only immutable `Sendable` value events across an `AsyncThrowingStream<StreamEvent, Error>` to the `@MainActor` store.
   - **Transferring ownership across isolation regions (`sending`)**: In Swift 6, use `sending` parameters/returns when a non-`Sendable` value is uniquely owned and handed off once to another isolation domain without retaining a local alias.

---

## 3. Protocol Witness & Delegate Conformance Isolation Traps

When implementing `AppKit` / `UIKit` / `Foundation` delegates (`NSWindowDelegate`, `NSTextViewDelegate`, `URLSessionTaskDelegate`) in Swift 6:
1. Call **`swift_sdk_interface`** (`module: "AppKit"`, `symbol: "protocol NSWindowDelegate"`) or **`swift_definition`** on the protocol name to see whether each protocol method is `@MainActor` or `nonisolated` in the 27.2 SDK.
2. If a `@MainActor` class implements a `nonisolated` delegate requirement that only passes `Sendable` parameters, mark that witness `nonisolated` and hop via `Task { @MainActor in ... }` if needed.
3. If the delegate requirement is already `@MainActor` in the 27.2 SDK `.swiftinterface`, implement it directly on your `@MainActor` class without `nonisolated`.
