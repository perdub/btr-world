"""Software preview of authored geometry; not a Minecraft client screenshot."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('preview',root/'scripts/render_preview.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.im=Image.new('RGB',(1440,940),'#f7f3ed');m.d=ImageDraw.Draw(m.im);d=m.d
font=m.f
d.text((30,20),'BTR WORLD · детали и выражения',font=font(30),fill='#373145')
for x,name,title in [(35,'drum_kit','Барабаны: стойки, обода, педаль'),(750,'bocchi_box','Коробка: клапаны, скотч, сгибы')]:
 d.rounded_rectangle((x,75,x+650,480),radius=16,fill='white',outline='#e3dce2',width=2)
 d.text((x+20,92),title,font=font(22),fill='#373145')
 model=json.loads((m.A/f'models/block/{name}.json').read_text())
 m.drawmodel(model,x+80,450,18)
for i,(mood,title) in enumerate([('happy','Радость'),('sleepy','Ожидание'),('surprised','Удивление'),('squint','><')]):
 x=30+i*350
 d.rounded_rectangle((x,500,x+330,875),radius=16,fill='white',outline='#e3dce2',width=2)
 d.text((x+20,517),title,font=font(21),fill='#373145')
 model=json.loads((m.A/f'models/item/nijika_chibi_{mood}.json').read_text())
 m.drawmodel(model,x+60,845,8.3)
d.text((30,902),'Программное превью JSON-моделей. Клиентский рендер Minecraft ещё не проверен.',font=font(18),fill='#766e80')
out=root/'docs/btr-details-preview.png';m.im.save(out);print(out)
