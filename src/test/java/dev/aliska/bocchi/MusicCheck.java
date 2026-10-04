package dev.aliska.bocchi;
public final class MusicCheck {
 public static void main(String[] args) {
  for(int heroine=0;heroine<4;heroine++) {
   boolean longerThanEight=false;
   for(int beat=0;beat<2048;beat++) {
    int note=OriginalMusic.note(heroine,beat);
    if(note<0 || note>24) throw new AssertionError("Outside note-block range");
    if(beat>=8 && beat<32 && note!=OriginalMusic.note(heroine,beat%8)) longerThanEight=true;
   }
   if(!longerThanEight) throw new AssertionError("Short eight-note loop instead of long phrase");
  }
  System.out.println("PASS: original phrases stay in note-block range and exceed eight-note loops.");
 }
}
