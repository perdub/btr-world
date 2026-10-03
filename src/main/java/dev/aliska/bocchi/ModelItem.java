package dev.aliska.bocchi;
import eu.pb4.polymer.core.api.item.PolymerItem;
import eu.pb4.polymer.resourcepack.api.PolymerResourcePackUtils;
import net.minecraft.item.*;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.Identifier;
public class ModelItem extends Item implements PolymerItem {
 private final int model;
 public ModelItem(String id, Settings settings) {
  super(settings);
  model = PolymerResourcePackUtils.requestModel(Items.PAPER, Identifier.of("bocchi", "item/"+id)).value();
 }
 @Override public Item getPolymerItem(ItemStack stack, ServerPlayerEntity player) { return Items.PAPER; }
 @Override public int getPolymerCustomModelData(ItemStack stack, ServerPlayerEntity player) { return model; }
}
