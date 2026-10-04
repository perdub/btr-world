package dev.aliska.bocchi;
import java.util.Random;
public final class GeneticsCheck {
 public static void main(String[] args) {
  var nijika=new CompanionGenes(1,1,0);var bocchi=new CompanionGenes(0,0,0);var rng=new Random(190319);
  int nijikas=0;
  for(int i=0;i<100000;i++) {
   var child=CompanionGenes.cross(1,0,0,0);
   if(child.heroineA()!=1 || child.heroineB()!=0 || child.generation()!=1) throw new AssertionError("Alleles/generation were not inherited");
   if(child.heroine(rng)==1) nijikas++;
  }
  if(nijikas<74000 || nijikas>76000) throw new AssertionError("Expected roughly 75% Nijika, got "+nijikas);
  for(int kind=0;kind<4;kind++) {
   var pure=new CompanionGenes(kind,kind,0);
   for(int i=0;i<100;i++) if(CompanionGenes.cross(kind,0,kind,0).heroine(rng)!=kind) throw new AssertionError("Pure parents changed heroine");
  }
  var third=CompanionGenes.cross(1,2,2,1);
  if(third.generation()!=3 || third.heroineA()!=1 || third.heroineB()!=2) throw new AssertionError("Lineage depth incorrect");
  for(int i=0;i<1000;i++) { int kind=third.heroine(rng);if(kind!=1 && kind!=2) throw new AssertionError("A non-parent heroine appeared"); }
  var invalid=new CompanionGenes(-20,900,5000);
  if(invalid.heroineA()!=0 || invalid.heroineB()!=3 || invalid.generation()!=1024) throw new AssertionError("NBT bounds not sanitized");
  System.out.println("PASS: genetics, pure lines, parent identities, generations, bounds; Nijika rate="+nijikas/1000.0+"%");
 }
}
