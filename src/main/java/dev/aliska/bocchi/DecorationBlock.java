package dev.aliska.bocchi;
import eu.pb4.polymer.blocks.api.*;
import net.minecraft.block.*;
import net.minecraft.util.hit.BlockHitResult;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.effect.*;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.*;
import net.minecraft.util.math.*;
import net.minecraft.util.shape.*;
import net.minecraft.world.*;
import net.minecraft.text.Text;
public class DecorationBlock extends Block implements PolymerTexturedBlock {
 private final BlockState visual;
 private final String id;
 public DecorationBlock(String id) {
  super(Settings.create().strength(0.7F).nonOpaque().noCollision().sounds(net.minecraft.sound.BlockSoundGroup.WOOD));
  this.id=id;
  visual=PolymerBlockResourceUtils.requestBlock(BlockModelType.TRIPWIRE_BLOCK_FLAT,PolymerBlockModel.of(Identifier.of("bocchi","block/"+id)));
 }
 @Override public BlockState getPolymerBlockState(BlockState state) { return visual; }
 @Override protected VoxelShape getOutlineShape(BlockState state, BlockView world, BlockPos pos, ShapeContext context) {
  return Block.createCuboidShape(2,0,2,14,id.endsWith("figurine")?13:12,14);
 }
 @Override protected VoxelShape getCollisionShape(BlockState state, BlockView world, BlockPos pos, ShapeContext context) {
  return VoxelShapes.empty();
 }
 @Override protected ActionResult onUse(BlockState state,World world,BlockPos pos,PlayerEntity player,BlockHitResult hit) {
  if(world.isClient) return ActionResult.SUCCESS;
  if(id.equals("bocchi_box")) {
   if(player.getItemCooldownManager().isCoolingDown(asItem())) return ActionResult.PASS;
   player.addStatusEffect(new StatusEffectInstance(StatusEffects.INVISIBILITY,200,0,false,false,true));
   player.getItemCooldownManager().set(asItem(),400);
   player.sendMessage(Text.literal("Коробка Боччи: десять секунд, чтобы собраться с мыслями."),true);
   return ActionResult.SUCCESS;
  }
  if(id.equals("drum_kit")) {
   player.addStatusEffect(new StatusEffectInstance(StatusEffects.HASTE,200,0,true,false,true));
   world.playSound(null,pos,net.minecraft.sound.SoundEvents.BLOCK_NOTE_BLOCK_SNARE.value(),net.minecraft.sound.SoundCategory.BLOCKS,0.6F,1);
   return ActionResult.SUCCESS;
  }
  return ActionResult.PASS;
 }
}
