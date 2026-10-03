package dev.aliska.bocchi;
import eu.pb4.polymer.blocks.api.*;
import net.minecraft.block.*;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.Identifier;
public class PaletteBlock extends Block implements PolymerTexturedBlock {
 private final BlockState clientState;
 public PaletteBlock(String id, Settings settings) {
  super(settings);
  clientState = PolymerBlockResourceUtils.requestBlock(BlockModelType.FULL_BLOCK, PolymerBlockModel.of(Identifier.of("bocchi", "block/"+id)));
 }
 @Override public BlockState getPolymerBlockState(BlockState state) { return clientState; }
}
