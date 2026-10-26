"""Validate published inventory metadata without access to private source files."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)


def relative_path(value):
    return isinstance(value, str) and not re.search(r"(^/|^[A-Za-z]:|\\|(^|/)\.\.(/|$))", value)


def main():
    assets = read("inventory/assets.json")
    sources = read("inventory/sources.json")
    sections = read("inventory/sections.json")
    models = assets["records"]
    files = sources["records"]
    categories = sections["sections"]
    check(len({d["snapshot_date"] for d in (assets, sources, sections)}) == 1, "Snapshot dates disagree")
    check(len({r["id"] for r in models}) == len(models), "Duplicate model IDs")
    check(len({r["path"] for r in files}) == len(files), "Duplicate source paths")
    check(len({r["id"] for r in categories}) == len(categories), "Duplicate category IDs")
    by_path = {r["path"]: r for r in files}
    by_category = {r["id"]: r for r in categories}
    public = {r["model"]["path"]: r for r in read("catalog.json")["assets"]}
    for row in files:
        check(relative_path(row["path"]), "Unsafe source path")
        check(sha(row["sha256"]), f"Bad source hash: {row['path']}")
        check(row["category"] in by_category, f"Unknown source category: {row['path']}")
        check(row["provenance"] in {"image-identical", "local-generated"}, "Unresolved provenance")
        check(isinstance(row["bytes"], int) and row["bytes"] >= 0, "Invalid source size")
    for row in models:
        path = row["source_path"].removeprefix("GAME DATA/")
        check(relative_path(path) and path in by_path, f"Missing source for {row['id']}")
        source = by_path[path]
        check(row["source_sha256"] == source["sha256"], f"Source hash mismatch: {row['id']}")
        check(row["source_bytes"] == source["bytes"], f"Source size mismatch: {row['id']}")
        check(row["category"] == source["category"], f"Source category mismatch: {row['id']}")
        check(sha(row["export_sha256"]), f"Invalid export hash: {row['id']}")
        check(row["availability"] in {"verified-local", "missing-local", "hash-mismatch"}, "Unknown availability")
        published = row.get("published_model")
        if published:
            check(published in public and relative_path(published), f"Unpublished download: {published}")
            check(public[published]["source_sha256"] == row["source_sha256"], "Published source mismatch")
            payload = ROOT / published
            check(payload.is_file(), f"Missing published payload: {published}")
            check(hashlib.sha256(payload.read_bytes()).hexdigest() == public[published]["model"]["sha256"], "Published model changed")
    for section in categories:
        source_rows = [r for r in files if r["category"] == section["id"]]
        model_rows = [r for r in models if r["category"] == section["id"]]
        expected = {
            "source_files": len(source_rows),
            "source_bytes": sum(r["bytes"] for r in source_rows),
            "image_identical": sum(r["provenance"] == "image-identical" for r in source_rows),
            "local_generated": sum(r["provenance"] == "local-generated" for r in source_rows),
            "historical_models": len(model_rows),
            "verified_local_models": sum(r["availability"] == "verified-local" for r in model_rows),
        }
        for key, value in expected.items():
            check(section[key] == value, f"Category total mismatch: {section['id']}/{key}")
    provenance = Counter(r["provenance"] for r in files)
    check(sources["summary"]["files"] == len(files), "Source total mismatch")
    check(sources["summary"]["image_identical"] == provenance["image-identical"], "Image total mismatch")
    check(sources["summary"]["local_only_generated"] == provenance["local-generated"], "Generated total mismatch")
    for filename, records, key in (("assets.csv", models, "id"), ("sources.csv", files, "path")):
        with (ROOT / "inventory" / filename).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        check(len(rows) == len(records), f"CSV count mismatch: {filename}")
        check({r[key] for r in rows} == {r[key] for r in records}, f"CSV IDs mismatch: {filename}")
        expected_rows = {r[key]: r for r in records}
        for row in rows:
            for field in ("sha256", "source_sha256", "export_sha256", "category", "provenance", "availability"):
                if field in row:
                    check(row[field] == str(expected_rows[row[key]][field]), f"CSV value mismatch: {filename}/{field}")
    print(f"PASS: {len(models)} model records, {len(files)} source files, {len(categories)} categories; CSV parity, source joins, totals and public downloads verified.")


if __name__ == "__main__":
    main()
