"""One localization policy for entities, summon tokens and hidden model items."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]/'src/main/resources/assets/bocchi/lang'
NAMES={'ru_ru':['Хитори Гото','Нидзика Идзити','Рё Ямада','Икуё Кита'],
       'be_by':['Хіторы Гота','Нідзіка Ідзіці','Ро Ямада','Ікуё Кіта'],
       'en_us':['Hitori Gotoh','Nijika Ijichi','Ryo Yamada','Ikuyo Kita']}
def standardize():
 for locale,names in NAMES.items():
  path=R/(locale+'.json');data=json.loads(path.read_text())
  forms={'ru_ru':['тсум','чиби'],'be_by':['тсум','чыбі'],'en_us':['Tsum','Chibi']}[locale]
  moods={'ru_ru':['радость','сон','удивление','зажмуренные глаза'],
         'be_by':['радасць','сон','здзіўленне','заплюшчаныя вочы'],
         'en_us':['Happy','Sleepy','Surprised','Squinting']}[locale]
  for kind,name in zip(['bocchi','nijika','ryo','kita'],names):
   for form,label in zip(['plush','chibi'],forms):
    stem=kind+'_'+form;title=name+' · '+label
    data['entity.bocchi.'+stem]=title
    data['item.bocchi.'+stem+'_summoner']={'ru_ru':'Позвать: ','be_by':'Паклікаць: ','en_us':'Summon: '}[locale]+title
    data['item.bocchi.'+stem+'_model']=title+' · '+{'ru_ru':'модель','be_by':'мадэль','en_us':'Model'}[locale]
    for mood,word in zip(['happy','sleepy','surprised','squint'],moods):data['item.bocchi.'+stem+'_'+mood+'_model']=title+' · '+word
   data['block.bocchi.'+kind+'_figurine']={'ru_ru':'Фигурка: ','be_by':'Фігурка: ','en_us':'Figurine: '}[locale]+name
  for mode,text in zip(['follow','close','roam'],{
    'ru_ru':['Следовать при удалении больше 32 блоков','Держаться рядом','Гулять в радиусе 16 блоков'],
    'be_by':['Ісці следам пры адлегласці больш за 32 блокі','Трымацца побач','Гуляць у радыусе 16 блокаў'],
    'en_us':['Follow beyond 32 blocks','Stay close','Roam within 16 blocks']}[locale]):data['message.bocchi.movement.'+mode]=text
  data['itemGroup.bocchi.little_stage']='BTR World'
  path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':standardize()
