package dev.aliska.bocchi;
import eu.pb4.polymer.core.api.item.PolymerItem;
import net.minecraft.entity.EquipmentSlot;
import net.minecraft.item.*;
import net.minecraft.component.DataComponentTypes;
import net.minecraft.component.type.DyedColorComponent;
import net.minecraft.component.type.AttributeModifiersComponent;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.world.World;
import net.minecraft.util.*;
/** Cosmetic leather rendering with no armour attributes or special buffs. */
public final class CostumeItem extends Item implements PolymerItem,Equipment {
 private final EquipmentSlot slot;private final Item appearance;
 public CostumeItem(EquipmentSlot slot,Item appearance) {
  super(new Item.Settings().maxCount(1).component(DataComponentTypes.DYED_COLOR,new DyedColorComponent(0xefa1c4,false)).component(DataComponentTypes.ATTRIBUTE_MODIFIERS,AttributeModifiersComponent.DEFAULT));
  this.slot=slot;this.appearance=appearance;
 }
 @Override public EquipmentSlot getSlotType() { return slot; }
 @Override public Item getPolymerItem(ItemStack stack,ServerPlayerEntity player) { return appearance; }
 @Override public TypedActionResult<ItemStack> use(World world,PlayerEntity player,Hand hand) { return equipAndSwap(this,world,player,hand); }
}
