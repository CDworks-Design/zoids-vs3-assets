# Zoids VS. III model and texture assets

An initial, organized collection of **92 GLB model variants covering 87 source IDs**, including **5 low-detail variants**. The pack also includes **102 texture images** extracted byte-for-byte from the GLBs.

## Use the models

1. Find an asset in [the model index](INDEX.md).
2. Download its `.glb` file. Each GLB contains its textures, so it can be moved independently.
3. Import it into a glTF 2.0-compatible application. The separate `textures/` folder is available when you want the image files directly.

The filenames preserve the game's source IDs. They are not a researched mapping to commercial Zoid names. The `low` variants are listed separately.

## Baked FBX animation downloads

[Download the checked animation packages](animations/README.md): **13 standard model IDs and 307 take records**, plus an optional overlapping A21 mixed56 approximation. Packages contain a multi-take FBX with embedded textures and documented limitations. This is not a complete roster export, and take records are not all distinct moving animations.

A01's new 102-slot baked package is separate from the original accessory/reference GLB. Its 30,000-FPS import clock changes global Blender scene FPS while preserving seconds. Its runtime companion is data and instructions, not completed camera/material integration; [read A01's limits](animations/README.md#a01-qualified-converted-asset-not-engine-ready-integration) before importing.

A02 adds a qualified 102-slot body-animation export with three exact atlases and diagnostic validation. Its 30,000-FPS import also changes global scene FPS; source-hidden helpers, auxiliary effects and native shaders remain outside qualification. [Read A02's limits](animations/README.md#a02-qualified-body-export-not-full-native-rendering).

The [animation download page](https://cdworks-design.github.io/zoids-vs3-assets/animations/) is separate from the existing GLB viewer. The original GLBs remain byte-for-byte unchanged.

## Complete asset inventory

Browse the [searchable asset inventory](https://cdworks-design.github.io/zoids-vs3-assets/inventory/) or the [inventory summary](INVENTORY.md) for **627 historical model conversion records**: **224 weapons, 207 stage assets, 108 character assets, and 88 Zoid entries**. All 627 exports were found locally and matched against the decoding catalog's source and export hashes in this refresh.

The inventory also lists **12,609 source files across 21 categories**, including audio, voices, menus, HUD, effects, particles, projectiles, textures, movies, and gameplay data. It separates **12,572 files matching the compared translated disc image** from **37 local generated files**. File counts include related data and copies; they are not counts of unique decoded objects. Stage exports include scenery, skyboxes, objects, and variants, not 207 distinct playable maps.

[Model records (JSON)](inventory/assets.json) · [Model records (CSV)](inventory/assets.csv) · [All source files (JSON)](inventory/sources.json) · [All source files (CSV)](inventory/sources.csv) · [Category totals](inventory/sections.json)

Inventory coverage and public downloads are tracked separately. The 92 GLBs in the existing gallery remain the published model collection; local weapon, stage, and character exports are inventoried here with their availability and validation status.

## Game decoding progress

[Game decoding progress dashboard](https://cdworks-design.github.io/zoids-vs3-assets/decoding-progress/) tracks asset families, decoder systems, current exports and unresolved identification. It publishes summary metadata only, not private research or additional game files.

## Scope and limitations

This is a model/texture release and metadata inventory, not a game, ROM, emulator, source-code release, or complete game-asset dump. Weapons, stage objects, and character assets from the broader conversion catalog are covered by the inventory; their binary payloads are not included in the initial model pack.

The original model collection uses GLB. Selected baked FBX animation packages are now provided separately; OBJ alternatives are not packaged. Units, orientation, rig behavior, materials in a particular engine, and visual fidelity should be checked in the destination application.

Most original GLBs have no animation clips. A01 preserves 102 accessory/reference clips, which are not authenticated body animations. A07 preserves two measured clips, `idle` and `walk_forward`; do not assume they are seamless loops. This release does not claim complete or gameplay-correct animation.

## Validation and provenance

All 92 GLBs passed the read-only checks described in [VALIDATION.md](VALIDATION.md). No model rendering or game execution was performed for this release. Original GLB bytes are preserved.

[The machine-readable catalog](catalog.json) records source asset IDs, source hashes, export hashes, sizes, mesh counts, embedded images, and animation caveats. [SHA256SUMS.txt](SHA256SUMS.txt) retains the original package checksums and includes the added animation downloads and changed documentation. [Animation checksums](animations/SHA256SUMS) cover the new animation package files and catalog.

Please read [ASSET_RIGHTS.md](ASSET_RIGHTS.md) before reuse. Publication does not imply an unrestricted, commercial-use, or open-source license for the original game content.



