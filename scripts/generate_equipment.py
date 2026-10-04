# Executed by generate_assets.py with its model helpers.
from PIL import Image,ImageDraw
im=Image.new('RGB',(64,64),'#ba8861');d=ImageDraw.Draw(im)
for y in range(0,64,4):d.line((0,y,63,y),fill='#ac7c54')
d.rectangle((0,0,63,63),outline='#714d33',width=2);d.rectangle((25,0,37,63),fill='#d7bc8a')
d.rectangle((5,22,58,43),fill='#e6d1a8');d.text((12,28),'MANGO',fill='#54693b')
d.ellipse((42,7,54,20),fill='#efa735');d.line((48,7,52,3),fill='#537740',width=2)
im.save(AS/'textures/block/model/mango.png');textures['mango']='bocchi:block/model/mango'
e=[element([0,0,0],[16,16,16],'cardboard'),element([-.15,0,-.15],[16.15,16,0],'mango'),element([0,15.8,0],[16,16.2,3],'carddark'),element([0,15.8,13],[16,16.2,16],'carddark')]
o=model(e);o['display']['head']={'rotation':[0,180,0],'translation':[0,0,0],'scale':[1,1,1]};js(AS/'models/item/mango_box_hat.json',o)
e=[element([7,15,7],[9,19,9],'yellow'),element([8,18,7],[12,20,9],'yellow',rotation={'origin':[8,18,8],'axis':'z','angle':22.5}),element([10,16,7],[12,19,9],'yellow')]
o=model(e);o['display']['head']={'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]};js(AS/'models/item/nijika_ahoge.json',o)
im=Image.new('RGB',(64,64),'#bc3545');d=ImageDraw.Draw(im);d.line([(17,2),(46,2),(61,17),(61,46),(46,61),(17,61),(2,46),(2,17),(17,2)],fill='#fff5e7',width=3)
glyphs={'S':['11111','10000','10000','11111','00001','00001','11111'],'T':['11111','00100','00100','00100','00100','00100','00100'],'O':['01110','10001','10001','10001','10001','10001','01110'],'P':['11110','10001','10001','11110','10000','10000','10000']}
for i,c in enumerate('STOP'):
 for y,row in enumerate(glyphs[c]):
  for x,v in enumerate(row):
   if v=='1':d.rectangle((9+i*12+x*2,25+y*2,10+i*12+x*2,26+y*2),fill='#fff5e7')
im.save(AS/'textures/block/model/stop.png');textures['stop']='bocchi:block/model/stop'
e=[element([7.3,-8,7.3],[8.7,14,8.7],'metal')]
for y0,y1,x0,x1 in [(10,12,4,12),(12,14,2,14),(14,22,0,16),(22,24,2,14),(24,26,4,12)]:
 part=element([x0,y0,7],[x1,y1,9],'red');part['faces']['north']={'texture':'#stop','uv':[16-x1,26-y1,16-x0,26-y0]};part['faces']['south']={'texture':'#stop','uv':[x0,26-y1,x1,26-y0]};e.append(part)
o=model(e);o['display']['thirdperson_righthand']={'rotation':[0,0,0],'translation':[0,2,0],'scale':[.9,.9,.9]};js(AS/'models/item/stop_sign.json',o)
labels={'mango_box_hat':('Коробка из-под манго','Mango Box Hat'),'nijika_ahoge':('Дори-ахоге Нидзики','Nijika’s Dorito Ahoge'),'stop_sign':('Дорожный знак STOP','STOP Sign'),'pink_hood':('Розовый спортивный капюшон','Pink Tracksuit Hood'),'pink_jacket':('Розовая спортивная куртка','Pink Tracksuit Jacket'),'pink_pants':('Розовые спортивные брюки','Pink Tracksuit Pants'),'pink_shoes':('Розовые кроссовки','Pink Trainers')}
for id,(ru,en) in labels.items():lang('item.bocchi.'+id,ru,en)
for id,base in [('pink_hood','leather_helmet'),('pink_jacket','leather_chestplate'),('pink_pants','leather_leggings'),('pink_shoes','leather_boots')]:
 js(AS/f'models/item/{id}.json',{'parent':'minecraft:item/'+base})
 js(DATA/f'recipe/{id}.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':'minecraft:'+base},{'item':'minecraft:pink_wool'},{'item':'minecraft:string'}],'result':{'id':'bocchi:'+id,'count':1}})
for id,pattern,key in [('mango_box_hat',['PPP','PAP','PPP'],{'P':'paper','A':'golden_apple'}),('nijika_ahoge',[' NN',' N ','S  '],{'N':'gold_nugget','S':'string'}),('stop_sign',['IRI','IRI',' S '],{'I':'iron_ingot','R':'red_dye','S':'stick'})]:
 js(DATA/f'recipe/{id}.json',{'type':'minecraft:crafting_shaped','pattern':pattern,'key':{k:{'item':'minecraft:'+v} for k,v in key.items()},'result':{'id':'bocchi:'+id,'count':1}})
