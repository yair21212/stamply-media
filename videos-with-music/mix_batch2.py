exec(open('mix.py').read().split('# 1) Talk-after')[0])
def build(track,T,orig_anchor,video_anchor,video,out,dur,music_lufs,fade_out):
    m=load(L+track,T); start=orig_anchor/T-video_anchor
    seg=m[int(start*SR):int(start*SR)+int(dur*SR)].copy(); seg=fade(seg,int(0.1*SR),int(fade_out*SR))
    s=sfx(video,len(seg)); mux(video,gain_to(gain_to(seg,music_lufs)+s,-14.0),out)
# How it works: Macario, stretched so bars 28.91..43.33 span 2.67..17.73 exactly (~95.2 BPM); step 1 (2.67s) on the +2 dB lift (bar 28.91), logo (17.73s) 24 beats later on bar 43.33
build('03_clean_product_demo/mixkit-macario-772.mp3',(43.33-28.91)/(17.73-2.67),28.91,2.67,'vid/how.mp4','out/w40-reel-how-it-works-music.mp4',24.133,-16.0,1.2)
import sys
if 'how' in sys.argv: raise SystemExit
# Stamps: Gummies 120 -> 112.5 BPM = one stamp per beat (0.533s); 10th stamp (5.27s) on a downbeat
build('02_playful_bloops/mixkit-gummies-1142.mp3',0.9375,22.36,5.27,'vid/stamps2.mp4','out/w40-tue-wow-stamps-music.mp4',8.5,-17.0,1.0)
# Wallet: House 02 122.95 -> 122.7 BPM; a card lands every 3 beats, first landing (0.95s) on a downbeat
build('04_energetic_ads/mixkit-house-02-744.mp3',122.7/122.95,23.73,0.95,'vid/wallet2.mp4','out/w40-mon-wow-wallet-music.mp4',8.0,-17.0,1.0)
