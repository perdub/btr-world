package dev.aliska.bocchi;

import java.util.HashMap;
import java.util.Map;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.minecraft.entity.decoration.ArmorStandEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.BlockPos;

/** Vanilla marker seats: no client mod is required. */
public final class BoxSeats {
 private static final String TAG = "btr_box_seat";
 private static final Map<ArmorStandEntity, BlockPos> SEATS = new HashMap<>();
 private BoxSeats() {}
 public static void initialize() {
  ServerEntityEvents.ENTITY_LOAD.register((entity, world) -> {
   if (entity instanceof ArmorStandEntity stand && stand.getCommandTags().contains(TAG)) {
    SEATS.put(stand, BlockPos.ofFloored(stand.getX(), stand.getY(), stand.getZ()));
   }
  });
  ServerTickEvents.END_WORLD_TICK.register(world -> SEATS.entrySet().removeIf(entry -> {
   ArmorStandEntity seat = entry.getKey();
   if (seat.getWorld() != world) return false;
   if (seat.isRemoved()) return true;
   if (!seat.hasPassengers() || !world.getBlockState(entry.getValue()).isOf(BocchiMod.BLOCKS.get("bocchi_box"))) {
    seat.discard();
    return true;
   }
   return false;
  }));
  ServerLifecycleEvents.SERVER_STOPPED.register(server -> SEATS.clear());
 }
 public static boolean sit(ServerWorld world, BlockPos pos, PlayerEntity player) {
  if (player.isSneaking() || player.hasVehicle()) return false;
  for (var entry : SEATS.entrySet()) {
   if (entry.getKey().getWorld() == world && !entry.getKey().isRemoved()
       && entry.getValue().equals(pos) && entry.getKey().hasPassengers()) return false;
  }
  ArmorStandEntity seat = new ArmorStandEntity(world, pos.getX() + .5, pos.getY() + .1, pos.getZ() + .5);
  configure(seat);
  seat.setPosition(pos.getX() + .5, pos.getY() + .1, pos.getZ() + .5);
  seat.addCommandTag(TAG);
  if (!world.spawnEntity(seat)) return false;
  if (!player.startRiding(seat, true)) { seat.discard(); return false; }
  SEATS.put(seat, pos.toImmutable());
  return true;
 }
 static void configure(ArmorStandEntity seat) {
  NbtCompound flags = new NbtCompound();
  flags.putBoolean("Marker", true);
  flags.putBoolean("Invisible", true);
  flags.putBoolean("NoGravity", true);
  flags.putBoolean("Invulnerable", true);
  flags.putBoolean("Silent", true);
  seat.readNbt(flags);
 }

}
