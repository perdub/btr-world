package dev.aliska.bocchi.mixin;
import net.minecraft.entity.decoration.DisplayEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.client.render.model.json.ModelTransformationMode;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;
@Mixin(DisplayEntity.ItemDisplayEntity.class)
public interface ItemDisplayAccessor {
 @Invoker("getItemStack") ItemStack bocchi$getItemStack();
 @Invoker("setItemStack") void bocchi$setItemStack(ItemStack stack);
 @Invoker("setTransformationMode") void bocchi$setMode(ModelTransformationMode mode);
}
