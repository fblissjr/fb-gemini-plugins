# Every heylook route

All `/v1` operations (plus `/health` and `/login`), grouped by who calls them.
An inference integration needs only the first group; the rest is here so a
client knows what exists. Request and response shapes are in the running
server's `/openapi.json`; heylook's own behaviour spec for each group is
`docs/frontend_v3_spec.md` §4 in the heylook repo. When the server-wide access
gate is enabled (`HEYLOOK_API_KEY` or mode-`0600` `<HOME>/.heylook/api_key`),
every route except `/health` and `/login` assets requires `x-api-key`,
`Authorization: Bearer`, or a `/login` session cookie (`wire_reference.md`,
Access). "Admin" additionally marks routes behind optional `HEYLOOK_ADMIN_TOKEN`
(`X-Heylook-Admin-Token`, headless callers only — the web UI never sends it).
Every route sits behind the Host check and the always-on `Origin` /
`Sec-Fetch-Site` check on state-changing methods.

Read from heylook's `docs/api_integration.md` §9 and checked against the
generated OpenAPI document at the version in SKILL.md's frontmatter: the
tables below cover every operation it lists.

## Choosing your surface

| Dimension | Direct `POST /v1/messages` | Presets + `/v1/messages` | Conversation Store `/v1/conversations/{id}/generate` |
|---|---|---|---|
| **System prompt** | Top-level `system` string (`system_prompt` -> 422) | Preset `system_prompt` copied into `system` (empty/`null` leaves existing prompt alone) | `system_prompt` column on the conversation |
| **Thinking keys** | `thinking` (bool or `{type, budget_tokens}`), `reasoning_effort` | Stored as `enable_thinking` + `thinking_budget_tokens`; client renames to `thinking` | Store keys: `enable_thinking`, `thinking_budget_tokens`, `reasoning_effort` |
| **Unknown / bad keys** | Refused list -> 422; other unknown keys silently ignored | Stored `params` 422-validated on write; client filters depth before `/v1/messages` | Stored `params` 422-validated on write; one-shot `overrides` silently drops unknown/unsupported keys |
| **History & media** | Client owns history; base64 or http(s) `url` | Client owns history | Server DuckDB store; nested `source` only; media relocated to `/media/{media_id}` |
| **Cancel / End thinking** | `DELETE /v1/requests/{id}`, `POST /v1/requests/{id}/reasoning-end`; disconnect stops SSE | Same as `/v1/messages` | `DELETE /v1/conversations/{id}/generate`, `POST .../generate/reasoning-end`; run **outlives** disconnect |

## Inference

| Route | Purpose |
|---|---|
| `POST /v1/messages` | The inference wire (`wire_reference.md`) |
| `GET /v1/models` | Served models, capabilities, the `engine` object |
| `GET /v1/capabilities` | Server version, optimizations, Metal info |
| `POST /v1/models/{id}/load[?warm=true]` | Pay a model load up front |
| `POST /v1/models/{id}/image-plan` | Tokens and resize target per image size; resident models only (409 otherwise) |
| `DELETE /v1/requests/{request_id}` | Cancel by `X-Request-ID` |
| `POST /v1/requests/{request_id}/reasoning-end` | Close the open thinking block early, by `X-Request-ID` (`wire_reference.md`) |
| `POST /v1/embeddings` | One vector per input item, embedding models only (`embeddings.md`) |

## Conversation store

A server-side alternative to keeping history in the client: the server stores
messages and media (DuckDB) and builds each request from them. heylook's own
chat page uses it.

| Route | Purpose |
|---|---|
| `GET/POST /v1/conversations` | List `{conversations, total}` (each row includes `generating: bool`, not paged); create (201) from `{title, model_id?, system_prompt?, params?, applied_preset_id?}`, answered with the whole conversation (`id`, `messages: []`, ...) |
| `GET/PUT/DELETE /v1/conversations/{id}` | Read with messages (`generating: bool` included); patch metadata (`system_prompt`, `params`, `applied_preset_id`, `model_id`, `title`); delete (media included) |
| `POST /v1/conversations/{id}/clone` | Copy a conversation, media included |
| `POST /v1/conversations/{id}/messages` | Append a message `{role, content, thinking?}` |
| `DELETE /v1/conversations/{id}/messages?after={pos}` | Truncate: delete every message after a position |
| `PUT/DELETE /v1/conversations/{id}/messages/{msg_id}` | Edit or delete one message |
| `POST /v1/conversations/{id}/generate` | Generate into the conversation |
| `DELETE /v1/conversations/{id}/generate` | Stop the active generation; the partial persists. 404 when none is active |
| `POST /v1/conversations/{id}/generate/reasoning-end` | Close the active generation's open thinking block; `{"signalled": 1, "conversation_id"}`, 404 when none is active |
| `POST /v1/conversations/{id}/prompt` | The exact prompt string generate would feed the model; persists nothing |
| `GET /v1/conversations/{id}/media/{media_id}` | A stored image or audio blob |

**What differs from `/v1/messages`:**

- **The server builds the request.** `generate` takes
  `{mode: "append"|"regenerate"|"continue", message_id?, user_content?,
  overrides?, stop_sequences?}` (`user_content` is a string or a block list,
  as on `/v1/messages`) and reads the conversation's `system_prompt`,
  `params`, `model_id` and rows. `append` stores `user_content` as a new user
  turn first; `regenerate` replaces everything from the `message_id` anchor;
  `continue` extends the anchor row. `overrides` layers one-shot sampler
  values (and `model`) over the stored `params`.
- **`params` and `overrides` use the store's key names, not the wire's.**
  The keys are exactly `temperature`, `top_p`, `top_k`, `min_p`, `max_tokens`,
  `repetition_penalty`, `repetition_context_size`, `presence_penalty`,
  `enable_thinking`, `reasoning_effort`, `seed` and `thinking_budget_tokens`,
  plus `model` in `overrides`. Anything else is **dropped silently**, so
  `{"thinking": false}` in `overrides` leaves thinking at the model's
  default. So is a key the model lacks the capability for (`enable_thinking`
  needs `thinking`, `reasoning_effort` needs `reasoning_effort`,
  `thinking_budget_tokens` needs `thinking_budget`).
- **One extra event, always last.** The stream is the `/v1/messages` grammar
  plus `event: heylook_saved`, carrying `end_reason`
  (`complete`, `aborted` or `error`), the stored rows this run wrote in
  `messages` (the new user turn and the reply, not the whole thread),
  `dropped_media` and `timing` (the same object as `message_stop.performance`).
  Merge those rows into client state by `id`, not by counting positions.
- **Stop it with `DELETE /v1/conversations/{id}/generate`.** `DELETE
  /v1/requests/{id}` does not reach a conversation generate, even with the
  `X-Request-ID` it was sent with.
- **An `error` event does not end the saga.** It may precede `heylook_saved`,
  and a partial reply still persists. On `/v1/messages` an error event ends
  the stream.
- **Persistence is server-owned and detached from the HTTP stream.** A
  conversation generation runs in a background task (`_Run`) on the server, so
  client disconnect does **not** abort it: the server completes generation and
  commits the full reply (use `GET /v1/conversations/{id}` and its `generating`
  flag when reconnecting; call `DELETE /v1/conversations/{id}/generate` to
  explicitly abort and persist a partial reply). Errors before any output
  persist nothing; a failed regenerate or continue leaves the thread untouched.
- **`applied_preset_id` tracks explicit preset actions only.** Set at create or
  explicit Apply/Update/Save (`null` clears it); never inferred from matching
  fields and never placed inside `params`. If the referenced preset is deleted,
  clients treat a dangling id as no stamp.
- **One generation per conversation.** While one runs, a second `generate`,
  any message write and a conversation delete are each a 409
  `{"error":{"code":"generation_in_progress"}}`. Metadata `PUT`s stay open.
- **Unknown fields are ignored, not refused.** Unlike `/v1/messages`, this
  route has no 422 for retired fields.
- **A stored `params` bag is validated on write, and a bad one is a 422.** This
  covers conversations, notebooks and presets, create and update, with the same
  key names and ranges as above. An unknown key or a bad value (`top_p: "high"`)
  is a 422 naming it, and a `null` is not stored. It is the opposite of
  `overrides` on `generate`, which drops unknown keys silently.
- **Stored media comes back by reference.** Send base64 as usual; the stored
  block becomes `{"type": "image", "source": {"type": "url", "url":
  "/v1/conversations/{id}/media/{media_id}", "media_type", "media_id"}}`, and
  the bytes are served from that URL with `Cache-Control: immutable`. Media
  the target model cannot take is dropped from the request and counted in
  `dropped_media`.
- **Messages carry both `content` and `content_blocks`**: the flattened text,
  and the full stored block list. `PUT /v1/conversations/{id}` returns the
  conversation **without** its messages.
- **A stored thinking depth the model does not offer is dropped**, and the
  model runs at its default; `/v1/messages` answers 400 instead.
- **`prompt`** takes the same body as `generate` plus `edits`, and returns
  `{prompt, model_id, provider, mode, continuation, dropped_media,
  unrendered_media, char_count, markers}`, rendered by the model's own
  template. 409 when the model is not resident: a preview never loads one.
  On MLX images in history are not rendered into it.

## Notebooks and presets

| Route | Purpose |
|---|---|
| `GET/POST /v1/notebooks` | List (content omitted); create |
| `GET/PUT/DELETE /v1/notebooks/{id}` | Read, patch, delete a plain-text notebook |
| `GET/POST /v1/presets` | List `{presets, total}` (not paged; there is no route to fetch one preset, so filter the list); create (201; duplicate name 409, blank 400) |
| `PUT/DELETE /v1/presets/{id}` | Patch, delete |

A preset is a named bundle of `system_prompt` and sampler `params`. The
**client** expands it: copy `system_prompt` into the request and `params` into
the sampler fields. Follow the **override-box rule**: a preset whose
`system_prompt` is `null` or empty (`""`) makes no claim on the prompt, so
applying it leaves the caller's or conversation's existing prompt intact rather
than clearing it. `params` uses the store's key names, so rename exactly
two on the way to `/v1/messages`: `enable_thinking` becomes `thinking`, and
`thinking_budget_tokens` becomes `thinking: {"budget_tokens": N}`, merged
into one object when a preset has both. Every other key carries over
unchanged, except that a `reasoning_effort` the target model does not offer
must be dropped: the store drops it silently, `/v1/messages` answers 400.
Recipe: `client_recipes.md`, Expanding a preset. Sent
unrenamed, `enable_thinking` is a 422 there. The server never applies a preset to a request, and
`preset` on `/v1/messages` is a 422. A preset stores only the fields it pins,
so absent fields still fall to the server cascade. `PUT /v1/presets/{id}`
patches only the top-level fields you send, while a sent `params` object
**replaces** the stored `params` map wholesale (it is not merged).

## Model administration (admin)

| Route | Purpose |
|---|---|
| `GET/POST /v1/admin/models`, `GET/PATCH/DELETE /v1/admin/models/{id}` | Per-model config in the model's `model.heylook.toml` sidecar (or `heylook.toml` entry); PATCH reports `reload_required_fields` (`null` clears a field back to default) |
| `POST /v1/admin/models/validate` | Validate a config without saving |
| `GET /v1/admin/model-options` | Every settable field per provider, and when a change takes effect |
| `GET/PUT /v1/admin/models/scan-config` | The folders models are discovered from |
| `POST /v1/admin/models/{id}/fit` | Whether it fits memory, with optional candidate edits |
| `GET /v1/admin/models/{id}/status` | Loaded state, memory, context use, requests active and queued |
| `POST /v1/admin/models/{id}/unload` | Unload (409 while it is generating) |
| `POST /v1/admin/models/{id}/reload[?warm=true]` | Unload then load (and optionally warm) as one operation; optional JSON body `{ctx_size, flash_attn}` |
| `GET/PUT/DELETE /v1/admin/models/{id}/chat-template` | Read, override (`chat_template.heylook.jinja`) or reset the chat template in force; gguf reads also report `engine_gaps` (static scan for Python methods `llama-server` lacks) |
| `GET/PUT /v1/admin/config`, `DELETE /v1/admin/config/{key}` | Server operational settings, plus read-only `access: {enabled, source, source_detail, admin_token_enabled, error?}` (never includes the key) |
| `GET /v1/admin/config/logs?stream={events\|metrics}&limit=` | Recent observability JSONL records, newest first (`limit` 1-500) |
| `POST /v1/admin/reload` | Re-read config and clear loaded models without a restart |

Admin config writes answer **409** when the server runs with
`HEYLOOK_READONLY_MODEL_CONFIG`, and **422** if a PATCH names a `file_only`
field (`server_binary`, `extra_args`, `chat_template_path`, `rpc`,
`pipeline_peers`), which can only be edited in `model.heylook.toml`.

## Maintenance, auth, and observability

| Route | Purpose |
|---|---|
| `GET/HEAD /health` | Unauthenticated liveness check returning only `{"status": "ok"}` (exempt from the access gate; reveals no version, hardware, or models) |
| `GET/HEAD/POST /login`, `POST /logout` | Browser session sign-in (`heylook_session` cookie) and server-side session revocation (`include_in_schema=False`; API clients send `x-api-key` or `Authorization: Bearer` directly instead) |
| `POST /v1/cache/clear` (admin) | Clear prompt and vision caches for one model or all |
| `POST /v1/data/clear` (admin) | Delete every conversation, message and notebook. Presets survive |
| `GET /v1/system/metrics` | RAM, loaded models, per-model memory; unknown readings are null |
| `GET /v1/performance/profile/{1h\|6h\|24h\|7d}` | Aggregated timing by phase |
| `POST /v1/telemetry/events` | heylook's own frontend events; not for integrations |
