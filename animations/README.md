# Baked animation downloads

13 standard model IDs, 307 take records. This is an incomplete, experimental collection, not 307 unique moving animations or a complete roster export.

| Source ID | Edition | Take records | Download |
| --- | --- | ---: | --- |
| A01 | Converted asset · 30,000-FPS import clock | 102 | [Download ZIP](downloads/A01_102_TAKES_IMPORTCLOCK30000.zip) |
| A02 | Qualified body export · 30,000-FPS import clock | 102 | [Download ZIP](downloads/A02_102_TAKES_IMPORTCLOCK30000.zip) |
| A04 | Blender compatibility | 1 | [Download ZIP](downloads/A04-blender-compat-1-takes.zip) |
| A05 | Blender compatibility | 1 | [Download ZIP](downloads/A05-blender-compat-1-takes.zip) |
| A06 | Blender compatibility | 1 | [Download ZIP](downloads/A06-blender-compat-1-takes.zip) |
| A21 | Blender compatibility | 55 | [Download ZIP](downloads/A21-blender-compat-55-takes.zip) |
| A21 | Optional mixed56 approximation | 56 | [Download ZIP](downloads/A21-mixed56-approximation-56-takes.zip) |
| A24 | Blender compatibility | 1 | [Download ZIP](downloads/A24-blender-compat-1-takes.zip) |
| A25 | Blender compatibility | 1 | [Download ZIP](downloads/A25-blender-compat-1-takes.zip) |
| B03 | Blender compatibility | 1 | [Download ZIP](downloads/B03-blender-compat-1-takes.zip) |
| B24 | Blender compatibility | 1 | [Download ZIP](downloads/B24-blender-compat-1-takes.zip) |
| B26 | Blender compatibility | 20 | [Download ZIP](downloads/B26-blender-compat-20-takes.zip) |
| B27 | Blender compatibility | 1 | [Download ZIP](downloads/B27-blender-compat-1-takes.zip) |
| B33 | Blender compatibility | 20 | [Download ZIP](downloads/B33-blender-compat-20-takes.zip) |

## What is included
Each ZIP contains one multi-take FBX, a README and a rights notice. A01 and A02 include their NOTICE.txt; the repository's ASSET_RIGHTS.md remains applicable and unchanged. Exact texture atlases are embedded in every FBX. All ZIPs except B33 also contain a standalone atlas. For B33, [download its separate exact atlas](downloads/b33_tex_014560_cmpr.png) and place it beside the extracted FBX if your importer needs external textures.

The existing GLBs and their viewer remain unchanged. These FBX downloads are not played in the browser gallery.

## A01: qualified converted asset, not engine-ready integration

A01 adds a separate 102-slot baked FBX bank. The old A01 GLB and its 102 accessory/reference clips are unchanged; they are not the same deliverable and are not added again to the FBX count. The new slots include static poses, a body-static slot000 with effect motion, and short fragments, not 102 uniquely named gameplay animations.

Import uses a **30,000-FPS compatibility clock and changes the global Blender scene FPS**. Physical take seconds are preserved. Use an isolated scene or separately validated clock normalization; do not silently retime or mix clocks. All 102 actions passed 17,956 deterministic actual-Blender witness queries (87,032,732 vertex comparisons, maximum position error 0.002316012 against the unchanged 0.005 gate). Sampled success does not certify engine resampling or native-game equivalence.

The runtime companion is **data, formulas and instructions, not executable integration**. Four billboard strips need camera-facing geometry and material/render-state implementation in the target runtime; the FBX supplies their animated anchors, not rendered camera-facing effects. Four ordinary rigid strips are already included in the FBX and must not be duplicated. The additive source-alpha-plus-destination contract and depth/cull settings are documented in the package, but target-engine camera/material/pass integration remains unverified. Body/attachment and atlas diagnostics were inspected; that does not certify billboard additive rendering. Unreal and native-game playback are not certified.

## A02: qualified body export, not full native rendering

A02 contains 102 finite body-animation slots, including short fragments and poses, not 102 uniquely named gameplay animations. The flat-world baked delivery rig contains six retained draw meshes and three exact atlases, both embedded and external. Source-hidden helper boxes are omitted based on verified default-hidden flags. Runtime visibility, node3 auxiliary effects, dynamic materials and original shaders/pass behavior remain unqualified.

The **30,000-FPS import clock changes global Blender scene FPS while preserving physical seconds**. Use an isolated scene or separately validated clock normalization. Do not reset FPS alone or silently mix other-rate animations. All 102 actions passed 102,330 actual-Blender witness queries (534,674,250 vertex comparisons; maximum position error 0.00286301847375 against the unchanged 0.005 gate). Four diagnostic views were inspected for body/attachment coherence and atlas placement. These checks do not establish Unreal/other-engine equivalence, seamless gameplay loops or original hardware/shader behavior. Package VALIDATION.json and previews provide bounded evidence, not additional completed-runtime claims.

## Important limits
- The standard A21 package has 55 takes. The optional mixed56 package overlaps all 55 and adds only slot006, a fixed-120-Hz approximation. Do not add 55 and 56 together. Slot006 was checked at nominal 30/60/120-Hz samples; arbitrary-time interpolation remains unqualified and off-grid error was substantially higher.
- B26 has 17 moving takes and three static representatives (075, 081, 097). Slot006 retains its targeted-preview label, not strict qualification.
- B33 is the 12-part default-visible model, not the full 18-part variant. NATIVE_STANDARD_WEIGHT in retained take names describes weighting, not validated native-game playback.
- A04, A05, A06, A24, A25, B03, B24 and B27 currently provide only their first checked take, slot001. No claim is made that their other animations are finished.
- Compatibility exports were checked in Blender 4.3.2. Geometric normals, corrected visibility metadata and selected winding fixes are documented approximations. Source positions, animation data and exact FBX bytes are preserved by this packaging step; no re-export or resampling was performed.
- Unreal behavior, native-game fidelity, source frame-rate interpretation, arbitrary-time interpolation and seamless loops are not certified. Read each package README for its specific validation and limits.
- Held, provisional and unverified candidates are excluded. No ROMs, executables, research caches or private paths are included.

[Machine-readable catalog](catalog.json) · [SHA-256 checksums](SHA256SUMS) · [Asset rights](../ASSET_RIGHTS.md)

Publication does not imply unrestricted, commercial-use or open-source rights to original game content.



