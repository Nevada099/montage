from pathlib import Path
import subprocess,json,concurrent.futures
D=Path(__file__).resolve().parent
import os
os.chdir(D)
V='sources/IMG_8576.MOV'
P=[ 'sources/087866F6-1B92-4162-8B97-0A16171B6DB4_4_5005_c.jpeg', 'sources/242F4C42-6D4E-46E2-9D08-1D5F3BB9C2B5_4_5005_c.jpeg', 'sources/94F0242C-5A40-4917-9B18-3C8B2B3DD87F_4_5005_c.jpeg', 'sources/0C8A562B-D188-4264-A4D2-76D210F67442_4_5005_c.jpeg']
scenes=[(p,0,2.5) for p in P]+[(V,.5,4),(V,6,2.5),(V,9,3),(V,20,4),(V,28,3),(V,1.5,3.5)]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def render(item):
 i,(p,start,dur)=item
 args=['ffmpeg','-y','-hide_banner','-loglevel','error','-threads','2']
 if p!=V:
  args+=['-i',p]
  # Preserve complete source photo, use a blurred background for mismatched aspect ratios.
  base="[0:v]split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2[back];[fg]scale=1080:1920:force_original_aspect_ratio=decrease[front];[back][front]overlay=(W-w)/2:(H-h)/2,setsar=1,zoompan=z='1+0.035*on/74':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=75:s=1080x1920:fps=30"
 else:
  args+=['-ss',str(start),'-i',p]
  base='[0:v:0]fps=30,scale=1080:1920,setsar=1'
 label={0:'AVANT',1:'LE CHANTIER',3:'LA TRANSFORMATION',4:'LE STUDIO PREND FORME'}.get(i)
 if label:
  base+=f",drawbox=x=60:y=260:w={min(900,45+len(label)*25)}:h=78:color=black@0.55:t=fill,drawtext=fontfile={font}:text='{label}':x=82:y=281:fontsize=38:fontcolor=white"
 if i==9: base+=f',fade=t=out:st={dur-.5}:d=0.5'
 base+='[v]'
 args+=['-filter_complex_threads','1','-filter_complex',base,'-map','[v]','-an','-t',str(dur),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-threads','2','-map_metadata','-1',str(D/f'segment-{i:02}.mp4')]
 subprocess.run(args,check=True)
 print('segment',i,'ready',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(render,enumerate(scenes)))
(D/'concat.txt').write_text(''.join(f"file 'segment-{i:02}.mp4'\n" for i in range(len(scenes))))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(D/'concat.txt'),'-c','copy','-movflags','+faststart','-map_metadata','-1',str(D/'studio-renovation.mp4')],check=True)
(D/'montage.json').write_text(json.dumps([{'scene':i+1,'source':p,'in':s,'duration':d} for i,(p,s,d) in enumerate(scenes)],indent=2))
print('DONE',flush=True)
