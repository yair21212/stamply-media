// Stamply music library — deterministic music selection (stage 6). Never random.
// Input: what the storyboard already knows. Output: ranked tracks with the reason for each.
import type {LibraryTrack} from './beatSync';

export type Category =
  | '01_premium_tech'
  | '02_playful_bloops'
  | '03_clean_product_demo'
  | '04_energetic_ads'
  | '05_minimal_voiceover'
  | '06_soft_background';

export type LibraryEntry = LibraryTrack & {
  id: string;
  title: string;
  categories: Category[];
  primaryCategory: Category;
  energy: 1 | 2 | 3 | 4 | 5;
  hasVocals: boolean | 'possible' | 'unknown';
  voiceoverFriendly: boolean;
  motionGraphicsFit: number;
  introQuality: number;
  loopFriendly: boolean;
  durationSec: number;
  mood: string[];
};

export type MusicBrief = {
  videoType: 'ui-product' | 'product-reveal' | 'talking-head' | 'fast-ad' | 'explainer' | 'kinetic-typography' | 'stories-bts';
  voDensity: 'none' | 'light' | 'dense'; // share of the video with speech: none <10%, light <50%, dense >=50%
  editPace: 'slow' | 'medium' | 'fast'; // average scene length: >3 s / 1.5-3 s / <1.5 s
  durationSec: number;
  animationStyle?: 'beat-synced' | 'smooth' | 'minimal';
  brandTone?: 'premium' | 'playful' | 'calm'; // Stamply default: premium + a little playful
  mood?: string[]; // from creativeDirection.feeling, e.g. ['positive', 'futuristic']
  exclude?: string[]; // track ids used in the last videos (avoid repetition)
};

/** Which categories fit a video. First entry = best fit. */
export const categoriesFor = (b: MusicBrief): Category[] => {
  if (b.voDensity === 'dense' || b.videoType === 'talking-head') return ['05_minimal_voiceover', '06_soft_background', '03_clean_product_demo'];
  if (b.videoType === 'fast-ad') return ['04_energetic_ads', '01_premium_tech', '02_playful_bloops'];
  if (b.videoType === 'product-reveal') return ['01_premium_tech', '04_energetic_ads', '03_clean_product_demo'];
  if (b.videoType === 'ui-product') return b.brandTone === 'playful' ? ['02_playful_bloops', '01_premium_tech', '03_clean_product_demo'] : ['01_premium_tech', '02_playful_bloops', '03_clean_product_demo'];
  if (b.videoType === 'kinetic-typography') return ['02_playful_bloops', '01_premium_tech', '04_energetic_ads'];
  if (b.videoType === 'stories-bts') return ['06_soft_background', '03_clean_product_demo', '05_minimal_voiceover'];
  if (b.durationSec <= 20 && b.editPace === 'fast') return ['04_energetic_ads', '01_premium_tech', '02_playful_bloops']; // short fast explainer
  return ['03_clean_product_demo', '05_minimal_voiceover', '01_premium_tech']; // explainer
};

const targetEnergy = (b: MusicBrief) => {
  let e = {slow: 2, medium: 3, fast: 4}[b.editPace];
  if (b.voDensity === 'dense') e = Math.min(e, 2);
  else if (b.voDensity === 'light') e = Math.min(e, 3);
  if (b.videoType === 'fast-ad') e = Math.max(e, 4);
  return e;
};

export const selectMusic = (library: LibraryEntry[], b: MusicBrief, n = 3) => {
  const cats = categoriesFor(b);
  const eT = targetEnergy(b);
  const scored = library
    .filter((t) => !(b.exclude ?? []).includes(t.id))
    .filter((t) => (b.voDensity === 'none' ? true : t.hasVocals === false)) // any VO → instrumental only
    .filter((t) => (b.voDensity === 'dense' ? t.voiceoverFriendly : true))
    .filter((t) => t.durationSec - (t.syncStartSec ?? 0) >= b.durationSec + 2) // must cover the whole video
    .map((t) => {
      const why: string[] = [];
      let s = 0;
      const ci = cats.findIndex((c) => t.categories.includes(c));
      if (ci >= 0) {
        s += [6, 3.5, 2][ci];
        why.push(`category ${cats[ci]}`);
      }
      if (t.primaryCategory === cats[0]) s += 1;
      s -= Math.abs(t.energy - eT) * 1.2;
      why.push(`energy ${t.energy} vs target ${eT}`);
      if (b.animationStyle === 'beat-synced') {
        s += (t.motionGraphicsFit - 3) * 0.8;
        why.push(`motion fit ${t.motionGraphicsFit}`);
      }
      if (b.durationSec <= 20) s += (t.introQuality - 3) * 0.8; // short videos need music that works from second 0
      if (b.voDensity !== 'none' && t.voiceoverFriendly) {
        s += 1.5;
        why.push('VO friendly');
      }
      if (b.durationSec > t.durationSec * 0.9 && t.loopFriendly) s += 0.5;
      const moodHits = (b.mood ?? []).filter((m) => t.mood.includes(m)).length;
      s += moodHits * 0.7;
      if (moodHits) why.push(`mood match ×${moodHits}`);
      return {track: t, score: Math.round(s * 100) / 100, why};
    })
    .sort((a, b2) => b2.score - a.score || a.track.id.localeCompare(b2.track.id)); // stable, never random
  return scored.slice(0, n);
};
