package dev.aliska.bocchi;
import net.minecraft.entity.EntityType;
import net.minecraft.item.*;
import net.minecraft.util.ActionResult;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.BlockPos;
import net.minecraft.text.Text;
public class CompanionSummoner extends ModelItem {
 private final EntityType<CompanionEntity> type;
 public CompanionSummoner(String id, EntityType<CompanionEntity> type) { super(id,new Item.Settings()); this.type=type; }
 @Override public ActionResult useOnBlock(ItemUsageContext context) {
  if(!(context.getWorld() instanceof ServerWorld world)) return ActionResult.SUCCESS;
  BlockPos pos=context.getBlockPos().offset(context.getSide());
  CompanionEntity entity=type.create(world);
  if(entity==null) return ActionResult.FAIL;
  entity.refreshPositionAndAngles(pos.getX()+0.5,pos.getY(),pos.getZ()+0.5,context.getPlayerYaw()+180,0);
  if(!world.isSpaceEmpty(entity,entity.getBoundingBox())) return ActionResult.FAIL;
  entity.setCustomName(Text.literal(entity.kind().name+(entity.plush()?" · тсум":" · чиби")));
  if(!world.spawnEntity(entity)) return ActionResult.FAIL;
  if(context.getPlayer()!=null && !context.getPlayer().getAbilities().creativeMode) context.getStack().decrement(1);
  return ActionResult.SUCCESS;
 }
}
