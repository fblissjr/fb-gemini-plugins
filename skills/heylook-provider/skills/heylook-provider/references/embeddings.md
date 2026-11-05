# Embeddings

`POST /v1/embeddings` is a separate operation from generation: non-streaming,
one pooled vector per input item, served by embedding models on either engine
(`mlx` or `gguf`) with one request schema. Shapes are in the running server's
`/openapi.json`; heylook's own contract is `docs/frontend_v3_spec.md` §4
("Embeddings") and `docs/api_integration.md` §10 in the heylook repo.

## Finding an embedding model

An embedding model's `/v1/models` row carries `engine.embedding` (null on a
chat model), and its `capabilities` list `embedding` plus the input
modalities it takes, with **no `chat`**. So:

- a chat selector filters on `chat`; an embedding selector on `embedding`
  (`probe.py --need embedding`);
- `/v1/messages` to an embedding model is a 400 (`Embedding models accept
  /v1/embeddings, not generation`), after the model loads.

`engine.embedding` holds what to send:

| Field | Use |
|---|---|
| `modalities` | Block types the model embeds (`text`, `image`, `audio`, `video`) |
| `dimensions`, `native_dimensions` | Widths `dimensions` may take; the default width |
| `max_input_tokens` | The expanded item must fit; nothing is truncated |
| `prompts` | Prompt name to prefix, from the checkpoint's sentence-transformers config |
| `normalization` | `l2` |
| `video_audio` | `separate_audio_block`: a video embeds frames only |
| `video_windows` | MLX video models (`null` on gguf): `{max_seconds, sampling, default_sampling}` for windowed video embeddings |
| `limits` | `{items, blocks_per_item, text_chars, media_bytes: {image, audio, video}, request_media_bytes}`, built from the schema the server enforces; read caps here rather than copying them |
| `load_profile` | gguf only: the context and batch it loads with |

Pick prompt names, widths, and limits from this object, never from an example.

## Request

```json
{
  "model": "<id whose row has engine.embedding>",
  "dimensions": 256,
  "input": [
    {"prompt_name": "SearchQuery",
     "content": [{"type": "text", "text": "a dog on a beach"}]},
    {"content": [{"type": "image", "source": {"type": "base64",
      "media_type": "image/jpeg", "data": "<base64, no data: prefix>"}}]},
    {"content": [{"type": "video", "windows": {}, "source": {"type": "url",
      "media_type": "video/mp4", "url": "https://example.org/clip.mp4"}}]}
  ]
}
```

- `input` is a string, a list of strings, or a list of items. Each item is
  one vector, however many ordered blocks it holds; a list is a batch of
  independent vectors.
- Blocks are `text`, or `image` / `audio` / `video` with a nested `source`
  (`base64` with `data`, or `url` with an http(s) `url`). A video's
  soundtrack needs its own `audio` block.
- **Windowed video embeddings (MLX only; check `engine.embedding.video_windows`; gguf answers 400):**
  To search inside a long video, add `"windows": {}` (or `{"seconds": N, "sampling": "content" | "fps"}`)
  to its video block. `seconds` omitted uses and caps at `video_windows.max_seconds` (32 s on
  EmbeddingGemma 2). `sampling` defaults to `"content"` (evenly spaced anchors plus the frames least
  like them from 4 fps candidates, catching brief moments a fixed 1 fps grid steps over); `"fps"` takes
  frames at the model's own rate (decoding about a quarter as many frames). A windowed item must hold
  **only** that video block (422 otherwise); `windows` on a non-video block is a 422.
- Omit `prompt_name` for no prefix; a named one is applied once, before the
  content.
- **The body is strict.** Any field beyond `model`, `input` and `dimensions`
  is a 422 (`extra_forbidden`), a sampler knob included. This is the reverse
  of `/v1/messages`, which ignores unknown fields.

## Response

`{model, dimensions, data: [{index, embedding, prompt_name, windows}], input_tokens,
request_id, elapsed_ms}`. Read `data` in `index` order. Vectors are truncated
to `dimensions`, then L2-normalized, so a dot product is a cosine similarity.
When `windows` was requested on a video block, the row keeps its whole-video
`embedding` and adds `windows: [{start, end, frame_times, embedding}]` (null
otherwise), one L2-normalized vector per consecutive window: rank windows
against a query to find the moment and seek to `start`.
Store the model id, engine, prompt name and width beside an index: equal
widths do not make two checkpoints, or the same weights on two engines,
interchangeable. The server stores neither inputs nor vectors.

## Errors

| Code | Condition |
|---|---|
| 404 | Unknown embedding model (the generation route says 400 for this) |
| 400 | A modality, width, prompt name or `windows` (on gguf) the model does not offer; undecodable media; input over the context |
| 409 | Cancelled cooperatively |
| 422 | Schema violation, including any extra field, `windows` on a non-video block, or a windowed video item with other blocks |
| 503 | Queue full: the same backpressure envelope and `Retry-After` as generation |
| 500 | Backend failure |

A failure is atomic: no partial result.

Limits (`engine.embedding.limits`, from `schema/embeddings.py` in the heylook
repo): 16 items, 32 blocks per item, 131072 characters per text block, 32 MiB
decoded per image or audio block, 256 MiB per video block, and 256 MiB of media
in total.

## Operations

Embeddings share the load and eviction policy and the one generation queue,
so an embedding call can evict a resident chat model and waits behind a long
generation. Send a fresh `X-Request-ID`; `DELETE /v1/requests/{id}` cancels,
and a forward already running may finish first.
