package dev.aliska.bocchi;

/** Exact automatic labels used by old summoners, not arbitrary player names. */
public final class CompanionNames {
 private CompanionNames() {}
 public static boolean isLegacyGeneratedName(String name) {
  for (String heroine : new String[]{"Хитори", "Нидзика", "Рё", "Кита"}) {
   for (String form : new String[]{"тсум", "чиби"}) {
    if (name.equals(heroine + " · " + form)) return true;
   }
  }
  return false;
 }
}
