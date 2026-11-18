from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops
import json, shutil, hashlib, os

root=Path(__file__).parent
backup=root/'originals-before-domain-change'
backup.mkdir(exist_ok=True)
files=sorted((root/'img').glob('*.png'))
report=[]
for p in files:
    original=backup/p.name
    if not original.exists(): shutil.copy2(p,original)
    if p.stem.startswith('image') and int(p.stem[5:])>=43:
        shutil.copy2(original,p)
        report.append({'file':p.name,'status':'already_has_correct_domain','all_pixels_unchanged':True,'backup':str(original.relative_to(root)).replace('\\','/')})
        continue
    src=Image.open(original).convert('RGB')
    w,h=src.size
    top=round(h*646/724)
    band_h=h-top
    # Reuse clean unlettered paper from the left edge, preserving texture.
    patch=src.crop((0,top,round(w*100/2172),h))
    band=Image.new('RGB',(w,band_h))
    for x in range(0,w,patch.width):
        tile=patch if (x//patch.width)%2==0 else patch.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        band.paste(tile,(x,0))
    scale=4
    big=band.resize((w*scale,band_h*scale),Image.Resampling.BICUBIC)
    d=ImageDraw.Draw(big)
    font=ImageFont.truetype('C:/Windows/Fonts/georgiab.ttf',round(68*w/2172*scale))
    text='givegoodnews.com'
    box=d.textbbox((0,0),text,font=font)
    tw,th=box[2]-box[0],box[3]-box[1]
    tx=(w*scale-tw)//2-box[0]
    ty=(band_h*scale-th)//2-box[1]-round(2*scale*h/724)
    d.text((tx,ty),text,font=font,fill=(66,27,15))
    gap=round(32*w/2172*scale)
    left=(w*scale-tw)//2-gap
    right=(w*scale+tw)//2+gap
    line_y=round((680*h/724-top)*scale)
    thickness=max(2,round(6*h/724*scale))
    for a,b in [(round(w*.055*scale),left),(right,round(w*.945*scale))]:
        d.rounded_rectangle((a,line_y-thickness//2,b,line_y+thickness//2),radius=thickness//2,fill=(249,182,7))
    band=big.resize((w,band_h),Image.Resampling.LANCZOS)
    dst=src.copy()
    dst.paste(band,(0,top))
    assert ImageChops.difference(src.crop((0,0,w,top)),dst.crop((0,0,w,top))).getbbox() is None
    temp=p.with_name(p.stem+'.domain-update.tmp')
    dst.save(temp,format='PNG',compress_level=6)
    os.replace(temp,p)
    with Image.open(p) as reopened:
        check=reopened.convert('RGB')
    assert check.size==src.size
    assert ImageChops.difference(src.crop((0,0,w,top)),check.crop((0,0,w,top))).getbbox() is None
    report.append({'file':p.name,'dimensions':[w,h],'edited_region':[0,top,w,h],'artwork_pixels_unchanged':True,'backup':str(original.relative_to(root)).replace('\\','/'),'original_bytes':original.stat().st_size,'updated_bytes':p.stat().st_size})
(root/'domain-change-report.json').write_text(json.dumps({'domain':'givegoodnews.com','resized':False,'lossy_compression':False,'files':report},indent=2),encoding='utf-8')
# Keep the existing gallery branding consistent; image paths remain PNG.
for p in root.glob('*.html'):
    text=p.read_text(encoding='utf-8')
    text=text.replace('givegood<span>.news</span>','givegoodnews<span>.com</span>').replace('givegood.news','givegoodnews.com')
    p.write_text(text,encoding='utf-8')
print(json.dumps({'updated':len(report),'artwork_pixel_checks':'passed','dimensions':'unchanged','backup':str(backup)}))
