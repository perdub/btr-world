package dev.aliska.bocchi;
import eu.pb4.polymer.core.api.entity.PolymerEntity;
import dev.aliska.bocchi.mixin.ItemDisplayAccessor;
import dev.aliska.bocchi.mixin.DisplayAccessor;
import net.minecraft.util.math.AffineTransformation;
import org.joml.Vector3f;
import org.joml.Quaternionf;
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
 private int hidingTicks, grassTicks, happyTicks, panicTicks;
 private java.util.UUID bandLeader;
 private float visualMountOffset = Float.NaN;
 public CompanionEntity(EntityType<? extends WolfEntity> type, World world) {
  super(type, world);
  setInvisible(true); setSilent(true); setPersistent();
 }
 public CharacterKind kind() { return BocchiMod.KINDS.getOrDefault(getType(), CharacterKind.BOCCHI); }
 public boolean plush() { return BocchiMod.PLUSH_TYPES.contains(getType()); }
 @Override protected void initGoals() {
  goalSelector.add(0,new SwimGoal(this));
  goalSelector.add(1,new SitGoal(this));
  goalSelector.add(2,new FleeEntityGoal<HostileEntity>(this,HostileEntity.class,7,1.15,1.4) {
   @Override public boolean canStart() { return kind()==CharacterKind.BOCCHI && panicTicks>0 && !isSitting() && super.canStart(); }
   @Override public boolean shouldContinue() { return panicTicks>0 && !isSitting() && super.shouldContinue(); }
  });
  goalSelector.add(3,new FollowBandGoal());
  goalSelector.add(3,new FollowOwnerGoal(this,1.1,3.0F,1.5F));
  goalSelector.add(4,new WanderAroundFarGoal(this,0.65));
  goalSelector.add(5,new LookAtEntityGoal(this,PlayerEntity.class,6.0F));
  goalSelector.add(6,new LookAroundGoal(this));
 }
 @Override public EntityType<?> getPolymerEntityType(ServerPlayerEntity player) { return EntityType.WOLF; }
 @Override public ActionResult interactMob(PlayerEntity player, Hand hand) {
  ItemStack held = player.getStackInHand(hand);
  if (getWorld().isClient) return ActionResult.SUCCESS;
  if (!isTamed() && held.isOf(kind().treat)) {
   happyTicks=100; consume(player,held); setOwner(player); setSitting(false); heal(getMaxHealth());
   getWorld().sendEntityStatus(this,(byte)7);
   player.sendMessage(Text.literal(kind().name+": теперь пойдём вместе! 💛"),true);
   return ActionResult.SUCCESS;
  }
  if (isOwner(player)) {
   if (kind()==CharacterKind.RYO && held.isOf(Items.EMERALD)) {
    happyTicks=60; consume(player,held);
    Item item = BocchiMod.FIGURINES.get(CharacterKind.values()[random.nextInt(4)]);
    if(!player.giveItemStack(new ItemStack(item))) player.dropItem(new ItemStack(item),false);
    player.sendMessage(Text.literal("Рё: фигурка за изумруд. Никаких возвратов."),true);
    return ActionResult.SUCCESS;
   }
   if (held.isOf(kind().treat)) { happyTicks=80; consume(player,held); heal(6); getWorld().sendEntityStatus(this,(byte)7); return ActionResult.SUCCESS; }
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
  if(happyTicks>0) happyTicks--;
  if(panicTicks>0 && --panicTicks==0) hidingTicks=60;
  if(hidingTicks>0) { hidingTicks--; navigation.stop(); }
  if(grassTicks>0) { grassTicks--; navigation.stop(); }
  if(kind()==CharacterKind.BOCCHI && age%20==0) {
   boolean danger=!world.getEntitiesByClass(HostileEntity.class,getBoundingBox().expand(5),Entity::isAlive).isEmpty();
   if(danger && !isSitting() && panicTicks==0 && hidingTicks==0) panicTicks=60;
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
  if(kind()==CharacterKind.NIJIKA && bandLeader!=null && !isSitting() && age%40==0) {
   Entity leader=world.getEntity(bandLeader);
   if(leader instanceof CompanionEntity bocchi && bocchi.kind()==CharacterKind.BOCCHI && bocchi.panicTicks>0 && squaredDistanceTo(bocchi)<36) {
    bocchi.panicTicks=Math.max(1,bocchi.panicTicks-10);
    world.spawnParticles(ParticleTypes.NOTE,getX(),getY()+.9,getZ(),1,0,0,0,0);
    world.playSound(null,getBlockPos(),SoundEvents.BLOCK_NOTE_BLOCK_SNARE.value(),net.minecraft.sound.SoundCategory.NEUTRAL,.15F,1.4F);
   }
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
   visualMountOffset=Float.NaN;
   display=new DisplayEntity.ItemDisplayEntity(EntityType.ITEM_DISPLAY,world);
   display.setPosition(getPos());
   display.addCommandTag("bocchi_companion_visual");
   ((ItemDisplayAccessor)display).bocchi$setMode(ModelTransformationMode.NONE);
   world.spawnEntity(display); display.startRiding(this,true);
  }
  // The client sees a vanilla wolf, whose mount attachment differs from this custom type.
  // Compensate its mount height in tracked display data (server positioning alone cannot do this).
  if(Float.isNaN(visualMountOffset)) {
   WolfEntity vanillaWolf=new WolfEntity(EntityType.WOLF,world);
   visualMountOffset=(float)(vanillaWolf.getPassengerRidingPos(display).y-vanillaWolf.getY());
   ((DisplayAccessor)display).bocchi$setTransformation(new AffineTransformation(
   new Vector3f(0,-visualMountOffset,0),new Quaternionf(),new Vector3f(1,1,1),new Quaternionf()));
  }
  String mood=hurtTime>0?"surprised":happyTicks>0?"happy":(grassTicks>0 || panicTicks>0)?"squint":isSitting()?"sleepy":"";
  String name=kind().id+(plush()?"_plush":"_chibi")+(mood.isEmpty()?"":"_"+mood);
  Item visual=hidingTicks>0?BocchiMod.BOX_MODEL:BocchiMod.MODELS.get(name);
  if (!((ItemDisplayAccessor)display).bocchi$getItemStack().isOf(visual)) ((ItemDisplayAccessor)display).bocchi$setItemStack(new ItemStack(visual));
  display.setYaw(getYaw()); display.setPitch(0);
  display.setGlowing(kind()==CharacterKind.KITA);
 }
 @Override protected void updatePassengerPosition(Entity passenger, Entity.PositionUpdater updater) {
  if(passenger instanceof DisplayEntity.ItemDisplayEntity) updater.accept(passenger,getX(),getY(),getZ());
  else super.updatePassengerPosition(passenger,updater);
 }
 // Natural encounters are a band; item summons still create only the requested girl.
 @Override public EntityData initialize(ServerWorldAccess access, LocalDifficulty difficulty, SpawnReason reason, EntityData data) {
  EntityData result=super.initialize(access,difficulty,reason,data);
  if(reason==SpawnReason.NATURAL && access instanceof ServerWorld world) {
   var members=new java.util.ArrayList<CompanionEntity>(); members.add(this);
   int offset=0;
   for(CharacterKind wanted:CharacterKind.values()) {
    if(wanted==kind()) continue;
    EntityType<?> type=BocchiMod.KINDS.keySet().stream().filter(t->BocchiMod.KINDS.get(t)==wanted && BocchiMod.PLUSH_TYPES.contains(t)==plush()).findFirst().orElseThrow();
    CompanionEntity friend=(CompanionEntity)type.create(world);
    if(friend==null) continue;
    boolean placed=false;
    int[][] spots={{2,0},{-2,0},{0,2},{0,-2},{2,2},{-2,-2}};
    for(int i=0;i<spots.length && !placed;i++) {
     int[] spot=spots[(i+offset)%spots.length];
     for(int dy:new int[]{0,1,-1}) {
      BlockPos pos=getBlockPos().add(spot[0],dy,spot[1]);
      friend.refreshPositionAndAngles(pos.getX()+.5,pos.getY(),pos.getZ()+.5,getYaw(),0);
      if(world.getBlockState(pos.down()).isSolidBlock(world,pos.down()) && world.isSpaceEmpty(friend) && !world.containsFluid(friend.getBoundingBox())) {
       if(world.spawnEntity(friend)) { members.add(friend); placed=true; } break;
      }
     }
    }
    offset++;
   }
   CompanionEntity leader=members.stream().filter(m->m.kind()==CharacterKind.BOCCHI).findFirst().orElse(this);
   for(CompanionEntity member:members) member.bandLeader=leader.getUuid();
  }
  return result;
 }
 private final class FollowBandGoal extends Goal {
  private CompanionEntity leader;
  private int repath;
  FollowBandGoal() { setControls(java.util.EnumSet.of(Control.MOVE)); }
  private CompanionEntity findLeader() {
   if(bandLeader==null || bandLeader.equals(getUuid()) || !(getWorld() instanceof ServerWorld world)) return null;
   Entity entity=world.getEntity(bandLeader);
   return entity instanceof CompanionEntity girl && girl.isAlive()?girl:null;
  }
  @Override public boolean canStart() {
   leader=findLeader();
   return !isTamed() && !isSitting() && grassTicks==0 && hidingTicks==0 && leader!=null && squaredDistanceTo(leader)>6.25 && squaredDistanceTo(leader)<1024;
  }
  @Override public boolean shouldContinue() {
   return !isTamed() && !isSitting() && grassTicks==0 && leader!=null && leader.isAlive() && squaredDistanceTo(leader)>3 && squaredDistanceTo(leader)<1024;
  }
  @Override public void start() { repath=0; }
  @Override public void tick() {
   if(--repath<=0) { repath=10; navigation.startMovingTo(leader,leader.panicTicks>0?1.25:.9); }
   getLookControl().lookAt(leader,20,20);
  }
  @Override public void stop() { navigation.stop(); leader=null; }
 }
 @Override public void remove(RemovalReason reason) {
  // Passengers remain saved with their parent on chunk unload; discard only on actual destruction.
  if(reason.shouldDestroy()) for(Entity passenger:getPassengerList()) passenger.discard();
  super.remove(reason);
 }
 @Override public void writeCustomDataToNbt(NbtCompound nbt) { super.writeCustomDataToNbt(nbt); nbt.putInt("BocchiHiding",hidingTicks); nbt.putInt("BocchiPanic",panicTicks); if(bandLeader!=null) nbt.putUuid("BocchiBandLeader",bandLeader); }
 @Override public void readCustomDataFromNbt(NbtCompound nbt) { super.readCustomDataFromNbt(nbt); hidingTicks=nbt.getInt("BocchiHiding"); panicTicks=nbt.getInt("BocchiPanic"); bandLeader=nbt.containsUuid("BocchiBandLeader")?nbt.getUuid("BocchiBandLeader"):null; setInvisible(true); setSilent(true); }
}
