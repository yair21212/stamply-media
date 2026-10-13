import sys
exec(open('mix.py').read().split('# 1) Talk-after')[0])
# Stamply_with_phone_v2 (38.5s): Macario. The build (bars 62.53-64.92) plays under the hook,
# the drop (bar 67.32) lands on the Stamply logo (4.13s), and the end card (33.27s) lands exactly 12 bars later (bar 96.11).
v=sys.argv[1]; out=sys.argv[2]; dur=38.5
T=(96.11-67.32)/(33.27-4.13)
m=load(L+'03_clean_product_demo/mixkit-macario-772.mp3',T)
start=67.32/T-4.13; seg=m[int(start*SR):int(start*SR)+int(dur*SR)].copy(); seg=fade(seg,int(0.15*SR),int(2.5*SR))
s=sfx(v,len(seg)); mux(v,gain_to(gain_to(seg,-16.0)+s,-14.0),out)
