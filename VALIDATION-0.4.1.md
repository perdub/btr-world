# BTR World 0.4.1 — Polymer block crash fix

Before fix: simulated exhaustion of FULL_BLOCK, TRIPWIRE_BLOCK_FLAT and TRIPWIRE_BLOCK reproduced NullPointerException in PolymerBlockUtils.getBlockStateSafely (out is null), identified bocchi:bocchi_light_matte.
After fix: normal and exhausted runs each validated all 80 states of 55 registered blocks, including initShapeCache, and built the Polymer resource pack successfully.
Build and genetics/music checks passed. Test environment: Minecraft 1.21.1, Java 21, Fabric Loader 0.16.10, Polymer 0.9.18. User log: Loader 0.19.5, Polymer 0.9.19, additional mods/datapacks not present locally.
Both launches stop at EULA gate; no gameplay world or client visual session was tested. User datapack errors h-nigh/creeperoverhaul are independent unresolved issues in the supplied log.
No new external release was uploaded here.
