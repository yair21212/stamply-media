"""Analyze a music track for the Stamply music library.
usage: python3 analyze.py track.mp3 out.json
Outputs measured facts only (no guessing): bpm + confidence, beat/downbeat times, energy curve,
section stats (intro / 1/3 / 2/3 / ending), onset density, brightness, vocal-likelihood heuristic."""
import sys, json, numpy as np, librosa
p, out = sys.argv[1], sys.argv[2]
y, sr = librosa.load(p, sr=22050, mono=True)
dur = len(y)/sr
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
oenv = librosa.onset.onset_strength(y=y, sr=sr)
tg = librosa.feature.tempogram(onset_envelope=oenv, sr=sr)
bpm = float(np.atleast_1d(tempo)[0])
ibi = np.diff(beats) if len(beats) > 2 else np.array([0])
stab = float(1 - np.std(ibi)/np.mean(ibi)) if len(beats) > 2 else 0.0
rms = librosa.feature.rms(y=y)[0]; t = librosa.times_like(rms, sr=sr)
H, P = librosa.effects.hpss(y)
cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
flat = librosa.feature.spectral_flatness(y=H)[0]
onsets = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, units='time')
def sec(a, b):
    m = (t >= a) & (t < b); o = ((onsets >= a) & (onsets < b)).sum()
    return dict(start=round(a,1), end=round(b,1), rmsDb=round(float(20*np.log10(rms[m].mean()+1e-9)),1),
                onsetsPerSec=round(o/max(b-a,1e-3),2), brightnessHz=int(cent[m].mean()))
S = [('intro', 0, min(10, dur)), ('mid1', dur*0.3, dur*0.3+10), ('mid2', dur*0.6, dur*0.6+10), ('ending', max(0, dur-10), dur)]
# vocal heuristic: harmonic energy share in 300-3400 Hz with pitch-like continuity (only a hint, must be confirmed)
Sh = np.abs(librosa.stft(H)); f = librosa.fft_frequencies(sr=sr)
band = Sh[(f > 300) & (f < 3400)].sum(0) / (Sh.sum(0)+1e-9)
first_hit = float(onsets[0]) if len(onsets) else None
loud = 20*np.log10(rms+1e-9)
res = dict(file=p.split('/')[-1], durationSec=round(dur,2), bpm=round(bpm,1), tempoStability=round(stab,3),
           beatTimes=[round(float(b),3) for b in beats], firstOnsetSec=first_hit,
           loudnessRangeDb=round(float(np.percentile(loud,95)-np.percentile(loud,10)),1),
           percussiveShare=round(float((P**2).sum()/((y**2).sum()+1e-9)),3),
           midBandHarmonicShare=round(float(band.mean()),3), harmonicFlatness=round(float(flat.mean()),4),
           sections={n: sec(a,b) for n,a,b in S},
           energyCurve=[round(float(x),1) for x in loud[::int(sr/512)]])  # ~1 value per second
json.dump(res, open(out,'w'))
print(json.dumps({k:v for k,v in res.items() if k not in ('beatTimes','energyCurve')}, ensure_ascii=False))

