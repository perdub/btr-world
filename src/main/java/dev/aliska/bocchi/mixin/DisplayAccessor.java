package dev.aliska.bocchi.mixin;
import net.minecraft.entity.decoration.DisplayEntity;
import net.minecraft.util.math.AffineTransformation;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;
@Mixin(DisplayEntity.class)
public interface DisplayAccessor {
 @Invoker("setTransformation") void bocchi$setTransformation(AffineTransformation transformation);
}
