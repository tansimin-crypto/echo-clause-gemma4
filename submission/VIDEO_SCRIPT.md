# EchoClause Demo Video Script (R9)

**Target duration:** ~52 seconds (±5 s)  
**Format:** 1920×1080 H.264/AAC, 30 fps, **no subtitles** (narration audio only)  
**Narration:** Kokoro-82M `am_michael` @ 1.08 (local, bib pipeline)  
**Demo data:** Synthetic Nuru Credit assets only — no real personal/company data  
**Gemma label:** Recorded replay shown — not live inference

## Scene map

| Time | Scene ID | Visual | Narration |
|------|----------|--------|-----------|
| 0–6.5 s | `hook` | Ad vs contract side-by-side | Zero interest. No hidden fees. / Then you sign — and the contract tells a different story. |
| 6.5–15 s | `evidence` | Four source thumbnails (ad, chat, contract, audio) | Four evidence sources for fictional lender Nuru Credit: / advertisement, sales pitch audio, support chat, and contract. |
| 15–24.5 s | `extraction` | SourceClaim JSON + **RECORDED REPLAY** badge | Gemma 4 extracts structured claims… / with verbatim evidence quotes. / Recorded replay — not live inference. |
| 24.5–33 s | `conflicts` | Five-row contradiction table + hidden-fee callout | Five contradictions detected. / A hidden platform fee of one hundred fifty dollars / never appeared in the marketing. |
| 33–42.5 s | `evidence-detail` | Promise vs contract evidence panels | Each conflict cites quoted evidence. / Promised no hidden fees — contract shows one hundred fifty dollars. Status: contradicted. |
| 42.5–47.5 s | `questions` | Clarification question list | EchoClause generates clarification questions / before you sign. |
| 47.5–52 s | `tagline` | Branded closing slide | EchoClause. / What they said versus what you sign. |

## Timing changes (v2)

- Scene durations tightened to fit narration (was 90 s total with long hold frames).
- Inter-cue lead/gap/tail reduced: 0.15 s lead, 0.06 s gap, 0.08 s tail (was 0.35 / 0.14 / 0.15).
- Explicit `cue_pauses` removed — no artificial hold frames between sentences.
- Subtitles removed from render pipeline (no burn-in, no sidecar SRT/VTT).

## Deliverables

| Artifact | Path |
|----------|------|
| Final MP4 | `submission/echo-clause-demo-90s.mp4` (52 s; filename kept for submission compatibility) |
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
