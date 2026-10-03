package dev.aliska.bocchi;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.fabricmc.fabric.api.biome.v1.*;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import eu.pb4.polymer.core.api.entity.PolymerEntityUtils;
import eu.pb4.polymer.core.api.item.PolymerItemGroupUtils;
import eu.pb4.polymer.resourcepack.api.PolymerResourcePackUtils;
import net.minecraft.entity.*;
import net.minecraft.entity.passive.WolfEntity;
import net.minecraft.item.*;
import net.minecraft.block.*;
import net.minecraft.registry.*;
import net.minecraft.text.Text;
import net.minecraft.server.command.CommandManager;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.world.biome.BiomeKeys;
import java.util.*;
public class BocchiMod implements ModInitializer {
 public static final Map<EntityType<?>,CharacterKind> KINDS=new HashMap<>();
 public static final Set<EntityType<?>> PLUSH_TYPES=new HashSet<>();
 public static final Map<String,Item> MODELS=new HashMap<>();
 public static final Map<CharacterKind,Item> FIGURINES=new EnumMap<>(CharacterKind.class);
 public static final Map<String,Block> BLOCKS=new LinkedHashMap<>();
 public static final List<Item> ITEMS=new ArrayList<>();
 public static Item BOX_MODEL;
 public static Identifier id(String path) { return Identifier.of("bocchi",path); }
 public static <T extends Item> T item(String path,T item) { Registry.register(Registries.ITEM,id(path),item); ITEMS.add(item); return item; }
 @Override public void onInitialize() {
  PolymerResourcePackUtils.addModAssets("bocchi");
  PolymerResourcePackUtils.markAsRequired();
  BOX_MODEL=Registry.register(Registries.ITEM,id("hiding_box"),new ModelItem("hiding_box",new Item.Settings()));
  for(CharacterKind kind:CharacterKind.values()) {
   for(String form:List.of("plush","chibi")) {
    String name=kind.id+"_"+form;
    MODELS.put(name,Registry.register(Registries.ITEM,id(name+"_model"),new ModelItem(name,new Item.Settings())));
    for(String mood:List.of("happy","sleepy","surprised","squint")) {
     String variant=name+"_"+mood;
     MODELS.put(variant,Registry.register(Registries.ITEM,id(variant+"_model"),new ModelItem(variant,new Item.Settings())));
    }
    EntityType<CompanionEntity> type=Registry.register(Registries.ENTITY_TYPE,id(name),EntityType.Builder.create(CompanionEntity::new,SpawnGroup.CREATURE).dimensions(0.65F,0.75F).maxTrackingRange(8).build(null));
    KINDS.put(type,kind); if(form.equals("plush")) PLUSH_TYPES.add(type);
    FabricDefaultAttributeRegistry.register(type,WolfEntity.createWolfAttributes());
    PolymerEntityUtils.registerType(type);
    item(name+"_summoner",new CompanionSummoner(name+"_summoner",type));
    BiomeModifications.addSpawn(BiomeSelectors.includeByKey(BiomeKeys.PLAINS,BiomeKeys.FOREST,BiomeKeys.MEADOW),SpawnGroup.CREATURE,type,2,1,1);
   }
   for(String shade:List.of("light","base","dark")) for(String finish:List.of("matte","tile","lamp")) {
    String name=kind.id+"_"+shade+"_"+finish;
    PaletteBlock block=new PaletteBlock(name,AbstractBlock.Settings.create().strength(1.5F).luminance(state->finish.equals("lamp")?15:0));
    Registry.register(Registries.BLOCK,id(name),block); BLOCKS.put(name,block);
    item(name,new PaletteItem(name,block));
   }
   String name=kind.id+"_figurine";
   DecorationBlock block=new DecorationBlock(name); Registry.register(Registries.BLOCK,id(name),block); BLOCKS.put(name,block);
   FIGURINES.put(kind,item(name,new PaletteItem(name,block)));
  }
  for(String name:List.of("bocchi_box","amplifier","speaker","drum_kit","microphone","guitar_case","starry_sign")) {
   DecorationBlock block=new DecorationBlock(name); Registry.register(Registries.BLOCK,id(name),block); BLOCKS.put(name,block); item(name,new PaletteItem(name,block));
  }
  item("guitar",new GuitarItem());
  PolymerItemGroupUtils.registerPolymerItemGroup(id("little_stage"),PolymerItemGroupUtils.builder().displayName(Text.literal("BTR World")).icon(()->new ItemStack(FIGURINES.get(CharacterKind.NIJIKA))).entries((context,entries)->ITEMS.forEach(entries::add)).build());
  if (Boolean.getBoolean("bocchi.validateResources")) {
   VisualValidation.run();
   if (!PolymerItemGroupUtils.contains(id("little_stage")) || ITEMS.size() != 56) {
    throw new IllegalStateException("BTR World creative tab registration failed: " + ITEMS.size() + " player-facing entries");
   }
   org.slf4j.LoggerFactory.getLogger("bocchi").info("Creative tab BTR World registered with {} player-facing entries.", ITEMS.size());
   boolean built=PolymerResourcePackUtils.buildMain(java.nio.file.Path.of("polymer/bocchi-validation-pack.zip"));
   if(!built) throw new IllegalStateException("Bocchi resource pack validation failed");
   org.slf4j.LoggerFactory.getLogger("bocchi").info("Resource pack validation passed.");
  }
  org.slf4j.LoggerFactory.getLogger("bocchi").info("Little Stage registered: 8 companions, 47 blocks, 56 recipes.");
  CommandRegistrationCallback.EVENT.register((dispatcher,access,env)-> {
   dispatcher.register(CommandManager.literal("bocchi").then(CommandManager.literal("stage").requires(source->source.hasPermissionLevel(2)).executes(context-> {
    var player=context.getSource().getPlayerOrThrow(); ServerWorld world=player.getServerWorld();
    BlockPos origin=player.getBlockPos().add(0,0,3);
    // Never replace existing builds. The entire footprint must be air before placing anything.
    for(int x=-3;x<=3;x++) for(int z=0;z<=4;z++) for(int y=0;y<=3;y++) if(!world.getBlockState(origin.add(x,y,z)).isAir()) {
     context.getSource().sendError(Text.literal("Нужно свободное место 7×4×5 перед игроком (по оси +Z).")); return 0;
    }
    for(int x=-3;x<=3;x++) for(int z=0;z<=4;z++) world.setBlockState(origin.add(x,0,z),BLOCKS.get("ryo_dark_matte").getDefaultState());
    for(int x=-3;x<=3;x++) world.setBlockState(origin.add(x,1,4),BLOCKS.get("nijika_base_lamp").getDefaultState());
    world.setBlockState(origin.add(-2,1,2),BLOCKS.get("speaker").getDefaultState());
    world.setBlockState(origin.add(2,1,2),BLOCKS.get("amplifier").getDefaultState());
    world.setBlockState(origin.add(0,1,3),BLOCKS.get("drum_kit").getDefaultState());
    world.setBlockState(origin.add(0,1,1),BLOCKS.get("microphone").getDefaultState());
    world.setBlockState(origin.add(1,1,3),BLOCKS.get("starry_sign").getDefaultState());
    int x=-2; for(CharacterKind kind:CharacterKind.values()) world.setBlockState(origin.add(x++,1,0),BLOCKS.get(kind.id+"_figurine").getDefaultState());
    context.getSource().sendFeedback(()->Text.literal("Маленькая сцена готова!"),false); return 1;
   })));
  });
 }
}
