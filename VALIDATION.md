# Validation scope

Validation date: 2026-10-23 UTC.

## Passed for the included 92 GLBs

- Source-preservation manifest hashes and every input chunk's SHA-256 matched the selected export bytes.
- GLB 2.0 headers, total lengths, chunk lengths/alignment, JSON and binary chunks.
- Self-contained binary buffers and embedded images, with no external resource URIs.
- Buffer-view and accessor ranges, component/stride alignment, finite floating-point accessor values.
- Nonempty mesh primitives, triangle indices within position ranges, matching vertex-attribute counts.
- Scene, node, skin, inverse-bind-matrix, material/texture, and animation references.
- Embedded PNG images decoded successfully; separately supplied images are exact copies of the embedded bytes.
- JSON metadata was screened for local absolute paths, credential patterns, and private file URLs. PNG ancillary chunks were restricted to ordinary image/color metadata.
- All 92 GLBs have distinct complete-file SHA-256 values. Duplicate application copies and research export variants were not packaged.

The largest GLB is 4,671,680 bytes. Models total 75,204,812 bytes and the separately extracted textures total 16,793,691 bytes. No single package file reaches 100,000,000 bytes.

## Not established by these checks

This is a focused structural audit, not a full Khronos conformance-validator result. It does not establish appearance, complete topology fidelity, engine-specific import behavior, units/orientation, original-game material/shader equivalence, rig correctness, animation correctness, seamless loops, or legal reuse rights.

No model was rendered, animated, or executed, and no game or emulator was run. Source IDs are preserved rather than assigning unverified character names. Small valid exports can represent small or partial source objects; structural validity is not a claim that each ID is a complete playable character.

## Selection

The first release selects the 88 `zoid` exports from the existing static conversion catalog plus the existing A01, A03, A07, and A17 primary exports. The 5 low-detail variants are counted separately. All selected files passed these checks; none was dropped as corrupt. Additional alternate or experimental exports were not selected, rather than being claimed corrupt.
