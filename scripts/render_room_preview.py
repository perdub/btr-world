"""Preview authored room models and poster textures, not an in-game screenshot."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('preview',root/'scripts/render_preview.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.im=Image.new('RGB',(1280,840),'#f7f3ed');m.d=ImageDraw.Draw(m.im);d=m.d
f=m.f
d.text((30,20),'BTR WORLD · уютный декор',font=f(28),fill='#373145')
for x,name,title in [(30,'jimihen_plush','Дзимихен'),(340,'mini_slime_plush','Мини-слизень'),(650,'starry_neon_star','Звезда STARRY'),(960,'fairy_lights','Гирлянда')]:
 d.rounded_rectangle((x,75,x+285,365),radius=15,fill='white')
 d.text((x+15,88),title,font=f(20),fill='#373145')
 model=json.loads((m.A/f'models/block/{name}.json').read_text());m.drawmodel(model,x+20,345,8)
for x,name,title in [(40,'kessoku_poster','Постер · 1×1'),(445,'indie_poster','Инди-афиша · 1×2'),(745,'festival_poster','Фестиваль · 2×1')]:
 d.text((x,402),title,font=f(22),fill='#373145')
 texture=Image.open(m.A/f'textures/block/model/{name}.png')
 scale=1.25 if name=='indie_poster' else 1.7
 texture=texture.resize((int(texture.width*scale),int(texture.height*scale)),Image.Resampling.NEAREST);m.im.paste(texture,(x,450))
d.text((30,800),'Программное превью моделей и текстур; не скриншот Minecraft.',font=f(18),fill='#766e80')
out=root/'docs/btr-room-preview.png';m.im.save(out);print(out)
