# Extractor asset inventory

Verified snapshot: **2026-10-26** (America/New_York).

[Browse and search the inventory](inventory/) · [Model JSON](inventory/assets.json) · [Model CSV](inventory/assets.csv) · [Source-file JSON](inventory/sources.json) · [Source-file CSV](inventory/sources.csv)

**631 model records** combine **627 historical conversions** with **4 preserved public exports**. All **631 verified local GLBs** match their recorded SHA-256 and pass bounded container and embedding checks. This covers 224 weapons, 207 maps/stage objects, 108 character-category models, 92 Zoid records. These are model records; their counts do not establish complete maps or verified weapon identities.

The source census contains **12,609 files**: **12,572** match the retained translated-image comparison and **37** are local generated files. Backups and other copies remain separate file records. The 92 published gallery models overlap the model inventory and must not be added to it as unique assets.

| Family | Source files | Image-identical | Local generated | Model records | Historical conversions | Preserved exports | Verified local GLBs | Published models |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Audio and music | 419 | 419 | 0 | 0 | 0 | 0 | 0 | 0 |
| Characters | 296 | 296 | 0 | 108 | 108 | 0 | 108 | 0 |
| Debug resources | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| Disc metadata and program binaries | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| Effects | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| Ending and credits | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| Filters | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| Gameplay data and miscellaneous | 4,416 | 4,416 | 0 | 0 | 0 | 0 | 0 | 0 |
| HUD and display | 117 | 117 | 0 | 0 | 0 | 0 | 0 | 0 |
| Interface layouts | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| Maps and stages | 457 | 457 | 0 | 207 | 207 | 0 | 207 | 0 |
| Menus and UI | 1,427 | 1,427 | 0 | 0 | 0 | 0 | 0 | 0 |
| Movies | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| Particles | 12 | 12 | 0 | 0 | 0 | 0 | 0 | 0 |
| Projectiles | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| Standalone textures | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| Text rendering | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| Unclassified resources | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| Voices | 1,272 | 1,272 | 0 | 0 | 0 | 0 | 0 | 0 |
| Weapons | 3,215 | 3,215 | 0 | 224 | 224 | 0 | 224 | 0 |
| Zoid models and related parameters | 944 | 907 | 37 | 92 | 88 | 4 | 92 | 92 |

## Weapons and stage coverage

These filename groups make unconverted resources visible without treating every source file as a complete model. Their statuses come from the hash-matched historical conversion report.

| Source filename group | Files | Converted | Unsupported | Failed |
| --- | ---: | ---: | ---: | ---: |
| Canonical weapon filenames (wa/wb/ws + four digits) | 432 | 223 | 202 | 7 |
| Base stage filenames (st + two digits) | 95 | 94 | 0 | 1 |
| Base sky filenames (skymap + two digits) | 95 | 68 | 27 | 0 |
| Stage object DAT filenames | 24 | 23 | 0 | 1 |

The converted weapon set includes `weapon/debug.dat`. Stage exports include sky, variant and object resources, so their total does not represent assembled maps. All source files, including unsupported and failed resources, remain searchable in the source-file inventory.

## Reading the inventory

There are 8,875 distinct source SHA-256 values across the file census. `same_content_files` identifies byte-identical copies without merging their paths. Distinct hashes are still not a count of semantically unique assets. Where the conversion report covers a source file, `historical_conversion_status` preserves its converted, unsupported, failed, existing or not-model result.

`source_path` and source-file `path` values are relative to the extractor's `GAME DATA` directory. SHA-256 values identify exact source and export bytes. `availability` describes locally verified bytes; `validation_source` distinguishes extractor exports from preserved public models. `published_model` is populated only for an existing public gallery download. Local-only conversion records do not imply a new public payload release.

The upstream catalog records **631 models included in 22 packages** and **0 pending recovered models**. `catalog_snapshot` preserves that metadata independently of local verification and public download availability. Package archives were not downloaded or revalidated in this pass; manifest membership, sizes and hashes were reconciled with the catalog. Private package paths and locators are omitted.

**217 weapon records** carry retained UI labels, bounded resource-code/part-ID joins and explicit confidence. The parts table hash, resource strings and label offsets were checked. Catalog display labels may omit trailing ASCII spaces; the exact retained source label, byte length and normalization flag are recorded. Canonical names, mounts, the runtime table copy and runtime identities remain unverified.

**31 stage-info resources** carry labels from **146 statically linked B/M map-info files**; **4 resources have multiple labels within a version**. Working translations and retained Japanese backups remain separate. Catalog display text omits trailing ASCII/ideographic spaces and CR/LF; the original bounded source labels are retained as metadata. Labels describe entry-zero display text and may be mission or subarea names. These joins attach to exact `.i` and `.mg` sources. Only `stage/st54.dat` additionally carries the catalog's explicit same-stage-argument association with the retained Zoid Road label; complete map assembly and the battle-selection caller chain remain unverified.

The GLB check covers magic/version, file and chunk lengths/alignment, JSON, buffer and buffer-view bounds, embedded image references, and resource URI counts. It records mesh/image/texture/material/animation counts. It does not establish full glTF conformance, topology, visual fidelity, application import, animation correctness, complete map assembly, collision or runtime behavior. The image itself was not independently re-extracted in this pass.

## Provenance and regeneration

The builder uses the decoding catalog's 631 model records, section descriptions, retained-label evidence and package manifest, the extractor source census and image comparison, and the public gallery catalog. Each JSON includes the input hashes and repository commit IDs. Input `hash_mode` distinguishes exact evidence bytes from catalog JSON with CRLF normalized to LF, so metadata fingerprints remain consistent across checkouts. Source-file and model hashes always identify exact bytes. Static consumer analysis is inherited from the hashed catalog evidence with its source ELF hash checked; no runtime claim is added. Absolute workstation paths, private package locators, research code and raw game payloads are excluded. Upstream records carry a 2026-10-27 date; that original value is recorded separately from this verification date.

Run with Python 3.11 or newer; only the standard library is needed:

```text
python scripts/build_inventory.py --extractor-root <extractor-workspace> --reference-root <decoding-repository> --snapshot-date 2026-10-26
```

The command checks the complete current source tree against the retained evidence, rehashes local model exports and existing published models, then writes the JSON/CSV files and this document. Source-tree or source-hash drift aborts generation. Missing or changed historical exports are explicitly recorded; invalid matching GLB containers abort generation. Inputs must be the evidence version intended for the new snapshot.

Validate the published metadata, CSV parity, category totals and public download hashes without the extractor workspace:

```text
python scripts/validate_inventory.py
```
