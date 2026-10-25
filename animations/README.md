# Baked animation downloads

11 standard model IDs, 103 take records. This is an incomplete, experimental collection, not 103 unique moving animations or a complete roster export.

| Source ID | Edition | Take records | Download |
| --- | --- | ---: | --- |
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
Each ZIP contains one multi-take FBX, a README and the original asset-rights notice. Exact texture atlases are embedded in every FBX. All ZIPs except B33 also contain a standalone atlas. For B33, [download its separate exact atlas](downloads/b33_tex_014560_cmpr.png) and place it beside the extracted FBX if your importer needs external textures.

The existing GLBs and their viewer remain unchanged. These FBX downloads are not played in the browser gallery.

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

