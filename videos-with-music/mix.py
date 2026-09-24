import numpy as np, soundfile as sf, pyloudnorm as pyln, subprocess, json, sys
SR=44100; L='lib/music-library/'
def load(path, tempo=1.0):
    af=['-af',f'atempo={tempo}'] if tempo!=1.0 else []
    raw=subprocess.run(['ffmpeg','-loglevel','error','-i',path,*af,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
def fade(x,n_in,n_out):
    if n_in: x[:n_in]*=np.linspace(0,1,n_in)[:,None]
    if n_out: x[-n_out:]*=np.linspace(1,0,n_out)[:,None]
    return x
def loopify(seg,dur,xf):
    # seg has dur+xf seconds; mix the overflow tail into the head with an equal-power crossfade
    n=int(dur*SR); k=int(xf*SR); out=seg[:n].copy(); tail=seg[n:n+k]
    t=np.linspace(0,1,k)[:,None]
    out[:k]=out[:k]*np.sin(t*np.pi/2)+tail*np.cos(t*np.pi/2)
    return out
meter=pyln.Meter(SR)
def gain_to(x,lufs): return x*10**((lufs-meter.integrated_loudness(x))/20)
def limit(x,ceil=0.89):  # -1 dBFS soft ceiling
    p=np.abs(x).max(); return x*(ceil/p) if p>ceil else x
def mux(video,audio,out):
    sf.write('tmp.wav',audio,SR,subtype='FLOAT')
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',video,'-i','tmp.wav','-map','0:v:0','-map','1:a:0','-af','alimiter=limit=0.89:attack=1:release=60:level=disabled','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',out],check=True)
def sfx(video,n):
    raw=subprocess.run(['ffmpeg','-loglevel','error','-i',video,'-vn','-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    a=np.frombuffer(raw,np.float32).reshape(-1,2).copy(); a=np.pad(a,((0,max(0,n-len(a))),(0,0)))[:n]; return a

# 1) Talk-after ad: Digital Clouds, drop on the brand reveal (4.70s), cut at 11.33s on beat 14
T=0.9804; dur=19.033; drop_orig=29.95
m=load(L+'01_premium_tech/mixkit-digital-clouds-175.mp3',T)
start=drop_orig/T-4.70; seg=m[int(start*SR):int((start+dur)*SR)]
seg=fade(seg,int(0.12*SR),int(1.1*SR))
mux('/home/user/stamply-media/stamply-ad-talk-after.mp4',limit(gain_to(seg,-14.0)),'out/stamply-ad-talk-after-music.mp4')

# 2) Wallet drop loop (8s): Brainiac -> 120 BPM, downbeat on every card landing (0.22 + 2k s)
T=120/117.6; dur=8.0; db_orig=28.54
m=load(L+'01_premium_tech/mixkit-brainiac-167.mp3',T)
start=db_orig/T-0.22; seg=loopify(m[int(start*SR):int((start+dur+0.3)*SR)],dur,0.3)
v='vid/e858be6cc4a0a0e3aeb8196f393bdc5d.mp4'; s=sfx(v,len(seg))
mix=gain_to(seg,-19.0)+s*10**(3/20)   # SFX stay on top, music is the bed
mux(v,gain_to(mix,-14.0),'out/wow-wallet-drop-music.mp4')

# 3) Stamps loop (6.67s): Gummies 120 -> 117 BPM = exactly 13 beats per loop, downbeat on the 10th stamp (3.47s)
T=117/120; dur=200/30; db_orig=22.36
m=load(L+'02_playful_bloops/mixkit-gummies-1142.mp3',T)
start=db_orig/T-3.47; seg=loopify(m[int(start*SR):int((start+dur+0.3)*SR)],dur,0.3)
v='vid/be2edffdd142af0b14fc6986496f31a0.mp4'; s=sfx(v,len(seg))
mix=gain_to(seg,-19.0)+s*10**(3/20)
mux(v,gain_to(mix,-14.0),'out/wow-stamps-music.mp4')
print('ok')
