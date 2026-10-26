# Zoids VS. III model and texture assets

An initial, organized collection of **92 GLB model variants covering 87 source IDs**, including **5 low-detail variants**. The pack also includes **102 texture images** extracted byte-for-byte from the GLBs.

## Use the models

1. Find an asset in [the model index](INDEX.md).
2. Download its `.glb` file. Each GLB contains its textures, so it can be moved independently.
3. Import it into a glTF 2.0-compatible application. The separate `textures/` folder is available when you want the image files directly.

The filenames preserve the game's source IDs. They are not a researched mapping to commercial Zoid names. The `low` variants are listed separately.

## Baked FBX animation downloads

[Download the checked animation packages](animations/README.md): **12 standard model IDs and 205 take records**, plus an optional overlapping A21 mixed56 approximation. Packages contain a multi-take FBX with embedded textures and documented limitations. This is not a complete roster export, and take records are not all distinct moving animations.

A01's new 102-slot baked package is separate from the original accessory/reference GLB. Its 30,000-FPS import clock changes global Blender scene FPS while preserving seconds. Its runtime companion is data and instructions, not completed camera/material integration; [read A01's limits](animations/README.md#a01-qualified-converted-asset-not-engine-ready-integration) before importing.

The [animation download page](https://cdworks-design.github.io/zoids-vs3-assets/animations/) is separate from the existing GLB viewer. The original GLBs remain byte-for-byte unchanged.

## Scope and limitations

This is a model/texture release, not a game, ROM, emulator, source-code release, or complete game-asset dump. Weapons, stage objects, and character portraits from the broader conversion catalog are not included in this initial pack.

The original model collection uses GLB. Selected baked FBX animation packages are now provided separately; OBJ alternatives are not packaged. Units, orientation, rig behavior, materials in a particular engine, and visual fidelity should be checked in the destination application.

Most original GLBs have no animation clips. A01 preserves 102 accessory/reference clips, which are not authenticated body animations. A07 preserves two measured clips, `idle` and `walk_forward`; do not assume they are seamless loops. This release does not claim complete or gameplay-correct animation.

## Validation and provenance

All 92 GLBs passed the read-only checks described in [VALIDATION.md](VALIDATION.md). No model rendering or game execution was performed for this release. Original GLB bytes are preserved.

[The machine-readable catalog](catalog.json) records source asset IDs, source hashes, export hashes, sizes, mesh counts, embedded images, and animation caveats. [SHA256SUMS.txt](SHA256SUMS.txt) retains the original package checksums and includes the added animation downloads and changed documentation. [Animation checksums](animations/SHA256SUMS) cover the new animation package files and catalog.

Please read [ASSET_RIGHTS.md](ASSET_RIGHTS.md) before reuse. Publication does not imply an unrestricted, commercial-use, or open-source license for the original game content.


