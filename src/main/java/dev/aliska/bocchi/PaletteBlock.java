package dev.aliska.bocchi;
import eu.pb4.polymer.blocks.api.*;
import net.minecraft.block.*;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.Identifier;
public class PaletteBlock extends Block implements PolymerTexturedBlock {
 private final BlockState clientState;
 public PaletteBlock(String id, Settings settings) {
  super(settings);
  clientState = BlockVisuals.allocate(id, PolymerBlockModel.of(Identifier.of("bocchi", "block/"+id)),true);
 }
 @Override public BlockState getPolymerBlockState(BlockState state) { return clientState!=null?clientState:Blocks.WHITE_WOOL.getDefaultState(); }
}
