#!/usr/bin/env python3
"""Deterministic Prompt Compiler, Linter & Budget Estimator for Gemini Omni 1.2 Flash.

Zero-dependency Python 3 stdlib CLI tool supporting:
  - lint:      Audits a draft prompt + configuration against 12 Gemini Omni 1.2 Flash
               prompting & Interactions API traps.
  - compile:   Compiles structured flags or JSON specs into a role-tagged
               Gemini Omni 1.2 Flash prompt + Interactions API Python/REST payload.
  - cost:      Estimates draft-to-upscale workflow cost ($0.07/s 720p base, 30% savings
               vs. Omni 1.1 Flash).
  - --self-test: Runs offline deterministic unit tests.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_MODEL = "gemini-omni-1.2-flash"
VALID_MODES = ("generate", "edit", "extend", "multiturn")
VALID_ASPECT_RATIOS = ("16:9", "9:16")
VALID_RESOLUTIONS = ("360p", "720p", "1080p", "4k")
UNSUPPORTED_API_FIELDS = (
    "temperature",
    "top_p",
    "top_k",
    "system_instruction",
    "stop_sequences",
    "negative_prompt",
)

# Approximate per-second rates (USD) for Omni 1.2 Flash vs Omni 1.1 Flash baseline
RATE_PER_SEC_1_2: Dict[str, float] = {
    "360p": 0.05,
    "720p": 0.07,
    "1080p": 0.14,
    "4k": 0.28,
}
RATE_PER_SEC_1_1: Dict[str, float] = {
    "360p": 0.07,
    "720p": 0.10,
    "1080p": 0.20,
    "4k": 0.40,
}

SINGLE_SHOT_PATTERNS = (
    r"\bsingle\s+unbroken\s+scene\b",
    r"\bsingle\s+continuous\s+shot\b",
    r"\bunbroken\b.*\bshot\b",
    r"\bcontinuous\b.*\bshot\b",
    r"\bno\s+scene\s+cuts\b",
    r"\bsingle[- ]take\b",
)

MULTI_SHOT_PATTERNS = (
    r"\brapid[- ]fire\b",
    r"\bevery\s+\d+(\.\d+)?\s*s(ec(ond)?s?)?\b",
    r"\bcut\s+to\b",
    r"\bmontage\b",
    r"\[\d+\s*-\s*\d+s?\]",
)

ANCHOR_PATTERNS = (
    r"\bkeep\s+everything\s+else\s+the\s+same\b",
    r"\bkeep\b.+\bidentical\b",
    r"\bkeep\b.+\bintact\b",
    r"\bkeep\b.+\bthe\s+same\b",
    r"\bkeep\b.+\buntouched\b",
    r"\bonly\s+change\b",
)

DIALOGUE_PATTERNS = (
    r"\bsays\s*[:\"]",
    r"\bspeaking\b",
    r"\bdialogue\s*:",
    r"\breplies\s*[:\"]",
    r"\bwhispers\s*[:\"]",
    r"\bshouts\s*[:\"]",
)

NEW_AUDIO_PATTERNS = (
    r"\bsynthwave\b",
    r"\btechno\s+beat\b",
    r"\bbackground\s+music\b",
    r"\bnew\s+audio\b",
    r"\bnew\s+soundtrack\b",
    r"\bragtime\b",
    r"\borchestral\s+score\b",
    r"\blo-?fi\s+beat\b",
)


def parse_timecode_spans(prompt: str) -> List[Tuple[float, float]]:
    """Extract [start-end s] timecode brackets from a prompt."""
    spans: List[Tuple[float, float]] = []
    for match in re.finditer(r"\[\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*s?\s*\]", prompt):
        spans.append((float(match.group(1)), float(match.group(2))))
    return spans


def extract_indexed_tags(prompt: str, prefix: str) -> List[int]:
    """Extract integer indices N from tags like <IMAGE_REF_N> or <VIDEO_REF_N>."""
    pattern = rf"<{prefix}_(\d+)>"
    return sorted({int(m.group(1)) for m in re.finditer(pattern, prompt)})


def lint_prompt(
    prompt: str,
    mode: str = "generate",
    duration: int = 10,
    resolution: str = "720p",
    aspect_ratio: str = "16:9",
    task: Optional[str] = None,
    has_source_audio: bool = False,
    strip_audio: bool = False,
    is_uploaded_video: bool = False,
    previous_interaction_id: Optional[str] = None,
    store: bool = True,
    delivery: str = "inline",
    unsupported_params: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Audit a draft Gemini Omni 1.2 Flash prompt and config against 12 rules."""
    findings: List[Dict[str, str]] = []
    suggestions: List[str] = []
    text = prompt.strip()

    def add_finding(rule_id: str, severity: str, message: str, fix: str) -> None:
        findings.append(
            {
                "rule_id": rule_id,
                "severity": severity,
                "message": message,
                "fix": fix,
            }
        )

    # R01: Duration bounds (3..15s for generate in Omni 1.2 Flash; 3..10s for edit/extend)
    if mode == "generate":
        if duration < 3 or duration > 15:
            add_finding(
                "R01_DURATION_BOUNDS",
                "error",
                f"duration={duration}s is outside Gemini Omni 1.2 Flash's supported 3s-15s generation range.",
                "Set duration_seconds to an integer between 3 and 15 (e.g. 5, 10, or 15).",
            )
    elif mode in ("edit", "extend"):
        if duration < 3 or duration > 10:
            add_finding(
                "R01_DURATION_BOUNDS",
                "error",
                f"duration={duration}s exceeds the 3s-10s per-turn limit for '{mode}' mode.",
                "Trim input videos to <=10s and extend in 3s-10s increments (up to 30s-40s total across turns).",
            )

    # R02: Single-shot lock vs multi-shot director default
    if mode == "generate":
        has_single_lock = any(re.search(p, text, re.IGNORECASE) for p in SINGLE_SHOT_PATTERNS)
        has_multi_cue = any(re.search(p, text, re.IGNORECASE) for p in MULTI_SHOT_PATTERNS)
        if not has_single_lock and not has_multi_cue:
            add_finding(
                "R02_SINGLE_SHOT_LOCK",
                "warning",
                "Prompt lacks both a single-shot continuity lock and explicit multi-shot timecode/cut cues. "
                "By default, Omni Flash cuts between multiple shots automatically.",
                'Prepend "Continuous, unbroken shot in a single scene. No scene cuts." (or add [0-5s]/[5-10s] beat brackets).',
            )

    # R03: Minimal Delta + Anchor in edit / multiturn modes
    if mode in ("edit", "multiturn"):
        has_anchor = any(re.search(p, text, re.IGNORECASE) for p in ANCHOR_PATTERNS)
        word_count = len(text.split())
        if not has_anchor:
            add_finding(
                "R03_EDIT_MINIMAL_DELTA_ANCHOR",
                "error",
                f"'{mode}' prompt is missing an explicit Anchor Clause. Unanchored edits cause background/subject drift.",
                'Append "Keep everything else the same." or "Keep [subject, lighting, and camera framing] identical to the source video."',
            )
        if word_count > 45:
            add_finding(
                "R03_EDIT_MINIMAL_DELTA_ANCHOR",
                "warning",
                f"'{mode}' prompt is verbose ({word_count} words). Re-describing the existing scene causes unintended re-generation.",
                "Strip scene re-descriptions and state only the imperative delta + 'Keep everything else the same.'",
            )

    # R04: <LAST_FRAME> requires <FIRST_FRAME>
    has_first_frame = "<FIRST_FRAME>" in text
    has_last_frame = "<LAST_FRAME>" in text
    if has_last_frame and not has_first_frame:
        add_finding(
            "R04_LAST_FRAME_REQUIRES_FIRST_FRAME",
            "error",
            "<LAST_FRAME> is present without <FIRST_FRAME>. Omni Flash requires <FIRST_FRAME> whenever <LAST_FRAME> is used.",
            "Include both <FIRST_FRAME> and <LAST_FRAME> (pass the same image to both if creating a seamless loop).",
        )

    # R05: <IMAGE_REF_N> (0..5) and <VIDEO_REF_N> (0..2) indexing & limits
    img_refs = extract_indexed_tags(text, "IMAGE_REF")
    vid_refs = extract_indexed_tags(text, "VIDEO_REF")
    if img_refs:
        if len(img_refs) > 6 or max(img_refs) > 5:
            add_finding(
                "R05_REF_TAG_INDEXING_AND_LIMITS",
                "error",
                f"Found image reference indices {img_refs}; Omni 1.2 Flash supports up to 6 reference images (<IMAGE_REF_0>..<IMAGE_REF_5>).",
                "Use 0-indexed tags <IMAGE_REF_0> through <IMAGE_REF_5> (up to 6 total, max 3 per character).",
            )
        expected_img = list(range(len(img_refs)))
        if img_refs != expected_img:
            add_finding(
                "R05_REF_TAG_INDEXING_AND_LIMITS",
                "warning",
                f"<IMAGE_REF_N> tags {img_refs} are not contiguous 0-indexed {expected_img}.",
                "Start image reference tags at <IMAGE_REF_0> and increment sequentially without gaps.",
            )
    if vid_refs:
        if len(vid_refs) > 3 or max(vid_refs) > 2:
            add_finding(
                "R05_REF_TAG_INDEXING_AND_LIMITS",
                "error",
                f"Found video reference indices {vid_refs}; Omni 1.2 Flash supports at most 3 reference videos (<VIDEO_REF_0>..<VIDEO_REF_2>).",
                "Use at most 3 reference clips (~3s each) tagged <VIDEO_REF_0> through <VIDEO_REF_2>.",
            )
        expected_vid = list(range(len(vid_refs)))
        if vid_refs != expected_vid:
            add_finding(
                "R05_REF_TAG_INDEXING_AND_LIMITS",
                "warning",
                f"<VIDEO_REF_N> tags {vid_refs} are not contiguous 0-indexed {expected_vid}.",
                "Start video reference tags at <VIDEO_REF_0> and increment sequentially.",
            )

    # R06: Role disambiguation guardrail when using explicit [# References ...] or multi-role tags
    if "[# References" in text or "[# Sources" in text:
        has_img_guardrail = "as a reference" in text.lower() or "as references" in text.lower()
        has_vid_guardrail = "source for video editing" in text.lower()
        if img_refs and not has_img_guardrail:
            add_finding(
                "R06_ROLE_DISAMBIGUATION_GUARDRAIL",
                "warning",
                "Explicit [# References ...] header used with <IMAGE_REF_N>, but closing image role guardrail sentence is missing.",
                'Append: "Use the given image(s) as references for video generation. The images should not be used as literal initial frames."',
            )
        if vid_refs and not has_vid_guardrail:
            add_finding(
                "R06_ROLE_DISAMBIGUATION_GUARDRAIL",
                "warning",
                "Explicit [# References ...] header used with <VIDEO_REF_N>, but closing video role guardrail sentence is missing.",
                'Append: "Use the given video(s) as references. Do not use them as a source for video editing."',
            )

    # R07: task="extend" + multimodal reference collision
    if task == "extend" and (img_refs or vid_refs):
        add_finding(
            "R07_EXTEND_TASK_REF_COLLISION",
            "error",
            'task="extend" is set alongside <IMAGE_REF_N> or <VIDEO_REF_N>. Setting task="extend" in the API disables multimodal reference inputs.',
            'Omit the task="extend" API parameter and trigger extension via the prompt text ("Extend this video. ...").',
        )
    if mode == "extend" and not re.search(r"\b(extend\s+this\s+video|the\s+scene\s+continues)\b", text, re.IGNORECASE):
        add_finding(
            "R07_EXTEND_TASK_REF_COLLISION",
            "warning",
            'Extension prompt does not include an explicit phrase like "Extend this video" or "The scene continues".',
            'Start the prompt with "Extend this video. The scene continues..." so you can omit task="extend".',
        )

    # R08: Extending an uploaded video with new spoken dialogue
    has_dialogue_request = any(re.search(p, text, re.IGNORECASE) for p in DIALOGUE_PATTERNS)
    if mode == "extend" and is_uploaded_video and not previous_interaction_id and has_dialogue_request:
        add_finding(
            "R08_UPLOADED_EXTEND_DIALOGUE_LOCK",
            "error",
            "Cannot extend an uploaded video where someone is talking to add additional spoken dialogue.",
            "Either keep characters silent during uploaded video extensions, or extend a model-generated video via previous_interaction_id.",
        )

    # R09: Audio Stream Gate in edit mode
    requests_new_audio = any(re.search(p, text, re.IGNORECASE) for p in NEW_AUDIO_PATTERNS)
    if mode == "edit" and has_source_audio and not strip_audio and requests_new_audio:
        add_finding(
            "R09_AUDIO_REGENERATION_GATE",
            "error",
            "Prompt requests a brand-new music/audio track while editing a video that still has its original audio stream attached.",
            "Strip the audio track before uploading (ffmpeg -i input.mp4 -c:v copy -an input_silent.mp4) so Omni Flash regenerates audio from scratch.",
        )

    # R10: Unsupported API parameters
    if unsupported_params:
        bad = [p for p in unsupported_params if p in UNSUPPORTED_API_FIELDS]
        if bad:
            add_finding(
                "R10_UNSUPPORTED_API_PARAMS",
                "error",
                f"Unsupported API parameters detected: {bad}. Gemini Omni Flash rejects {', '.join(UNSUPPORTED_API_FIELDS)}.",
                'Remove those fields from the API payload and embed negative constraints directly in the prompt (e.g., "No dialogue. No embellishments.").',
            )

    # R11: Timecode span continuity and bounds
    spans = parse_timecode_spans(text)
    for start_s, end_s in spans:
        if end_s <= start_s:
            add_finding(
                "R11_TIMECODE_SPAN_ALIGNMENT",
                "error",
                f"Invalid timecode bracket [{start_s:g}-{end_s:g}s]: end time must be greater than start time.",
                "Ensure each [start-end s] bracket increases monotonically.",
            )
        if end_s > duration:
            add_finding(
                "R11_TIMECODE_SPAN_ALIGNMENT",
                "warning",
                f"Timecode bracket [{start_s:g}-{end_s:g}s] exceeds configured duration ({duration}s).",
                f"Increase duration_seconds to {int(end_s)} (up to 15s in Omni 1.2 Flash) or compress timecode beats to fit within [0-{duration}s].",
            )
            if mode == "extend":
                suggestions.append(
                    "Note: In 'extend' mode, 0s refers to the start of the newly extended segment, not the start of the original clip."
                )

    # R12: URI Delivery for >4MB payloads & store=True for multi-turn
    if (resolution in ("1080p", "4k") or duration >= 12) and delivery != "uri":
        add_finding(
            "R12_DELIVERY_AND_STORE_HYGIENE",
            "warning",
            f"Generating {duration}s at {resolution} with delivery='{delivery}' may exceed the 4 MB inline response cap.",
            'Set response_format={"type": "video", "aspect_ratio": "'
            + aspect_ratio
            + '", "resolution": "'
            + resolution
            + '", "delivery": "uri"} and poll client.files.get().',
        )
    if mode == "multiturn" and not store:
        add_finding(
            "R12_DELIVERY_AND_STORE_HYGIENE",
            "error",
            "store=False disables stateful editing via previous_interaction_id in subsequent turns.",
            "Set store=True (the default) whenever you plan to refine or extend the video across turns.",
        )

    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")

    return {
        "valid": errors == 0,
        "model": DEFAULT_MODEL,
        "mode": mode,
        "duration_seconds": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "error_count": errors,
        "warning_count": warnings,
        "findings": findings,
        "notes": suggestions,
    }


def compile_prompt_and_payload(
    mode: str = "generate",
    duration: int = 10,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    single_shot: bool = False,
    first_frame: Optional[str] = None,
    last_frame: Optional[str] = None,
    source_video: Optional[str] = None,
    previous_interaction_id: Optional[str] = None,
    image_refs: Optional[List[str]] = None,
    video_refs: Optional[List[str]] = None,
    subject: Optional[str] = None,
    action: Optional[str] = None,
    beats: Optional[List[str]] = None,
    camera: Optional[str] = None,
    lighting: Optional[str] = None,
    text_overlays: Optional[List[str]] = None,
    audio: Optional[str] = None,
    negatives: Optional[List[str]] = None,
    keep_anchor: Optional[str] = None,
    strip_audio: bool = False,
) -> Dict[str, Any]:
    """Compile structured inputs into a Gemini Omni 1.2 Flash prompt and Interactions API payload."""
    img_refs = [x.strip() for x in (image_refs or []) if x.strip()]
    vid_refs = [x.strip() for x in (video_refs or []) if x.strip()]
    beat_list = [b.strip() for b in (beats or []) if b.strip()]
    overlays = [t.strip() for t in (text_overlays or []) if t.strip()]
    neg_list = [n.strip() for n in (negatives or []) if n.strip()]

    # Build explicit [# Sources ...] and [# References ...] headers when media inputs are supplied
    sources_tokens: List[str] = []
    references_tokens: List[str] = []
    closing_guardrails: List[str] = []

    image_counter = 0
    video_counter = 0

    if first_frame:
        image_counter += 1
        first_idx = image_counter
        sources_tokens.append(f"<FIRST_FRAME>@Image{first_idx}")
        if last_frame:
            if last_frame == first_frame:
                sources_tokens.append(f"<LAST_FRAME>@Image{first_idx}")
                closing_guardrails.append("Use this image as the first frame and the last frame.")
            else:
                image_counter += 1
                last_idx = image_counter
                sources_tokens.append(f"<LAST_FRAME>@Image{last_idx}")
                closing_guardrails.append(
                    f"Use Image{first_idx} as the starting frame and Image{last_idx} as the final frame."
                )
        else:
            closing_guardrails.append(f"Use Image{first_idx} as the starting frame.")

    if source_video:
        video_counter += 1
        sources_tokens.append(f"<VIDEO_0>@Video{video_counter}")

    for idx, _ in enumerate(img_refs):
        image_counter += 1
        references_tokens.append(f"<IMAGE_REF_{idx}>@Image{image_counter}")
    if img_refs:
        closing_guardrails.append(
            "Use the given image(s) as references for video generation. "
            "The images should not be used as literal initial frames."
        )

    for idx, _ in enumerate(vid_refs):
        video_counter += 1
        references_tokens.append(f"<VIDEO_REF_{idx}>@Video{video_counter}")
    if vid_refs:
        closing_guardrails.append(
            "Use the given video(s) as references. Do not use them as a source for video editing."
        )

    header_parts: List[str] = []
    if sources_tokens:
        header_parts.append(f"[# Sources {' '.join(sources_tokens)}]")
    if references_tokens:
        header_parts.append(f"[# References {' '.join(references_tokens)}]")

    body_lines: List[str] = []
    if header_parts:
        body_lines.append(" ".join(header_parts))

    if mode == "extend":
        body_lines.append("Extend this video. The scene continues seamlessly.")

    if mode == "generate" and single_shot:
        cam_desc = f" {camera.strip()}" if camera else ""
        body_lines.append(f"Continuous, unbroken{cam_desc} shot in a single scene. No scene cuts.")
    elif camera and mode != "edit":
        body_lines.append(f"Camera: {camera.strip().rstrip('.')}.")

    if subject:
        body_lines.append(subject.strip().rstrip(".") + ".")

    if action:
        body_lines.append(action.strip().rstrip(".") + ".")

    for beat in beat_list:
        if ":" in beat and not beat.lstrip().startswith("["):
            span, desc = beat.split(":", 1)
            span_clean = span.strip().rstrip("s")
            body_lines.append(f"[{span_clean}s] {desc.strip().rstrip('.')}.")
        else:
            body_lines.append(beat.strip())

    if lighting:
        body_lines.append(f"Lighting and atmosphere: {lighting.strip().rstrip('.')}.")

    for text_str in overlays:
        clean_quote = text_str.strip().strip('"')
        body_lines.append(f'Include readable on-screen text: "{clean_quote}".')

    if mode in ("edit", "multiturn"):
        anchor_text = (
            keep_anchor.strip().rstrip(".") + "."
            if keep_anchor
            else "Keep everything else the same."
        )
        body_lines.append(anchor_text)

    if audio:
        body_lines.append(f"Sound design: {audio.strip().rstrip('.')}.")

    if neg_list:
        formatted_negs = []
        for neg in neg_list:
            n_clean = neg.strip().rstrip(".")
            if not n_clean.lower().startswith("no "):
                n_clean = f"No {n_clean}"
            formatted_negs.append(n_clean + ".")
        body_lines.append(" ".join(formatted_negs))

    if closing_guardrails:
        body_lines.append(" ".join(closing_guardrails))

    compiled_prompt = "\n".join(body_lines).strip()

    delivery = "uri" if (resolution in ("1080p", "4k") or duration >= 12) else "inline"

    response_format: Dict[str, Any] = {
        "type": "video",
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
    }
    if delivery == "uri":
        response_format["delivery"] = "uri"

    api_payload: Dict[str, Any] = {
        "model": DEFAULT_MODEL,
        "input": compiled_prompt,
        "generation_config": {
            "video_config": {
                "duration_seconds": duration,
            }
        },
        "response_format": response_format,
    }
    if previous_interaction_id:
        api_payload["previous_interaction_id"] = previous_interaction_id

    lint_report = lint_prompt(
        prompt=compiled_prompt,
        mode=mode,
        duration=duration,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
        task=None,  # Intentionally omitted to allow multimodal references
        has_source_audio=bool(source_video) and not strip_audio,
        strip_audio=strip_audio,
        is_uploaded_video=bool(source_video) and not previous_interaction_id,
        previous_interaction_id=previous_interaction_id,
        store=True,
        delivery=delivery,
    )

    python_snippet = _build_python_snippet(
        compiled_prompt=compiled_prompt,
        duration=duration,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        delivery=delivery,
        previous_interaction_id=previous_interaction_id,
    )

    return {
        "compiled_prompt": compiled_prompt,
        "interactions_payload": api_payload,
        "python_sdk_snippet": python_snippet,
        "lint": lint_report,
    }


def _build_python_snippet(
    compiled_prompt: str,
    duration: int,
    aspect_ratio: str,
    resolution: str,
    delivery: str,
    previous_interaction_id: Optional[str],
) -> str:
    prev_line = (
        f'\n    previous_interaction_id="{previous_interaction_id}",'
        if previous_interaction_id
        else ""
    )
    delivery_line = f'\n        "delivery": "{delivery}",' if delivery == "uri" else ""
    return (
        "from google import genai\n"
        "from google.genai import interactions\n\n"
        "client = genai.Client()\n\n"
        "interaction = client.interactions.create(\n"
        f'    model="{DEFAULT_MODEL}",{prev_line}\n'
        f"    input={json.dumps(compiled_prompt)},\n"
        "    generation_config=interactions.GenerationConfig(\n"
        "        video_config=interactions.VideoConfig(\n"
        f"            duration_seconds={duration},\n"
        "        )\n"
        "    ),\n"
        "    response_format={\n"
        '        "type": "video",\n'
        f'        "aspect_ratio": "{aspect_ratio}",\n'
        f'        "resolution": "{resolution}",{delivery_line}\n'
        "    },\n"
        ")"
    )


def estimate_cost(
    duration: int = 15,
    draft_resolution: str = "720p",
    draft_turns: int = 2,
    final_resolution: str = "1080p",
) -> Dict[str, Any]:
    """Calculate draft-to-upscale workflow cost on Omni 1.2 Flash vs Omni 1.1 Flash."""
    draft_rate_12 = RATE_PER_SEC_1_2[draft_resolution]
    final_rate_12 = RATE_PER_SEC_1_2[final_resolution]
    draft_cost_12 = round(duration * draft_rate_12 * draft_turns, 4)
    final_cost_12 = round(duration * final_rate_12, 4)
    total_12 = round(draft_cost_12 + final_cost_12, 4)

    draft_rate_11 = RATE_PER_SEC_1_1[draft_resolution]
    final_rate_11 = RATE_PER_SEC_1_1[final_resolution]
    total_11 = round(duration * draft_rate_11 * draft_turns + duration * final_rate_11, 4)
    savings_usd = round(total_11 - total_12, 4)
    savings_pct = round((savings_usd / total_11) * 100.0, 1) if total_11 > 0 else 0.0

    return {
        "model": DEFAULT_MODEL,
        "duration_seconds": duration,
        "draft_resolution": draft_resolution,
        "draft_turns": draft_turns,
        "final_resolution": final_resolution,
        "draft_cost_usd": draft_cost_12,
        "final_render_cost_usd": final_cost_12,
        "total_omni_1_2_usd": total_12,
        "baseline_omni_1_1_usd": total_11,
        "savings_vs_1_1_usd": savings_usd,
        "savings_vs_1_1_pct": savings_pct,
    }


def run_self_test() -> int:
    """Run deterministic offline unit tests."""
    # Test 1: 15s single-shot generation compile + lint clean
    compiled = compile_prompt_and_payload(
        mode="generate",
        duration=15,
        aspect_ratio="16:9",
        resolution="720p",
        single_shot=True,
        first_frame="start.jpg",
        image_refs=["hero.png", "bottle.png"],
        video_refs=["orbit.mp4"],
        beats=[
            "0-5:Slow push-in on <IMAGE_REF_0> holding <IMAGE_REF_1>",
            "5-10:Camera orbits following <VIDEO_REF_0>",
            "10-15:Macro close-up on the bottle label",
        ],
        text_overlays=["LUMEN 1.2"],
        audio="Calm ambient synth pad",
        negatives=["dialogue", "scene cuts"],
    )
    assert compiled["lint"]["valid"], f"Expected valid compile, got: {compiled['lint']}"
    assert "[# Sources <FIRST_FRAME>@Image1]" in compiled["compiled_prompt"]
    assert "[# References <IMAGE_REF_0>@Image2 <IMAGE_REF_1>@Image3 <VIDEO_REF_0>@Video1]" in compiled["compiled_prompt"]
    assert compiled["interactions_payload"]["response_format"]["delivery"] == "uri"

    # Test 2: Catch verbose unanchored edit + unstripped source audio + <LAST_FRAME> orphan
    bad_edit = lint_prompt(
        prompt=(
            "<LAST_FRAME> In the video of the man sitting on the leather sofa in the living room, "
            "please add a small black cat that runs from the right side of the screen and replace "
            "the audio with a synthwave beat."
        ),
        mode="edit",
        duration=12,
        task="extend",
        has_source_audio=True,
        strip_audio=False,
        unsupported_params=["temperature", "negative_prompt"],
    )
    assert not bad_edit["valid"]
    rule_ids = {f["rule_id"] for f in bad_edit["findings"]}
    for expected_rule in (
        "R01_DURATION_BOUNDS",
        "R03_EDIT_MINIMAL_DELTA_ANCHOR",
        "R04_LAST_FRAME_REQUIRES_FIRST_FRAME",
        "R09_AUDIO_REGENERATION_GATE",
        "R10_UNSUPPORTED_API_PARAMS",
    ):
        assert expected_rule in rule_ids, f"Missing expected rule {expected_rule} in {rule_ids}"

    # Test 3: Catch task="extend" + <IMAGE_REF_0> collision and uploaded video dialogue extension
    bad_extend = lint_prompt(
        prompt='Extend this video. The character in <IMAGE_REF_0> enters and says: "Hello there!"',
        mode="extend",
        duration=10,
        task="extend",
        is_uploaded_video=True,
        previous_interaction_id=None,
    )
    extend_rules = {f["rule_id"] for f in bad_extend["findings"]}
    assert "R07_EXTEND_TASK_REF_COLLISION" in extend_rules
    assert "R08_UPLOADED_EXTEND_DIALOGUE_LOCK" in extend_rules

    # Test 4: Cost estimator verifies 30% savings at 720p ($0.07/s vs $0.10/s)
    cost = estimate_cost(duration=15, draft_resolution="720p", draft_turns=2, final_resolution="1080p")
    assert cost["savings_vs_1_1_pct"] == 30.0, f"Unexpected savings: {cost}"

    print(
        json.dumps(
            {
                "self_test": "PASSED",
                "tests_run": 4,
                "model": DEFAULT_MODEL,
            },
            indent=2,
        )
    )
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gemini Omni 1.2 Flash (gemini-omni-1.2-flash) Prompt Compiler, Linter & Cost Estimator."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic offline unit tests and exit.",
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # lint subcommand
    lint_p = subparsers.add_parser("lint", help="Audit a draft prompt and config against 12 Omni 1.2 Flash rules.")
    lint_p.add_argument("--prompt", required=True, help="Draft prompt string to audit.")
    lint_p.add_argument("--mode", choices=VALID_MODES, default="generate", help="Operational mode.")
    lint_p.add_argument("--duration", type=int, default=10, help="Target video duration in seconds (3..15).")
    lint_p.add_argument("--resolution", choices=VALID_RESOLUTIONS, default="720p", help="Output resolution.")
    lint_p.add_argument("--aspect-ratio", choices=VALID_ASPECT_RATIOS, default="16:9", help="Output aspect ratio.")
    lint_p.add_argument("--task", default=None, help="Optional video_config.task value.")
    lint_p.add_argument("--has-source-audio", action="store_true", help="Input video has an existing audio track.")
    lint_p.add_argument("--strip-audio", action="store_true", help="Audio will be stripped with ffmpeg -an.")
    lint_p.add_argument("--is-uploaded-video", action="store_true", help="Target is an uploaded video file.")
    lint_p.add_argument("--previous-interaction-id", default=None, help="Stateful previous_interaction_id.")
    lint_p.add_argument("--no-store", action="store_true", help="Indicate store=False is set.")
    lint_p.add_argument("--delivery", choices=("inline", "uri"), default="inline", help="Response delivery mode.")
    lint_p.add_argument(
        "--unsupported-params",
        default="",
        help="Comma-separated list of extra API fields present in caller's request.",
    )

    # compile subcommand
    comp_p = subparsers.add_parser(
        "compile",
        help="Compile structured flags into a role-tagged Gemini Omni 1.2 Flash prompt + Interactions API snippet.",
    )
    comp_p.add_argument("--mode", choices=VALID_MODES, default="generate")
    comp_p.add_argument("--duration", type=int, default=10, help="Duration in seconds (3..15 for generate).")
    comp_p.add_argument("--aspect-ratio", choices=VALID_ASPECT_RATIOS, default="16:9")
    comp_p.add_argument("--resolution", choices=VALID_RESOLUTIONS, default="720p")
    comp_p.add_argument("--single-shot", action="store_true", help="Lock output to a single unbroken shot.")
    comp_p.add_argument("--first-frame", default=None, help="Path or label for <FIRST_FRAME> image.")
    comp_p.add_argument("--last-frame", default=None, help="Path or label for <LAST_FRAME> image.")
    comp_p.add_argument("--source-video", default=None, help="Path or label for <VIDEO_0> source clip.")
    comp_p.add_argument("--previous-interaction-id", default=None, help="Interaction ID from prior turn.")
    comp_p.add_argument("--image-refs", default="", help="Comma-separated image reference labels/paths (up to 6).")
    comp_p.add_argument("--video-refs", default="", help="Comma-separated video reference labels/paths (up to 3).")
    comp_p.add_argument("--subject", default=None, help="Subject, costume, or product micro-detail description.")
    comp_p.add_argument("--action", default=None, help="Primary action or edit delta instruction.")
    comp_p.add_argument(
        "--beats",
        default="",
        help="Pipe-separated timecode beats, e.g. '0-5:Opening shot|5-10:Orbit|10-15:Hero close-up'.",
    )
    comp_p.add_argument("--camera", default=None, help="Camera trajectory and framing description.")
    comp_p.add_argument("--lighting", default=None, help="Lighting and environment description.")
    comp_p.add_argument("--text-overlays", default="", help="Pipe-separated on-screen text strings to quote.")
    comp_p.add_argument("--audio", default=None, help="Audio, Foley, or music direction.")
    comp_p.add_argument("--negatives", default="", help="Comma-separated negative constraints (e.g. 'dialogue,scene cuts').")
    comp_p.add_argument("--keep-anchor", default=None, help="Custom anchor clause for edit/multiturn mode.")
    comp_p.add_argument("--strip-audio", action="store_true", help="Mark source video as audio-stripped.")

    # cost subcommand
    cost_p = subparsers.add_parser("cost", help="Estimate draft-to-upscale cost on Gemini Omni 1.2 Flash.")
    cost_p.add_argument("--duration", type=int, default=15, help="Clip duration in seconds (3..15).")
    cost_p.add_argument("--draft-resolution", choices=VALID_RESOLUTIONS, default="720p")
    cost_p.add_argument("--draft-turns", type=int, default=2, help="Number of conversational draft/edit turns.")
    cost_p.add_argument("--final-resolution", choices=VALID_RESOLUTIONS, default="1080p")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if args.subcommand == "lint":
        extra_params = [x.strip() for x in args.unsupported_params.split(",") if x.strip()]
        result = lint_prompt(
            prompt=args.prompt,
            mode=args.mode,
            duration=args.duration,
            resolution=args.resolution,
            aspect_ratio=args.aspect_ratio,
            task=args.task,
            has_source_audio=args.has_source_audio,
            strip_audio=args.strip_audio,
            is_uploaded_video=args.is_uploaded_video,
            previous_interaction_id=args.previous_interaction_id,
            store=not args.no_store,
            delivery=args.delivery,
            unsupported_params=extra_params,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["valid"] else 1

    if args.subcommand == "compile":
        result = compile_prompt_and_payload(
            mode=args.mode,
            duration=args.duration,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            single_shot=args.single_shot,
            first_frame=args.first_frame,
            last_frame=args.last_frame,
            source_video=args.source_video,
            previous_interaction_id=args.previous_interaction_id,
            image_refs=[x for x in args.image_refs.split(",") if x.strip()],
            video_refs=[x for x in args.video_refs.split(",") if x.strip()],
            subject=args.subject,
            action=args.action,
            beats=[x for x in args.beats.split("|") if x.strip()],
            camera=args.camera,
            lighting=args.lighting,
            text_overlays=[x for x in args.text_overlays.split("|") if x.strip()],
            audio=args.audio,
            negatives=[x for x in args.negatives.split(",") if x.strip()],
            keep_anchor=args.keep_anchor,
            strip_audio=args.strip_audio,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["lint"]["valid"] else 1

    if args.subcommand == "cost":
        result = estimate_cost(
            duration=args.duration,
            draft_resolution=args.draft_resolution,
            draft_turns=args.draft_turns,
            final_resolution=args.final_resolution,
        )
        print(json.dumps(result, indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
