"""Preview real generated structure voxels, not a Minecraft screenshot."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from structure_nbt import read
R=Path(__file__).resolve().parents[1]
im=Image.new('RGB',(1500,670),'#f7f3ed');d=ImageDraw.Draw(im)
f=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
d.text((28,20),'BTR WORLD · большие статуи',font=f(30),fill='#373145')
d.text((28,65),'Шаблоны 11 × 18 × 11 блоков · редкие природные структуры',font=f(18),fill='#766e80')
colours={'pink_terracotta':'#a76666','white_terracotta':'#d2b3a3','black_concrete':'#272331','white_concrete':'#e5e3da','red_concrete':'#b4434d','light_blue_concrete':'#72bdd3','yellow_concrete':'#e3b840','stone_bricks':'#77787c','smooth_stone':'#b4b1ab'}
hero={'bocchi':'#efa1c4','nijika':'#efc657','ryo':'#526fa4','kita':'#ca5258'}
names={'bocchi':'Хитори','nijika':'Нидзика','ryo':'Рё','kita':'Кита'}
faces=[((0,0,-1),[(0,0,0),(1,0,0),(1,1,0),(0,1,0)],.9),((1,0,0),[(1,0,0),(1,0,1),(1,1,1),(1,1,0)],.73),((0,1,0),[(0,1,0),(1,1,0),(1,1,1),(0,1,1)],1.08)]
for i,kind in enumerate(hero):
 x0=22+i*372;d.rounded_rectangle((x0,110,x0+354,615),16,fill='white',outline='#e3dce2',width=2)
 d.text((x0+20,128),names[kind],font=f(23),fill='#373145')
 nbt=read(R/f'src/main/resources/data/bocchi/structure/statues/{kind}.nbt')
 blocks={tuple(b['pos']):nbt['palette'][b['state']]['Name'] for b in nbt['blocks']}
 def proj(x,y,z):return(x0+24+(x+z)*13,530+(x-z)*7.5-y*15)
 polygons=[]
 for (x,y,z),mat in blocks.items():
  col=('#ffcedf' if '_light_' in mat else hero[kind]) if mat.startswith('bocchi:') else colours[mat.split(':')[1]]
  rgb=tuple(bytes.fromhex(col[1:]))
  for (dx,dy,dz),vertices,shade in faces:
   if (x+dx,y+dy,z+dz) in blocks:continue
   points=[(x+vx,y+vy,z+vz) for vx,vy,vz in vertices]
   depth=sum(a-b+c*.35 for a,c,b in points)/4
   polygons.append((depth,[proj(*v) for v in points],tuple(min(255,int(c*shade)) for c in rgb)))
 for depth,points,col in sorted(polygons):d.polygon(points,fill=col);d.line(points+[points[0]],fill=tuple(int(c*.88) for c in col),width=1)
d.text((28,637),'Программный рендер NBT-шаблонов. Генерация в игровом мире ещё не проверена.',font=f(18),fill='#766e80')
out=R/'docs/btr-statues-preview.png';im.save(out);print(out)
