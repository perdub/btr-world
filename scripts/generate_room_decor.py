"""Original room decorations, generated reproducibly without external artwork."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
R=Path(__file__).resolve().parents[1]/'src/main/resources';A=R/'assets/bocchi';D=R/'data/bocchi'
def js(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
colors={'cream':'#f5e7ca','brown':'#a17858','dark':'#342a34','blue':'#68aec3','green':'#88c977','warm':'#ffd294','wire':'#5d505b','pink':'#ef9ebd','yellow':'#edc75b','red':'#c65866'}
for name,color in colors.items():Image.new('RGB',(16,16),color).save(A/f'textures/block/model/room_{name}.png')
textures={n:'bocchi:block/model/room_'+n for n in colors}
def box(a,b,tex,glow=False):
 e={'from':a,'to':b,'faces':{f:{'texture':'#'+tex,'uv':[0,0,16,16]} for f in ['north','south','east','west','up','down']}}
 if glow:e['shade']=False
 return e
font=ImageFont.load_default()
poster_specs=[('kessoku_poster',(128,128),'KESSOKU BAND','LIVE AT STARRY'),('indie_poster',(128,256),'INDIE NIGHT','OPEN MIC / 19:00'),('festival_poster',(256,128),'STARRY FEST','LIVE / TICKETS')]
for name,(w,h),title,subtitle in poster_specs:
 im=Image.new('RGB',(w,h),'#282238');draw=ImageDraw.Draw(im)
 draw.rectangle((3,3,w-4,h-4),outline='#ffd294',width=2)
 draw.text((10,12),title,font=font,fill='#fff1d5');draw.text((10,h-22),subtitle,font=font,fill='#ffd294')
 if name=='kessoku_poster':
  for i,c in enumerate(['pink','yellow','blue','red']):
   x=14+i*26;draw.ellipse((x,40,x+21,61),fill=colors[c]);draw.rectangle((x+3,62,x+18,90),fill=colors[c]);draw.rectangle((x+5,49,x+7,51),fill='#342a34');draw.rectangle((x+14,49,x+16,51),fill='#342a34')
 elif name=='indie_poster':
  for y,t in [(55,'KESSOKU BAND'),(82,'LOCAL INDIE'),(109,'GUITAR SESSION'),(136,'DRUM SOLO'),(171,'ADMIT ONE')]:
   draw.text((12,y),t,font=font,fill=colors['yellow' if y==171 else 'pink'])
  draw.rectangle((9,162,w-10,192),outline='#ffd294')
 else:
  for i,t in enumerate(['KESSOKU BAND','INDIE STAGE','NIGHT JAM']):draw.text((12,44+i*18),t,font=font,fill=['#ef9ebd','#edc75b','#68aec3'][i])
  draw.rectangle((180,38,238,91),outline='#ffd294',width=2);draw.text((187,53),'TICKET',font=font,fill='#ffd294');draw.text((194,72),'01',font=font,fill='#ef9ebd')
 im.save(A/f'textures/block/model/{name}.png');textures[name]='bocchi:block/model/'+name
models={}
# Rounded cuboid plush dog: floppy ears, muzzle, stitched paws and collar.
models['jimihen_plush']=[box([4,1,4],[12,6,12],'cream'),box([4,5,3],[12,11,10],'cream'),box([2.5,5,4],[4.5,10,8],'brown'),box([11.5,5,4],[13.5,10,8],'brown'),box([6,6,1.8],[10,8.5,3.1],'cream'),box([7,7.5,1.6],[9,8.5,1.9],'dark'),box([5,8.5,2.8],[6,9.5,3],'dark'),box([10,8.5,2.8],[11,9.5,3],'dark'),box([3.5,0,3],[6.5,2,6],'brown'),box([9.5,0,3],[12.5,2,6],'brown'),box([4,5,9],[12,6,10],'blue'),box([7,4.5,9.8],[9,6,10.2],'warm'),box([11,2,11],[13,5,13],'brown')]
models['mini_slime_plush']=[box([4,0,4],[12,6,12],'green'),box([5,6,5],[11,7,11],'green'),box([5,3.5,3.8],[6.5,5,4],'dark'),box([9.5,3.5,3.8],[11,5,4],'dark'),box([7,2,3.8],[9,2.7,4],'dark'),box([4.5,2.5,3.7],[6,3.1,3.9],'pink'),box([10,2.5,3.7],[11.5,3.1,3.9],'pink')]
for name,(w,h),_,_ in poster_specs:
 width,height=w/128*16,h/128*16
 models[name]=[box([0,0,15],[width,height,15.7],name)]
# Thin stepped star tubing; flattened depth and warm backing.
star=[]
pts=[]
for i in range(10):
 angle=-math.pi/2+i*math.pi/5;r=6.5 if i%2==0 else 2.8;pts.append((8+math.cos(angle)*r,8-math.sin(angle)*r))
for a,b in zip(pts,pts[1:]+pts[:1]):
 for k in range(10):
  x=a[0]+(b[0]-a[0])*k/9;y=a[1]+(b[1]-a[1])*k/9
  star.append(box([x-.35,y-.35,14.9],[x+.35,y+.35,15.5],'warm',True))
models['starry_neon_star']=star+[box([3,1,15.5],[13,2,15.8],'wire')]
lights=[]
for i in range(16):
 y=13-2*math.sin(math.pi*i/15);lights.append(box([i,y,15.4],[i+1,y+.25,15.7],'wire'))
for i in [1,4,7,10,13]:
 y=13-2*math.sin(math.pi*i/15);lights += [box([i+.3,y-1.5,15.2],[i+.55,y,15.6],'wire'),box([i,y-2.3,14.8],[i+.85,y-1.35,15.6],'warm',True)]
models['fairy_lights']=lights
translations={
 'jimihen_plush':('Плюшевый Дзимихен','Плюшавы Дзіміхэн','Jimihen plush'),
 'mini_slime_plush':('Плюшевый мини-слизень','Плюшавы міні-слізень','Mini slime plush'),
 'kessoku_poster':('Постер Kessoku Band · 1×1','Постар Kessoku Band · 1×1','Kessoku Band poster · 1×1'),
 'indie_poster':('Инди-афиша · 1×2','Індзі-афіша · 1×2','Indie poster · 1×2'),
 'festival_poster':('Фестивальная афиша · 2×1','Фестывальная афіша · 2×1','Festival poster · 2×1'),
 'starry_neon_star':('Неоновая звезда STARRY','Неонавая зорка STARRY','STARRY neon star'),
 'fairy_lights':('Тонкая гирлянда','Тонкая гірлянда','Fairy lights')}
ingredients={'jimihen_plush':['white_wool','brown_dye','string'],'mini_slime_plush':['lime_wool','slime_ball','string'],'kessoku_poster':['paper','pink_dye','black_dye'],'indie_poster':['paper','blue_dye','black_dye'],'festival_poster':['paper','red_dye','black_dye'],'starry_neon_star':['gold_nugget','glowstone_dust','glass_pane'],'fairy_lights':['string','glowstone_dust','iron_nugget']}
guitar=json.loads((A/'models/item/guitar.json').read_text())
models['guitar_stand']=guitar['elements']
for el in models['guitar_stand']:
 for key in ['from','to']:
  el[key]=[el[key][0]*.5+4,el[key][1]*.5+1,el[key][2]*.5+4]
textures.update(guitar['textures'])
models['guitar_stand'] += [box([3,0,4],[13,1,12],'brown'),box([7.5,1,10],[8.5,11,11],'dark')]
translations['guitar_stand']=('Гитара на стойке','Гітара на стойцы','Guitar stand')
ingredients['guitar_stand']=['bocchi:guitar','minecraft:stick','minecraft:oak_slab']
for name,elements in models.items():
 js(A/f'models/block/{name}.json',{'textures':textures,'elements':elements})
 js(A/f'models/item/{name}.json',{'parent':'bocchi:block/'+name,'display':{'gui':{'rotation':[15,25,0],'translation':[0,-2,0],'scale':[.5,.5,.5]},'fixed':{'rotation':[0,180,0],'translation':[0,0,-7],'scale':[.5,.5,.5]}}})
 wall=name not in ['jimihen_plush','mini_slime_plush','guitar_stand'];variants={}
 if wall:
  for face,y in [('north',0),('east',90),('south',180),('west',270)]:variants['facing='+face]={'model':'bocchi:block/'+name,'y':y}
  # All states must be authored, even when vertical placement is disallowed.
  for face,x in [('down',90),('up',270)]:variants['facing='+face]={'model':'bocchi:block/'+name,'x':x}
 else:variants['']={'model':'bocchi:block/'+name}
 js(A/f'blockstates/{name}.json',{'variants':variants})
 js(D/f'recipe/{name}.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':i if ':' in i else 'minecraft:'+i} for i in ingredients[name]],'result':{'id':'bocchi:'+name,'count':2 if name=='fairy_lights' else 1}})
 js(D/f'loot_table/blocks/{name}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'bocchi:'+name}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
for locale,index in [('ru_ru',0),('be_by',1),('en_us',2)]:
 path=A/f'lang/{locale}.json';lang=json.loads(path.read_text())
 for name,names in translations.items():lang['block.bocchi.'+name]=names[index]
 js(path,lang)
js(D/'advancement/recipes/welcome.json',{'criteria':{'join':{'trigger':'minecraft:tick'}},'rewards':{'recipes':['bocchi:'+p.stem for p in sorted((D/'recipe').glob('*.json'))]}})
print('Room decor: 8 blocks, 8 recipes, RU/BE/EN.')
