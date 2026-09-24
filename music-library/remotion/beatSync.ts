// Stamply music library — beat sync helpers for Remotion (stage 7).
// Standalone module: copy into src/music/ of a NEW video. It does not change existing videos.
//
// Rule: sync only the moments that carry the story, never every animation.
//   SYNC      scene cuts, the hero text reveal of a scene, stamp/confirmation pops,
//             a UI state change the viewer should notice, the logo hit, the CTA button.
//   DON'T     word-by-word kinetic stagger, camera push-ins, background drift, secondary UI,
//             anything under dense voice-over (the VO sets the rhythm there, not the music).
// Beat times come from music-library.json (measured with librosa, not typed by hand).
import React from 'react';
import {Audio, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

export type LibraryTrack = {
  file: string; // e.g. "music-library/01_premium_tech/mixkit-xxx-123.mp3"
  bpm: number;
  beatTimes: number[]; // seconds, measured
  downbeatPhase?: number; // 0-3: index of the first bar-start beat (estimated)
  syncStartSec?: number; // suggested start offset inside the track (skips a weak intro)
};

/** Beat frames that fall inside the video, given where the music starts in the track. */
export const beatFrames = (track: LibraryTrack, fps: number, startSec = track.syncStartSec ?? 0): number[] =>
  track.beatTimes.filter((t) => t >= startSec).map((t) => Math.round((t - startSec) * fps));

/** Bar starts only (every 4th beat from the downbeat) — use for scene cuts. */
export const barFrames = (track: LibraryTrack, fps: number, startSec = track.syncStartSec ?? 0): number[] => {
  const phase = track.downbeatPhase ?? 0;
  const beats = track.beatTimes.filter((t) => t >= startSec);
  const firstIdx = track.beatTimes.indexOf(beats[0] ?? 0);
  return beats.filter((_, i) => (i + firstIdx - phase) % 4 === 0).map((t) => Math.round((t - startSec) * fps));
};

/**
 * Snap a planned frame to the nearest beat, only if one is close enough.
 * Keeps the storyboard timing as the source of truth: a cut planned at 72 moves to 70 or 74,
 * never to a far beat that would break the minimum hold of a line (tokens.timing.minHold).
 */
export const snapToBeat = (frame: number, beats: number[], toleranceFrames = 4): number => {
  let best = frame;
  let bestD = toleranceFrames + 1;
  for (const b of beats) {
    const d = Math.abs(b - frame);
    if (d < bestD) {
      best = b;
      bestD = d;
    }
  }
  return bestD <= toleranceFrames ? best : frame;
};

/** Turn a list of planned scene lengths into beat-snapped lengths (sum stays close to the plan). */
export const snapSceneDurations = (durations: number[], beats: number[], toleranceFrames = 4): number[] => {
  const out: number[] = [];
  let planned = 0;
  let prev = 0;
  for (const d of durations) {
    planned += d;
    const cut = snapToBeat(planned, beats, toleranceFrames);
    out.push(Math.max(1, cut - prev));
    prev = cut;
  }
  return out;
};

/** Frames since the most recent beat (or Infinity before the first one). */
const sinceBeat = (frame: number, beats: number[]) => {
  let last = -Infinity;
  for (const b of beats) {
    if (b > frame) break;
    last = b;
  }
  return frame - last;
};

/**
 * Small accent on chosen beats only (logo, stamp, CTA). Returns a scale multiplier ~1.00–1.04.
 * Pass the specific beat frames you want (e.g. [bars[6]]), not the whole beat grid.
 */
export const useBeatAccent = (accentBeats: number[], amount = 0.04, decayFrames = 8): number => {
  const frame = useCurrentFrame();
  const d = sinceBeat(frame, accentBeats);
  if (!Number.isFinite(d)) return 1;
  return 1 + amount * interpolate(d, [0, decayFrames], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
};

/** Spring that starts exactly on a beat (for a stamp pop / text reveal landing on the beat). */
export const useSpringOnBeat = (beat: number, config = {damping: 14, stiffness: 180, mass: 0.7}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - beat, fps, config});
};

/**
 * Music bed with VO ducking and fades. voRanges are [startFrame, endFrame] pairs.
 * bedDb: level without VO. duckDb: level under VO (−10 to −14 dB below the bed is typical).
 */
export const MusicBed: React.FC<{
  track: LibraryTrack;
  totalFrames: number;
  voRanges?: [number, number][];
  bedDb?: number;
  duckDb?: number;
  fadeInFrames?: number;
  fadeOutFrames?: number;
}> = ({track, totalFrames, voRanges = [], bedDb = -6, duckDb = -18, fadeInFrames = 6, fadeOutFrames = 24}) => {
  const {fps} = useVideoConfig();
  const g = (db: number) => Math.pow(10, db / 20);
  const ramp = 6; // frames to duck in/out
  return (
    <Audio
      src={staticFile(track.file)}
      startFrom={Math.round((track.syncStartSec ?? 0) * fps)}
      volume={(f) => {
        let level = g(bedDb);
        for (const [a, b] of voRanges) {
          const k = interpolate(f, [a - ramp, a, b, b + ramp], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          level = Math.min(level, g(bedDb) + (g(duckDb) - g(bedDb)) * k);
        }
        const fade = interpolate(f, [0, fadeInFrames, totalFrames - fadeOutFrames, totalFrames], [0, 1, 1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        return level * fade;
      }}
    />
  );
};
