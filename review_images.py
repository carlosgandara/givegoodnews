from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, features
import json
root=Path(__file__).parent
out=root/'image-review'
out.mkdir(exist_ok=True)
files=sorted((root/'img').glob('image*.png'),key=lambda p:int(p.stem[5:]))
files+=sorted((root/'img').glob('achievement*.png'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
inventory=[]
for start in range(0,len(files),6):
    group=files[start:start+6]
    sheet=Image.new('RGB',(1086,400*len(group)), 'white')
    d=ImageDraw.Draw(sheet)
    for j,p in enumerate(group):
        im=Image.open(p).convert('RGB')
        inventory.append({'file':p.name,'width':im.width,'height':im.height,'bytes':p.stat().st_size})
        d.text((10,j*400+3),p.name,font=font,fill='black')
        im.thumbnail((1086,362))
        sheet.paste(im,(0,j*400+35))
    sheet.save(out/f'contact-{start//6+1}.jpg',quality=95)
(out/'inventory.json').write_text(json.dumps(inventory,indent=2))
print(json.dumps({'count':len(files),'webp':features.check('webp'),'sheets':(len(files)+5)//6}))
