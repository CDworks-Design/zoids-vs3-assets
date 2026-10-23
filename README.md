# Zoids VS. III model and texture assets

An initial, organized collection of **92 GLB model variants covering 87 source IDs**, including **5 low-detail variants**. The pack also includes **102 texture images** extracted byte-for-byte from the GLBs.

## Use the models

1. Find an asset in [the model index](INDEX.md).
2. Download its `.glb` file. Each GLB contains its textures, so it can be moved independently.
3. Import it into a glTF 2.0-compatible application. The separate `textures/` folder is available when you want the image files directly.

The filenames preserve the game's source IDs. They are not a researched mapping to commercial Zoid names. The `low` variants are listed separately.

## Scope and limitations

This is a model/texture release, not a game, ROM, emulator, source-code release, or complete game-asset dump. Weapons, stage objects, and character portraits from the broader conversion catalog are not included in this initial pack.

GLB is the only model format in this release. OBJ and FBX alternatives have not been packaged or validated here. Units, orientation, rig behavior, materials in a particular engine, and visual fidelity should be checked in the destination application.

Most models have no animation clips. A01 preserves 102 accessory/reference clips, which are not authenticated body animations. A07 preserves two measured clips, `idle` and `walk_forward`; do not assume they are seamless loops. This release does not claim complete or gameplay-correct animation.

## Validation and provenance

All 92 GLBs passed the read-only checks described in [VALIDATION.md](VALIDATION.md). No model rendering or game execution was performed for this release. Original GLB bytes are preserved.

[The machine-readable catalog](catalog.json) records source asset IDs, source hashes, export hashes, sizes, mesh counts, embedded images, and animation caveats. [SHA256SUMS.txt](SHA256SUMS.txt) covers the public package files other than itself.

Please read [ASSET_RIGHTS.md](ASSET_RIGHTS.md) before reuse. Publication does not imply an unrestricted, commercial-use, or open-source license for the original game content.
