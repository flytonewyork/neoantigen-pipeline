#!/usr/bin/env python3
"""
Neoantigen Candidate Ranking

Custom scoring function that re-ranks pVACseq output.
This is where current approaches fail and where novel methods plug in.

CURRENT APPROACH (v0 - standard heuristic):
    Score = weighted combination of:
    - MHC binding affinity (lower = better)
    - Mutant vs wildtype binding fold change (higher = better)
    - Variant allele frequency (proxy for clonality)
    - RNA expression level (if available)

FUTURE APPROACH (v1 - your research):
    Incorporate cross-scale information features:
    - Structural dissimilarity (mutant vs self, via ESM/AlphaFold embeddings)
    - Entropy of the local sequence context
    - TCR recognition probability
    - Tumour microenvironment features

The gap between v0 and v1 is the research opportunity.
"""

import argparse
import pandas as pd
import numpy as np
import sys


def load_pvacseq_results(filepath):
    """Load pVACseq output TSV."""
    try:
        df = pd.read_csv(filepath, sep="\t")
        print(f"Loaded {len(df)} neoantigen candidates.")
        return df
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)


def score_v0_heuristic(df, expression_data=None):
    """
    V0: Standard heuristic neoantigen scoring.

    This is approximately what the field uses today.
    It works, but produces too many false positives.

    Clinical reasoning for each feature:
    - Binding affinity: peptide must bind MHC to be presented. <500nM is standard threshold.
    - Fold change: mutant should bind BETTER than wildtype (otherwise immune tolerance applies).
    - VAF: higher variant allele frequency → mutation is clonal (present in all cancer cells)
      → better vaccine target (kills more of the tumor).
    - Expression: mutation must be transcribed to produce the neoantigen protein.
    """

    scored = df.copy()

    # --- Binding affinity score (0-1, lower affinity = higher score) ---
    # Standard threshold: 500nM. Strong binders: <50nM
    if "Median MT IC50 Score" in scored.columns:
        affinity_col = "Median MT IC50 Score"
    elif "Best MT IC50 Score" in scored.columns:
        affinity_col = "Best MT IC50 Score"
    else:
        print("WARNING: No binding affinity column found. Using placeholder.")
        scored["affinity_score"] = 0.5
        affinity_col = None

    if affinity_col:
        # Log-transform and invert: lower IC50 → higher score
        scored["affinity_score"] = 1 - np.clip(
            np.log10(scored[affinity_col].clip(lower=1)) / np.log10(50000),
            0, 1
        )

    # --- Fold change score (0-1, higher fold change = higher score) ---
    if "Median Fold Change" in scored.columns:
        scored["fold_change_score"] = np.clip(
            np.log2(scored["Median Fold Change"].clip(lower=1)) / 5,
            0, 1
        )
    else:
        scored["fold_change_score"] = 0.5

    # --- VAF score (0-1, higher VAF = more clonal = higher score) ---
    if "Tumor DNA VAF" in scored.columns:
        scored["vaf_score"] = scored["Tumor DNA VAF"].clip(0, 1)
    else:
        scored["vaf_score"] = 0.5

    # --- Expression score (0-1) ---
    if "Tumor RNA Depth" in scored.columns:
        scored["expression_score"] = np.clip(
            scored["Tumor RNA Depth"] / scored["Tumor RNA Depth"].quantile(0.95),
            0, 1
        )
    elif expression_data is not None:
        # TODO: merge external expression data
        scored["expression_score"] = 0.5
    else:
        scored["expression_score"] = 0.5

    # --- Composite score ---
    # Weights reflect clinical importance (adjustable)
    weights = {
        "affinity_score": 0.35,
        "fold_change_score": 0.25,
        "vaf_score": 0.20,
        "expression_score": 0.20,
    }

    scored["composite_score"] = sum(
        scored[col] * weight for col, weight in weights.items()
    )

    scored = scored.sort_values("composite_score", ascending=False)

    return scored


def score_v1_entropy(df):
    """
    V1: Entropy-aware neoantigen scoring.

    PLACEHOLDER — this is where your research goes.

    The hypothesis: immunogenicity depends not just on binding affinity
    but on the INFORMATION CONTENT of the mutation — how much "surprise"
    it introduces relative to self-peptide space.

    Potential features to add:
    - Shannon entropy of the local peptide sequence context
    - Structural dissimilarity score (mutant vs wildtype via ESM embeddings)
    - Information-theoretic distance from nearest self-peptide
    - Cross-scale propagation score (sequence → structure → binding → TCR)

    This function will be developed as the research progresses.
    """
    raise NotImplementedError(
        "V1 entropy-aware scoring is under development. "
        "This is the research frontier."
    )


def format_report(scored_df, top_n=10):
    """Generate a human-readable neoantigen report."""

    top = scored_df.head(top_n)

    report_cols = [
        "Chromosome", "Start", "Stop",
        "Variant Type", "Gene Name",
        "HLA Allele", "MT Epitope Seq", "WT Epitope Seq",
        "composite_score",
        "affinity_score", "fold_change_score", "vaf_score", "expression_score",
    ]

    # Use only columns that exist
    available = [c for c in report_cols if c in top.columns]

    print(f"\n{'='*80}")
    print(f"  TOP {top_n} NEOANTIGEN CANDIDATES")
    print(f"{'='*80}\n")

    for i, (_, row) in enumerate(top.iterrows(), 1):
        gene = row.get("Gene Name", "unknown")
        epitope = row.get("MT Epitope Seq", "unknown")
        score = row.get("composite_score", 0)
        hla = row.get("HLA Allele", "unknown")

        print(f"  #{i}: {gene} — {epitope}")
        print(f"      HLA: {hla} | Score: {score:.3f}")
        print(f"      Affinity: {row.get('affinity_score', 0):.2f} | "
              f"Fold change: {row.get('fold_change_score', 0):.2f} | "
              f"VAF: {row.get('vaf_score', 0):.2f} | "
              f"Expression: {row.get('expression_score', 0):.2f}")
        print()

    return top


def main():
    parser = argparse.ArgumentParser(description="Rank neoantigen candidates")
    parser.add_argument("--input", required=True, help="pVACseq output TSV")
    parser.add_argument("--top", type=int, default=10, help="Number of top candidates")
    parser.add_argument("--output", default=None, help="Output ranked TSV")
    parser.add_argument("--method", default="v0", choices=["v0", "v1"],
                        help="Scoring method: v0 (heuristic) or v1 (entropy)")

    args = parser.parse_args()

    df = load_pvacseq_results(args.input)

    if args.method == "v0":
        scored = score_v0_heuristic(df)
    elif args.method == "v1":
        scored = score_v1_entropy(df)

    top = format_report(scored, top_n=args.top)

    if args.output:
        scored.to_csv(args.output, sep="\t", index=False)
        print(f"Full ranked results saved to: {args.output}")

    # Summary statistics
    print(f"\n{'='*80}")
    print(f"  PIPELINE SUMMARY")
    print(f"{'='*80}")
    print(f"  Total candidates from pVACseq: {len(df)}")
    print(f"  After scoring & ranking: top {args.top} selected")
    print(f"  Score range: {scored['composite_score'].min():.3f} — {scored['composite_score'].max():.3f}")
    print(f"\n  NOTE: These {args.top} candidates would form the vaccine construct.")
    print(f"  See 07_construct_design/ for the next step.")


if __name__ == "__main__":
    main()
