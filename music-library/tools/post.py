"""Post-pass measurements. usage: python3 post.py track.mp3 analyzer.json out.json
- dropDb: biggest rise of 2 s-smoothed loudness within 2 s, after the track first reaches its body level
  (i.e. breakdown -> drop, not the intro entrance)
- fingerprint: 12-bin chroma + 20-bin loudness profile, to find duplicate audio published under two titles
- downbeatPhase (estimate): which of the 4 beat phases carries the most low-frequency onset energy"""
import sys, json, numpy as np, librosa
p, an, out = sys.argv[1], sys.argv[2], sys.argv[3]
a = json.load(open(an))
y, sr = librosa.load(p, sr=22050, mono=True); hop = 512; fps = sr/hop
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; db = np.maximum(20*np.log10(rms+1e-9), -80.0)
w = int(2*fps); sm = np.convolve(db, np.ones(w)/w, mode='valid')
med = np.median(sm); st = np.where(sm >= med-3)[0]; st = int(st[0]) if len(st) else 0
end = len(sm)-1
while end > st and sm[end] < med-6: end -= 1
body = sm[st:end]; g = int(2*fps)
drop = float(np.max(body[g:] - body[:-g])) if len(body) > g+1 else 0.0
dip = float(med - np.min(body)) if len(body) else 0.0          # deepest breakdown inside the body
chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop).mean(1)
prof = np.interp(np.linspace(0, len(sm)-1, 20), np.arange(len(sm)), sm)
# downbeat phase estimate from low-band onset strength at beat positions
S = np.abs(librosa.stft(y, hop_length=hop)); f = librosa.fft_frequencies(sr=sr)
low = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[f < 200]), sr=sr, hop_length=hop)
bt = np.array(a['beatTimes']); bf = np.clip((bt*fps).astype(int), 0, len(low)-1)
phase_score = [float(low[bf[k::4]].mean()) if len(bf[k::4]) else 0 for k in range(4)]
ph = int(np.argmax(phase_score)); conf = float(max(phase_score)/(np.mean(phase_score)+1e-9))
res = dict(dropDb=round(drop,1), breakdownDipDb=round(dip,1), bodyStartSec=round(st/fps,1), bodyEndSec=round((end+w)/fps,1),
           chromaFp=[round(float(v),3) for v in chroma], loudFp=[round(float(v),1) for v in prof],
           downbeatPhase=ph, downbeatConfidence=round(conf,2))
json.dump(res, open(out,'w')); print(json.dumps({k:v for k,v in res.items() if 'Fp' not in k}))
