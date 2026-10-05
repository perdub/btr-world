from pathlib import Path
from PIL import Image, ImageDraw
import json,random,copy
ROOT=Path(__file__).resolve().parents[1]/'src/main/resources'
AS=ROOT/'assets/bocchi'; DATA=ROOT/'data/bocchi'
for d in ['textures/block','textures/block/model','textures/item','models/block','models/item','blockstates','lang']: (AS/d).mkdir(parents=True,exist_ok=True)
for d in ['recipe','loot_table/blocks','advancement/recipes']: (DATA/d).mkdir(parents=True,exist_ok=True)
def js(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
colors={'bocchi':('#efa1c4','#ffcedf','#b75b8e'),'nijika':('#efc657','#fff0a1','#b78a32'),'ryo':('#526fa4','#a4bfde','#2f426a'),'kita':('#ca5258','#f7a5a2','#843c4b')}
names={'bocchi':'Хитори','nijika':'Нидзика','ryo':'Рё','kita':'Кита'}
ru={};en={}
def lang(key,name,english):ru[key]=name;en[key]=english
random.seed(2026)
materials={'skin':'#ffdfc5','outline':'#3f3047','white':'#fff5e7','black':'#34313f','metal':'#9cb2bd','pink':'#f3a0c0','blue':'#74cce8','red':'#d34657','yellow':'#f1d35e','cardboard':'#ba8861','carddark':'#80553c','wood':'#99734b','green':'#6c9852'}
for k,(base,light,dark) in colors.items(): materials[k]=base;materials[k+'_light']=light;materials[k+'_dark']=dark
for name,color in materials.items(): Image.new('RGB',(16,16),color).save(AS/f'textures/block/model/{name}.png')
# Pixel faces belong to the newly built Minecraft models, not extracted anime artwork.
for kind in colors:
 im=Image.new('RGB',(16,16),materials['skin']);d=ImageDraw.Draw(im)
 if kind=='bocchi':
  d.line([(3,5),(6,7),(3,9)],fill=materials['outline'],width=2);d.line([(12,5),(9,7),(12,9)],fill=materials['outline'],width=2)
  d.rectangle((6,11,9,12),fill=materials['outline'])
 else:
  d.rectangle((3,6,4,8),fill=materials['outline']);d.rectangle((11,6,12,8),fill=materials['outline'])
  d.line([(6,11),(8,12),(10,11)],fill=materials['outline'],width=1)
 d.rectangle((1,10,3,11),fill='#ee9f9f');d.rectangle((12,10,14,11),fill='#ee9f9f')
 im.save(AS/f'textures/block/model/{kind}_face.png')
# Expressions reuse the same UV layout as the neutral face.
for kind in colors:
 for mood in ['happy','sleepy','surprised','squint']:
  im=Image.new('RGB',(16,16),materials['skin']);d=ImageDraw.Draw(im)
  ink=materials['outline']
  if mood=='happy':
   d.line([(2,8),(4,6),(6,8)],fill=ink,width=1);d.line([(10,8),(12,6),(14,8)],fill=ink,width=1)
   d.arc((6,9,10,13),0,180,fill=ink,width=1)
  elif mood=='sleepy':
   d.line((2,8,5,8),fill=ink);d.line((10,8,13,8),fill=ink);d.rectangle((7,11,8,11),fill=ink)
  elif mood=='squint':
   d.line([(2,5),(5,7),(2,9)],fill=ink,width=2);d.line([(13,5),(10,7),(13,9)],fill=ink,width=2)
   d.rectangle((6,11,9,12),fill=ink)
  else:
   d.ellipse((2,5,6,9),fill=materials['white'],outline=ink);d.ellipse((10,5,14,9),fill=materials['white'],outline=ink)
   d.point((4,7),fill=ink);d.point((12,7),fill=ink);d.ellipse((7,11,9,13),outline=ink)
  d.rectangle((1,10,3,11),fill='#ee9f9f');d.rectangle((12,10,14,11),fill='#ee9f9f')
  im.save(AS/f'textures/block/model/{kind}_face_{mood}.png')
def element(a,b,tex,north=None,rotation=None):
 faces={s:{'uv':[0,0,16,16],'texture':'#'+tex} for s in ['north','south','east','west','up','down']}
 if north: faces['north']['texture']='#'+north
 result={'from':a,'to':b,'faces':faces}
 if rotation:result['rotation']=rotation
 return result
textures={k:'bocchi:block/model/'+k for k in materials}
textures.update({k+'_face':'bocchi:block/model/'+k+'_face' for k in colors}); textures['particle']='bocchi:block/model/pink'
textures.update({k+'_face_'+m:'bocchi:block/model/'+k+'_face_'+m for k in colors for m in ['happy','sleepy','surprised','squint']})
def model(elements,item=True):
 obj={'textures':textures,'elements':elements}
 if item: obj['display']={'gui':{'rotation':[18,145,0],'translation':[0,-3,0],'scale':[0.75,0.75,0.75]},'ground':{'translation':[0,0,0],'scale':[0.5,0.5,0.5]},'fixed':{'scale':[0.7,0.7,0.7]},'thirdperson_righthand':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[0.5,0.5,0.5]},'firstperson_righthand':{'rotation':[0,-35,0],'translation':[0,-3,0],'scale':[0.7,0.7,0.7]}}
 return obj
all_mob_models={}
for kind in colors:
 hair=kind
 for form in ['plush','chibi']:
  e=[]
  if form=='plush':
   e+=[element([1,9,2],[15,15,14],hair,kind+'_face'),element([3,8,3],[13,16,13],hair)]
   e+=[element([2,14,1.7],[14,16,5],hair),element([1,9,1.5],[3,15,5],hair),element([13,9,1.5],[15,15,5],hair)]
   e+=[element([2,8,1],[5,10,4],'skin'),element([11,8,1],[14,10,4],'skin')]
   top=16
  else:
   e+=[element([5,8,6],[7,11,10],'black'),element([9,8,6],[11,11,10],'black')]
   e+=[element([4,11,5],[12,17,11],'pink' if kind=='bocchi' else 'white')]
   e+=[element([2,11,6],[4,16,10],'skin'),element([12,11,6],[14,16,10],'skin')]
   e+=[element([3,17,3],[13,26,13],'skin',kind+'_face'),element([2.5,24,2.5],[13.5,27,13.5],hair),element([2,17,3],[4,26,14],hair),element([12,17,3],[14,26,14],hair),element([3,17,12.5],[13,26,14],hair)]
   e+=[element([4,23.5,2.6],[6,25,3],hair),element([7,24,2.6],[10,25,3],hair)]
   top=27
  if kind=='bocchi':e+=[element([13,top-2,3],[15,top,5],'blue'),element([13,top-4,3],[15,top-2,5],'yellow')]
  if kind=='nijika':
   e+=[element([7,top,7],[10,top+2,8],'yellow',rotation={'origin':[8,top,8],'axis':'z','angle':22.5}),element([14,10,8],[16,top-1,12],hair),element([12,top-3,7],[15,top-1,10],'red')]
  if kind=='ryo':e+=[element([2,top-5,2.5],[4,top-4,3],'white')]
  if kind=='kita':e+=[element([2,10,10],[4,top-3,14],hair),element([12,10,10],[14,top-3,14],hair)]
  ident=kind+'_'+form
  all_mob_models[ident]=model(e)
  js(AS/f'models/item/{ident}.json',model(e))
  for mood in ['happy','sleepy','surprised','squint']:
   variant=copy.deepcopy(e)
   for el in variant:
    for face in el['faces'].values():
     if face['texture']=='#'+kind+'_face':face['texture']='#'+kind+'_face_'+mood
   if mood=='surprised':
    # Small raised whites and pupils add a physical anime surprise expression.
    y0,y1,z=(11,13,1.8) if form=='plush' else (21,23,2.95)
    for x in ([4,10] if form=='plush' else [5,9]):
     variant.append(element([x,y0,z-.35],[x+1.5,y1,z],'white'))
     variant.append(element([x+.5,y0+.6,z-.45],[x+1,y0+1.3,z-.35],'black'))
   js(AS/f'models/item/{ident}_{mood}.json',model(variant))
   lang('item.bocchi.'+ident+'_'+mood+'_model',names[kind]+' · '+mood,kind.title()+' '+mood+' model')
  js(AS/f'models/item/{ident}_summoner.json',{'parent':f'bocchi:item/{ident}'})
  lang('item.bocchi.'+ident+'_model',names[kind]+' · модель '+('тсум' if form=='plush' else 'чиби'),kind.title()+' '+form+' model')
  lang('item.bocchi.'+ident+'_summoner','Позвать: '+names[kind]+' · '+('тсум' if form=='plush' else 'чиби'),'Summon '+kind.title()+' '+form)
  lang('entity.bocchi.'+ident,names[kind]+' · '+('тсум' if form=='plush' else 'чиби'),kind.title()+' '+form)
  # Survival summoning recipe, intentionally distinct between the two forms.
  js(DATA/f'recipe/{ident}_summoner.json',{'type':'minecraft:crafting_shaped','pattern':[' W ','DCD',' T '],'key':{'W':{'item':'minecraft:white_wool' if form=='plush' else 'minecraft:oak_planks'},'D':{'item':'minecraft:'+{'bocchi':'pink','nijika':'yellow','ryo':'blue','kita':'red'}[kind]+'_dye'},'C':{'item':'minecraft:cookie'},'T':{'item':'minecraft:amethyst_shard'}},'result':{'id':'bocchi:'+ident+'_summoner','count':1}})
 # Figurines use the exact chibi mesh scaled onto a base in block coordinates.
 elems=copy.deepcopy(all_mob_models[kind+'_chibi']['elements'])
 for el in elems:
  for field in ['from','to']:el[field]=[8+(el[field][0]-8)*.60,(el[field][1]-8)*.60+1,8+(el[field][2]-8)*.60]
  if 'rotation' in el:el['rotation']['origin']=[8+(el['rotation']['origin'][0]-8)*.60,(el['rotation']['origin'][1]-8)*.60+1,8+(el['rotation']['origin'][2]-8)*.60]
 elems.insert(0,element([3,0,3],[13,1,13],'black'))
 ident=kind+'_figurine';js(AS/f'models/block/{ident}.json',model(elems,False))
 js(AS/f'models/item/{ident}.json',{'parent':f'bocchi:block/{ident}'})
 js(AS/f'blockstates/{ident}.json',{'variants':{'':{'model':f'bocchi:block/{ident}'}}})
 lang('block.bocchi.'+ident,'Фигурка: '+names[kind],kind.title()+' figurine')
# Color palettes have subtle pixel grain; tiles and lights have their own patterns.
for kind,cs in colors.items():
 for shade,color in zip(['base','light','dark'],cs):
  for finish in ['matte','tile','lamp']:
   ident=f'{kind}_{shade}_{finish}';im=Image.new('RGB',(16,16),color);pix=im.load();rgb=im.getpixel((0,0))
   for y in range(16):
    for x in range(16):
     v=random.randint(-5,5);pix[x,y]=tuple(max(0,min(255,c+v)) for c in rgb)
   d=ImageDraw.Draw(im)
   if finish=='tile':
    for q in [0,8]:d.line((q,0,q,15),fill=cs[2]);d.line((0,q,15,q),fill=cs[2])
    d.line((3,3,5,5),fill=cs[1]);d.line((11,11,13,13),fill=cs[1])
   if finish=='lamp':
    d.rectangle((0,0,15,15),outline=cs[2],width=2);d.rectangle((3,3,12,12),fill=cs[1]);d.line((4,4,11,4),fill='#fff5ee')
   im.save(AS/f'textures/block/{ident}.png')
   js(AS/f'models/block/{ident}.json',{'parent':'minecraft:block/cube_all','textures':{'all':f'bocchi:block/{ident}'}})
   js(AS/f'models/item/{ident}.json',{'parent':f'bocchi:block/{ident}'})
   js(AS/f'blockstates/{ident}.json',{'variants':{'':{'model':f'bocchi:block/{ident}'}}})
   lang('block.bocchi.'+ident,names[kind]+': '+{'base':'основной','light':'светлый','dark':'тёмный'}[shade]+' '+{'matte':'матовый блок','tile':'кафель','lamp':'светильник'}[finish],kind.title()+' '+shade+' '+finish)
   dye={'bocchi':'pink','nijika':'yellow','ryo':'blue','kita':'red'}[kind]
   ingredients=[{'item':'minecraft:white_concrete'},{'item':'minecraft:'+dye+'_dye'}]
   if shade!='base':ingredients.append({'item':'minecraft:'+('white' if shade=='light' else 'black')+'_dye'})
   if finish=='tile':ingredients.append({'item':'minecraft:quartz'})
   if finish=='lamp':ingredients.append({'item':'minecraft:glowstone_dust'})
   js(DATA/f'recipe/{ident}.json',{'type':'minecraft:crafting_shapeless','ingredients':ingredients,'result':{'id':'bocchi:'+ident,'count':1}})
# Corrugated cardboard front: tape, creases, handle and shipping marks.
im=Image.new('RGB',(64,64),'#ba8861');d=ImageDraw.Draw(im)
for y in range(0,64,4):d.line((0,y,63,y),fill='#b17f59')
d.rectangle((0,0,63,63),outline='#80553c',width=2)
d.rectangle((27,0,36,63),fill='#d8b786');d.line((31,0,31,63),fill='#aa845e')
d.rectangle((7,19,22,25),fill='#674732');d.line((8,20,21,20),fill='#d5a376')
d.rectangle((42,35,59,52),fill='#e5d3ac');d.line((44,39,56,39),fill='#725b43');d.line((44,43,53,43),fill='#725b43')
for x in range(44,57,2):d.line((x,46,x,50),fill='#725b43')
d.line([(2,48),(9,51),(4,59)],fill='#976a48');d.line([(58,2),(54,11),(61,15)],fill='#976a48')
im.save(AS/'textures/block/model/cardboard_detail.png');textures['cardboard_detail']='bocchi:block/model/cardboard_detail'
# Stage props, constructed from low-poly cuboids.
props={
'bocchi_box':[element([1,0,1],[15,9,2],'cardboard'),element([1,0,14],[15,9,15],'cardboard'),element([1,0,2],[2,9,14],'cardboard'),element([14,0,2],[15,9,14],'cardboard'),element([2,0,2],[14,1,14],'cardboard'),element([1,8,0],[15,9,3],'carddark'),element([1,8,13],[15,9,16],'carddark'),element([6,3,.95],[10,5,1],'carddark')],
'amplifier':[element([2,0,3],[14,11,13],'black'),element([3,2,2.9],[13,8,3],'metal'),element([3,9,2.8],[4,10,3],'yellow'),element([6,9,2.8],[7,10,3],'red'),element([6,11,6],[10,12,9],'black')],
'speaker':[element([3,0,3],[13,14,13],'black'),element([4,2,2.9],[12,8,3],'metal'),element([6,10,2.8],[10,13,3],'metal'),element([5,3,2.8],[11,7,2.9],'black')],
'drum_kit':[element([5,1,3],[11,7,9],'yellow'),element([5,2,2.9],[11,6,3],'white'),element([2,6,7],[6,9,11],'yellow'),element([10,6,7],[14,9,11],'yellow'),element([2,9,7],[6,9.5,11],'white'),element([10,9,7],[14,9.5,11],'white'),element([1,0,12],[2,11,13],'metal'),element([0,11,10],[5,11.4,15],'yellow'),element([13,0,12],[14,11,13],'metal'),element([11,11,10],[16,11.4,15],'yellow')],
'microphone':[element([4,0,4],[12,1,12],'black'),element([7.5,1,7.5],[8.5,13,8.5],'metal'),element([7,12,4],[9,14,9],'black')],
'guitar_case':[element([4,0,4],[12,2,14],'black'),element([6,0,1],[10,2,6],'black'),element([11,1,8],[13,2,10],'metal')],
'starry_sign':[element([1,0,7],[15,10,9],'black')]
}
# Reinforced box panels, folded lips, taped seam and physical edge creases.
box=props['bocchi_box'];box[0]['faces']['north']['texture']='#cardboard_detail';box[0]['faces']['south']['texture']='#cardboard_detail'
box += [element([1,0,.9],[1.3,9,15.1],'carddark'),element([14.7,0,.9],[15,9,15.1],'carddark'),
        element([1,0,1],[15,.3,15],'carddark'),element([7.2,0,.85],[8.8,8.5,.95],'wood'),
        element([1,8.5,3],[2,9.1,13],'carddark'),element([14,8.5,3],[15,9.1,13],'carddark')]
# Stepped octagonal drums: shells, contrasting rims, skins, lugs and a supported rack.
def drum(cx,cy,cz,r,height,axis='y'):
 parts=[]
 def piece(a,b,tex):
  if axis=='z':a=[a[0],cy+a[2]-cz,cz+a[1]-cy];b=[b[0],cy+b[2]-cz,cz+b[1]-cy]
  parts.append(element(a,b,tex))
 for dy,h,tex in [(0,height,'red'),(-.15,.3,'metal'),(height-.15,.3,'metal'),(height+.15,.1,'white')]:
  for strip in range(8):
   x0=-r+strip*r/4;x1=x0+r/4
   half=min(r,r*1.41421356-max(abs(x0),abs(x1)))
   piece([cx+x0,cy+dy,cz-half],[cx+x1,cy+dy+h,cz+half],tex)
 for dx,dz in [(-r,0),(r,0),(0,-r),(0,r)]:
  piece([cx+dx-.15,cy+.3,cz+dz-.15],[cx+dx+.15,cy+height-.3,cz+dz+.15],'metal')
 return parts
drums=drum(8,3.7,4.2,3.2,3,'z')
drums+=drum(4.3,6.7,8.2,2.2,2.2)+drum(10,7.5,9,2.1,2.1)+drum(13,2.5,12,2.4,4)
drums+=drum(3,4.2,4,1.9,1)
for x,z,top in [(1.6,11,12),(13.8,4,10.8),(3,4,4.2),(13,12,2.5)]:
 drums.append(element([x-.14,.3,z-.14],[x+.14,top,z+.14],'metal'))
 for dx,dz in [(-1,0),(1,0),(0,1)]:
  drums.append(element([min(x,x+dx),0,min(z,z+dz)],[max(x,x+dx)+.18,.3,max(z,z+dz)+.18],'metal'))
 if top>10:
  drums.append(element([x-1.9,top,z-1.5],[x+1.9,top+.16,z+1.5],'yellow'))
  drums.append(element([x-.6,top+.16,z-.6],[x+.6,top+.45,z+.6],'yellow'))
# Bass pedal, rack, throne, drumsticks resting across the snare.
drums += [element([7,0,1],[9,.25,3],'metal'),element([7.5,.25,1.5],[8.5,.5,3],'black'),
          element([7.85,3,8],[8.15,9.5,8.3],'metal'),element([4,7.5,8],[11,7.8,8.3],'metal'),
          element([7.8,0,13],[8.2,3.7,13.4],'metal'),element([6.5,3.7,12],[9.5,4.3,14.5],'black'),
          element([1.5,5.4,3.3],[4.5,5.55,3.45],'wood'),element([2.6,5.4,2.5],[2.75,5.55,5.5],'wood')]
props['drum_kit']=drums
# STARRY plaque: stepped bevel silhouette, raised rim bulbs and neon lettering.
# Authored procedural Minecraft asset; reference image is not copied into the pack.
W,H=256,192
im=Image.new('RGB',(W,H),'#29282c');d=ImageDraw.Draw(im)
# Restrained deterministic metal grain.
rng=random.Random(77)
for y in range(H):
 for x in range(W):
  v=rng.randrange(36,44);im.putpixel((x,y),(v,v,v+3))
outline=[(2,62),(80,2),(253,2),(253,157),(185,189),(2,157),(2,62)]
d.line(outline,fill='#656368',width=3)
# Tall outlined strokes, like bent neon tubes. T and the second R are red.
letters={
 'S':[[(22,0),(5,0),(0,5),(0,20),(22,36),(22,51),(17,56),(0,56)]],
 'T':[[(0,0),(26,0)],[(13,0),(13,56)]],
 'A':[[(0,56),(0,5),(5,0),(19,0),(24,5),(24,56)],[(0,31),(24,31)]],
 'R':[[(0,56),(0,0),(18,0),(24,6),(24,22),(18,28),(0,28)],[(12,28),(25,56)]],
 'Y':[[(0,0),(12,28),(24,0)],[(12,28),(12,56)]]}
for i,ch in enumerate('STARRY'):
 x=19+i*36;y=61
 paths=[[(x+px,y+py*1.35) for px,py in path] for path in letters[ch]]
 red=i in (1,4)
 for path in paths:
  d.line([(px+2,py+3) for px,py in path],fill='#17171b',width=9)
  d.line(path,fill='#7d3038' if red else '#254572',width=8)
  d.line(path,fill='#d86a6c' if red else '#619bda',width=4)
  d.line([(px-1,py-1) for px,py in path],fill='#ee9c99' if red else '#99c7ed',width=1)
# Shooting star at the T.
d.line([(52,77),(55,66),(70,49),(85,45)],fill='#da7373',width=3)
d.polygon([(53,69),(56,74),(62,74),(58,78),(60,84),(54,81),(49,85),(50,79),(45,76),(51,75)],fill='#eb8886')
im.save(AS/'textures/block/model/starry.png');textures['starry']='bocchi:block/model/starry'
# Work in front-face coordinates so the text reads correctly from north.
def signpart(u0,v0,u1,v1,z0,z1,tex):
 e=element([16-u1,12-v1,z0],[16-u0,12-v0,z1],tex)
 if tex=='starry':
  for face in e['faces'].values():face['texture']='#black'
  e['faces']['north']={'texture':'#starry','uv':[u0,v0/12*16,u1,v1/12*16]}
 return e
sign=[]
for row in range(24):
 v0=row/2;v1=v0+.5
 left=max(0,(4-v0)*1.25)
 right=16-max(0,(v1-10)*2)
 sign.append(signpart(left,v0,right,v1,7,8,'starry'))
# Lamps follow all six edges and project in front of the metal panel.
perimeter=[(.65,4.3),(5.2,.65),(15.35,.65),(15.35,9.55),(11.6,11.35),(.65,9.55)]
for i,(u,v) in enumerate(perimeter):
 end=perimeter[(i+1)%len(perimeter)]
 n=max(1,round(((end[0]-u)**2+(end[1]-v)**2)**.5/1.65))
 for j in range(n):
  x=u+(end[0]-u)*j/n;y=v+(end[1]-v)*j/n
  sign.append(signpart(x-.3,y-.3,x+.3,y+.3,6.78,7,'metal'))
  sign.append(signpart(x-.21,y-.21,x+.21,y+.21,6.55,6.78,'yellow'))
props['starry_sign']=sign
for ident,e in props.items():
 js(AS/f'models/block/{ident}.json',model(e,False));js(AS/f'models/item/{ident}.json',{'parent':f'bocchi:block/{ident}'})
 js(AS/f'blockstates/{ident}.json',{'variants':{'':{'model':f'bocchi:block/{ident}'}}})
 lang('block.bocchi.'+ident,{'bocchi_box':'Коробка Боччи','amplifier':'Гитарный усилитель','speaker':'Колонка','drum_kit':'Барабаны Нидзики','microphone':'Микрофон Киты','guitar_case':'Гитарный кейс','starry_sign':'Вывеска STARRY'}[ident],ident.replace('_',' ').title())
 js(DATA/f'recipe/{ident}.json',{'type':'minecraft:crafting_shaped','pattern':['PPP','PIP','PPP'],'key':{'P':{'item':'minecraft:oak_planks'},'I':{'item':'minecraft:'+{'bocchi_box':'paper','amplifier':'redstone','speaker':'note_block','drum_kit':'yellow_dye','microphone':'iron_ingot','guitar_case':'leather','starry_sign':'glow_ink_sac'}[ident]}},'result':{'id':'bocchi:'+ident,'count':1}})
# Box visual in entity space starts at y=8 to align its bottom with display origin.
e=copy.deepcopy(props['bocchi_box'])
for el in e:
 for f in ['from','to']:el[f][1]+=8
js(AS/'models/item/hiding_box.json',model(e));lang('item.bocchi.hiding_box','Модель укрытия Боччи','Bocchi hiding box model')
guitar=[element([4,8,7],[12,15,9],'black'),element([6,15,7],[10,18,9],'black'),element([7,18,7],[9,27,8],'wood'),element([6.5,26,7],[9.5,29,8],'black'),element([7.7,11,6.9],[8.3,27,7],'metal')]
js(AS/'models/item/guitar.json',model(guitar));lang('item.bocchi.guitar','Гитара решимости','Guitar of courage')
js(DATA/'recipe/guitar.json',{'type':'minecraft:crafting_shaped','pattern':[' S ',' P ','IPI'],'key':{'S':{'item':'minecraft:string'},'P':{'item':'minecraft:oak_planks'},'I':{'item':'minecraft:iron_ingot'}},'result':{'id':'bocchi:guitar','count':1}})
for kind in colors:
 ident=kind+'_figurine'
 js(DATA/f'recipe/{ident}.json',{'type':'minecraft:crafting_shaped','pattern':[' D ',' C ',' S '],'key':{'D':{'item':'minecraft:'+{'bocchi':'pink','nijika':'yellow','ryo':'blue','kita':'red'}[kind]+'_dye'},'C':{'item':'minecraft:clay_ball'},'S':{'item':'minecraft:smooth_stone'}},'result':{'id':'bocchi:'+ident,'count':1}})
# Every placed block drops itself, including props and figurines.
for path in (AS/'blockstates').glob('*.json'):
 ident=path.stem
 js(DATA/f'loot_table/blocks/{ident}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'bocchi:'+ident}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
# Unlock survival recipes from the start; also accessible with /recipe give.
js(DATA/'advancement/recipes/welcome.json',{'criteria':{'join':{'trigger':'minecraft:tick'}},'rewards':{'recipes':['bocchi:'+p.stem for p in (DATA/'recipe').glob('*.json')]}})
import runpy
runpy.run_path(str(Path(__file__).with_name('generate_equipment.py')),init_globals={'AS':AS,'DATA':DATA,'js':js,'element':element,'model':model,'lang':lang,'textures':textures})
js(AS/'lang/ru_ru.json',ru);js(AS/'lang/en_us.json',en)
(ROOT/'pack.mcmeta').write_text(json.dumps({'pack':{'pack_format':34,'description':'BTR World · 1.21.1'}},ensure_ascii=False))
print('Generated',len(ru),'translations;',len(list((DATA/'recipe').glob('*.json'))),'recipes')

# Keep the expansion deterministic when regenerating base assets.
import runpy
runpy.run_path(str(Path(__file__).with_name("generate_expansion.py")))

runpy.run_path(str(Path(__file__).with_name("generate_room_decor.py")))

runpy.run_path(str(Path(__file__).with_name("generate_craft_guide.py")))

from standardize_names import standardize
standardize()
