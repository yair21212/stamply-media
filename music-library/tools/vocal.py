"""Vocal check (heuristic, stronger than the analyzer hint). usage: python3 vocal.py track.mp3 out.json
REPET-SIM foreground/background separation (librosa docs 'Vocal separation'), then pYIN on the
foreground of three 20 s excerpts. Voices give long voiced runs with pitch glides; the result is still
an estimate, not a fact."""
import sys, json, numpy as np, librosa
p, out = sys.argv[1], sys.argv[2]
y, sr = librosa.load(p, sr=22050, mono=True); dur = len(y)/sr
res = []
for c in (0.25, 0.5, 0.75):
    seg = y[int(dur*c*sr):int(min(dur, dur*c+20)*sr)]
    S_full, phase = librosa.magphase(librosa.stft(seg))
    S_filter = librosa.decompose.nn_filter(S_full, aggregate=np.median, metric='cosine',
                                           width=int(librosa.time_to_frames(2, sr=sr)))
    S_filter = np.minimum(S_full, S_filter)
    mask_v = librosa.util.softmask(S_full - S_filter, 10 * S_filter, power=2)
    S_fg = mask_v * S_full
    fgShare = float((S_fg**2).sum() / ((S_full**2).sum() + 1e-12))
    fg = librosa.istft(S_fg * phase, length=len(seg))
    f0, vf, vp = librosa.pyin(fg, fmin=80, fmax=1000, sr=sr, frame_length=2048)
    v = vf & (vp > 0.5)
    # voiced runs >= 0.25 s whose pitch moves (glide/vibrato) — typical of singing, rare in synth arps
    hop_s = 512/sr; runs = []; start = None
    for i, b in enumerate(np.append(v, False)):
        if b and start is None: start = i
        if not b and start is not None:
            if (i-start)*hop_s >= 0.25:
                cents = 1200*np.log2(f0[start:i]/440)
                runs.append(float(np.std(np.diff(cents))))
            start = None
    moving = [r for r in runs if 3 < r < 60]
    res.append(dict(at=round(dur*c,1), fgShare=round(fgShare,3), voicedShare=round(float(v.mean()),3),
                    longRuns=len(runs), movingRuns=len(moving)))
score = np.mean([r['voicedShare'] for r in res]) * np.mean([r['fgShare'] for r in res]) * 10
verdict = 'likely' if (score > 0.25 and sum(r['movingRuns'] for r in res) >= 6) else ('possible' if score > 0.12 else 'unlikely')
json.dump(dict(excerpts=res, vocalScore=round(float(score),3), vocalVerdict=verdict), open(out,'w'))
print(verdict, round(float(score),3), res)
