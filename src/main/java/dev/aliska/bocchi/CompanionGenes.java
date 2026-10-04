package dev.aliska.bocchi;
import java.util.random.RandomGenerator;
/** Parent heroine identities and lineage depth; weighted heroine inheritance. */
public record CompanionGenes(int heroineA,int heroineB,int generation) {
 private static final int[] WEIGHTS={1,3,2,2}; // Hitori, Nijika, Ryo, Kita
 public CompanionGenes { heroineA=clamp(heroineA);heroineB=clamp(heroineB);generation=Math.max(0,Math.min(1024,generation)); }
 private static int clamp(int n) { return Math.max(0,Math.min(3,n)); }
 public static CompanionGenes cross(int firstHeroine,int firstGeneration,int secondHeroine,int secondGeneration) {
  return new CompanionGenes(firstHeroine,secondHeroine,Math.max(firstGeneration,secondGeneration)+1);
 }
 public int heroine(RandomGenerator r) { return r.nextInt(WEIGHTS[heroineA]+WEIGHTS[heroineB])<WEIGHTS[heroineA]?heroineA:heroineB; }
}
