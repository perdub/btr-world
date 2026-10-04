# BTR World 0.4.1

- Fix null Polymer block mappings when shared model state pools are exhausted.
- Decorations try ordinary tripwire states when flat tripwire states are unavailable.
- Safe vanilla fallbacks prevent startup crashes; warnings identify each unavailable model.
- Validate all 80 states of 55 blocks, including collision caches, with normal and exhausted pools before world load.
- CI uses Modrinth Publish v2.5.2 with JSON file list and API readback verification.
