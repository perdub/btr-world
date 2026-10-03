"""Checks references and 1.21.1 JSON constraints in the authored resource/data pack."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]/'src/main/resources';A=R/'assets/bocchi';D=R/'data/bocchi'
count=0
for p in R.rglob('*.json'):
 obj=json.loads(p.read_text()); count+=1
 if '/models/' in str(p):
  parent=obj.get('parent','')
  if parent.startswith('bocchi:'): assert (A/'models'/ (parent.split(':')[1]+'.json')).exists(),p
  for k,tex in obj.get('textures',{}).items():
   if tex.startswith('bocchi:'):
    sprite=tex.split(':',1)[1]
    assert (A/'textures'/(sprite+'.png')).exists(),(p,k)
    # Minecraft 1.21.1 blocks atlas scans block/ and item/ directories.
    # A PNG outside those folders can exist but still render as missing.
    assert sprite.startswith(('block/','item/')), (p,k,'texture outside block/item atlas',sprite)
  for e in obj.get('elements',[]):
   assert all(-16<=v<=32 for v in e['from']+e['to']),p
   assert all(a<b for a,b in zip(e['from'],e['to'])),p
   if 'rotation' in e:assert e['rotation']['angle'] in [-45,-22.5,0,22.5,45],p
   for face in e['faces'].values(): assert face['texture'][1:] in obj['textures'],p
 if '/recipe/' in str(p):
  assert 'id' in obj['result'] and 'item' not in obj['result'],p
  assert obj['result']['id'].startswith('bocchi:'),p
for p in (A/'blockstates').glob('*.json'):
 assert (D/'loot_table/blocks'/p.name).exists(),p
 assert (A/'models/item'/p.name).exists(),p
 assert (D/'recipe'/p.name).exists(),p
ru=json.loads((A/'lang/ru_ru.json').read_text());en=json.loads((A/'lang/en_us.json').read_text());assert ru.keys()==en.keys()
assert len(list((A/'blockstates').glob('*.json')))==47
assert len(list((D/'recipe').glob('*.json')))==56
print(f'PASS: {count} JSON files; texture/model references and atlas coverage, geometry, 47 block drops and 56 recipes.')
