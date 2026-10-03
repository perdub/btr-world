package dev.aliska.bocchi;
import eu.pb4.polymer.core.api.entity.PolymerEntity;
import dev.aliska.bocchi.mixin.ItemDisplayAccessor;
import net.minecraft.entity.*;
import net.minecraft.entity.ai.goal.*;
import net.minecraft.entity.passive.*;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.decoration.DisplayEntity;
import net.minecraft.entity.effect.*;
import net.minecraft.client.render.model.json.ModelTransformationMode;
import net.minecraft.item.*;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.text.Text;
import net.minecraft.util.*;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.*;
import net.minecraft.block.Blocks;
import net.minecraft.sound.SoundEvent;
import net.minecraft.sound.SoundEvents;

public class CompanionEntity extends WolfEntity implements PolymerEntity {
 private int hidingTicks, grassTicks;
 public CompanionEntity(EntityType<? extends WolfEntity> type, World world) {
  super(type, world);
  setInvisible(true); setSilent(true); setPersistent();
 }
 public CharacterKind kind() { return BocchiMod.KINDS.getOrDefault(getType(), CharacterKind.BOCCHI); }
 public boolean plush() { return BocchiMod.PLUSH_TYPES.contains(getType()); }
 @Override protected void initGoals() {
  goalSelector.add(0,new SwimGoal(this));
  goalSelector.add(1,new SitGoal(this));
  goalSelector.add(2,new FollowOwnerGoal(this,1.1,3.0F,1.5F));
  goalSelector.add(3,new WanderAroundFarGoal(this,0.65));
  goalSelector.add(4,new LookAtEntityGoal(this,PlayerEntity.class,6.0F));
  goalSelector.add(5,new LookAroundGoal(this));
 }
 @Override public EntityType<?> getPolymerEntityType(ServerPlayerEntity player) { return EntityType.WOLF; }
 @Override public ActionResult interactMob(PlayerEntity player, Hand hand) {
  ItemStack held = player.getStackInHand(hand);
  if (getWorld().isClient) return ActionResult.SUCCESS;
  if (!isTamed() && held.isOf(kind().treat)) {
   consume(player,held); setOwner(player); setSitting(false); heal(getMaxHealth());
   getWorld().sendEntityStatus(this,(byte)7);
   player.sendMessage(Text.literal(kind().name+": теперь пойдём вместе! 💛"),true);
   return ActionResult.SUCCESS;
  }
  if (isOwner(player)) {
   if (kind()==CharacterKind.RYO && held.isOf(Items.EMERALD)) {
    consume(player,held);
    Item item = BocchiMod.FIGURINES.get(CharacterKind.values()[random.nextInt(4)]);
    if(!player.giveItemStack(new ItemStack(item))) player.dropItem(new ItemStack(item),false);
    player.sendMessage(Text.literal("Рё: фигурка за изумруд. Никаких возвратов."),true);
    return ActionResult.SUCCESS;
   }
   if (held.isOf(kind().treat)) { consume(player,held); heal(6); getWorld().sendEntityStatus(this,(byte)7); return ActionResult.SUCCESS; }
   if (held.isEmpty()) {
    setSitting(!isSitting()); navigation.stop();
    player.sendMessage(Text.literal(kind().name+(isSitting()?": подожду здесь.":": иду за Алиской!")),true);
    return ActionResult.SUCCESS;
   }
  }
  // Keep name tags and leads, but prevent vanilla bone taming or another player's commands.
  if (held.isOf(Items.NAME_TAG) || held.isOf(Items.LEAD)) return super.interactMob(player,hand);
  return ActionResult.PASS;
 }
 private void consume(PlayerEntity player, ItemStack stack) { if(!player.getAbilities().creativeMode) stack.decrement(1); }
 @Override public boolean isBreedingItem(ItemStack stack) { return false; }
 @Override public WolfEntity createChild(ServerWorld world, PassiveEntity entity) { return null; }
 @Override protected SoundEvent getAmbientSound() { return null; }
 @Override public void tick() {
  super.tick();
  if (!(getWorld() instanceof ServerWorld world) || !isAlive()) return;
  setInvisible(true);
  if(hidingTicks>0) { hidingTicks--; navigation.stop(); }
  if(grassTicks>0) { grassTicks--; navigation.stop(); }
  if(kind()==CharacterKind.BOCCHI && age%20==0) {
   boolean danger=!world.getEntitiesByClass(HostileEntity.class,getBoundingBox().expand(5),Entity::isAlive).isEmpty();
   if(danger) hidingTicks=40;
  }
  if(kind()==CharacterKind.RYO && !isSitting() && hidingTicks==0 && age%20==0) eatGrass(world);
  if(kind()==CharacterKind.KITA && age%10==0) {
   world.spawnParticles(ParticleTypes.END_ROD,getX(),getY()+0.7,getZ(),2,0.3,0.2,0.3,0.01);
   if(isTamed() && getOwner()!=null && distanceTo(getOwner())<8 && age%40==0)
    getOwner().addStatusEffect(new StatusEffectInstance(StatusEffects.NIGHT_VISION,240,0,true,false,true));
  }
  if(kind()==CharacterKind.NIJIKA && isTamed() && !isSitting() && age%200==0 && getOwner()!=null && distanceTo(getOwner())<8) {
   getOwner().addStatusEffect(new StatusEffectInstance(StatusEffects.HASTE,100,0,true,false,true));
   world.spawnParticles(ParticleTypes.NOTE,getX(),getY()+0.9,getZ(),1,0,0,0,0);
   world.playSound(null,getBlockPos(),SoundEvents.BLOCK_NOTE_BLOCK_SNARE.value(),net.minecraft.sound.SoundCategory.NEUTRAL,0.2F,1.2F);
  }
  updateVisual(world);
 }
 private void eatGrass(ServerWorld world) {
  BlockPos pos=getBlockPos();
  if(world.getBlockState(pos).isOf(Blocks.SHORT_GRASS)) {
   if(world.getGameRules().getBoolean(GameRules.DO_MOB_GRIEFING)) world.breakBlock(pos,false,this);
   grassTicks=30; heal(1);
   world.spawnParticles(ParticleTypes.HAPPY_VILLAGER,getX(),getY()+0.4,getZ(),3,0.2,0.1,0.2,0);
  } else if(world.getBlockState(pos.down()).isOf(Blocks.GRASS_BLOCK) && age%100==0) {
   if(world.getGameRules().getBoolean(GameRules.DO_MOB_GRIEFING)) world.setBlockState(pos.down(),Blocks.DIRT.getDefaultState());
   grassTicks=30; heal(1);
  }
 }
 private void updateVisual(ServerWorld world) {
  DisplayEntity.ItemDisplayEntity display=null;
  for(Entity passenger:getPassengerList()) if(passenger instanceof DisplayEntity.ItemDisplayEntity item) { display=item; break; }
  if(display==null) {
   display=new DisplayEntity.ItemDisplayEntity(EntityType.ITEM_DISPLAY,world);
   display.setPosition(getPos());
   display.addCommandTag("bocchi_companion_visual");
   ((ItemDisplayAccessor)display).bocchi$setMode(ModelTransformationMode.NONE);
   world.spawnEntity(display); display.startRiding(this,true);
  }
  Item visual=hidingTicks>0?BocchiMod.BOX_MODEL:BocchiMod.MODELS.get(kind().id+(plush()?"_plush":"_chibi"));
  if (!((ItemDisplayAccessor)display).bocchi$getItemStack().isOf(visual)) ((ItemDisplayAccessor)display).bocchi$setItemStack(new ItemStack(visual));
  display.setYaw(getYaw()); display.setPitch(grassTicks>0?20:0);
  display.setGlowing(kind()==CharacterKind.KITA);
 }
 @Override protected void updatePassengerPosition(Entity passenger, Entity.PositionUpdater updater) {
  if(passenger instanceof DisplayEntity.ItemDisplayEntity) updater.accept(passenger,getX(),getY(),getZ());
  else super.updatePassengerPosition(passenger,updater);
 }
 @Override public void remove(RemovalReason reason) {
  // Passengers remain saved with their parent on chunk unload; discard only on actual destruction.
  if(reason.shouldDestroy()) for(Entity passenger:getPassengerList()) passenger.discard();
  super.remove(reason);
 }
 @Override public void writeCustomDataToNbt(NbtCompound nbt) { super.writeCustomDataToNbt(nbt); nbt.putInt("BocchiHiding",hidingTicks); }
 @Override public void readCustomDataFromNbt(NbtCompound nbt) { super.readCustomDataFromNbt(nbt); hidingTicks=nbt.getInt("BocchiHiding"); setInvisible(true); setSilent(true); }
}
