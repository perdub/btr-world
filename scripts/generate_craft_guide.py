"""Generate the Russian crafting reference from the actual recipe JSON."""
from pathlib import Path
import json,collections
root=Path(__file__).resolve().parents[1];r=root/'src/main/resources';lang=json.loads((r/'assets/bocchi/lang/ru_ru.json').read_text())
vanilla=dict(zip('amethyst_shard black_dye blue_dye brown_dye clay_ball cookie glass_pane glow_ink_sac glowstone_dust gold_ingot gold_nugget golden_apple iron_ingot iron_nugget leather leather_boots leather_chestplate leather_helmet leather_leggings lime_wool note_block oak_planks oak_slab paper pink_dye pink_wool quartz red_dye redstone slime_ball smooth_stone stick string white_concrete white_dye white_wool yellow_dye'.split(),['осколок аметиста','чёрный краситель','синий краситель','коричневый краситель','комок глины','печенье','стеклянная панель','светящийся чернильный мешок','светокаменная пыль','золотой слиток','кусочек золота','золотое яблоко','железный слиток','кусочек железа','кожа','кожаные ботинки','кожаная куртка','кожаный шлем','кожаные штаны','лаймовая шерсть','нотный блок','дубовые доски','дубовая плита','бумага','розовый краситель','розовая шерсть','кварц','красный краситель','редстоун','слизь','гладкий камень','палка','нить','белый бетон','белый краситель','белая шерсть','жёлтый краситель']))
def name(ident):
 ns,path=ident.split(':',1)
 return vanilla.get(path,ident) if ns=='minecraft' else lang.get('block.'+ns+'.'+path,lang.get('item.'+ns+'.'+path,ident))
groups=collections.defaultdict(list)
for f in sorted((r/'data/bocchi/recipe').glob('*.json')):
 o=json.loads(f.read_text());ident=f.stem
 group='Палитра блоков' if any(ident.endswith('_'+x) for x in ['matte','tile','lamp']) else 'Призыв спутниц' if ident.endswith('_summoner') else 'Фигурки и игрушки' if ident.endswith(('_figurine','_plush')) else 'Одежда и аксессуары' if ident in ['mango_box_hat','nijika_ahoge','stop_sign','pink_hood','pink_jacket','pink_pants','pink_shoes'] else 'Сцена и декор'
 if 'pattern' in o:
  pattern=' / '.join(row.replace(' ','·') for row in o['pattern']);count=collections.Counter(''.join(o['pattern']));ingredients=[]
  for symbol,value in o['key'].items():ingredients.append(f"{symbol} = {name(value['item'])} ×{count[symbol]}")
  how=f'`{pattern}`';parts='; '.join(ingredients)
 else:
  count=collections.Counter(i['item'] for i in o['ingredients']);how='Любой порядок';parts='; '.join(f'{name(i)} ×{n}' for i,n in count.items())
 groups[group].append(f"| {name(o['result']['id'])} (`{ident}`) | {how} | {parts} | {o['result'].get('count',1)} |")
lines=['<!-- CRAFT GUIDE -->','## Полный справочник крафтов','', 'Все рецепты выполняются на верстаке. В схеме строки отделены `/`, знак `·` означает пустую ячейку. Например, `PPP / PIP / PPP`: три доски сверху, доска–ингредиент–доска посередине и три доски снизу. Буквы указаны в колонке ингредиентов; количества относятся ко всему рецепту. «Любой порядок» — бесформенный рецепт, расположение не важно.','', 'Предметы имеют префикс `bocchi:`. Рецепты доступны в книге рецептов после входа; команда оператора `/recipe give @s *` открывает все рецепты. Для просмотра в JEI нужны клиентские JEI, BTR World и его зависимости.','']
for group in ['Призыв спутниц','Палитра блоков','Фигурки и игрушки','Сцена и декор','Одежда и аксессуары']:
 lines += ['### '+group,'','| Предмет / ID | Схема | Ингредиенты | Выход |','|---|---|---|---|',*groups[group],'']
p=root/'docs/CRAFTING.md';p.write_text('# Крафты BTR World\n\n'+'\n'.join(lines)+'\n')
readme=root/'README.md';base=readme.read_text().split('<!-- CRAFT GUIDE -->')[0].rstrip()
readme.write_text(base+'\n\n<!-- CRAFT GUIDE -->\n<details>\n<summary>Полный справочник всех 72 рецептов</summary>\n\n'+'\n'.join(lines[1:])+'\n</details>\n')
print(f'Craft guide: {sum(map(len,groups.values()))} recipes.')
