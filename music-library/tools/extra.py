"""Supplementary measurements (Stamply music library). usage: python3 extra.py track.mp3 out.json
All values are measured from the audio; the vocal fields are heuristics (hints, not facts)."""
import sys, json, numpy as np, librosa
p, out = sys.argv[1], sys.argv[2]
y, sr = librosa.load(p, sr=22050, mono=True); dur = len(y)/sr
hop = 512
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
# BPM cross-check: tempogram-based tempo estimate (independent of the beat tracker's DP)
bpm_tg = float(np.atleast_1d(librosa.feature.tempo(onset_envelope=oenv, sr=sr, hop_length=hop))[0])
# plp-based pulse clarity: mean PLP peak strength (higher = clearer, steadier pulse)
plp = librosa.beat.plp(onset_envelope=oenv, sr=sr, hop_length=hop)
pulse = float(np.mean(plp))
S = np.abs(librosa.stft(y, hop_length=hop))**2; f = librosa.fft_frequencies(sr=sr)
tot = S.sum(0)+1e-12
speech = float((S[(f>=1000)&(f<=4000)].sum(0)/tot).mean())   # VO intelligibility band occupancy
low = float((S[f<150].sum(0)/tot).mean())                     # sub/bass weight
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; db = np.maximum(20*np.log10(rms+1e-9), -80.0)  # floor digital silence
fps = sr/hop; w = int(fps)                                    # 1 s smoothing
sm = np.convolve(db, np.ones(w)/w, mode='same'); med = float(np.median(sm))
act = np.where(sm >= med-3)[0]; ramp = float(act[0]/fps) if len(act) else None
tail = sm[-int(3*fps):]; endDrop = float(med - tail[-int(fps//2):].mean())
endingType = 'fade' if endDrop > 15 and (tail[0]-tail[-1]) > 8 else ('cold/hit' if endDrop > 15 else 'sustained/cut')
# biggest 1-second loudness jump (drop/build detector)
jump = float(np.max(sm[w:]-sm[:-w])) if len(sm) > 2*w else 0.0
# loop similarity: chroma of first vs last 8 s of the body (excluding intro ramp and fade)
chroma = librosa.feature.chroma_cqt(y=librosa.effects.harmonic(y), sr=sr, hop_length=hop)
a0 = int(((ramp or 0)+0.5)*fps); b1 = len(sm)-1
while b1 > a0 and sm[b1] < med-6: b1 -= 1
def cv(a,b):
    x=chroma[:,a:b].mean(1); z=chroma[:,max(a,0):b]
    return x
A = cv(a0, a0+int(8*fps)); B = cv(max(a0,b1-int(8*fps)), b1)
loopSim = float(A@B/(np.linalg.norm(A)*np.linalg.norm(B)+1e-9))
# vocal hint: pYIN on harmonic excerpts; voices glide/vibrato, synth leads are mostly steady.
H = librosa.effects.harmonic(y)
frames=0; voiced=0; wobbly=0
for c in (0.3, 0.6):
    seg = H[int(dur*c*sr):int((dur*c+12)*sr)]
    if len(seg) < sr: continue
    f0, vf, vp = librosa.pyin(seg, fmin=90, fmax=900, sr=sr, frame_length=2048, hop_length=hop)
    frames += len(f0); v = vf & (vp > 0.6); voiced += int(v.sum())
    cents = 1200*np.log2(np.where(v, f0, np.nan)/440)
    k = 8  # ~0.19 s windows
    for i in range(0, len(cents)-k, k):
        c_ = cents[i:i+k]
        if np.isnan(c_).any(): continue
        d = np.abs(np.diff(c_)); 
        if 15 < np.std(c_) < 120 and d.max() < 150: wobbly += k
res = dict(bpmTempogram=round(bpm_tg,1), pulseClarity=round(pulse,3), speechBandShare=round(speech,3),
           lowEndShare=round(low,3), introRampSec=round(ramp,1) if ramp is not None else None,
           endingType=endingType, endDropDb=round(endDrop,1), maxJumpDbPerSec=round(jump,1),
           loopChromaSim=round(loopSim,3), voicedShare=round(voiced/max(frames,1),3),
           vocalWobbleShare=round(wobbly/max(frames,1),3))
json.dump(res, open(out,'w')); print(json.dumps(res))
