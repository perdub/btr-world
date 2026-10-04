package dev.aliska.bocchi;

import java.util.EnumMap;
import eu.pb4.polymer.blocks.api.*;
import net.minecraft.block.*;
import net.minecraft.item.ItemPlacementContext;
import net.minecraft.state.StateManager;
import net.minecraft.state.property.DirectionProperty;
import net.minecraft.state.property.Properties;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.*;
import net.minecraft.util.shape.*;
import net.minecraft.world.*;

public final class WallDecorBlock extends Block implements PolymerTexturedBlock {
 public static final DirectionProperty FACING=Properties.FACING;
 private final EnumMap<Direction,BlockState> visuals=new EnumMap<>(Direction.class);
 private final boolean ceiling;
 public WallDecorBlock(String id,int light,boolean ceiling) {
  super(Settings.create().strength(.3F).nonOpaque().noCollision().luminance(state->light).sounds(net.minecraft.sound.BlockSoundGroup.WOOD));
  this.ceiling=ceiling;
  setDefaultState(getStateManager().getDefaultState().with(FACING,Direction.NORTH));
  for(Direction direction:Direction.values()) {
   if(!ceiling && direction.getAxis().isVertical()) continue;
   int x=direction==Direction.DOWN?90:direction==Direction.UP?270:0;
   int y=switch(direction) {case EAST->90;case SOUTH->180;case WEST->270;default->0;};
   visuals.put(direction,BlockVisuals.allocate(id+"/"+direction.getName(),PolymerBlockModel.of(Identifier.of("bocchi","block/"+id),x,y),false));
  }
 }
 @Override protected void appendProperties(StateManager.Builder<Block,BlockState> builder) { builder.add(FACING); }
 @Override public BlockState getPolymerBlockState(BlockState state) { if(visuals==null) return Blocks.AIR.getDefaultState(); BlockState visual=visuals.getOrDefault(state.get(FACING),visuals.get(Direction.NORTH)); return visual!=null?visual:Blocks.AIR.getDefaultState(); }
 @Override public BlockState getPlacementState(ItemPlacementContext context) {
  Direction face=context.getSide();
  if(!ceiling && face.getAxis().isVertical()) return null;
  return getDefaultState().with(FACING,face);
 }
 @Override protected boolean canPlaceAt(BlockState state,WorldView world,BlockPos pos) {
  Direction facing=state.get(FACING);
  BlockPos support=pos.offset(facing.getOpposite());
  return world.getBlockState(support).isSideSolidFullSquare(world,support,facing);
 }
 @Override protected BlockState getStateForNeighborUpdate(BlockState state,Direction direction,BlockState neighbor,WorldAccess world,BlockPos pos,BlockPos neighborPos) {
  return direction==state.get(FACING).getOpposite() && !state.canPlaceAt(world,pos)?Blocks.AIR.getDefaultState():state;
 }
 @Override protected VoxelShape getOutlineShape(BlockState state,BlockView world,BlockPos pos,ShapeContext context) {
  return switch(state.get(FACING)) {
   case NORTH->Block.createCuboidShape(0,0,14,16,16,16);
   case SOUTH->Block.createCuboidShape(0,0,0,16,16,2);
   case EAST->Block.createCuboidShape(0,0,0,2,16,16);
   case WEST->Block.createCuboidShape(14,0,0,16,16,16);
   case DOWN->Block.createCuboidShape(0,14,0,16,16,16);
   case UP->Block.createCuboidShape(0,0,0,16,2,16);
  };
 }
}
