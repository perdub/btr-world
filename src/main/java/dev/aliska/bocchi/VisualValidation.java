package dev.aliska.bocchi;
import dev.aliska.bocchi.mixin.DisplayAccessor;
import dev.aliska.bocchi.mixin.ItemDisplayAccessor;
import eu.pb4.polymer.common.api.PolymerCommonUtils;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.passive.WolfEntity;
import net.minecraft.entity.decoration.DisplayEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.client.render.model.json.ModelTransformationMode;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.nbt.NbtElement;
import net.minecraft.util.math.AffineTransformation;
import org.joml.Vector3f;
import org.joml.Quaternionf;
final class VisualValidation {
 static void run() {
  int checked=0;
  for(var entry:BocchiMod.BLOCKS.entrySet()) for(var state:entry.getValue().getStateManager().getStates()) {
   try {
    state.initShapeCache();
    if(((eu.pb4.polymer.blocks.api.PolymerTexturedBlock)entry.getValue()).getPolymerBlockState(state)==null) throw new IllegalStateException("Null client state");
    checked++;
   } catch(Exception error) { throw new IllegalStateException("Invalid Polymer mapping: bocchi:"+entry.getKey()+" "+state,error); }
  }
  org.slf4j.LoggerFactory.getLogger("bocchi").info("Validated {} Polymer block states including collision caches.",checked);
  if(BocchiMod.MODELS.size()!=40) throw new IllegalStateException("Expected 8 neutral and 32 expression models");
  var world=PolymerCommonUtils.getFakeWorld();
  var seat=new net.minecraft.entity.decoration.ArmorStandEntity(net.minecraft.entity.EntityType.ARMOR_STAND,world);
  BoxSeats.configure(seat);
  if (!seat.isMarker() || !seat.isInvisible() || !seat.hasNoGravity() || !seat.isInvulnerable()) throw new IllegalStateException("Box seat configuration failed");
  var display=new DisplayEntity.ItemDisplayEntity(EntityType.ITEM_DISPLAY,world);
  var wolf=new WolfEntity(EntityType.WOLF,world);
  float offset=(float)(wolf.getPassengerRidingPos(display).y-wolf.getY());
  if(offset<=0 || offset>2) throw new IllegalStateException("Unexpected wolf mount height "+offset);
  ((DisplayAccessor)display).bocchi$setTransformation(new AffineTransformation(new Vector3f(0,-offset,0),new Quaternionf(),new Vector3f(1,1,1),new Quaternionf()));
  ((ItemDisplayAccessor)display).bocchi$setMode(ModelTransformationMode.NONE);
  for(var item:BocchiMod.MODELS.values()) {
   ((ItemDisplayAccessor)display).bocchi$setItemStack(new ItemStack(item));
   if(!((ItemDisplayAccessor)display).bocchi$getItemStack().isOf(item)) throw new IllegalStateException("Display expression swap failed");
  }
  var nbt=new NbtCompound();display.writeNbt(nbt);
  float saved=nbt.getCompound("transformation").getList("translation",NbtElement.FLOAT_TYPE).getFloat(1);
  if(Math.abs(offset+saved)>0.00001) throw new IllegalStateException("Mount correction is not synchronized/saved");
  var type=BocchiMod.KINDS.keySet().stream().filter(t->BocchiMod.KINDS.get(t)==CharacterKind.BOCCHI).findFirst().orElseThrow();
  var probe=(CompanionEntity)type.create(world);
  var familyNbt=new NbtCompound();probe.writeCustomDataToNbt(familyNbt);
  familyNbt.putIntArray("BtrGenes",new int[]{1,0,3});familyNbt.putInt("BtrGrowth",1200);familyNbt.putInt("BtrBreedCooldown",4000);
  probe.readCustomDataFromNbt(familyNbt);
  var savedFamily=new NbtCompound();probe.writeCustomDataToNbt(savedFamily);
  if(!java.util.Arrays.equals(savedFamily.getIntArray("BtrGenes"),new int[]{1,0,3}) || savedFamily.getInt("BtrGrowth")!=1200 || savedFamily.getInt("BtrBreedCooldown")!=4000) throw new IllegalStateException("Family data did not survive NBT round trip");
  try {
   var mod=net.fabricmc.loader.api.FabricLoader.getInstance().getModContainer("bocchi").orElseThrow();
   for(var kind:CharacterKind.values()) {
    var path=mod.findPath("data/bocchi/structure/statues/"+kind.id+".nbt").orElseThrow();
    var templateNbt=net.minecraft.nbt.NbtIo.readCompressed(path,net.minecraft.nbt.NbtSizeTracker.ofUnlimitedBytes());
    for(var tag:templateNbt.getList("palette",NbtElement.COMPOUND_TYPE)) {
     var name=net.minecraft.util.Identifier.of(((NbtCompound)tag).getString("Name"));
     if(!net.minecraft.registry.Registries.BLOCK.containsId(name)) throw new IllegalStateException("Unknown statue block "+name);
    }
    var template=new net.minecraft.structure.StructureTemplate();
    template.readNbt(net.minecraft.registry.Registries.BLOCK.getReadOnlyWrapper(),templateNbt);
    if(template.getSize().getY()!=18 || templateNbt.getList("blocks",NbtElement.COMPOUND_TYPE).size()<500) throw new IllegalStateException("Invalid statue template "+kind.id);
   }
  } catch(Exception e) { throw new IllegalStateException("Statue validation failed",e); }
  // Entity names belong to Entity NBT, not readCustomDataFromNbt. Use the full
  // serialization path so CustomName is loaded before companion migration.
  // These checks run in CI against Minecraft's actual NBT/block registries.
  var legacy=new NbtCompound();probe.writeNbt(legacy);
  legacy.putString("CustomName","{\"text\":\"Хитори · чиби\"}");
  probe.readNbt(legacy);
  if(probe.hasCustomName()) throw new IllegalStateException("Automatic legacy name was not migrated");
  legacy.putString("CustomName","{\"text\":\"Алискина подруга\"}");
  legacy.putBoolean("BtrStagePerformer",true);legacy.putIntArray("BtrStageHome",new int[]{4,65,9});
  probe.readNbt(legacy);
  var stageSave=new NbtCompound();probe.writeNbt(stageSave);
  if(!probe.getName().getString().equals("Алискина подруга") || !stageSave.getBoolean("BtrStagePerformer")
      || !java.util.Arrays.equals(stageSave.getIntArray("BtrStageHome"),new int[]{4,65,9})) throw new IllegalStateException("Stage/name persistence failed: name="+probe.getName().getString()+", stage="+stageSave.getBoolean("BtrStagePerformer")+", home="+java.util.Arrays.toString(stageSave.getIntArray("BtrStageHome")));
  try {
   var mod=net.fabricmc.loader.api.FabricLoader.getInstance().getModContainer("bocchi").orElseThrow();
   for(String style:new String[]{"starry","school","indie"}) for(String population:new String[]{"chibi","tsum","mixed"}) {
    var path=mod.findPath("data/bocchi/structure/stages/"+style+"_"+population+".nbt").orElseThrow();
    var stage=net.minecraft.nbt.NbtIo.readCompressed(path,net.minecraft.nbt.NbtSizeTracker.ofUnlimitedBytes());
    for(var tag:stage.getList("palette",NbtElement.COMPOUND_TYPE)) {
     var stateNbt=(NbtCompound)tag;
     var id=net.minecraft.util.Identifier.of(stateNbt.getString("Name"));
     if(!net.minecraft.registry.Registries.BLOCK.containsId(id)) throw new IllegalStateException("Unknown stage block "+id);
     var block=net.minecraft.registry.Registries.BLOCK.get(id);
     var properties=stateNbt.getCompound("Properties");
     for(String key:properties.getKeys()) {
      var property=block.getStateManager().getProperty(key);
      if(property==null || property.parse(properties.getString(key)).isEmpty()) throw new IllegalStateException("Invalid stage block property "+id+" "+key);
     }
    }
    var template=new net.minecraft.structure.StructureTemplate();
    template.readNbt(net.minecraft.registry.Registries.BLOCK.getReadOnlyWrapper(),stage);
    if(stage.getList("entities",NbtElement.COMPOUND_TYPE).size()!=4) throw new IllegalStateException("Stage needs four live performers");
    for(var tag:stage.getList("entities",NbtElement.COMPOUND_TYPE)) {
     var mob=((NbtCompound)tag).getCompound("nbt");
     var id=net.minecraft.util.Identifier.of(mob.getString("id"));
     if(!net.minecraft.registry.Registries.ENTITY_TYPE.containsId(id)) throw new IllegalStateException("Unknown stage mob "+id);
     var actor=net.minecraft.registry.Registries.ENTITY_TYPE.get(id).create(world);
     if(!(actor instanceof CompanionEntity girl)) throw new IllegalStateException("Invalid stage mob "+id);
     girl.readCustomDataFromNbt(mob);
     var savedActor=new NbtCompound();girl.writeCustomDataToNbt(savedActor);
     if(!savedActor.getBoolean("BtrStagePerformer") || girl.hasCustomName()) throw new IllegalStateException("Invalid performer NBT "+id);
    }
   }
  } catch(Exception e) { throw new IllegalStateException("Stage validation failed",e); }
  org.slf4j.LoggerFactory.getLogger("bocchi").info("Validated 9 stage templates, 36 live performers and legacy name migration.");
  org.slf4j.LoggerFactory.getLogger("bocchi").info("Visual validation passed: 40 models, display invokers, mount correction {} blocks.",offset);
 }
}
