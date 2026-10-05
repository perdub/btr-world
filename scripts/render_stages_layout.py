"""Show actual NBT floor plans; this is not an in-game screenshot."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from structure_nbt import read
R=Path(__file__).resolve().parents[1]
im=Image.new('RGB',(1500,900),'#f7f3ed');draw=ImageDraw.Draw(im)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
draw.text((35,22),'BTR World · три концертные площадки',font=font(30),fill='#30283f')
draw.text((35,66),'Планы настоящих NBT-шаблонов · потолок скрыт · четыре живых участницы',font=font(18),fill='#706776')
colors={'bocchi':'#eea1c1','nijika':'#f1cf5a','ryo':'#698cb4','kita':'#d66c6c'}
for i,(style,title) in enumerate([('starry','STARRY'),('school','Школьный фестиваль'),('indie','Инди-клуб')]):
 left=25+i*495;draw.rounded_rectangle((left,112,left+475,790),radius=16,fill='white',outline='#e2dce5',width=2)
 draw.text((left+22,132),title,font=font(24),fill='#30283f')
 n=read(R/f'src/main/resources/data/bocchi/structure/stages/{style}_mixed.nbt');w,h,d=n['size'];s=17;x0=left+(475-w*s)//2;y0=206
 palette=n['palette'];blocks={tuple(b['pos']):palette[b['state']]['Name'] for b in n['blocks']}
 equipment={'drum_kit':'Б','microphone':'М','guitar_stand':'Г','amplifier':'У','speaker':'К','guitar_case':'Ф','bocchi_box':'□'}
 for x in range(w):
  for z in range(d):
   # Stage is at y=1; floor at y=0. Draw actual footprint from the back to entry.
   mat=blocks.get((x,0,z),'');col='#a9a7ab'
   if 'planks' in mat:col='#c9a67c'
   if 'white_concrete' in mat:col='#efeeee'
   if 'black_concrete' in mat:col='#38343d'
   if x in (0,w-1) or z==d-1:col='#625964'
   if blocks.get((x,1,z))=='minecraft:dark_oak_planks':col='#796050'
   xx=x0+x*s;yy=y0+(d-1-z)*s
   draw.rectangle((xx,yy,xx+s-1,yy+s-1),fill=col)
   for y in [1,2]:
    name=blocks.get((x,y,z),'').split(':')[-1]
    if name in equipment:
     draw.rectangle((xx+1,yy+1,xx+s-2,yy+s-2),fill='#373046')
     draw.text((xx+3,yy),equipment[name],font=font(12),fill='white')
    if name=='chest':draw.rectangle((xx+2,yy+2,xx+s-3,yy+s-3),fill='#a56530')
    if name.endswith('stairs') and 'dark_oak' not in name:draw.rectangle((xx+2,yy+2,xx+s-3,yy+s-3),fill='#8a644a')
 for entity in n['entities']:
  x,y,z=entity['pos'];kind=entity['nbt']['id'].split(':')[1].split('_')[0]
  xx=x0+x*s;yy=y0+(d-z)*s
  draw.ellipse((xx-7,yy-7,xx+7,yy+7),fill=colors[kind],outline='#3b3443',width=1)
 draw.text((left+30,704),f'{w} × {h} × {d} блоков',font=font(19),fill='#30283f')
 draw.text((left+30,738),'Вход снизу · сцена сверху',font=font(17),fill='#706776')
draw.text((35,809),'Г — гитара   Б — барабаны   М — микрофон   У — усилитель   К — колонка',font=font(18),fill='#30283f')
draw.text((35,849),'Цветные кружки — Боччи, Нидзика, Рё и Кита. Схема; игровой вид ещё не проверен.',font=font(17),fill='#706776')
out=R/'docs/stages-layout.png';im.save(out);print(out)
