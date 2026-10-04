package dev.aliska.bocchi;
/** Original note-block phrases. No anime soundtrack recordings or transcriptions. */
public final class OriginalMusic {
 private OriginalMusic() {}
 private static final int[][] PHRASES={
  {12,16,19,16,14,17,21,17,12,19,16,14,9,12,16,12,14,17,19,21,19,17,14,12,9,12,14,16,14,12,9,12},
  {12,12,19,16,12,14,17,14,16,16,21,19,17,14,12,12,19,16,14,12,14,17,19,17,16,14,12,9,12,16,14,12},
  {0,7,3,7,5,12,8,12,3,10,7,10,0,7,5,3,8,3,0,3,5,0,8,5,3,10,5,7,0,3,7,0},
  {16,19,21,19,17,16,14,12,14,17,21,19,16,14,12,16,19,21,24,21,19,17,16,14,17,19,16,14,12,14,16,12}
 };
 public static int note(int heroine,int beat) {
  int[] phrase=PHRASES[Math.floorMod(heroine,PHRASES.length)];
  int section=Math.floorDiv(beat,phrase.length);
  int note=phrase[Math.floorMod(beat,phrase.length)];
  // Alternate verse, response, quieter register, and refrain without short loops.
  if(section%4==1) note=phrase[(Math.floorMod(beat,phrase.length)+8)%phrase.length];
  if(section%4==2) note=Math.max(0,note-5);
  return Math.min(24,note);
 }
}
