# BTR World 0.5.1

- Исправлена ложная ошибка `Stage/name persistence failed` в проверке CI: имя загружается и сохраняется через полный NBT сущности.
- При ошибке проверки выводятся фактические значения имени, сценического флага и координат.

# BTR World 0.5.0

- Три вида генерируемых концертных зданий: STARRY, школьный фестиваль, инди-клуб.
- Девять шаблонов с четырьмя живыми участницами: чиби, тсумы, смешанный квартет.
- Неприручённые сценические обитатели играют при зрителях, остаются возле сцены и становятся обычными питомцами после приручения.
- Разные инструменты могут играть одновременно; гитарные стойки резервируются раздельно.
- Единые имена RU/BE/EN, исправлено жёстко заданное русское имя предметного призыва.
- Исследование источников оформления, планировки и команды в docs.

# 0.4.2

- Коробка и ахоге теперь используют носимый клиентский предмет: доступны слот шлема и ПКМ.
- Обычное следование начинается дальше 32 блоков, заканчивается на 24; без телепортации.
- Мягкое устранение пересечений питомцев, включая сидящих; игрок не отталкивается.

# BTR World 0.4.1

- Fix null Polymer block mappings when shared model state pools are exhausted.
- Decorations try ordinary tripwire states when flat tripwire states are unavailable.
- Safe vanilla fallbacks prevent startup crashes; warnings identify each unavailable model.
- Validate all 80 states of 55 blocks, including collision caches, with normal and exhausted pools before world load.
- CI uses Modrinth Publish v2.5.2 with JSON file list and API readback verification.
