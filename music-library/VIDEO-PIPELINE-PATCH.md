# Proposed addition to `config/videoPipeline` (stages 6–7 of the brief) — not applied yet

The current `config/videoPipeline` has Yair's music rule from 24.09: "use only music Yair sends (mp3) or
Instagram's music library; without music from Yair, deliver an SFX-only version". The block below
would add the Mixkit library as a third allowed source. It changes that rule, so it is applied to the HQ
only after Yair approves.

---

MUSIC (Mixkit library — config/musicLibrary, files in HQ/Git under music-library/):
- Allowed music sources: (1) an mp3 Yair sends, (2) Instagram's music library, (3) the Stamply music
  library (config/musicLibrary, 24 Mixkit tracks, Free License, measured BPM/beats). Music synthesized in
  code is never allowed.
- Choose music AFTER the storyboard and BEFORE the Remotion build, never at random: run
  music-library/remotion/selectMusic.ts with {videoType, voDensity, editPace, durationSec,
  animationStyle, brandTone, mood, exclude: tracks used in the last 5 videos}. Write the choice +
  the reasons it returns into videoJobs/<id>.music = {trackId, file, reasons[], syncStartSec}.
  Mapping: UI/product → premium_tech or playful_bloops · talking head + VO → minimal_voiceover ·
  15-second ad → energetic_ads · product reveal → premium_tech · stories/BTS → soft_background.
- Any VO → instrumental tracks only (hasVocals false). Dense VO → voiceoverFriendly only, with the
  music ducked 10–14 dB under speech (MusicBed voRanges).
- Beat sync (music-library/remotion/beatSync.tsx): snap scene cuts to bars (snapSceneDurations,
  tolerance ≤ 4 frames), and land only the key moments on a beat: the hero text reveal of a scene,
  stamp/confirmation pops, the one UI change that matters, the logo, and the CTA. Do NOT sync
  word-by-word staggers, camera push-ins, background motion, secondary UI, or anything under dense
  VO. Never break timing.minHold to reach a beat.
- Start at syncStartSec when the track has a slow intro; fade out over the last 0.8 s; never cut
  mid-phrase at the end: prefer the last bar line before the end.
- License: Mixkit Stock Music Free License — OK for online ads and social media, no credit
  required; NOT for TV/radio broadcasts. Never upload a Mixkit track to Content ID.
