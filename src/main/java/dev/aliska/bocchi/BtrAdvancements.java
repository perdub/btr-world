package dev.aliska.bocchi;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.network.ServerPlayerEntity;
public final class BtrAdvancements {
 public static void grant(PlayerEntity player,String id) { grant(player,id,"done"); }
 public static void grant(PlayerEntity player,String id,String criterion) {
  if(player instanceof ServerPlayerEntity serverPlayer) {
   var root=serverPlayer.getServer().getAdvancementLoader().get(BocchiMod.id("root"));
   if(root!=null) serverPlayer.getAdvancementTracker().grantCriterion(root,"done");
   var entry=serverPlayer.getServer().getAdvancementLoader().get(BocchiMod.id(id));
   if(entry!=null) serverPlayer.getAdvancementTracker().grantCriterion(entry,criterion);
  }
 }
}
