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
  if(BocchiMod.MODELS.size()!=40) throw new IllegalStateException("Expected 8 neutral and 32 expression models");
  var world=PolymerCommonUtils.getFakeWorld();
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
  org.slf4j.LoggerFactory.getLogger("bocchi").info("Visual validation passed: 40 models, display invokers, mount correction {} blocks.",offset);
 }
}
