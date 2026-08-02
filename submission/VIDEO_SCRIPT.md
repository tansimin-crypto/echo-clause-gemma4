# EchoClause Demo Video Script (R9)

**Target duration:** 90 seconds (±5 s)  
**Format:** 1920×1080 H.264/AAC, 30 fps, burned English subtitles + sidecar SRT/VTT  
**Narration:** Kokoro-82M `am_michael` @ 1.08 (local, bib pipeline)  
**Demo data:** Synthetic Nuru Credit assets only — no real personal/company data  
**Gemma label:** Recorded replay shown — not live inference

## Scene map

| Time | Scene ID | Visual | Narration / subtitle cues |
|------|----------|--------|---------------------------|
| 0–9 s | `hook` | Ad vs contract side-by-side | Zero interest. No hidden fees. / Then you sign — and the contract tells a different story. |
| 9–24 s | `evidence` | Four source thumbnails (ad, chat, contract, audio) | Four evidence sources for fictional lender Nuru Credit: / advertisement, sales pitch audio, support chat, and contract. |
| 24–44 s | `extraction` | SourceClaim JSON + **RECORDED REPLAY** badge | Gemma 4 extracts structured claims… / with verbatim evidence quotes. / Recorded replay — not live inference. |
| 44–64 s | `conflicts` | Five-row contradiction table + hidden-fee callout | Five contradictions detected. / A hidden platform fee of one hundred fifty dollars / never appeared in the marketing. |
| 64–77 s | `evidence-detail` | Promise vs contract evidence panels | Each conflict cites quoted evidence. / Promised no hidden fees — contract shows one hundred fifty dollars. Status: contradicted. |
| 77–85 s | `questions` | Clarification question list | EchoClause generates clarification questions / before you sign. |
| 85–90 s | `tagline` | Branded closing slide | EchoClause. / What they said versus what you sign. |

## Deliverables

| Artifact | Path |
|----------|------|
| Final MP4 | `submission/echo-clause-demo-90s.mp4` |
| Sidecar SRT | `submission/echo-clause-demo-90s.srt` |
| Sidecar VTT | `submission/echo-clause-demo-90s.vtt` |
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
