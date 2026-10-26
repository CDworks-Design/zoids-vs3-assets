#!/usr/bin/env python3
"""Build a metadata-only inventory from locally verified extractor evidence.

Python 3.11+, standard library only. No source payloads are copied. Source files
are checked against both the census and image-comparison evidence before output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import struct
import subprocess
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path, PurePosixPath


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def relative_path(value):
    path = PurePosixPath(value)
    if not value or "\\" in value or ":" in value or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Invalid relative path: {value!r}")
    return path.as_posix()


def safe_file(root, value):
    path = (root / relative_path(value)).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Path escapes the supplied root")
    return path


def git_sha(root):
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def inspect_glb(path):
    """Bounded container and embedding checks, not a glTF conformance audit."""
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError(f"Truncated GLB: {path.name}")
    magic, version, declared = struct.unpack_from("<4sII", data)
    if (magic, version, declared) != (b"glTF", 2, len(data)):
        raise ValueError(f"Invalid GLB header: {path.name}")
    offset, chunks = 12, []
    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError(f"Truncated chunk: {path.name}")
        length, kind = struct.unpack_from("<II", data, offset)
        offset += 8
        if length % 4 or offset + length > len(data):
            raise ValueError(f"Invalid chunk bounds: {path.name}")
        chunks.append((kind, data[offset:offset + length]))
        offset += length
    if not chunks or chunks[0][0] != 0x4E4F534A or sum(k == 0x4E4F534A for k, _ in chunks) != 1:
        raise ValueError(f"Invalid JSON chunk: {path.name}")
    doc = json.loads(chunks[0][1].decode("utf-8"))
    if doc.get("asset", {}).get("version") != "2.0":
        raise ValueError(f"Invalid glTF asset version: {path.name}")
    bins = [b for k, b in chunks if k == 0x004E4942]
    if len(bins) > 1:
        raise ValueError(f"Multiple BIN chunks: {path.name}")
    buffers, views, images = doc.get("buffers", []), doc.get("bufferViews", []), doc.get("images", [])
    for index, buffer in enumerate(buffers):
        if "uri" not in buffer:
            if index != 0 or not bins or not 0 <= buffer["byteLength"] <= len(bins[0]) or len(bins[0]) - buffer["byteLength"] > 3:
                raise ValueError(f"Invalid embedded buffer: {path.name}")
    for view in views:
        index = view["buffer"]
        if not isinstance(index, int) or not 0 <= index < len(buffers):
            raise ValueError(f"Invalid buffer reference: {path.name}")
        start, length = view.get("byteOffset", 0), view["byteLength"]
        if start < 0 or length < 0 or start + length > buffers[index]["byteLength"]:
            raise ValueError(f"Invalid buffer view bounds: {path.name}")
    for image in images:
        if "bufferView" in image and not 0 <= image["bufferView"] < len(views):
            raise ValueError(f"Invalid image buffer view: {path.name}")
    external_images = sum("uri" in item and not item["uri"].startswith("data:") for item in images)
    external_buffers = sum("uri" in item and not item["uri"].startswith("data:") for item in buffers)
    return {
        "status": "passed-container-and-embedding-checks",
        "sha256_verified": True,
        "glb2_header_json_valid": True,
        "chunk_and_buffer_view_bounds_valid": True,
        "meshes": len(doc.get("meshes", [])),
        "images": len(images),
        "textures": len(doc.get("textures", [])),
        "materials": len(doc.get("materials", [])),
        "animations": len(doc.get("animations", [])),
        "embedded_buffer_view_images": sum("bufferView" in item for item in images),
        "data_uri_images": sum(item.get("uri", "").startswith("data:") for item in images),
        "external_image_uris": external_images,
        "external_buffer_uris": external_buffers,
        "runtime_verified": False,
        "visual_verified": False,
    }


def csv_text(records, columns):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, columns, lineterminator="\n")
    writer.writeheader()
    for record in records:
        row = {key: record.get(key, "") for key in columns}
        for key, value in row.items():
            if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
                row[key] = "'" + value
        writer.writerow(row)
    return output.getvalue()


def build(extractor, reference, destination, snapshot_date):
    date.fromisoformat(snapshot_date)
    source_input = "decompilation/source_inventory/inventory.json"
    compare_input = "decompilation/image_compare/image_comparison.json"
    conversion_input = "sandbox_converted/conversion_report.json"
    census = read_json(extractor / source_input)
    comparison = read_json(extractor / compare_input)
    conversion = read_json(extractor / conversion_input)
    historical = read_json(reference / "catalog/assets.json")
    section_input = read_json(reference / "catalog/sections.json")
    identity = read_json(reference / "catalog/identification.json")
    published = read_json(destination / "catalog.json")
    definitions = {item["id"]: item for item in section_input["sections"]}
    evidence = {
        "extractor_commit": git_sha(extractor),
        "decoding_catalog_commit": git_sha(reference),
        "decoding_catalog_recorded_date": historical["as_of"],
        "date_note": "Snapshot date uses the requested America/New_York date; upstream recorded dates are preserved as evidence, not substituted for this verification date.",
        "inputs": [
            {"name": source_input, "sha256": sha256(extractor / source_input)},
            {"name": compare_input, "sha256": sha256(extractor / compare_input)},
            {"name": conversion_input, "sha256": sha256(extractor / conversion_input)},
            *({"name": "decoding/" + item, "sha256": sha256(reference / item)} for item in (
                "catalog/assets.json", "catalog/sections.json", "catalog/identification.json")),
            {"name": "catalog.json", "sha256": sha256(destination / "catalog.json")},
        ],
        "verification": "Current local source bytes rehashed against the census and retained image comparison. Local GLBs rehashed against historical conversion records. The disc image itself was not rerun or independently authenticated in this pass.",
        "image_provenance": "The image-comparison evidence concerns the locally held translated game image; it does not establish unmodified retail provenance.",
    }
    known = {}
    for group, rows in comparison["rows"].items():
        if rows and group not in ("image_identical", "local_only_generated"):
            raise ValueError(f"Unresolved image-comparison group: {group}")
        for row in rows:
            name = relative_path(row["path"])
            if name in known:
                raise ValueError(f"Duplicate comparison path: {name}")
            known[name] = (row, "image-identical" if group == "image_identical" else "local-generated")
    source_by_path = {relative_path(row["path"]): row for row in census["files"]}
    if len(source_by_path) != census["file_count"] or set(source_by_path) != set(known):
        raise ValueError("Census and image-comparison path coverage differs")
    game_root = extractor / "GAME DATA"
    actual_paths = {p.relative_to(game_root).as_posix() for p in game_root.rglob("*") if p.is_file()}
    if actual_paths != set(source_by_path):
        raise ValueError(f"Source tree drift: {len(actual_paths - set(source_by_path))} extra, {len(set(source_by_path) - actual_paths)} missing files")

    def verify_source(item):
        name, row = item
        compared, provenance = known[name]
        local = safe_file(game_root, name)
        digest, size = sha256(local), local.stat().st_size
        if digest != row["sha256"] or size != row["size"] or digest != compared["sha256"] or size != compared["size"]:
            raise ValueError(f"Source evidence mismatch: {name}")
        category = name.split("/")[0] if "/" in name else "root-metadata-and-executables"
        return {"path": name, "category": category, "category_title": definitions[category]["title"],
                "bytes": size, "sha256": digest, "provenance": provenance}

    with ThreadPoolExecutor(max_workers=8) as pool:
        sources = sorted(pool.map(verify_source, source_by_path.items()), key=lambda row: row["path"])
    sources_by_path = {row["path"]: row for row in sources}
    content_counts = Counter(row["sha256"] for row in sources)
    for row in sources:
        row["same_content_files"] = content_counts[row["sha256"]]
    conversion_by_source = {}
    for item in conversion["records"]:
        if not item["source"].startswith("GAME DATA/"):
            raise ValueError("Unexpected conversion source root")
        name = relative_path(item["source"][len("GAME DATA/"):])
        if name in conversion_by_source or sources_by_path[name]["sha256"] != item["fingerprint"]:
            raise ValueError("Conversion census source mismatch or duplicate")
        conversion_by_source[name] = item
        sources_by_path[name]["historical_conversion_status"] = item["status"]
    if {item["id"] for item in conversion["records"] if item["status"] == "converted"} != {item["id"] for item in historical["records"]}:
        raise ValueError("Historical conversion catalog coverage differs")
    published_by_source = defaultdict(list)
    for item in published["assets"]:
        source = relative_path(item["source_asset"])
        if sources_by_path[source]["sha256"] != item["source_sha256"]:
            raise ValueError(f"Published source hash differs: {item['id']}")
        model = item["model"]
        if sha256(safe_file(destination, model["path"])) != model["sha256"]:
            raise ValueError(f"Published model hash differs: {item['id']}")
        published_by_source[(source, item["source_sha256"])].append(item)
    parts_path = "GAME DATA/etc/n_Parts.dat"
    if sha256(safe_file(extractor, parts_path)) != identity["sources"][parts_path]["sha256"]:
        raise ValueError("Weapon identification table hash differs")
    part_bytes = safe_file(extractor, parts_path).read_bytes()
    links = defaultdict(list)
    for link in identity["weapon_links"]["links"]:
        code = link["resource_code"]
        offset = link["resource_name_field_offset"]
        record_offset = link["part_id"] * 292
        if (link["part_record_offset"] != record_offset or offset != record_offset + 0x48
                or not re.fullmatch(r"w[abs]\d{4}", code)
                or part_bytes[offset:offset + len(code) + 1] != code.encode("ascii") + b"\0"):
            raise ValueError("Weapon resource-string join differs")
        links[link["export_id"]].append(link)
    records = []
    for item in sorted(historical["records"], key=lambda row: row["id"]):
        if not item["source_path"].startswith("GAME DATA/"):
            raise ValueError("Unexpected model source root")
        source = relative_path(item["source_path"][len("GAME DATA/"):])
        entry = sources_by_path[source]
        if entry["sha256"] != item["source_sha256"]:
            raise ValueError(f"Historical source hash differs: {item['id']}")
        path = safe_file(extractor, item["export_path"])
        availability, validation = "missing-local", None
        if path.is_file():
            if sha256(path) != item["export_sha256"] or path.stat().st_size != item["bytes"]:
                availability = "hash-mismatch"
            else:
                availability, validation = "verified-local", inspect_glb(path)
        matches = published_by_source.get((source, item["source_sha256"]), [])
        record = {
            "id": item["id"], "category": item["category"], "category_title": definitions[item["category"]]["title"],
            "label": item["label"], "label_confidence": item["label_confidence"],
            "source_path": source, "source_sha256": entry["sha256"], "source_bytes": entry["bytes"],
            "export_bytes": item["bytes"], "export_sha256": item["export_sha256"],
            "conversion_status": "historical-converted", "availability": availability,
            "published_model": matches[0]["model"]["path"] if matches else None,
            "published_export_matches_historical": matches[0]["model"]["sha256"] == item["export_sha256"] if matches else None,
            "validation": validation, "remaining_work": item["remaining_work"],
        }
        if item["id"] in links:
            matched = links[item["id"]]
            if any(l["source_path"] != item["source_path"] for l in matched):
                raise ValueError("Identification source join differs")
            record["identification"] = {"resource_code": matched[0]["resource_code"],
                "part_ids": sorted({l["part_id"] for l in matched}),
                "confidence": "exact resource string and source table hash verified; canonical name and runtime identity unverified"}
        records.append(record)
    if len({row["id"] for row in records}) != len(records):
        raise ValueError("Duplicate historical model IDs")
    sections = []
    for category, definition in sorted(definitions.items(), key=lambda pair: pair[1]["title"]):
        source_rows = [row for row in sources if row["category"] == category]
        models = [row for row in records if row["category"] == category]
        sections.append({"id": category, "title": definition["title"], "purpose": definition["purpose"],
            "purpose_confidence": definition["purpose_confidence"], "source_files": len(source_rows),
            "unique_source_hashes": len({row["sha256"] for row in source_rows}),
            "source_bytes": sum(row["bytes"] for row in source_rows),
            "image_identical": sum(row["provenance"] == "image-identical" for row in source_rows),
            "local_generated": sum(row["provenance"] == "local-generated" for row in source_rows),
            "historical_models": len(models), "verified_local_models": sum(row["availability"] == "verified-local" for row in models),
            "published_models": sum(len(items) for (source, _), items in published_by_source.items() if sources_by_path[source]["category"] == category)})
    model_summary = {"historical_models": len(records), "verified_local_models": sum(row["availability"] == "verified-local" for row in records),
        "missing_local_models": sum(row["availability"] == "missing-local" for row in records),
        "hash_mismatch_models": sum(row["availability"] == "hash-mismatch" for row in records),
        "export_bytes": sum(row["export_bytes"] for row in records), "published_models": len(published["assets"]),
        "weapon_resource_joins": sum("identification" in row for row in records)}
    source_summary = {"files": len(sources), "bytes": sum(row["bytes"] for row in sources),
        "unique_content_hashes": len(content_counts),
        "duplicate_content_groups": sum(count > 1 for count in content_counts.values()),
        "duplicate_file_records": sum(count - 1 for count in content_counts.values()),
        "image_identical": sum(row["provenance"] == "image-identical" for row in sources),
        "local_only_generated": sum(row["provenance"] == "local-generated" for row in sources)}
    model_groups = []
    for title, pattern in (
        ("Canonical weapon filenames (wa/wb/ws + four digits)", r"weapon/(?:wa|wb|ws)\d{4}\.dat"),
        ("Base stage filenames (st + two digits)", r"stage/st\d{2}\.dat"),
        ("Base sky filenames (skymap + two digits)", r"stage/skymap\d{2}\.dat"),
        ("Stage object DAT filenames", r"stage/map_obj/[^/]+\.dat"),
    ):
        members = [row for row in sources if re.fullmatch(pattern, row["path"])]
        model_groups.append({"title": title, "source_path_pattern": pattern, "source_files": len(members),
            "historical_conversion_statuses": dict(sorted(Counter(row.get("historical_conversion_status", "not-catalogued") for row in members).items()))})
    common = {"snapshot_date": snapshot_date, "provenance": evidence}
    outputs = {
        "inventory/assets.json": {"schema": "zoids-assets-inventory-v1", **common, "summary": model_summary,
            "source_model_groups": model_groups,
            "limits": ["Historical model records are not a unique asset or whole-game completion count.",
                "Verified-local means matching bytes and bounded GLB container/embedding checks, not visual, import, animation or runtime verification.",
                "Published download availability is separate from local conversion availability; only existing public models have download links."], "records": records},
        "inventory/sources.json": {"schema": "zoids-source-files-inventory-v1", **common, "summary": source_summary,
            "limits": ["Paths are relative to GAME DATA; this inventory contains metadata only.",
                "File families include backups, translated-disc files and locally generated outputs; counts are not unique decoded assets.",
                "Image-identical records inherit the retained comparison evidence after current local-byte verification."], "records": sources},
        "inventory/sections.json": {"schema": "zoids-sections-inventory-v1", **common, "summary": {**source_summary, **model_summary}, "sections": sections},
    }
    contents = {name: json.dumps(value, ensure_ascii=False, indent=2) + "\n" for name, value in outputs.items()}
    contents["inventory/assets.csv"] = csv_text(records, ["id", "category", "category_title", "label", "source_path", "source_sha256", "source_bytes", "export_bytes", "export_sha256", "availability", "published_model", "label_confidence", "remaining_work"])
    contents["inventory/sources.csv"] = csv_text(sources, ["path", "category", "category_title", "bytes", "sha256", "provenance", "same_content_files", "historical_conversion_status"])
    model_counts = Counter(row["category"] for row in records)
    model_labels = {"weapon": "weapons", "stage": "maps/stage objects", "chara": "character-category models", "zoid": "Zoid records"}
    model_breakdown = ", ".join(
        f"{model_counts[category]:,} {model_labels.get(category, definitions[category]['title'])}"
        for category in [*model_labels, *sorted(set(model_counts) - set(model_labels))]
        if model_counts[category]
    )
    lines = ["# Extractor asset inventory", "", f"Verified snapshot: **{snapshot_date}** (America/New_York).", "",
        "[Browse and search the inventory](inventory/) · [Model JSON](inventory/assets.json) · [Model CSV](inventory/assets.csv) · [Source-file JSON](inventory/sources.json) · [Source-file CSV](inventory/sources.csv)", "",
        f"**{len(records):,} historical model conversion records** were reconciled with the extractor files; **{model_summary['verified_local_models']:,} local GLBs** match their recorded SHA-256 and pass bounded container and embedding checks. This covers {model_breakdown}. These are model records; their counts do not establish complete maps or verified weapon identities.", "",
        f"The source census contains **{len(sources):,} files**: **{source_summary['image_identical']:,}** match the retained translated-image comparison and **{source_summary['local_only_generated']}** are local generated files. Backups and other copies remain separate file records. The {model_summary['published_models']:,} published gallery models overlap the model inventory and must not be added to it as unique assets.", "",
        "| Family | Source files | Image-identical | Local generated | Historical models | Verified local GLBs | Published models |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in sections:
        lines.append(f"| {row['title']} | {row['source_files']:,} | {row['image_identical']:,} | {row['local_generated']:,} | {row['historical_models']:,} | {row['verified_local_models']:,} | {row['published_models']:,} |")
    lines += ["", "## Weapons and stage coverage", "",
        "These filename groups make unconverted resources visible without treating every source file as a complete model. Their statuses come from the hash-matched historical conversion report.", "",
        "| Source filename group | Files | Converted | Unsupported | Failed |",
        "| --- | ---: | ---: | ---: | ---: |"]
    for group in model_groups:
        status = group["historical_conversion_statuses"]
        lines.append(f"| {group['title']} | {group['source_files']} | {status.get('converted', 0)} | {status.get('unsupported', 0)} | {status.get('failed', 0)} |")
    debug_note = "The converted weapon set includes `weapon/debug.dat`. " if any(row["source_path"] == "weapon/debug.dat" for row in records) else ""
    lines += ["", debug_note + "Stage exports include sky, variant and object resources, so their total does not represent assembled maps. All source files, including unsupported and failed resources, remain searchable in the source-file inventory."]
    lines += ["", "## Reading the inventory", "",
        f"There are {len(content_counts):,} distinct source SHA-256 values across the file census. `same_content_files` identifies byte-identical copies without merging their paths. Distinct hashes are still not a count of semantically unique assets. Where the conversion report covers a source file, `historical_conversion_status` preserves its converted, unsupported, failed, existing or not-model result.", "",
        "`source_path` and source-file `path` values are relative to the extractor's `GAME DATA` directory. SHA-256 values identify exact source and export bytes. `availability` describes the local extractor export; `published_model` is populated only for an existing public gallery download. Local-only conversion records do not imply a new public payload release.", "",
        f"{model_summary['weapon_resource_joins']} weapon records carry bounded resource-code/part-ID joins. The underlying parts table hash and resource string offsets were checked; canonical weapon names, mounts and runtime identity remain unverified. Stage codes and source filenames are preserved without inventing map names.", "",
        "The GLB check covers magic/version, file and chunk lengths/alignment, JSON, buffer and buffer-view bounds, embedded image references, and resource URI counts. It records mesh/image/texture/material/animation counts. It does not establish full glTF conformance, topology, visual fidelity, application import, animation correctness, complete map assembly, collision or runtime behavior. The image itself was not independently re-extracted in this pass.", "",
        "## Provenance and regeneration", "",
        f"The builder uses the decoding catalog's {len(records):,} historical records and section descriptions, the extractor source census and image comparison, and the public gallery catalog. Each JSON includes the input hashes and repository commit IDs. Absolute workstation paths, private package locators, research code and raw game payloads are excluded. Upstream records carry a {historical['as_of']} date; that original value is recorded separately from this verification date.", "",
        "Run with Python 3.11 or newer; only the standard library is needed:", "", "```text",
        f"python scripts/build_inventory.py --extractor-root <extractor-workspace> --reference-root <decoding-repository> --snapshot-date {snapshot_date}", "```", "",
        "The command checks the complete current source tree against the retained evidence, rehashes local model exports and existing published models, then writes the JSON/CSV files and this document. Source-tree or source-hash drift aborts generation. Missing or changed historical exports are explicitly recorded; invalid matching GLB containers abort generation. Inputs must be the evidence version intended for the new snapshot.", "",
        "Validate the published metadata, CSV parity, category totals and public download hashes without the extractor workspace:", "", "```text", "python scripts/validate_inventory.py", "```", ""]
    contents["INVENTORY.md"] = "\n".join(lines)
    # All evidence checks finish before any generated file is replaced.
    for name, content in contents.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return {"sources": source_summary, "models": model_summary, "categories": len(sections)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extractor-root", required=True, type=Path)
    parser.add_argument("--reference-root", required=True, type=Path)
    parser.add_argument("--snapshot-date", required=True, help="YYYY-MM-DD in America/New_York")
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(build(args.extractor_root.resolve(), args.reference_root.resolve(), args.output_root.resolve(), args.snapshot_date), indent=2))


if __name__ == "__main__":
    main()
