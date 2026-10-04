package dev.aliska.bocchi;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.ColorProviderRegistry;
import net.minecraft.component.type.DyedColorComponent;
public final class BtrClient implements ClientModInitializer {
 @Override public void onInitializeClient() {
  for(var item:BocchiMod.ITEMS) if(item instanceof CostumeItem) ColorProviderRegistry.ITEM.register((stack,tint)->tint==0?DyedColorComponent.getColor(stack,0xefa1c4):-1,item);
 }
}
