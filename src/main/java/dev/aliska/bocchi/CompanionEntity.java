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
 private CompanionGenes genes;
 private int pairingTicks, breedingCooldown, growthTicks;
 private int courtshipTicks;
 private java.util.UUID courtshipMate;
 private float lastScale=-1;
 private int rehearsalCooldown;
 private boolean performing;
 private int movementMode;
 private boolean hummingMuted;
 private int hummingDelay=600,hummingStep=-1,hummingBeat;
 private static final int[][] HUMMING_NOTES={{12,14,16,14,12,9,12,12},{12,16,19,16,14,12,14,12},{0,3,5,3,0,7,5,0},{12,16,17,19,17,16,14,12}};
 public CompanionGenes genes() {
  if(genes==null) genes=new CompanionGenes(kind().ordinal(),kind().ordinal(),0);
  return genes;
 }
 public void recall() { setSitting(false);navigation.stop();happyTicks=40; }
 private boolean ready() { return isAlive()&&isTamed()&&growthTicks==0&&breedingCooldown==0&&pairingTicks>0&&panicTicks==0&&hidingTicks==0; }
 private boolean compatible(CompanionEntity other) { return other!=this&&other.ready()&&java.util.Objects.equals(getOwnerUuid(),other.getOwnerUuid()); }
 private CompanionEntity partner(ServerWorld world) {
  if(courtshipMate!=null) {
   Entity locked=world.getEntity(courtshipMate);
   if(locked instanceof CompanionEntity girl && compatible(girl) && squaredDistanceTo(girl)<64) return girl;
  }
  return world.getEntitiesByClass(CompanionEntity.class,getBoundingBox().expand(8),this::compatible).stream().min(java.util.Comparator.comparingDouble(this::squaredDistanceTo)).orElse(null);
 }

 private float visualMountOffset = Float.NaN;
 public CompanionEntity(EntityType<? extends WolfEntity> type, World world) {
  super(type, world);
  setInvisible(true); setSilent(true); setPersistent();
  hummingDelay=400+random.nextInt(800);
 }
 // Keep terrain collision, but companions must not shove players or each other.
 @Override public boolean isPushable() { return false; }
 @Override public void pushAwayFrom(Entity entity) {}
 private void ensureNoPushTeam(ServerWorld world) {
  var scoreboard=world.getScoreboard();
  String name=getNameForScoreboard();
  // Do not overwrite a team assigned by another mod or an administrator.
  if(scoreboard.getScoreHolderTeam(name)!=null) return;
  var team=scoreboard.getTeam("btr_pets");
  if(team==null) team=scoreboard.addTeam("btr_pets");
  team.setCollisionRule(net.minecraft.scoreboard.AbstractTeam.CollisionRule.NEVER);
  scoreboard.addScoreHolderToTeam(name,team);
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
  goalSelector.add(2,new Goal() {
   private CompanionEntity mate;
   { setControls(java.util.EnumSet.of(Control.MOVE,Control.LOOK)); }
   @Override public boolean canStart() { return ready() && getWorld() instanceof ServerWorld world && (mate=partner(world))!=null; }
   @Override public boolean shouldContinue() { return ready()&&mate!=null&&compatible(mate)&&squaredDistanceTo(mate)<100; }
   @Override public void tick() {
    faceMate(mate);
    if(squaredDistanceTo(mate)>.72) navigation.startMovingTo(mate,.8);
    else navigation.stop();
   }
   @Override public void stop() { mate=null;navigation.stop(); }
  });
  goalSelector.add(3,new RehearsalGoal());
  goalSelector.add(3,new FollowBandGoal());
  goalSelector.add(3,new FollowOwnerGoal(this,1.1,3.0F,1.5F) {
   @Override public boolean canStart() { return movementMode==0 && super.canStart(); }
   @Override public boolean shouldContinue() { return movementMode==0 && super.shouldContinue(); }
  });
  goalSelector.add(3,new FollowOwnerGoal(this,1.0,1.5F,.8F) {
   @Override public boolean canStart() { return movementMode==1 && super.canStart(); }
   @Override public boolean shouldContinue() { return movementMode==1 && super.shouldContinue(); }
  });
  goalSelector.add(3,new Goal() {
   private int delay;
   { setControls(java.util.EnumSet.of(Control.MOVE)); }
   @Override public boolean canStart() { return movementMode==2 && isTamed() && !isSitting() && getOwner()!=null && panicTicks==0 && hidingTicks==0 && pairingTicks==0; }
   @Override public boolean shouldContinue() { return canStart(); }
   @Override public void tick() {
    var owner=getOwner();if(owner==null)return;
    if(squaredDistanceTo(owner)>225) { navigation.startMovingTo(owner,1);return; }
    if(--delay<=0) {
     delay=80+random.nextInt(80);
     var target=net.minecraft.entity.ai.FuzzyTargeting.find(CompanionEntity.this,10,4);
     if(target!=null && target.squaredDistanceTo(owner.getPos())<225) navigation.startMovingTo(target.x,target.y,target.z,.65);
    }
   }
   @Override public void stop() { navigation.stop(); }
  });
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
   BtrAdvancements.grant(player,"first_friend");
   BtrAdvancements.grant(player,"quartet",kind().id);
   return ActionResult.SUCCESS;
  }
  if (isOwner(player)) {
   BtrAdvancements.grant(player,"first_friend");
   BtrAdvancements.grant(player,"quartet",kind().id);
   if(held.isOf(Items.STICK) && player.isSneaking()) {
    movementMode=(movementMode+1)%3;setSitting(false);navigation.stop();
    player.sendMessage(net.minecraft.text.Text.literal(new String[]{"Следовать за хозяином","Держаться рядом","Гулять в радиусе 16 блоков"}[movementMode]),false);
    return ActionResult.SUCCESS;
   }
   if(held.isOf(kind().treat) && growthTicks>0) {
    consume(player,held);heal(6);happyTicks=60;
    growthTicks=Math.max(0,growthTicks-Math.max(1,growthTicks/10));
    ((ServerWorld)getWorld()).spawnParticles(ParticleTypes.HAPPY_VILLAGER,getX(),getY()+.5,getZ(),5,.25,.2,.25,0);
    return ActionResult.SUCCESS;
   }
   if(held.isOf(kind().treat) && growthTicks==0 && breedingCooldown==0 && pairingTicks==0 && getHealth()>=getMaxHealth()) {
    consume(player,held);pairingTicks=600;setSitting(false);happyTicks=60;
    ((ServerWorld)getWorld()).spawnParticles(ParticleTypes.HEART,getX(),getY()+.8,getZ(),5,.3,.2,.3,0);
    return ActionResult.SUCCESS;
   }
   if (kind()==CharacterKind.RYO && held.isOf(Items.EMERALD)) {
    happyTicks=60; consume(player,held);
    BtrAdvancements.grant(player,"ryo_trade");
    Item item = BocchiMod.FIGURINES.get(CharacterKind.values()[random.nextInt(4)]);
    if(!player.giveItemStack(new ItemStack(item))) player.dropItem(new ItemStack(item),false);
    return ActionResult.SUCCESS;
   }
   if (held.isOf(kind().treat) && getHealth()<getMaxHealth()) { happyTicks=80; consume(player,held); heal(6); getWorld().sendEntityStatus(this,(byte)7); return ActionResult.SUCCESS; }
   if (held.isEmpty()) {
    if(player.isSneaking()) {
     hummingMuted=!hummingMuted;hummingStep=-1;hummingDelay=100;
     if(!hummingMuted) ((ServerWorld)getWorld()).spawnParticles(ParticleTypes.NOTE,getX(),getY()+.9,getZ(),1,0,0,0,0);
     return ActionResult.SUCCESS;
    }
    setSitting(!isSitting()); navigation.stop();
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
  if(age%20==0) ensureNoPushTeam(world);
  if(rehearsalCooldown>0) rehearsalCooldown--;
  if(breedingCooldown>0) breedingCooldown--;
  if(growthTicks>0) growthTicks--;
  if(pairingTicks>0) pairingTicks--;
  if(ready()) tryPair(world);
  else { courtshipTicks=0;courtshipMate=null; }
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
  if(age%4==0 && !isSitting() && pairingTicks==0) {
   for(var other:world.getEntitiesByClass(CompanionEntity.class,getBoundingBox().expand(.2),girl->girl!=this && girl.isAlive())) {
    double dx=getX()-other.getX(),dz=getZ()-other.getZ(),distance=dx*dx+dz*dz;
    if(distance>=.2025) continue;
    if(distance<.0001) { dx=getId()<other.getId()?1:-1;dz=0;distance=1; }
    double strength=.015/Math.sqrt(distance);
    addVelocity(dx*strength,0,dz*strength);
   }
  }
  tickHumming(world);
  updateVisual(world);
 }
 private void tickHumming(ServerWorld world) {
  boolean calm=!performing && !hummingMuted && panicTicks==0 && hidingTicks==0 && pairingTicks==0 && grassTicks==0
    && getHealth()>=getMaxHealth() && world.getClosestPlayer(this,8)!=null;
  if(!calm) { hummingStep=-1;hummingDelay=Math.max(hummingDelay,100);return; }
  if(hummingStep<0) {
   if(--hummingDelay>0) return;
   // Nearby band members take turns rather than playing over one another.
   if(!world.getEntitiesByClass(CompanionEntity.class,getBoundingBox().expand(8),girl->girl!=this && girl.hummingStep>=0).isEmpty()) {
    hummingDelay=100+random.nextInt(200);return;
   }
   hummingStep=0;hummingBeat=0;
  }
  if(hummingBeat-- >0) return;
  int note=HUMMING_NOTES[kind().ordinal()][hummingStep];
  SoundEvent instrument=switch(kind()) {
   case BOCCHI -> SoundEvents.BLOCK_NOTE_BLOCK_HARP.value();
   case NIJIKA -> SoundEvents.BLOCK_NOTE_BLOCK_BELL.value();
   case RYO -> SoundEvents.BLOCK_NOTE_BLOCK_BASS.value();
   case KITA -> SoundEvents.BLOCK_NOTE_BLOCK_FLUTE.value();
  };
  world.playSound(null,getX(),getY(),getZ(),instrument,net.minecraft.sound.SoundCategory.NEUTRAL,.12F,(float)Math.pow(2,(note-12)/12.0));
  world.spawnParticles(ParticleTypes.NOTE,getX(),getY()+.9,getZ(),0,note/24.0,0,0,1);
  hummingBeat=7;
  if(++hummingStep>=HUMMING_NOTES[kind().ordinal()].length) {
   hummingStep=-1;hummingDelay=800+random.nextInt(700);
  }
 }
 private void faceMate(CompanionEntity mate) {
  getLookControl().lookAt(mate,30,30);
  // The visible model rotates with the body, not the invisible wolf's head.
  float facing=(float)(Math.atan2(mate.getZ()-getZ(),mate.getX()-getX())*180/Math.PI)-90;
  setYaw(facing);setBodyYaw(facing);setHeadYaw(facing);
 }
 private void tryPair(ServerWorld world) {
  CompanionEntity mate=partner(world);
  if(mate==null) { courtshipTicks=0;courtshipMate=null;return; }
  if(getId()>mate.getId()) return;
  if(mate.courtshipMate!=null && !mate.courtshipMate.equals(getUuid())) {
   courtshipTicks=0;courtshipMate=null;return;
  }
  if(!mate.getUuid().equals(courtshipMate)) courtshipTicks=0;
  courtshipMate=mate.getUuid();mate.courtshipMate=getUuid();
  if(squaredDistanceTo(mate)>1 || !canSee(mate)) { courtshipTicks=0;return; }
  faceMate(mate);mate.faceMate(this);
  happyTicks=Math.max(happyTicks,20);mate.happyTicks=Math.max(mate.happyTicks,20);
  if(++courtshipTicks%5==0) {
   for(CompanionEntity parent:new CompanionEntity[]{this,mate})
    world.spawnParticles(ParticleTypes.HEART,parent.getX(),parent.getY()+.75,parent.getZ(),3,.22,.18,.22,0);
  }
  if(courtshipTicks<60) return;
  // Retry a blocked birth position at most once per second.
  if(courtshipTicks>60 && courtshipTicks%20!=0) return;
  var inheritanceRandom=new java.util.Random(random.nextLong());
  CompanionGenes inherited=CompanionGenes.cross(kind().ordinal(),genes().generation(),mate.kind().ordinal(),mate.genes().generation());
  CharacterKind childKind=CharacterKind.values()[inherited.heroine(inheritanceRandom)];
  boolean childPlush=random.nextBoolean()?plush():mate.plush();
  var type=BocchiMod.KINDS.keySet().stream().filter(t->BocchiMod.KINDS.get(t)==childKind && BocchiMod.PLUSH_TYPES.contains(t)==childPlush).findFirst().orElseThrow();
  CompanionEntity child=(CompanionEntity)type.create(world);
  if(child==null || !(getOwner() instanceof PlayerEntity owner)) return;
  child.refreshPositionAndAngles((getX()+mate.getX())/2,getY(),(getZ()+mate.getZ())/2,getYaw(),0);
  if(!world.isSpaceEmpty(child)) return;
  child.genes=inherited;
  child.growthTicks=6000;child.setOwner(owner);child.setSitting(false);child.bandLeader=bandLeader;
  if(!world.spawnEntity(child)) return;
  courtshipTicks=mate.courtshipTicks=0;courtshipMate=mate.courtshipMate=null;
  pairingTicks=mate.pairingTicks=0;breedingCooldown=mate.breedingCooldown=6000;happyTicks=mate.happyTicks=100;
  world.spawnParticles(ParticleTypes.HEART,child.getX(),child.getY()+.5,child.getZ(),16,.4,.3,.4,0);
  BtrAdvancements.grant(owner,"new_generation");
  if(kind()!=mate.kind() || plush()!=mate.plush()) BtrAdvancements.grant(owner,"mixed_duet");
  if(child.genes.generation()>=3) BtrAdvancements.grant(owner,"family_tree");
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
   visualMountOffset=Float.NaN;lastScale=-1;
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
  }
  float scale=growthTicks>0?.6F:1F;
  if(lastScale!=scale || Float.isNaN(visualMountOffset)) {
   lastScale=scale;
   ((DisplayAccessor)display).bocchi$setTransformation(new AffineTransformation(
   new Vector3f(0,-visualMountOffset,0),new Quaternionf(),new Vector3f(scale,scale,scale),new Quaternionf()));
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
 private final class RehearsalGoal extends Goal {
  private BlockPos instrument;
  private int elapsed,played,searchDelay,sessionLength;
  RehearsalGoal() { setControls(java.util.EnumSet.of(Control.MOVE,Control.LOOK)); }
  private boolean available() {
   return isTamed() && growthTicks==0 && !isSitting() && !hummingMuted && panicTicks==0 && hidingTicks==0
     && pairingTicks==0 && getHealth()>=getMaxHealth() && getOwner()!=null && squaredDistanceTo(getOwner())<256;
  }
  private String instrumentId() { return switch(kind()) {case NIJIKA->"drum_kit";case KITA->"microphone";default->"guitar_stand";}; }
  @Override public boolean canStart() {
   if(!available() || rehearsalCooldown>0 || --searchDelay>0) return false;
   searchDelay=80;
   for(BlockPos candidate:BlockPos.iterateOutwards(getBlockPos(),8,3,8)) {
    if(!getWorld().getBlockState(candidate).isOf(BocchiMod.BLOCKS.get(instrumentId())))continue;
    if(getWorld() instanceof ServerWorld world && !world.getEntitiesByClass(CompanionEntity.class,getBoundingBox().expand(10),girl->girl!=CompanionEntity.this && girl.performing).isEmpty())return false;
    instrument=candidate.toImmutable();return true;
   }
   return false;
  }
  @Override public boolean shouldContinue() { return available() && (played>0 || elapsed<240) && played<sessionLength && instrument!=null && getWorld().getBlockState(instrument).isOf(BocchiMod.BLOCKS.get(instrumentId())); }
  @Override public void start() { elapsed=played=0;sessionLength=1800+random.nextInt(1201);performing=true;hummingStep=-1; }
  @Override public void tick() {
   elapsed++;
   double x=instrument.getX()+.5,y=instrument.getY(),z=instrument.getZ()+.5;
   if(squaredDistanceTo(x,y,z)>2.25) { navigation.startMovingTo(x,y,z,.8);return; }
   navigation.stop();
   float facing=(float)(Math.atan2(z-getZ(),x-getX())*180/Math.PI)-90;
   setYaw(facing);setBodyYaw(facing);setHeadYaw(facing);getLookControl().lookAt(x,y+.6,z);
   happyTicks=Math.max(happyTicks,20);
   if(played++%8==0 && getWorld() instanceof ServerWorld world) {
    int note=OriginalMusic.note(kind().ordinal(),played/8);
    SoundEvent sound=switch(kind()) {
     case NIJIKA->played%16<8?SoundEvents.BLOCK_NOTE_BLOCK_BASEDRUM.value():SoundEvents.BLOCK_NOTE_BLOCK_SNARE.value();
     case KITA->SoundEvents.BLOCK_NOTE_BLOCK_FLUTE.value();
     case RYO->SoundEvents.BLOCK_NOTE_BLOCK_BASS.value();
     case BOCCHI->SoundEvents.BLOCK_NOTE_BLOCK_GUITAR.value();
    };
    world.playSound(null,getX(),getY(),getZ(),sound,net.minecraft.sound.SoundCategory.NEUTRAL,.2F,(float)Math.pow(2,(note-12)/12.0));
    world.spawnParticles(ParticleTypes.NOTE,getX(),getY()+.95,getZ(),0,note/24.0,0,0,1);
    world.spawnParticles(ParticleTypes.NOTE,x,y+.9,z,0,note/24.0,0,0,1);
   }
  }
  @Override public void stop() { navigation.stop();performing=false;instrument=null;rehearsalCooldown=1200+random.nextInt(1200);hummingDelay=200; }
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
  if(reason.shouldDestroy()) {
   for(Entity passenger:getPassengerList()) passenger.discard();
   if(getWorld() instanceof ServerWorld world) {
    var team=world.getScoreboard().getScoreHolderTeam(getNameForScoreboard());
    if(team!=null && team.getName().equals("btr_pets")) world.getScoreboard().removeScoreHolderFromTeam(getNameForScoreboard(),team);
   }
  }
  super.remove(reason);
 }
 @Override public void writeCustomDataToNbt(NbtCompound nbt) { super.writeCustomDataToNbt(nbt); nbt.putInt("BocchiHiding",hidingTicks); nbt.putInt("BocchiPanic",panicTicks); if(bandLeader!=null) nbt.putUuid("BocchiBandLeader",bandLeader);
  nbt.putIntArray("BtrGenes",new int[]{genes().heroineA(),genes().heroineB(),genes().generation()});
  nbt.putInt("BtrMovementMode",movementMode);
  nbt.putBoolean("BtrHummingMuted",hummingMuted);
  nbt.putInt("BtrGrowth",growthTicks);nbt.putInt("BtrBreedCooldown",breedingCooldown);nbt.putInt("BtrPairing",pairingTicks); }
 @Override public void readCustomDataFromNbt(NbtCompound nbt) { super.readCustomDataFromNbt(nbt); hidingTicks=nbt.getInt("BocchiHiding"); panicTicks=nbt.getInt("BocchiPanic"); int[] g=nbt.getIntArray("BtrGenes");if(g.length==3) genes=new CompanionGenes(g[0],g[1],g[2]);
  movementMode=Math.max(0,Math.min(2,nbt.getInt("BtrMovementMode")));
  hummingMuted=nbt.getBoolean("BtrHummingMuted");hummingStep=-1;
  growthTicks=Math.max(0,Math.min(6000,nbt.getInt("BtrGrowth")));breedingCooldown=Math.max(0,Math.min(6000,nbt.getInt("BtrBreedCooldown")));pairingTicks=Math.max(0,Math.min(600,nbt.getInt("BtrPairing")));lastScale=-1;
  bandLeader=nbt.containsUuid("BocchiBandLeader")?nbt.getUuid("BocchiBandLeader"):null; setInvisible(true); setSilent(true); }
}
