"""Validate public inventory joins, labels, CSVs, totals and download bytes.

Only the public checkout is needed. Label checks establish evidence consistency,
not canonical game identities. Private extractor payloads are not read.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
AVAILABILITY = {"verified-local", "missing-local", "hash-mismatch"}
CONVERSIONS = {"historical-converted", "preserved-primary-export"}
SOURCE_STATUSES = {"converted", "unsupported", "failed", "existing", "not-model"}
PRIVATE_KEYS = {"package", "package_member", "export_path", "local_path", "download_url", "private_download_url"}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def sha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def nonnegative(value):
    return type(value) is int and value >= 0


def relative_path(value):
    return (isinstance(value, str) and bool(value) and ":" not in value
            and "\\" not in value and not value.startswith("/")
            and ".." not in PurePosixPath(value).parts
            and value == PurePosixPath(value).as_posix()
            and not any(ord(char) < 32 for char in value))


def privacy(value, location="document"):
    if isinstance(value, dict):
        for key, item in value.items():
            check(key not in PRIVATE_KEYS, f"Private payload locator at {location}/{key}")
            privacy(item, f"{location}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            privacy(item, f"{location}/{index}")
    elif isinstance(value, str):
        check(not re.search(r"(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|file://|\\\\[^\\]+\\)", value),
              f"Workstation locator at {location}")
        check(not re.search(r"https?://\S*(?:[?&](?:token|signature|auth)=|/assets/(?:nonzoid|zoids)/)", value, re.I),
              f"Private or signed payload URL at {location}")


def read_json(root, name):
    return json.loads((root / name).read_text(encoding="utf-8"))


def exact_totals(actual, expected, location):
    for key, value in expected.items():
        check(key in actual and actual[key] == value, f"Total mismatch: {location}/{key}")


def check_versions(info, location):
    versions = info.get("labels_by_version")
    check(isinstance(versions, dict) and versions, f"Missing map label versions: {location}")
    for version, labels in versions.items():
        check(version in {"working", "Japanese-backup"}, f"Unknown map version: {location}")
        check(isinstance(labels, list) and labels and len(set(labels)) == len(labels),
              f"Empty or duplicate map labels: {location}/{version}")
        for label in labels:
            check(isinstance(label, str) and label and "\0" not in label,
                  f"Invalid map label: {location}/{version}")
            check(len(label.encode("cp932")) < 50, f"Map label exceeds retained slot: {location}")
    check(type(info.get("multiple_labels_within_version")) is bool, f"Missing map ambiguity flag: {location}")
    check(info["multiple_labels_within_version"] == any(len(labels) > 1 for labels in versions.values()),
          f"Map ambiguity mismatch: {location}")
    expected_status = ("context-dependent-or-conflicting-labels" if info["multiple_labels_within_version"]
                       else "single-label-per-version; static-link-only")
    check(info.get("status") == expected_status, f"Map label qualification mismatch: {location}")


def retained_label(info, display_field, max_bytes, trim, location):
    raw, display = info.get("retained_source_label"), info.get(display_field)
    check(isinstance(raw, str) and raw and "\0" not in raw, f"Missing retained source text: {location}")
    check(len(raw.encode("cp932")) < max_bytes
          and info.get("label_source_byte_length") == len(raw.encode("cp932")),
          f"Retained label byte length mismatch: {location}")
    check(isinstance(display, str) and display and raw.rstrip(trim) == display,
          f"Retained/display normalization mismatch: {location}")
    check(type(info.get("label_whitespace_normalized")) is bool
          and info["label_whitespace_normalized"] == (raw != display),
          f"Label normalization flag mismatch: {location}")


def validate_map_info(files, models):
    stage_info = {}
    map_records = defaultdict(lambda: defaultdict(set))
    evidence_paths = defaultdict(list)
    for row in files:
        info = row.get("map_info")
        if info is None:
            continue
        location = row["path"]
        stage_id = info.get("stage_info_id")
        check(type(stage_id) is int and 0 <= stage_id <= 99, f"Bad stage-info ID: {location}")
        check(info.get("canonical_name", "missing") is None, f"Unqualified canonical map name: {location}")
        check(isinstance(info.get("status"), str) and info["status"], f"Missing map status: {location}")
        if re.fullmatch(r"stage/st\d{2}\.i", location):
            check(location == f"stage/st{stage_id:02d}.i", f"Stage-info resource mismatch: {location}")
            check(stage_id not in stage_info, f"Duplicate stage-info resource: {stage_id}")
            check_versions(info, location)
            stage_info[stage_id] = info
        else:
            path = PurePosixPath(location)
            check(row["category"] == "menu" and re.fullmatch(r"[BM]\d{3}\.mg", path.name),
                  f"Unproved map-info filename promoted: {location}")
            check(row["bytes"] == 0x3300, f"Map-info source length mismatch: {location}")
            version = info.get("version_kind")
            check(version in {"working", "Japanese-backup"}, f"Unknown map record version: {location}")
            expected_parent = ("menu/map_info_dat" if version == "working" else
                               "menu/map_info_dat/ACTUAL ACUTAL BACKUPS DO NOT EDIT/map_info_dat")
            check(path.parent.as_posix() == expected_parent, f"Unexpected retained map directory: {location}")
            label = info.get("entry_zero_label")
            check(isinstance(label, str) and label and "\0" not in label and len(label.encode("cp932")) < 50,
                  f"Invalid entry-zero map label: {location}")
            check(info.get("status") == "static-B-or-M-reader-renderer-link"
                  and info.get("stage_info_source_path") == f"stage/st{stage_id:02d}.i",
                  f"Unproved map-info source association: {location}")
            retained_label(info, "entry_zero_label", 50, " \r\n\u3000", location)
            check(info.get("label_absolute_offset") == 0x240, f"Map label offset mismatch: {location}")
            map_records[stage_id][version].add(label)
            evidence_paths[stage_id].append(location)
    check(set(stage_info) == set(map_records), "Stage-info resources and bounded map records differ")
    for stage_id, info in stage_info.items():
        actual = {key: set(labels) for key, labels in info["labels_by_version"].items()}
        check(actual == dict(map_records[stage_id]), f"Map labels disagree with retained records: {stage_id}")
        check(info.get("evidence_source_paths") == sorted(evidence_paths[stage_id]),
              f"Map evidence-source coverage mismatch: {stage_id}")
    for row in models:
        info = row.get("map_info")
        if info is None:
            continue
        stage_id = info.get("stage_info_id")
        check(type(stage_id) is int and stage_id in stage_info, f"Missing labeled stage-info source: {row['id']}")
        # Only stage54 has a separate, pinned same-argument geometry association.
        # A matching numeric filename is not enough evidence for other models.
        check(row["category"] == "stage" and row["id"] == "stage__st54" and stage_id == 54
              and row["source_path"] == "stage/st54.dat" and info.get("stage_info_source_path") == "stage/st54.i",
              f"Map label assigned to unrelated geometry: {row['id']}")
        check(info.get("association") == "source-supported same numeric stage argument in LoadStageData2__; battle-selection caller chain unverified",
              f"Missing qualified geometry association: {row['id']}")
        check_versions(info, row["id"])
        for field in stage_info[stage_id]:
            check(info.get(field) == stage_info[stage_id].get(field),
                  f"Model/source map label mismatch: {row['id']}/{field}")
    return {"map_info_resources": len(stage_info),
            "map_info_inputs": sum(len(paths) for paths in evidence_paths.values()),
            "ambiguous_map_info_resources": sum(info["multiple_labels_within_version"] for info in stage_info.values())}


def map_labels(row):
    info = row.get("map_info", {})
    if "labels_by_version" in info:
        return " | ".join(f"{version}: {label}" for version, labels in info["labels_by_version"].items() for label in labels)
    if "entry_zero_label" in info:
        return f"{info['version_kind']}: {info['entry_zero_label']}"
    return ""


def csv_value(row, field):
    if field == "retained_ui_display_label":
        value = row.get("identification", {}).get("retained_ui_display_label", "")
    elif field == "map_info_labels":
        value = map_labels(row)
    elif field == "map_info_status":
        value = row.get("map_info", {}).get("status", "")
    elif field == "catalog_snapshot_included":
        value = row.get("catalog_snapshot", {}).get("included", "")
    else:
        value = row.get(field, "")
    if value is None:
        return ""
    result = str(value)
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
        result = "'" + result
    return result


def validate_csv(root, name, records, key, required):
    with (root / "inventory" / name).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    check(len(fields) == len(set(fields)) and required <= set(fields), f"Missing/duplicate CSV columns: {name}")
    check(len(rows) == len(records) and len({row[key] for row in rows}) == len(rows), f"CSV row coverage mismatch: {name}")
    expected = {csv_value(row, key): row for row in records}
    check(set(expected) == {row[key] for row in rows}, f"CSV identity mismatch: {name}")
    for row in rows:
        check(None not in row and None not in row.values(), f"Ragged CSV row: {name}")
        for field in fields:
            check(row[field] == csv_value(expected[row[key]], field),
                  f"CSV value mismatch: {name}/{row[key]}/{field}")


def validate(root=ROOT):
    assets = read_json(root, "inventory/assets.json")
    sources = read_json(root, "inventory/sources.json")
    sections = read_json(root, "inventory/sections.json")
    models, files, categories = assets["records"], sources["records"], sections["sections"]
    for document, schema in ((assets, "zoids-assets-inventory-v1"), (sources, "zoids-source-files-inventory-v1"),
                             (sections, "zoids-sections-inventory-v1")):
        check(document.get("schema") == schema, "Unexpected inventory schema")
        date.fromisoformat(document["snapshot_date"])
        privacy(document)
    check(len({item["snapshot_date"] for item in (assets, sources, sections)}) == 1, "Snapshot dates disagree")
    check(assets["provenance"] == sources["provenance"] == sections["provenance"], "Provenance snapshots disagree")
    evidence = assets["provenance"]
    for field in ("extractor_commit", "decoding_catalog_commit"):
        check(re.fullmatch(r"[0-9a-f]{40}", evidence[field]) is not None, f"Invalid provenance commit: {field}")
    date.fromisoformat(evidence["decoding_catalog_recorded_date"])
    inputs = {entry["name"]: entry["sha256"] for entry in evidence["inputs"]}
    check(len(inputs) == len(evidence["inputs"]) and all(relative_path(name) and sha(value) for name, value in inputs.items()),
          "Invalid or duplicate provenance input")
    check(inputs.get("catalog.json") == digest(root / "catalog.json"), "Published catalog provenance hash differs")
    check(len({row["id"] for row in models}) == len(models), "Duplicate model IDs")
    check(len({row["path"] for row in files}) == len(files), "Duplicate source paths")
    check(len({row["id"] for row in categories}) == len(categories), "Duplicate category IDs")
    by_path = {row["path"]: row for row in files}
    by_category = {row["id"]: row for row in categories}
    hash_counts = Counter(row["sha256"] for row in files)
    public_catalog = read_json(root, "catalog.json")
    public = {row["model"]["path"]: row for row in public_catalog["assets"]}
    check(len(public) == len(public_catalog["assets"]), "Duplicate public model path")
    for row in files:
        name = row["path"]
        check(relative_path(name) and sha(row["sha256"]), f"Invalid source path/hash: {name}")
        check(row["category"] in by_category and row["category_title"] == by_category[row["category"]]["title"],
              f"Source category mismatch: {name}")
        check(row["category"] == (name.split("/")[0] if "/" in name else "root-metadata-and-executables"),
              f"Source family differs: {name}")
        check(row["provenance"] in {"image-identical", "local-generated"} and nonnegative(row["bytes"]),
              f"Invalid source status/size: {name}")
        check(row["same_content_files"] == hash_counts[row["sha256"]], f"Content-copy count mismatch: {name}")
        check(row.get("historical_conversion_status", "converted") in SOURCE_STATUSES,
              f"Unknown source conversion status: {name}")
    for path, row in public.items():
        check(relative_path(path) and path.startswith("models/") and path.endswith(".glb"),
              f"Unsafe public model path: {path}")
        source = by_path.get(row["source_asset"])
        check(source is not None and source["sha256"] == row["source_sha256"], f"Public source join mismatch: {path}")
        payload = (root / path).resolve()
        check(payload.is_relative_to(root.resolve()) and payload.is_file(), f"Missing/outside public model: {path}")
        check(payload.stat().st_size == row["model"]["bytes"] and digest(payload) == row["model"]["sha256"],
              f"Public model bytes changed: {path}")
    identified, display_labels, linked_downloads = 0, 0, set()
    for row in models:
        name, source_path = row["id"], row["source_path"]
        check(re.fullmatch(r"[a-z0-9_]+", name) and relative_path(source_path) and source_path in by_path,
              f"Invalid model/source identity: {name}")
        source = by_path[source_path]
        for field, source_field in (("source_sha256", "sha256"), ("source_bytes", "bytes"), ("category", "category"),
                                    ("category_title", "category_title")):
            check(row[field] == source[source_field], f"Model/source mismatch: {name}/{field}")
        check(sha(row["export_sha256"]) and nonnegative(row["export_bytes"]) and row["export_bytes"] > 0,
              f"Invalid export identity: {name}")
        check(row["availability"] in AVAILABILITY and row["conversion_status"] in CONVERSIONS, f"Unknown model status: {name}")
        check(row["validation_source"] in {"extractor-export", "published-model"}, f"Unknown validation source: {name}")
        historical = row["conversion_status"] == "historical-converted"
        check(row["validation_source"] == ("extractor-export" if historical else "published-model"),
              f"Model validation origin mismatch: {name}")
        check(source.get("historical_conversion_status") == ("converted" if historical else "existing"),
              f"Historical/source classification mismatch: {name}")
        snapshot = row["catalog_snapshot"]
        check(set(snapshot) == {"as_of", "included", "package_recorded"}, f"Unexpected upstream snapshot fields: {name}")
        date.fromisoformat(snapshot["as_of"])
        check(snapshot["as_of"] == evidence["decoding_catalog_recorded_date"], f"Upstream catalog date mismatch: {name}")
        check(type(snapshot["included"]) is bool and type(snapshot["package_recorded"]) is bool,
              f"Invalid upstream snapshot flags: {name}")
        check(snapshot["included"] == snapshot["package_recorded"], f"Snapshot inclusion/package evidence mismatch: {name}")
        published = row.get("published_model")
        if published is not None:
            check(published in public, f"Unpublished download: {name}")
            download = public[published]
            check(download["source_asset"] == source_path and download["source_sha256"] == row["source_sha256"],
                  f"Public/source identity mismatch: {name}")
            same_export = download["model"]["sha256"] == row["export_sha256"]
            if same_export:
                check(download["model"]["bytes"] == row["export_bytes"], f"Identical export hash has conflicting size: {name}")
            check(row["published_export_matches_record"] is same_export, f"Public export comparator mismatch: {name}")
            check(row.get("published_export_matches_historical") is (same_export if historical else None),
                  f"Historical public comparator mismatch: {name}")
            linked_downloads.add(published)
        else:
            check(row.get("published_export_matches_record") is None and row.get("published_export_matches_historical") is None,
                  f"Comparator without public model: {name}")
        if row["validation_source"] == "published-model" or not historical:
            check(published is not None and row["published_export_matches_record"] is True,
                  f"Preserved/public validation lacks exact model: {name}")
        validation = row.get("validation")
        if row["availability"] == "verified-local":
            check(isinstance(validation, dict) and validation.get("sha256_verified") is True
                  and validation.get("glb2_header_json_valid") is True, f"Verified record lacks bounded checks: {name}")
            check(validation.get("runtime_verified") is False and validation.get("visual_verified") is False,
                  f"Unqualified fidelity claim: {name}")
            check(validation.get("chunk_and_buffer_view_bounds_valid") is True
                  and validation.get("status") == "passed-container-and-embedding-checks",
                  f"Verified record lacks bounded container checks: {name}")
            for field in ("meshes", "images", "textures", "materials", "animations", "embedded_buffer_view_images",
                          "data_uri_images", "external_image_uris", "external_buffer_uris"):
                check(nonnegative(validation.get(field)), f"Invalid GLB count: {name}/{field}")
            check(validation["images"] == validation["embedded_buffer_view_images"] + validation["data_uri_images"]
                  and validation["external_image_uris"] == validation["external_buffer_uris"] == 0,
                  f"Embedded GLB accounting mismatch: {name}")
        else:
            check(validation is None, f"Unavailable record has passed validation: {name}")
        if "animation_status" in row:
            check(isinstance(row["animation_status"], str) and row["animation_status"], f"Invalid animation qualification: {name}")
        identity = row.get("identification")
        if identity is not None:
            identified += 1
            code, parts = identity["resource_code"], identity["part_ids"]
            check(row["category"] == "weapon" and re.fullmatch(r"w[abs]\d{4}", code)
                  and source_path == f"weapon/{code}.dat", f"Weapon resource join mismatch: {name}")
            check(parts and parts == sorted(set(parts)) and all(type(part) is int and part > 0 for part in parts),
                  f"Invalid weapon part IDs: {name}")
            table = by_path["etc/n_Parts.dat"]
            check(all(part * 292 + 0x48 + len(code) < table["bytes"] for part in parts), f"Weapon part ID outside table: {name}")
            check(identity.get("canonical_name", "missing") is None, f"Unqualified weapon canonical name: {name}")
            label = identity.get("retained_ui_display_label")
            if label is not None:
                display_labels += 1
                check(isinstance(label, str) and label and "\0" not in label and len(label.encode("cp932")) < 21,
                      f"Invalid retained weapon label: {name}")
                check(identity.get("status") == "retained-UI-display-label; runtime-copy-unverified",
                      f"Missing retained-label qualification: {name}")
                check(identity.get("label_source_path") == table["path"]
                      and identity.get("label_source_sha256") == table["sha256"],
                      f"Weapon label source evidence mismatch: {name}")
                retained_label(identity, "retained_ui_display_label", 0x48 - 0x33, " ", name)
                check(identity.get("label_absolute_offset") in {part * 292 + 0x33 for part in parts},
                      f"Weapon label/part offset mismatch: {name}")
    check(linked_downloads == set(public), "Inventory does not cover every published model")
    check({row["source_path"] for row in models if row["conversion_status"] == "historical-converted"}
          == {row["path"] for row in files if row.get("historical_conversion_status") == "converted"},
          "Historical model census coverage differs")
    map_counts = validate_map_info(files, models)
    model_summary = {
        "model_records": len(models),
        "historical_models": sum(row["conversion_status"] == "historical-converted" for row in models),
        "preserved_models": sum(row["conversion_status"] == "preserved-primary-export" for row in models),
        "verified_local_models": sum(row["availability"] == "verified-local" for row in models),
        "missing_local_models": sum(row["availability"] == "missing-local" for row in models),
        "hash_mismatch_models": sum(row["availability"] == "hash-mismatch" for row in models),
        "export_bytes": sum(row["export_bytes"] for row in models), "published_models": len(public),
        "weapon_resource_joins": identified, "weapon_display_labels": display_labels, **map_counts,
        "upstream_included_models": sum(row["catalog_snapshot"]["included"] for row in models),
        "upstream_pending_models": sum(not row["catalog_snapshot"]["included"] for row in models),
    }
    provenance = Counter(row["provenance"] for row in files)
    source_summary = {
        "files": len(files), "bytes": sum(row["bytes"] for row in files), "unique_content_hashes": len(hash_counts),
        "duplicate_content_groups": sum(count > 1 for count in hash_counts.values()),
        "duplicate_file_records": sum(count - 1 for count in hash_counts.values()),
        "image_identical": provenance["image-identical"], "local_only_generated": provenance["local-generated"],
    }
    exact_totals(assets["summary"], model_summary, "models")
    # Package manifests are intentionally absent from the public inventory. Their
    # totals are inherited metadata; check shape/parity without claiming rehashing.
    for field in ("upstream_package_count", "upstream_package_bytes"):
        check(nonnegative(assets["summary"].get(field)), f"Invalid inherited package total: {field}")
    exact_totals(sources["summary"], source_summary, "sources")
    check(sections["summary"] == {**sources["summary"], **assets["summary"]}, "Section/model/source summaries disagree")
    for section in categories:
        source_rows = [row for row in files if row["category"] == section["id"]]
        model_rows = [row for row in models if row["category"] == section["id"]]
        expected = {
            "source_files": len(source_rows), "source_bytes": sum(row["bytes"] for row in source_rows),
            "unique_source_hashes": len({row["sha256"] for row in source_rows}),
            "image_identical": sum(row["provenance"] == "image-identical" for row in source_rows),
            "local_generated": sum(row["provenance"] == "local-generated" for row in source_rows),
            "model_records": len(model_rows),
            "historical_models": sum(row["conversion_status"] == "historical-converted" for row in model_rows),
            "preserved_models": sum(row["conversion_status"] == "preserved-primary-export" for row in model_rows),
            "verified_local_models": sum(row["availability"] == "verified-local" for row in model_rows),
            "published_models": sum(by_path[row["source_asset"]]["category"] == section["id"] for row in public.values()),
        }
        exact_totals(section, expected, section["id"])
    for group in assets["source_model_groups"]:
        matched = [row for row in files if re.fullmatch(group["source_path_pattern"], row["path"])]
        check(group["source_files"] == len(matched), f"Source group total mismatch: {group['title']}")
        check(group["historical_conversion_statuses"] == dict(Counter(row.get("historical_conversion_status", "not-catalogued") for row in matched)),
              f"Source group conversion mismatch: {group['title']}")
    validate_csv(root, "assets.csv", models, "id", {
        "id", "source_path", "source_sha256", "export_sha256", "availability", "published_model",
        "conversion_status", "validation_source", "retained_ui_display_label", "map_info_labels", "catalog_snapshot_included",
        "animation_status"})
    validate_csv(root, "sources.csv", files, "path", {
        "path", "sha256", "provenance", "same_content_files", "historical_conversion_status", "map_info_labels", "map_info_status"})
    return model_summary, source_summary, len(categories)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    models, sources, category_count = validate(args.root.resolve())
    print(f"PASS: {models['model_records']} model records ({models['historical_models']} historical + {models['preserved_models']} preserved), "
          f"{sources['files']} source files, {category_count} categories; {models['weapon_display_labels']} retained weapon labels, "
          f"{models['map_info_resources']} bounded stage-info joins; CSV parity, totals and {models['published_models']} public downloads verified.")


if __name__ == "__main__":
    main()
