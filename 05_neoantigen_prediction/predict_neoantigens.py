#!/usr/bin/env python3
"""
Neoantigen Prediction & Ranking

This module wraps pVACseq and adds custom ranking logic.
The ranking is where the signal-to-noise problem lives — and where
novel scoring approaches (entropy-based, cross-scale) would plug in.

Usage:
    python predict_neoantigens.py --vcf annotated.vcf --hla "HLA-A*02:01,HLA-B*07:02" --sample SAMPLE
    python rank_candidates.py --input pvacseq_output.tsv --top 10
"""

import argparse
import subprocess
import sys
import os


def run_pvacseq(vcf_path, sample_name, hla_alleles, output_dir, epitope_lengths="8,9,10,11"):
    """
    Run pVACseq neoantigen prediction.

    This is the core prediction step: given somatic mutations and patient HLA type,
    predict which mutant peptides will bind MHC class I molecules.

    Clinical context:
    - MHC-I presents intracellular peptides (8-11 aa) to CD8+ cytotoxic T-cells
    - Only peptides that bind the patient's specific HLA alleles can be presented
    - Binding is necessary but NOT sufficient for immunogenicity
    - This is where the false positive problem originates
    """

    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "pvacseq", "run",
        vcf_path,
        sample_name,
        hla_alleles,
        "NetMHCpan",  # Prediction algorithm
        output_dir,
        "-e1", epitope_lengths,
        "--iedb-install-directory", os.environ.get("IEDB_DIR", "/opt/iedb"),
        "-t", "4",  # threads
    ]

    print(f"Running pVACseq...")
    print(f"  VCF: {vcf_path}")
    print(f"  Sample: {sample_name}")
    print(f"  HLA: {hla_alleles}")
    print(f"  Epitope lengths: {epitope_lengths}")
    print(f"  Output: {output_dir}")
    print()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("pVACseq completed successfully.")
        print(f"Results in: {output_dir}/MHC_Class_I/")
    except subprocess.CalledProcessError as e:
        print(f"pVACseq failed: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("pvacseq not found. Install with: pip install pvactools")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run pVACseq neoantigen prediction")
    parser.add_argument("--vcf", required=True, help="VEP-annotated VCF file")
    parser.add_argument("--sample", required=True, help="Tumor sample name")
    parser.add_argument("--hla", required=True, help="Comma-separated HLA alleles")
    parser.add_argument("--output", default="output/pvacseq", help="Output directory")
    parser.add_argument("--epitope-lengths", default="8,9,10,11", help="Epitope lengths")

    args = parser.parse_args()
    run_pvacseq(args.vcf, args.sample, args.hla, args.output, args.epitope_lengths)
