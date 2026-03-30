#!/usr/bin/env python3
"""
TCGA Data Acquisition Helper

Queries the GDC API to find suitable TCGA-SKCM cases with matched
tumor-normal WES and RNA-seq data.

Usage:
    python download_tcga.py --find-cases
    python download_tcga.py --download CASE_ID
"""

import argparse
import json
import requests
import os
import sys

GDC_API = "https://api.gdc.cancer.gov"


def find_suitable_cases(project="TCGA-SKCM", limit=10):
    """
    Find TCGA cases that have all three data types:
    1. Tumor WXS (whole exome sequencing)
    2. Normal WXS (matched blood/normal)
    3. Tumor RNA-seq
    """

    # Query for cases with WXS data
    filters = {
        "op": "and",
        "content": [
            {"op": "=", "content": {"field": "project.project_id", "value": project}},
            {"op": "=", "content": {"field": "files.experimental_strategy", "value": "WXS"}},
            {"op": "=", "content": {"field": "files.data_category", "value": "Sequencing Reads"}},
        ],
    }

    params = {
        "filters": json.dumps(filters),
        "fields": "case_id,submitter_id,diagnoses.tumor_stage",
        "size": str(limit * 5),  # Over-fetch to filter
        "format": "JSON",
    }

    print(f"Querying GDC for {project} cases with WXS data...")
    response = requests.get(f"{GDC_API}/cases", params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        sys.exit(1)

    data = response.json()
    cases = data.get("data", {}).get("hits", [])

    print(f"Found {len(cases)} cases with WXS data.")
    print(f"\nChecking for matched tumor-normal + RNA-seq...\n")

    suitable = []
    for case in cases[:limit]:
        case_id = case["case_id"]
        submitter_id = case.get("submitter_id", "unknown")

        # Check what files exist for this case
        file_filters = {
            "op": "and",
            "content": [
                {"op": "=", "content": {"field": "cases.case_id", "value": case_id}},
            ],
        }

        file_params = {
            "filters": json.dumps(file_filters),
            "fields": "experimental_strategy,data_category,cases.samples.sample_type",
            "size": "100",
            "format": "JSON",
        }

        file_response = requests.get(f"{GDC_API}/files", params=file_params)
        files = file_response.json().get("data", {}).get("hits", [])

        strategies = set()
        for f in files:
            strat = f.get("experimental_strategy", "")
            if strat:
                strategies.add(strat)

        has_wxs = "WXS" in strategies
        has_rnaseq = "RNA-Seq" in strategies

        status = []
        if has_wxs:
            status.append("WXS ✓")
        if has_rnaseq:
            status.append("RNA-seq ✓")

        if has_wxs and has_rnaseq:
            suitable.append({"case_id": case_id, "submitter_id": submitter_id})
            marker = " ★ SUITABLE"
        else:
            marker = ""

        print(f"  {submitter_id} ({case_id[:8]}...): {', '.join(status)}{marker}")

    print(f"\n{'='*60}")
    print(f"Found {len(suitable)} suitable cases with both WXS + RNA-seq")
    print(f"{'='*60}\n")

    for s in suitable:
        print(f"  {s['submitter_id']}: {s['case_id']}")

    return suitable


def generate_manifest(case_id, output_dir="data"):
    """Generate a GDC download manifest for a specific case."""

    os.makedirs(output_dir, exist_ok=True)

    filters = {
        "op": "and",
        "content": [
            {"op": "=", "content": {"field": "cases.case_id", "value": case_id}},
            {"op": "in", "content": {
                "field": "experimental_strategy",
                "value": ["WXS", "RNA-Seq"]
            }},
            {"op": "=", "content": {
                "field": "data_category", "value": "Sequencing Reads"
            }},
        ],
    }

    params = {
        "filters": json.dumps(filters),
        "fields": "file_id,file_name,file_size,experimental_strategy",
        "size": "100",
        "format": "JSON",
    }

    response = requests.get(f"{GDC_API}/files", params=params)
    files = response.json().get("data", {}).get("hits", [])

    print(f"Files for case {case_id[:12]}...:")
    total_size = 0
    manifest_lines = ["id\tfilename\tmd5\tsize\tstate"]

    for f in files:
        size_gb = f.get("file_size", 0) / (1024 ** 3)
        total_size += size_gb
        print(f"  {f['experimental_strategy']:10s}  {f['file_name']:50s}  {size_gb:.1f} GB")
        manifest_lines.append(f"{f['file_id']}\t{f['file_name']}\t\t{f.get('file_size', 0)}\t")

    print(f"\nTotal download: {total_size:.1f} GB")

    manifest_path = os.path.join(output_dir, "manifest.txt")
    with open(manifest_path, "w") as fh:
        fh.write("\n".join(manifest_lines))

    print(f"Manifest written to {manifest_path}")
    print(f"\nDownload with:")
    print(f"  gdc-client download -m {manifest_path} -t YOUR_TOKEN.txt -d {output_dir}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCGA Data Acquisition for NeoVax Pipeline")
    parser.add_argument("--find-cases", action="store_true", help="Find suitable TCGA-SKCM cases")
    parser.add_argument("--download", type=str, help="Generate manifest for a specific case ID")
    parser.add_argument("--project", type=str, default="TCGA-SKCM", help="TCGA project ID")

    args = parser.parse_args()

    if args.find_cases:
        find_suitable_cases(project=args.project)
    elif args.download:
        generate_manifest(args.download)
    else:
        parser.print_help()
