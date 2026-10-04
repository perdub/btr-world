package dev.aliska.bocchi;
import net.minecraft.entity.EquipmentSlot;
import net.minecraft.item.*;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.world.World;
import net.minecraft.util.*;
public final class DecorativeHatItem extends ModelItem implements Equipment {
 public DecorativeHatItem(String model) { super(model,new Item.Settings().maxCount(1)); }
 @Override public EquipmentSlot getSlotType() { return EquipmentSlot.HEAD; }
 @Override public TypedActionResult<ItemStack> use(World world,PlayerEntity player,Hand hand) { return equipAndSwap(this,world,player,hand); }
}
