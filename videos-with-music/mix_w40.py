import sys; sys.argv=['x']
exec(open('mix.py').read().split('# 1) Talk-after')[0])
T=1.0175; dur=22.0; drop_orig=29.95; reveal=5.03
m=load(L+'01_premium_tech/mixkit-digital-clouds-175.mp3',T)
start=drop_orig/T-reveal+0.03; seg=m[int(start*SR):int((start+dur)*SR)].copy()
seg=fade(seg,int(0.12*SR),int(1.4*SR))
v='vid/w40.mp4'; s=sfx(v,len(seg))
mix=gain_to(seg,-16.0)+s          # music leads, SFX stay audible on top
mux(v,gain_to(mix,-14.0),'out/w40-reel-talk-after-music.mp4')
