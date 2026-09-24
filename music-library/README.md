# Stamply music library

24 Mixkit tracks (Mixkit Stock Music Free License) for the Stamply video pipeline, analyzed with librosa.

- `music-library.json` — full catalog. Per track: file, title, artist, source, sourceUrl, license,
  licenseSource, bpm (measured), energy 1–5, mood, tags, hasVocals, voiceoverFriendly, motionGraphicsFit,
  bestFor, introQuality, loopFriendly, notes, downloadedAt, beatTimes, and the raw measurements.
  `fieldProvenance` says which fields are measured, derived, heuristic, Mixkit metadata or editorial.
- `LICENSE-SOURCES.md` — URL, creator, source, license and download date of every track, plus how the license was verified.
- `01_premium_tech/` … `06_soft_background/` — the MP3s, in the folder of their primary category
  (a track can belong to more than one category; see `categories` in the JSON).
- `candidates-log.json` — all 456 candidates and why each was excluded, rejected or selected.
- `tools/` — the analyzer from HQ (`analyze.py`) + supplementary measurements (`extra.py`, `post.py`, `vocal.py`).
- `remotion/selectMusic.ts` — deterministic music choice from the storyboard facts (stage 6).
- `remotion/beatSync.tsx` — beat/bar frames, snap-to-beat cuts, beat accents, VO-ducked music bed (stage 7).
- `VIDEO-PIPELINE-PATCH.md` — the proposed `config/videoPipeline` addition (not applied yet).

Reproduce a measurement: `pip install librosa==0.11.0 numba==0.61.2 "numpy<2.3"` then
`python3 tools/analyze.py <track>.mp3 out.json`. numba 0.67 segfaults in `librosa.beat.beat_track`; use 0.61.2.
