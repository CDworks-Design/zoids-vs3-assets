# Gallery dependencies

The gallery uses **Three.js 0.170.0**, pinned to the official npm distribution `three@0.170.0`, from https://github.com/mrdoob/three.js (release tag `r170`).

The distribution archive's npm SHA-512 integrity value was verified before the required runtime files were copied. Only the core module, GLTFLoader, OrbitControls, BufferGeometryUtils, and the original license are included, under `vendor/three-0.170.0/`. No package installation is needed to serve this site.

Three.js is MIT licensed; see [the preserved Three.js license](vendor/three-0.170.0/LICENSE.three.txt). That license applies to the library code only. It grants no rights in Zoids game assets, renders, textures, names, or trademarks. See [ASSET_RIGHTS.md](ASSET_RIGHTS.md).

The gallery interface and integration code were authored for this project. No other website source or design was copied. The site uses system fonts, makes no analytics requests, and has no account or telemetry integration. Dependencies are served from the same site, with no runtime CDN requirement.
