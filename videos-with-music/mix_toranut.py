exec(open('mix.py').read().split('# 1) Talk-after')[0])
# Toranut swap (35s): Gummies at its native 120 BPM. Its first lift (bar 16.37) lands on the "what if" turn (8.5s);
# steps 1-4 (14.5 / 18.5 / 22.5 / 26.5s) then fall on downbeats. Quiet intro under the problem, fade on the end card.
v='vid/toranut.mp4'; dur=35.0
m=load(L+'02_playful_bloops/mixkit-gummies-1142.mp3')
start=16.37-8.5; seg=m[int(start*SR):int(start*SR)+int(dur*SR)].copy(); seg=fade(seg,int(0.15*SR),int(1.8*SR))
s=sfx(v,len(seg)); mux(v,gain_to(gain_to(seg,-16.0)+s,-14.0),'out/toranut-swap-music.mp4')
