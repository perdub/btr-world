package dev.aliska.bocchi;
import eu.pb4.polymer.blocks.api.*;
import net.minecraft.util.Identifier;
import net.minecraft.block.BlockState;
import net.minecraft.block.Blocks;
final class BlockVisuals {
 static BlockState allocate(String id, PolymerBlockModel model, boolean solid) {
  var primary=solid?BlockModelType.FULL_BLOCK:BlockModelType.TRIPWIRE_BLOCK_FLAT;
  BlockState state=PolymerBlockResourceUtils.requestBlock(primary,model);
  if(state==null && !solid) state=PolymerBlockResourceUtils.requestBlock(BlockModelType.TRIPWIRE_BLOCK,model);
  if(state!=null) return state;
  org.slf4j.LoggerFactory.getLogger("bocchi").warn("No Polymer model states available for bocchi:{} ({}). Using safe vanilla fallback; custom model unavailable. Other Polymer mods share this pool.",id,primary);
  return solid?Blocks.WHITE_WOOL.getDefaultState():Blocks.AIR.getDefaultState();
 }
 static void exhaustForTest() {
  if (!Boolean.getBoolean("bocchi.testExhaustedBlockStates")) return;
  for (var type : new BlockModelType[]{BlockModelType.FULL_BLOCK,BlockModelType.TRIPWIRE_BLOCK_FLAT,BlockModelType.TRIPWIRE_BLOCK}) {
   int count=PolymerBlockResourceUtils.getBlocksLeft(type);
   for(int i=0;i<count;i++) PolymerBlockResourceUtils.requestBlock(type,PolymerBlockModel.of(Identifier.of("bocchi","block/exhaustion_probe_"+type.name().toLowerCase()+"_"+i)));
  }
 }
}
