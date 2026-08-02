# EchoClause Demo Video Script (R9)

**Target duration:** ~59 seconds (±5 s)  
**Format:** 1920×1080 H.264/AAC, 30 fps, **no subtitles** (narration audio only)  
**Narration:** Kokoro-82M `am_michael` @ 1.08 (local, bib pipeline)  
**Demo data:** Synthetic Nuru Credit assets only — no real personal/company data  
**Gemma label:** Recorded replay shown — not live inference

## Scene map

| Time | Scene ID | Visual | Narration |
|------|----------|--------|-----------|
| 0–7 s | `hook` | Ad vs contract side-by-side | Zero interest. No hidden fees. / Then you sign — and the contract tells a different story. |
| 7–17 s | `evidence` | Four source thumbnails (ad, chat, contract, audio) | Four evidence sources for fictional lender Nuru Credit: / advertisement, sales pitch audio, support chat, and contract. |
| 17–27.5 s | `extraction` | SourceClaim JSON + **RECORDED REPLAY** badge | Gemma 4 extracts structured claims… / with verbatim evidence quotes. / Recorded replay — not live inference. |
| 27.5–37.5 s | `conflicts` | Five-row contradiction table + hidden-fee callout | Five contradictions detected. / A hidden platform fee of one hundred fifty dollars / never appeared in the marketing. |
| 37.5–48 s | `evidence-detail` | Promise vs contract evidence panels | Each conflict cites quoted evidence. / Promised no hidden fees — contract shows one hundred fifty dollars. Status: contradicted. |
| 48–53.5 s | `questions` | Clarification question list | EchoClause generates clarification questions / before you sign. |
| 53.5–59 s | `tagline` | Branded closing slide | EchoClause. / What they said versus what you sign. |

## Timing changes (v3 — moderate pacing)

- Scene durations increased ~13% from v2 (52 s → 59 s) for breathing room without returning to 90 s holds.
- Inter-cue lead/gap/tail raised modestly: **0.20 s lead**, **0.08 s gap**, **0.12 s tail** (v2 was 0.15 / 0.06 / 0.08).
- Small `cue_pauses` on key slides only:
  - `evidence`: 0.30 s hold after source list intro
  - `conflicts`: 0.25 s hold after "Five contradictions detected."
- Subtitles remain off (no burn-in, no sidecar SRT/VTT).

## Deliverables

| Artifact | Path |
|----------|------|
| Final MP4 | `submission/echo-clause-demo-90s.mp4` (59 s; filename kept for submission compatibility) |
| Manifest | `D:\Agent\echo-clause-video\video-manifest-echo-clause-90s.json` |
| Render scripts | `D:\Agent\echo-clause-video\render_slides.py`, `render_video.py` |
| Validation | `submission/echo-clause-video-validation.json` |

## Reproduce

```powershell
# 1. Generate demo assets (if missing)
Set-Location D:\kaggle\gemma-finance\echo-clause-gemma4
python scripts/generate_demo_assets.py

# 2. Render video (uses bib Kokoro + FFmpeg)
Set-Location D:\Agent\echo-clause-video
python render_video.py
```

**Bib tooling used:** `D:\CodexWorkspaces\bib` — Kokoro ONNX (`work/voice/kokoro/`), FFmpeg vendor (`work/video/vendor/imageio_ffmpeg/`), cue-sync pattern from `scripts/render-kaggle-video-v5-kokoro-sentence-sync.py`.

## Disclosures

- AI narration synthesized locally (Kokoro); no paid TTS API.
- Gemma extraction scene shows **recorded replay**, not live GPU inference.
- All lender/marketing/contract content is synthetic (Nuru Credit demo case).
