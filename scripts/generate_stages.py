"""Author compact concert buildings with three permanent population variants.
No borrowed images: vanilla blocks + existing BTR models. Deterministic NBT.
"""
from pathlib import Path
import json
from structure_nbt import write
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'src/main/resources/data/bocchi'
KINDS=['bocchi','nijika','ryo','kita']
SIZES={'starry':(19,10,21),'school':(23,12,27),'indie':(19,10,23)}
def js(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def build(style,population):
 w,h,d=SIZES[style];blocks={};extra={}
 def put(x,y,z,name,**props):blocks[x,y,z]=(name,tuple(sorted(props.items())))
 def fill(x0,y0,z0,x1,y1,z1,name,**props):
  for x in range(x0,x1+1):
   for y in range(y0,y1+1):
    for z in range(z0,z1+1):put(x,y,z,name,**props)
 # Explicit air clears a usable interior; terrain is adapted underneath by jigsaw.
 fill(0,0,0,w-1,h-1,d-1,'minecraft:air')
 fill(0,0,0,w-1,0,d-1,'minecraft:stone_bricks')
 floor='minecraft:polished_andesite' if style=='starry' else 'minecraft:oak_planks'
 fill(1,0,1,w-2,0,d-2,floor)
 wall={'starry':'minecraft:deepslate_tiles','school':'minecraft:white_terracotta','indie':'minecraft:bricks'}[style]
 fill(0,1,0,w-1,h-2,0,wall);fill(0,1,d-1,w-1,h-2,d-1,wall)
 fill(0,1,1,0,h-2,d-2,wall);fill(w-1,1,1,w-1,h-2,d-2,wall)
 fill(0,h-1,0,w-1,h-1,d-1,'minecraft:deepslate_tiles')
 # Three-block entrance, overhead awning and a safe level approach.
 fill(w//2-1,1,0,w//2+1,3,0,'minecraft:air')
 fill(w//2-2,4,0,w//2+2,4,0,'minecraft:polished_blackstone')
 rear=d-5
 fill(2,1,rear-2,w-3,1,d-2,'minecraft:dark_oak_planks')
 fill(w//2-1,1,rear-3,w//2+1,1,rear-3,'minecraft:dark_oak_stairs',facing='south',half='bottom',shape='straight',waterlogged='false')
 # Tall curtains and a proper rig leave sightlines across the whole stage.
 curtain='minecraft:red_wool' if style=='school' else 'minecraft:black_wool'
 fill(1,2,d-2,2,h-3,d-2,curtain);fill(w-3,2,d-2,w-2,h-3,d-2,curtain)
 fill(2,h-3,rear-2,w-3,h-3,rear-2,'minecraft:polished_blackstone')
 for i,kind in enumerate(KINDS):
  x=3+i*(w-7)//3
  put(x,h-4,rear-2,'minecraft:sea_lantern')
  put(x,h-5,rear-2,'minecraft:'+['pink','yellow','blue','red'][i]+'_stained_glass')
  # Accent columns use all four heroines' colours.
  fill(x,2,d-1,x,h-4,d-1,'bocchi:'+kind+'_dark_matte')
 # Equipment and actor spots never occupy the same block.
 instruments=[('guitar_stand',4,rear-1),('drum_kit',w//2,rear+1),('guitar_stand',w-5,rear-1),('microphone',w//2+3,rear-2)]
 actors=[(4,rear),(w//2,rear+2),(w-5,rear),(w//2+3,rear-1)]
 for name,x,z in instruments:put(x,2,z,'bocchi:'+name)
 for x in (2,w-3):
  put(x,2,rear-2,'bocchi:speaker');put(x,2,rear+1,'bocchi:amplifier')
 put(3,2,d-3,'bocchi:guitar_case');put(w-4,2,d-3,'bocchi:bocchi_box')
 # Back wall signage has a full supporting block behind it.
 if style=='starry':
  put(w//2,4,d-2,'bocchi:starry_sign')
  put(w//2,6,d-2,'bocchi:starry_neon_star',facing='north')
 else:put(w//2,5,d-2,'bocchi:festival_poster' if style=='school' else 'bocchi:indie_poster',facing='north')
 for z in (4,8,rear-4):
  put(1,3,z,'bocchi:kessoku_poster' if style=='starry' else 'bocchi:indie_poster',facing='east')
  put(w-2,3,z,'bocchi:festival_poster',facing='west')
 # Ceiling fairy lights, side benches and a small bar / backstage storage.
 for x in range(3,w-3,3):
  for z in (5,rear-4):put(x,h-2,z,'bocchi:fairy_lights',facing='down')
 for z in range(4,rear-4,3):
  for x,facing in [(2,'east'),(w-3,'west')]:put(x,1,z,'minecraft:spruce_stairs',facing=facing,half='bottom',shape='straight',waterlogged='false')
 fill(2,1,2,5,1,2,'minecraft:spruce_planks')
 put(2,2,2,'bocchi:jimihen_plush');put(4,2,2,'bocchi:mini_slime_plush')
 chest=(w-3,1,2);put(*chest,'minecraft:chest',facing='west',type='single',waterlogged='false')
 extra[chest]={'id':(8,'minecraft:chest'),'LootTable':(8,'bocchi:chests/stage_backstage')}
 if style=='school':
  # Gym floor lines and high windows distinguish it from a club.
  for x in (5,w-6):
   for z in range(2,rear-3):put(x,0,z,'minecraft:white_concrete')
  for z in range(4,rear,4):
   fill(0,6,z,0,8,z+1,'minecraft:light_blue_stained_glass')
   fill(w-1,6,z,w-1,8,z+1,'minecraft:light_blue_stained_glass')
  for x in range(2,w-2):put(x,0,3,'minecraft:white_concrete')
 elif style=='indie':
  for x in range(3,w-3):
   for z in range(4,rear-3):put(x,0,z,'minecraft:white_concrete' if (x+z)%2 else 'minecraft:black_concrete')
  for x in (2,w-3):fill(x,2,1,x,h-2,1,'minecraft:iron_bars',north='false',east='false',south='false',west='false',waterlogged='false')
 else:
  # Low ceiling, warm entrance and side stripe evoke a compact live house.
  for x in (1,w-2):put(x,3,1,'minecraft:ochre_froglight',axis='y')
  fill(1,1,1,1,1,rear-4,'minecraft:yellow_terracotta')
 entities=[]
 for kind,(x,z) in zip(KINDS,actors):
  form='chibi' if population=='chibi' or (population=='mixed' and kind in ['bocchi','kita']) else 'plush'
  nbt={'id':(8,'bocchi:'+kind+'_'+form),'Pos':(9,(6,[x+.5,2.,z+.5])),
       'Rotation':(9,(5,[180.,0.])), 'PersistenceRequired':(1,1),'Silent':(1,1),'Invisible':(1,1),'BtrStagePerformer':(1,1)}
  entities.append({'pos':(9,(6,[x+.5,2.,z+.5])),'blockPos':(9,(3,[x,2,z])),'nbt':(10,nbt)})
 palette=sorted(set(blocks.values()));indices={state:i for i,state in enumerate(palette)}
 entries=[]
 for pos,state in sorted(blocks.items()):
  entry={'pos':(9,(3,list(pos))),'state':(3,indices[state])}
  if pos in extra:entry['nbt']=(10,extra[pos])
  entries.append(entry)
 states=[]
 for name,props in palette:
  entry={'Name':(8,name)}
  if props:entry['Properties']=(10,{key:(8,value) for key,value in props})
  states.append(entry)
 write(D/f'structure/stages/{style}_{population}.nbt',{'DataVersion':(3,3955),'size':(9,(3,[w,h,d])),
       'palette':(9,(10,states)),'blocks':(9,(10,entries)),'entities':(9,(10,entities))})

for style in SIZES:
 for population in ['chibi','tsum','mixed']:build(style,population)
 js(D/f'worldgen/template_pool/stages/{style}.json',{'name':'bocchi:stages/'+style,'fallback':'minecraft:empty',
    'elements':[{'weight':weight,'element':{'element_type':'minecraft:single_pool_element','location':f'bocchi:stages/{style}_{population}',
    'processors':'minecraft:empty','projection':'rigid'}} for population,weight in [('chibi',4),('tsum',3),('mixed',1)]]})
 js(D/f'worldgen/structure/{style}_stage.json',{'type':'minecraft:jigsaw','biomes':'#bocchi:has_stage',
    'step':'surface_structures','spawn_overrides':{},'terrain_adaptation':'beard_thin','start_pool':'bocchi:stages/'+style,
    'size':0,'start_height':{'absolute':0},'project_start_to_heightmap':'WORLD_SURFACE_WG','max_distance_from_center':48,'use_expansion_hack':False})
js(D/'worldgen/structure_set/stages.json',{'structures':[{'structure':f'bocchi:{style}_stage','weight':1} for style in SIZES],
   'placement':{'type':'minecraft:random_spread','spacing':36,'separation':12,'salt':2374029}})
js(D/'tags/worldgen/biome/has_stage.json',{'values':['minecraft:plains','minecraft:sunflower_plains','minecraft:meadow','minecraft:birch_forest']})
js(D/'loot_table/chests/stage_backstage.json',{'type':'minecraft:chest','pools':[
 {'rolls':{'type':'minecraft:uniform','min':4,'max':7},'entries':[{'type':'minecraft:item','name':name,'weight':weight,
 'functions':[{'function':'minecraft:set_count','count':{'type':'minecraft:uniform','min':1,'max':count}}]}
 for name,weight,count in [('minecraft:cookie',6,8),('minecraft:wheat',6,8),('minecraft:glow_berries',6,8),('minecraft:cake',3,1),('bocchi:rehearsal_bell',1,1),('bocchi:mango_box_hat',1,1)]]}]})
print('Generated 9 stage templates, 3 locatable structures and backstage loot.')
