"""Deterministic 0.3 data: three-language advancements and vanilla structure templates."""
from pathlib import Path
import json,gzip,struct
ROOT=Path(__file__).resolve().parents[1]/'src/main/resources';A=ROOT/'assets/bocchi';D=ROOT/'data/bocchi'
def js(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
js(A/'models/item/rehearsal_bell.json',{'parent':'minecraft:item/bell'})
js(D/'recipe/rehearsal_bell.json',{'type':'minecraft:crafting_shaped','pattern':[' S ','GAG',' G '],'key':{'S':{'item':'minecraft:string'},'G':{'item':'minecraft:gold_ingot'},'A':{'item':'minecraft:amethyst_shard'}},'result':{'id':'bocchi:rehearsal_bell','count':1}})
# title and description in Russian, Belarusian and English.
entries=[
('root','minecraft:amethyst_shard',('Маленькая сцена','Получи предмет BTR World или приручи спутницу.','Маленькая сцэна','Атрымай прадмет BTR World або прыручы спадарожніцу.','A Little Stage','Obtain a BTR World item or befriend a companion.')),
('first_friend','minecraft:cookie',('Теперь мы вместе','Приручи первую спутницу.','Цяпер мы разам','Прыручы першую спадарожніцу.','Together at Last','Befriend your first companion.')),
('quartet','minecraft:note_block',('Весь Жгут в сборе','Приручи Хитори, Нидзику, Рё и Киту.','Увесь гурт разам','Прыручы Хіторы, Нідзіку, Ро і Кіту.','The Whole Band','Befriend Hitori, Nijika, Ryo and Kita.')),
('new_generation','minecraft:amethyst_cluster',('Новое поколение','Получи первого маленького потомка.','Новае пакаленне','Атрымай першага маленькага нашчадка.','A New Generation','Create your first little descendant.')),
('mixed_duet','minecraft:pink_dye',('Неожиданный дуэт','Соедини разных героинь или разные формы.','Нечаканы дуэт','Спалучы розных гераінь або розныя формы.','An Unexpected Duet','Pair different heroines or different forms.')),
('family_tree','minecraft:oak_sapling',('Семейное дерево','Получи потомка третьего поколения.','Сямейнае дрэва','Атрымай нашчадка трэцяга пакалення.','Family Tree','Create a third-generation descendant.')),
('ryo_trade','minecraft:emerald',('Никаких возвратов','Обменяй изумруд у приручённой Рё.','Вяртання няма','Абмяняй смарагд у прыручанай Ро.','No Refunds','Trade an emerald with your tamed Ryo.')),
('rehearsal','minecraft:bell',('На репетицию!','Позови спутницу колокольчиком репетиции.','На рэпетыцыю!','Пакліч спадарожніцу званочкам рэпетыцыі.','Rehearsal Time!','Call a companion with the rehearsal bell.')),
('power_chord','minecraft:note_block',('Аккорд решимости','Оттолкни враждебного моба гитарой.','Акорд рашучасці','Адштурхні варожага моба гітарай.','Power Chord','Push a hostile mob away with the guitar.')),
('statue','minecraft:chiseled_stone_bricks',('Больше сцены','Найди большую статую одной из героинь.','Больш за сцэну','Знайдзі вялікую статую адной з гераінь.','Larger Than the Stage','Discover a giant heroine statue.'))]
ru=json.loads((A/'lang/ru_ru.json').read_text());en=json.loads((A/'lang/en_us.json').read_text())
# Existing item names fall back to Russian; every new achievement is explicitly translated.
be=dict(ru)
be.update({'item.bocchi.'+key:value for key,value in {'mango_box_hat':'Скрынка з-пад манга','nijika_ahoge':'Доры-ахоге Нідзікі','stop_sign':'Дарожны знак STOP','pink_hood':'Ружовы спартыўны капюшон','pink_jacket':'Ружовая спартыўная куртка','pink_pants':'Ружовыя спартыўныя штаны','pink_shoes':'Ружовыя красоўкі'}.items()})
for id,icon,words in entries:
 for lang,offset in [(ru,0),(be,2),(en,4)]:
  lang['advancements.bocchi.'+id+'.title']=words[offset];lang['advancements.bocchi.'+id+'.description']=words[offset+1]
 display={'icon':{'id':icon},'title':{'translate':'advancements.bocchi.'+id+'.title'},'description':{'translate':'advancements.bocchi.'+id+'.description'},'frame':'challenge' if id in ('quartet','family_tree') else 'task','show_toast':True,'announce_to_chat':True,'hidden':False}
 criteria={'done':{'trigger':'minecraft:impossible'}}
 if id=='root':criteria={'done':{'trigger':'minecraft:inventory_changed','conditions':{'items':[{'items':'#bocchi:creative_content'}]}}};display['background']='minecraft:textures/block/pink_concrete.png'
 if id=='quartet':criteria={kind:{'trigger':'minecraft:impossible'} for kind in ['bocchi','nijika','ryo','kita']}
 if id=='statue':criteria={'done':{'trigger':'minecraft:location','conditions':{'player':[{'condition':'minecraft:entity_properties','entity':'this','predicate':{'location':{'structures':'bocchi:heroine_statue'}}}]}}}
 obj={'display':display,'criteria':criteria,'requirements':[[key] for key in criteria]}
 if id!='root':obj['parent']='bocchi:'+({'quartet':'first_friend','new_generation':'first_friend','mixed_duet':'new_generation','family_tree':'mixed_duet'}.get(id,'root'))
 js(D/f'advancement/{id}.json',obj)
for lang,name in [(ru,'ru_ru'),(be,'be_by'),(en,'en_us')]:
 lang['item.bocchi.rehearsal_bell']={'ru_ru':'Колокольчик репетиции','be_by':'Званочак рэпетыцыі','en_us':'Rehearsal Bell'}[name]
 js(A/f'lang/{name}.json',lang)
recipes=sorted((D/'recipe').glob('*.json'))
js(D/'tags/item/creative_content.json',{'values':[json.loads(p.read_text())['result']['id'] for p in recipes]})
js(D/'advancement/recipes/welcome.json',{'criteria':{'join':{'trigger':'minecraft:tick'}},'rewards':{'recipes':['bocchi:'+p.stem for p in recipes]}})
# Minimal standard big-endian NBT encoder, with deterministic gzip output.
def string(s):b=s.encode();return struct.pack('>H',len(b))+b
def payload(t,v):
 if t==3:return struct.pack('>i',v)
 if t==8:return string(v)
 if t==9:
  sub,items=v;return bytes([sub])+struct.pack('>i',len(items))+b''.join(payload(sub,x) for x in items)
 if t==10:return b''.join(bytes([typ])+string(key)+payload(typ,value) for key,(typ,value) in v.items())+b'\0'
 raise ValueError(t)
for kind in ['bocchi','nijika','ryo','kita']:
 blocks={};hair=f'bocchi:{kind}_base_matte';skin='minecraft:white_terracotta';black='minecraft:black_concrete';white='minecraft:white_concrete'
 def fill(x0,y0,z0,x1,y1,z1,mat):
  for x in range(x0,x1+1):
   for y in range(y0,y1+1):
    for z in range(z0,z1+1):blocks[x,y,z]=mat
 # Compact chibi proportions: short shoes/legs, shaped torso, shallow head.
 fill(0,0,0,10,0,10,'minecraft:stone_bricks');fill(1,1,1,9,1,9,'minecraft:smooth_stone')
 fill(3,2,3,4,2,6,black);fill(6,2,3,7,2,6,black)
 fill(3,3,4,4,4,6,hair if kind=='bocchi' else skin);fill(6,3,4,7,4,6,hair if kind=='bocchi' else skin)
 fill(3,5,3,7,7,7,hair if kind=='bocchi' else white)
 fill(4,8,4,6,8,6,hair if kind=='bocchi' else white)
 if kind!='bocchi':
  fill(3,5,3,7,5,7,black);fill(5,7,2,5,8,2,hair)
 else:
  fill(5,5,2,5,7,2,white);fill(3,6,2,4,6,2,'bocchi:bocchi_light_matte');fill(6,6,2,7,6,2,'bocchi:bocchi_light_matte')
 fill(2,7,4,2,8,6,hair if kind=='bocchi' else white);fill(8,7,4,8,8,6,hair if kind=='bocchi' else white)
 fill(2,5,4,2,6,5,skin);fill(8,5,4,8,6,5,skin)
 fill(2,9,2,8,13,7,skin)
 # Hair cap and stepped silhouette instead of a tall rectangular curtain.
 fill(2,14,2,8,14,8,hair);fill(3,15,3,7,15,7,hair)
 fill(1,10,3,2,13,8,hair);fill(8,10,3,9,13,8,hair)
 fill(2,8,7,8,13,8,hair)
 fill(2,12,1,3,13,2,hair);fill(4,13,1,6,13,2,hair);fill(7,12,1,8,13,2,hair)
 fill(3,9,1,7,11,1,skin)
 fill(3,10,1,3,11,1,white);fill(7,10,1,7,11,1,white)
 fill(3,10,1,3,10,1,black);fill(7,10,1,7,10,1,black)
 fill(5,9,1,5,9,1,'minecraft:pink_terracotta')
 if kind=='nijika':
  fill(5,16,5,6,16,5,hair);fill(6,17,5,6,17,5,hair)
  fill(9,7,5,10,12,7,hair);fill(9,6,6,9,6,7,hair)
  fill(9,12,4,10,13,5,'minecraft:red_concrete')
 if kind=='bocchi':
  fill(8,12,1,9,13,2,'minecraft:light_blue_concrete');fill(8,10,1,9,11,2,'minecraft:yellow_concrete')
  fill(2,7,7,3,9,8,hair);fill(7,7,7,8,9,8,hair)
 if kind=='ryo':fill(1,11,2,2,11,2,white)
 if kind=='kita':
  fill(1,7,6,2,9,7,hair);fill(8,7,6,9,9,7,hair)
  fill(2,6,7,3,7,8,hair);fill(7,6,7,8,7,8,hair)
 for x,z in [(1,1),(9,1),(1,9),(9,9)]:blocks[x,2,z]=f'bocchi:{kind}_base_lamp'
 palette=sorted(set(blocks.values()));states={name:i for i,name in enumerate(palette)}
 nbt={'DataVersion':(3,3955),'size':(9,(3,[11,18,11])),'palette':(9,(10,[{'Name':(8,name)} for name in palette])),'blocks':(9,(10,[{'pos':(9,(3,list(pos))),'state':(3,states[mat])} for pos,mat in sorted(blocks.items())])),'entities':(9,(10,[]))}
 path=D/f'structure/statues/{kind}.nbt';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(gzip.compress(b'\x0a\0\0'+payload(10,nbt),mtime=0))
js(D/'worldgen/template_pool/statues.json',{'name':'bocchi:statues','fallback':'minecraft:empty','elements':[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':'bocchi:statues/'+kind,'processors':'minecraft:empty','projection':'rigid'}} for kind in ['bocchi','nijika','ryo','kita']]})
js(D/'worldgen/structure/heroine_statue.json',{'type':'minecraft:jigsaw','biomes':'#bocchi:has_statue','step':'surface_structures','spawn_overrides':{},'terrain_adaptation':'beard_thin','start_pool':'bocchi:statues','size':0,'start_height':{'absolute':0},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':32,'use_expansion_hack':False})
js(D/'worldgen/structure_set/heroine_statues.json',{'structures':[{'structure':'bocchi:heroine_statue','weight':1}],'placement':{'type':'minecraft:random_spread','spacing':48,'separation':16,'salt':2374018}})
js(D/'tags/worldgen/biome/has_statue.json',{'values':['minecraft:plains','minecraft:sunflower_plains','minecraft:meadow','minecraft:birch_forest']})
print('Expansion: 10 advancements x 3 languages, 4 statue templates, 64 recipes.')

from standardize_names import standardize
standardize()
