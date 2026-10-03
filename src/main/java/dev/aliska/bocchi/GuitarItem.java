package dev.aliska.bocchi;
import net.minecraft.item.*;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.entity.Entity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.*;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.sound.*;
import net.minecraft.util.math.Vec3d;
import net.minecraft.world.World;
public class GuitarItem extends ModelItem {
 public GuitarItem() { super("guitar",new Item.Settings().maxCount(1)); }
 @Override public TypedActionResult<ItemStack> use(World world,PlayerEntity player,Hand hand) {
  if(!world.isClient && !player.getItemCooldownManager().isCoolingDown(this)) {
   for(HostileEntity mob:world.getEntitiesByClass(HostileEntity.class,player.getBoundingBox().expand(4),Entity::isAlive)) {
    Vec3d direction=mob.getPos().subtract(player.getPos()).normalize();
    mob.addVelocity(direction.x*0.8,0.25,direction.z*0.8); mob.velocityModified=true;
   }
   world.playSound(null,player.getBlockPos(),SoundEvents.BLOCK_NOTE_BLOCK_GUITAR.value(),SoundCategory.PLAYERS,0.8F,1.2F);
   ((ServerWorld)world).spawnParticles(ParticleTypes.NOTE,player.getX(),player.getY()+1,player.getZ(),8,1,0.2,1,0);
   player.getItemCooldownManager().set(this,100);
  }
  return TypedActionResult.success(player.getStackInHand(hand));
 }
}
