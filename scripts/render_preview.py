"""Orthographic preview of the actual Minecraft JSON cuboids and pixel textures."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json, math
R=Path(__file__).resolve().parents[1]; A=R/'src/main/resources/assets/bocchi'
W,H=1440,890
im=Image.new('RGB',(W,H),'#f7f3ed'); d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=lambda size:ImageFont.truetype(font,size)
d.text((40,26),'BTR WORLD · ОДИНОКИЙ РОКЕР',font=f(30),fill='#373145')
d.text((40,70),'Модели прототипа • ортографический рендер JSON • Minecraft 1.21.1',font=f(17),fill='#766e80')
ns={'bocchi':'Хитори','nijika':'Нидзика','ryo':'Рё','kita':'Кита'}
cs={'bocchi':'#efa1c4','nijika':'#efc657','ryo':'#526fa4','kita':'#ca5258'}
faces={'north':[(0,1,0),(1,1,0),(1,0,0),(0,0,0)],'east':[(1,1,0),(1,1,1),(1,0,1),(1,0,0)],'up':[(0,1,1),(1,1,1),(1,1,0),(0,1,0)]}
texcache={}
def drawmodel(model,cx,cy,scale):
 polys=[]
 def proj(p):x,y,z=p;return(cx+scale*(.82*x+.57*z),cy+scale*(.29*x-.42*z-.86*y))
 for el in model['elements']:
  a,b=el['from'],el['to']
  def point(v):
   p=[a[t]+(b[t]-a[t])*v[t] for t in range(3)]
   rot=el.get('rotation')
   if rot:
    origin=rot['origin'];ang=math.radians(rot['angle']);u=p[0]-origin[0];v=p[1]-origin[1]
    p[0]=origin[0]+u*math.cos(ang)-v*math.sin(ang);p[1]=origin[1]+u*math.sin(ang)+v*math.cos(ang)
   return p
  for face,vs in faces.items():
   points=[point(v) for v in vs];center=[sum(p[t] for p in points)/4 for t in range(3)]
   depth=center[0]-center[2]+center[1]*.65
   texture=model['textures'][el['faces'][face]['texture'][1:]];texture_path=A/'textures'/ (texture.split(':')[1]+'.png')
   if texture_path not in texcache:texcache[texture_path]=Image.open(texture_path).convert('RGB')
   polys.append((depth,[proj(p) for p in points],texcache[texture_path],face))
 for _,p,texture,face in sorted(polys,key=lambda x:x[0]):
  tw,th=texture.size
  # Face pixels are projected from the source texture, preserving the actual face design.
  def uv(u,v):return tuple(p[0][t]+u*(p[1][t]-p[0][t])+v*(p[3][t]-p[0][t]) for t in range(2))
  shade={'north':1,'east':.78,'up':1.08}[face]
  for yy in range(th):
   for xx in range(tw):
    col=tuple(min(255,int(c*shade)) for c in texture.getpixel((xx,yy)))
    d.polygon([uv(xx/tw,yy/th),uv((xx+1)/tw,yy/th),uv((xx+1)/tw,(yy+1)/th),uv(xx/tw,(yy+1)/th)],fill=col)
  d.line(p+[p[0]],fill='#574b58',width=1)
for row,form in enumerate(['plush','chibi']):
 for col,kind in enumerate(ns):
  x=40+col*350;y=125+row*325
  d.rounded_rectangle((x,y,x+325,y+300),radius=16,fill='white',outline='#e3dce2',width=2)
  d.rounded_rectangle((x+16,y+16,x+32,y+32),radius=6,fill=cs[kind])
  d.text((x+44,y+12),ns[kind]+' · '+('тсум' if form=='plush' else 'чиби'),font=f(19),fill='#373145')
  d.ellipse((x+80,y+245,x+245,y+267),fill='#eee9ee')
  model=json.loads((A/f'models/item/{kind}_{form}.json').read_text())
  drawmodel(model,x+65,y+280,7.3 if form=='plush' else 6.0)
  ability={'bocchi':'Прячется при опасности','nijika':'Поддерживает барабанным ритмом','ryo':'Ест траву • торгует фигурками','kita':'Сияет • дарит ночное зрение'}[kind]
  d.text((x+14,y+274),ability,font=f(13),fill='#766e80')
d.text((40,808),'Приручение: печенье / торт / пшеница / светящиеся ягоды',font=f(18),fill='#373145')
d.text((40,846),'Пустая рука: следовать ↔ ждать. Это превью геометрии, не скриншот из игры.',font=f(15),fill='#766e80')
out=R.parent/'btr-world-preview.png';im.save(out);print(out)
