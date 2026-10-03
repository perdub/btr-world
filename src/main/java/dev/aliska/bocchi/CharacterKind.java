package dev.aliska.bocchi;
import net.minecraft.item.Item;
import net.minecraft.item.Items;
public enum CharacterKind {
 BOCCHI("bocchi", "Хитори", Items.COOKIE),
 NIJIKA("nijika", "Нидзика", Items.CAKE),
 RYO("ryo", "Рё", Items.WHEAT),
 KITA("kita", "Кита", Items.GLOW_BERRIES);
 public final String id, name;
 public final Item treat;
 CharacterKind(String id, String name, Item treat) { this.id=id; this.name=name; this.treat=treat; }
}
