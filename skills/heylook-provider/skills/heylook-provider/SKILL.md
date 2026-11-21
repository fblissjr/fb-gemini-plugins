---
name: heylook-provider
description: Wire an application to heylook (heylookitsanllm), a local multimodal LLM server on Apple Silicon serving MLX and gguf models over an Anthropic Messages-conformant /v1/messages endpoint. Use when adding heylook as a provider alongside Gemini, OpenAI or Anthropic, choosing between direct /v1/messages, presets and the conversation store, tuning system prompts, sampler cascades or prompt caching (thinking replay, multi-image turns), configuring x-api-key or Bearer auth, debugging 400/401/403/404/409/422/503 errors, parsing SSE streams, cancelling requests or ending thinking early, computing multimodal embeddings, sending images or audio, or porting off the removed OpenAI route. Covers install-local model discovery, capability gating, Anthropic SDK vs raw HTTP tradeoffs, and client-side image resize. Not for hosted Gemini APIs or working inside heylook itself.
metadata:
  verified_against: "heylookitsanllm 2.0.264"
---

# heylook as an inference provider

Local inference server on Apple Silicon: MLX (`mlx-vlm` via heylook's thin `B=1` CoW runner or `BatchGenerator` fallback) plus gguf (`llama-server` subprocesses). Default base `http://localhost:8000`.

`POST /v1/messages` conforms to Anthropic's Messages API (typed content blocks, top-level `system`, `stop_sequences`, Messages SSE grammar with `ping` keepalives and no `[DONE]`), so Anthropic habits mostly transfer. What differs follows from the server being **local and single-user**: model ids belong to the install, capabilities vary per model, images are resized by you, unset sampler fields use the model's own cascade, and a busy server queues rather than scales.

This file states behaviour as of `metadata.verified_against`. For older servers, read `server_version` from `/v1/capabilities`, then `references/older_servers.md`.

<done>
Each line points to the section that states the rule; never weaken a pointer into a second copy.

- Model ids resolved at runtime, never literal in source, and always sent. → `<discovery>`
- Features gated on `capabilities` and `engine`, **plus** handling 400, in-band `invalid_request_error`, and the silent gguf case. → `<discovery>`
- Unset sampler fields omitted for cascade defaults; presets client-expanded with store-to-wire renames; conversation store distinguished from `/v1/messages`. → `<parameters>`
- Prompt caching kept warm via top-level `system`, replayed assistant `thinking` blocks, stable `reasoning_effort`, and single-turn multi-image sets. → `<caching>`
- Images downscaled client-side before the request is built. → `<image_resize>`
- `401` (`auth_required`), `403` (Host check or `csrf_rejected`), and `503` (`model_overloaded` backoff vs `auth_misconfigured` hard error) handled distinctly; in-band `error` events end `/v1/messages` streams and never render as assistant output. → `<status_codes>`
- Optional access key (`x-api-key` or `Authorization: Bearer`), always-on `Origin`/`Sec-Fetch-Site` rules, fresh per-request `X-Request-ID`, and explicit `DELETE` on non-streaming cancel honoured. → `<operations>`
- Telemetry null-checked, with `generation_duration_ms` as the throughput denominator. → `<operations>`
</done>

<discovery>
Model ids are **install-local**. The registry is override-only: any model under a scanned folder is served with derived defaults, so an id that worked on one machine is a 400 on another. There is no default model: a request without `model` is a 400 listing the ids.

Query the live server before writing client code; if it is down, ask the user to start it rather than guessing ids:

```bash
curl -s localhost:8000/v1/models        # add -H "x-api-key: $HEYLOOK_API_KEY" when gated
curl -s localhost:8000/v1/capabilities  # server version, Metal device, optimizations
python3 "${CLAUDE_SKILL_DIR:-skills/heylook-provider/skills/heylook-provider}/scripts/probe.py" --base http://localhost:8000 --need vision
```

`probe.py` automatically sends `--api-key`, `HEYLOOK_API_KEY`, or a mode-`0600` `<HOME>/.heylook/api_key` (`$HEYLOOK_API_KEY_FILE`). It exits `0` when matched, `2` when no model meets `--need` (including an empty roster), and `1` when unreadable (`401` = access gate or proxy requires a key; `403` = heylook Host check; `503 auth_misconfigured` = bad key-file permissions).

**Gate features on `capabilities`, not `modalities`.** Filter chat selectors on `chat`: embedding models advertise `embedding` and input modalities with no `chat` (sending `/v1/messages` to one is a 400; use `POST /v1/embeddings`, `references/embeddings.md`). MLX strips audio towers at load, so MLX never advertises `audio` (sending audio is a 400; gguf serves it with a projector).

Read finer controls from each row's `engine` object (`{value, provenance, source}` facts read at `.value`; `engine.thinking` is a plain object; full shape in `references/wire_reference.md`):

- `engine.context.length.value`: context window ceiling.
- `engine.thinking`: template switch, `depth` vocabulary (`values`, `aliases`, `default`, `off`, `changes_prefix`, `unknown`), and `budget`.
- `engine.decoding`: `mode` (`autoregressive` | `diffusion`), `request_fields` (hide controls not listed when non-null), and on loaded autoregressive MLX models `runner` (`b1_runner` vs `batch_generator`).
- `engine.cache`: `reuse_mode` (`cow_prefix` / `cow_prefix_recurrent` on `b1_runner`, `checkpoints` / `blocks` on fallback), `image_reuse`, `memory_budget_bytes`.
- `engine.template.prefix_stable` and `engine.template.caps` (`chat_template_caps` on loaded gguf; `not_applicable` on MLX).
- `engine.embedding`: non-null on embedding models (`modalities`, `dimensions`, `prompts`, `video_windows`, `limits`).

Handle media refusals anyway: MLX refuses images on non-user turns with a 400, explicit `heylook.toml` `capabilities` overrides are honoured verbatim, and gguf forwards blocks to `llama-server` (400 / `invalid_request_error` on rejection, or a silent 200 ignoring the image). Refusals arrive as HTTP 400 non-streaming or an in-band `event: error` (`invalid_request_error`) on streams. `GET /openapi.json` is generated at boot and outranks all prose.
</discovery>

<parameters>
Choose your integration surface and parameter spellings deliberately:

| Surface | System prompt | Sampler & thinking keys | History / media ownership |
|---|---|---|---|
| **Direct `POST /v1/messages`** | Top-level `system` string (`system_prompt` = 422) | Wire names: `thinking` (bool or `{type, budget_tokens}`), `reasoning_effort`, `max_tokens`, etc. | Client owns turns and media; stateless |
| **Presets `GET /v1/presets` -> `/v1/messages`** | Preset `system_prompt` expanded into top-level `system` | Client expands store `params`: rename `enable_thinking` & `thinking_budget_tokens` -> `thinking`; filter `reasoning_effort` | Client expands preset per request (`preset` on wire = 422) |
| **Conversation Store `/v1/conversations`** | `system_prompt` column on conversation | Store names (`enable_thinking`, `thinking_budget_tokens`): `params` 422-validated on write; `overrides` silently drops bad keys | Server DuckDB store + immutable `/media/{id}` blobs |

1. **4-layer sampler cascade (omit what you have no opinion on).** When `/v1/messages` omits a sampler knob, heylook resolves: `GLOBAL_SAMPLER_FLOOR` (`temperature: 1.0`, `top_p: 0.95`, `max_tokens: 16384`, penalties/top_k off) -> **vendor metadata** (`generation_config.json` on MLX, `general.sampling.*` on GGUF) -> model `heylook.toml` -> request. Inspect resolved values per model via `sampler_defaults` and `sampler_sources` on `/v1/models`. Unlike Anthropic, `max_tokens` is optional: hardcoding a client default overrides every model's vendor/configured floor.
2. **Presets are strictly client-expanded (`references/routes.md`, `references/client_recipes.md`).** Sending `preset` or `sampler` on `/v1/messages` is a 422. Follow the **override-box rule**: if a preset's `system_prompt` is `null` or `""`, leave the caller's or conversation's system prompt untouched rather than blanking it. Always rename `enable_thinking` / `thinking_budget_tokens` to `thinking` and drop unoffered `reasoning_effort` before posting to `/v1/messages`.
3. **Conversation Store (`/v1/conversations/{id}/generate`).** Server builds the prompt, persists turns, and runs generations in a detached task that **outlives client disconnect** (`GET` reports `generating: true|false`; stop only via `DELETE /v1/conversations/{id}/generate`). Only one run per conversation (`409 generation_in_progress`).
4. **Anthropic SDK vs. raw HTTP (`httpx`/`fetch`).** With the Anthropic SDK, set `base_url` to the origin (`http://localhost:8000`, no `/v1`) and pass `api_key` (the real key when the access gate is on, or any placeholder when off; `auth_token` also works via `Authorization: Bearer`). Tradeoffs: the SDK forces `max_tokens` (overriding the cascade), requires `extra_body` for extensions (`min_p`, `repetition_penalty`, `presence_penalty`, `seed`, `reasoning_effort`, `response_format`), and drops `heylook_progress` / `message_stop.performance`. Use raw HTTP when you want full cascade semantics, telemetry, and cancellation control.
</parameters>

<wire>
`/v1/messages` is the only inference route (`/v1/chat/completions` is 404; `references/openai_wire.md`).

Key differences from Anthropic's Messages API:

- **`max_tokens` is optional** (see `<parameters>`).
- **`thinking` takes a bool** or `{"type": "enabled"|"disabled", "budget_tokens": N}` (both fields optional; gate `budget_tokens` on `thinking_budget`; 400 on MLX harmony models).
- **`reasoning_effort`** uses each model's own template vocabulary (`engine.thinking.depth.values`, `depth.off` folds into off, `depth.unknown: "verbatim"` accepts any word). Never map a generic low/medium/high scale across models; an unoffered value is a 400.
- **No tools**: `tools` and `tool_choice` are a 422.
- **`response_format`** uses OpenAI's shape (`json_schema`, `json_object`, `text`); 400 on harmony, diffusion, and continuations.
- **Thinking blocks carry no `signature`**, and there is no `signature_delta`. Join only `text` output blocks for the answer (`thinking` blocks hold reasoning, echoed under both `thinking` and `text`).
- **`message_start.usage.input_tokens` is 0**; read usage from `message_delta`. Whole prompt = `input_tokens` (processed) + `cache_read_input_tokens` (reused).
- **A trailing assistant message is continued**, not answered; a thinking-only trailing assistant turn resumes inside that thought.
- **Refused vs ignored fields**: `logprobs`, `top_logprobs`, `sampler`, `preset`, `vision_tokens`, `tools`, `tool_choice`, `show_special_tokens: true`, and misspellings `enable_thinking`, `max_new_tokens`, `system_prompt`, `chat_template_kwargs` are a **422** naming the fix. Other unknown fields are **silently ignored**.
- **Extensions & engine notes**: `min_p`, `repetition_penalty`, `repetition_context_size`, `presence_penalty`, `seed`, `reasoning_effort`, `response_format`; on streams, `heylook_progress` and `message_stop.performance`. Note `presence_penalty` and `repetition_penalty` count **generated-only** tokens on MLX vs **prompt + generated** on GGUF; on MLX `mtp` drafters, penalties and `budget_tokens` draft (non-MTP drafters, `response_format`, logit bias, and prompts past `draft_max_context` run undrafted). Detail: `references/wire_reference.md`.
</wire>

<caching>
Both engines reuse KV prefixes automatically across turns and requests (MLX via `b1_runner` zero-copy CoW `PrefixCacheStore` or `BatchGenerator` APC; gguf via `llama-server` slot cache + `-cram`). Maximize hits by structuring prompts cleanly:

1. **Put shared instructions in top-level `system` (exact boundary cached on text and vision)** or place static preamble ahead of variable input in `user_only` turns (coarse interior checkpoints).
2. **Preserve assistant `thinking` blocks in multi-turn `messages` history.** `InputContentBlock` accepts `ThinkingBlock`. Replaying prior `thinking` blocks preserves KV prefix hits on models whose templates keep reasoning (e.g. Qwen3.8 on both engines); stripping them breaks the prefix at the closed thought. heylook adapts `thinking` per template (`reasoning_content`, `<think>` tags, or drop).
3. **Keep `reasoning_effort` steady mid-thread** when `engine.thinking.depth.changes_prefix` is true; changing it alters the rendered prefix and forces a full re-prefill.
4. **Send multi-image sets together in one turn.** Interleaved `text` + `image` block order is preserved on both engines. Text follow-ups in an image thread reuse both vision features and KV (`image_reuse: true` on `b1_runner`), whereas **adding a new image in a later turn** changes the whole-list media hash (`performance.cache.cause == "new_image_set"`), re-prefilling and re-encoding images.
5. **Verify reuse in responses:** check `engine.template.prefix_stable.value` up front and inspect `usage.cache_read_input_tokens` and `performance.cache` (`outcome`, `cause`, `cached_tokens`).
</caching>

<image_resize>
`/v1/messages` has no resize params; resize client-side before sending: longest edge ~2048px, photos as JPEG ~0.85 quality, PNG kept as PNG, EXIF orientation applied. Only `base64` (raw, no `data:` prefix) and `http(s)` URLs (MLX refuses local paths). Prefer Anthropic's nested `source` object (`/v1/conversations` requires it). `POST /v1/models/{id}/image-plan` (resident models only; 409 otherwise) returns token cost and engine resize `target` (null on gguf) for disclosure. Recipes: `references/client_recipes.md`.
</image_resize>

<status_codes>
| Code | Meaning | Response |
|---|---|---|
| 400 | Pick a different model or input | No `model`, unknown/disabled id (ids in `detail`), or model refusal (unoffered capability/depth, over-long prompt, harmony budget/schema, audio on MLX, non-user image on MLX) |
| 401 | Authentication required | `{"error":{"code":"auth_required"}}` (+ `WWW-Authenticate: Bearer`) when the server access gate is on and `x-api-key` / `Authorization: Bearer` / session cookie is missing or invalid; or `X-Heylook-Admin-Token` missing on admin routes |
| 403 | Host or Origin/Sec-Fetch-Site check | Unknown `Host` header (`allowed_hosts` fix in `detail`), or state-changing request (`POST`/`PUT`/`PATCH`/`DELETE`) with mismatched `Origin` or `Sec-Fetch-Site` (`cross-site`/`same-site`) (`{"error":{"code":"csrf_rejected"}}`) |
| 409 | Conflict / not resident | Conversation busy (`generation_in_progress`), `/image-plan` or `/prompt` on unloaded model, unload while generating, or cancelled embedding |
| 422 | Malformed body | Refused/misspelt/unbuilt field, empty media payload, out-of-range value, or extra field on strict `/v1/embeddings` |
| 500 | Broken model or decode error | Load failure or gguf decode error |
| 503 | Backpressure (retry) or key misconfigured | `{"error":{"code":"model_overloaded"}}` + `Retry-After` (retry with backoff), **or** `{"error":{"code":"auth_misconfigured"}}` (key file has group/other bits or is empty — fail fast, do not retry) |

503 `model_overloaded` is normal queue backpressure on a single-user server: retry with backoff on `Retry-After` (floor >= 1s), after checking `error.code != "auth_misconfigured"`. On a stream after headers flush (HTTP 200), late refusals arrive as `event: error` (`invalid_request_error` -> 400 path; `api_error` -> 500 path), ending `/v1/messages` streams immediately. Ignore `ping` and unrecognized events.
</status_codes>

<operations>
- **Cold loads are silent on the wire.** Startup loads nothing, and loading happens before HTTP headers are written (no `message_start`, no `ping`). Use `POST /v1/models/{id}/load` (percent-encode `{id}`) to turn loads into a labellable request; add `?warm=true` only on startup/model-switch (pays 1-token Metal JIT behind the generation gate).
- **One model is resident by default (LRU), and one engine family at a time**: switching MLX <-> gguf evicts the other. Batch work by model.
- **Opt-in server-wide access gate + always-on browser guards.** Setting `HEYLOOK_API_KEY` or creating a mode-`0600` `<HOME>/.heylook/api_key` (`$HEYLOOK_API_KEY_FILE`, never in `heylook.toml`) gates **every** route, static asset, and SSE stream with zero source-IP exemptions (only `GET/HEAD /health` -> `{"status":"ok"}` and `/login` assets are unauthenticated). Clients send `x-api-key: <key>`, `Authorization: Bearer <key>`, or sign in once at `/login` (`heylook_session` cookie; `POST /logout` revokes). Independently of any key, every response carries `Content-Security-Policy: frame-ancestors 'self'` (no CORS), `HostCheckMiddleware` enforces `allowed_hosts`, and state-changing requests (`POST`/`PUT`/`PATCH`/`DELETE`) with mismatched `Origin` or `Sec-Fetch-Site` (`cross-site`/`same-site`) answer `403 csrf_rejected` (`tailscale serve` requires its `.ts.net` name in `allowed_hosts`; non-browser HTTP clients omit both headers and pass). `HEYLOOK_ADMIN_TOKEN` (`X-Heylook-Admin-Token`) is an optional second factor for headless admin callers only — the web UI never sends it.
- **Send a fresh `X-Request-ID` per request** (UUID matches `[A-Za-z0-9._:-]{1,128}`). Reused ids cancel every request sharing them! Track it for `DELETE /v1/requests/{request_id}` (essential for non-streaming calls since hanging up does not stop them; cancelled runs return `stop_reason: "max_tokens"`).
- **End thinking early with the same id**: `POST /v1/requests/{request_id}/reasoning-end` closes the open `thinking` block at the next token and continues to the reply (`200` = signalled, not yet closed). Use `DELETE`/`POST` under `/v1/conversations/{id}/generate` for conversation runs.
- **Telemetry is always on and optional per field.** Null-check `performance` (absent in streams vs `null` non-streaming) and every sub-field. Throughput denominator is `generation_duration_ms` (excludes queue wait and load); TTFT is never returned (time the first delta yourself).
</operations>

<references>
| File | Holds | Load when |
|---|---|---|
| `references/wire_reference.md` | Every `/v1/messages` field, block, cascade, caching, stream event, error, Access gate, and `/v1/models` `engine` row | Writing or debugging a request |
| `references/older_servers.md` | Version boundaries by topic | Target server predates `metadata.verified_against` |
| `references/openai_wire.md` | Porting off removed `/v1/chat/completions` | Migrating an OpenAI-SDK client |
| `references/embeddings.md` | `POST /v1/embeddings`: multimodal inputs, `limits`, `video_windows` (`"fps"` default vs `"content"`) | Computing embeddings |
| `references/routes.md` | Surface comparison matrix, `/health` & `/login`, conversation store, presets, and admin routes | Using presets, conversation store, or admin endpoints |
| `references/gemini_migration.md` | Field mapping and structural mismatches vs Gemini `generateContent` | Adding heylook beside Gemini |
| `references/client_recipes.md` | Auth-ready streaming clients, Anthropic SDK setup, preset expansion, embeddings batching, image resize | Writing client code |
| `scripts/probe.py` | Capability matrix from a live server (`<HOME>/.gemini/config/plugins/heylook-provider/skills/heylook-provider/scripts/probe.py` when installed globally) | Discovery |

Authoritative beyond all of these: the running server's `/openapi.json`, then `docs/api_integration.md` in `heylookitsanllm`.
</references>
