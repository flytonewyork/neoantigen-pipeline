#!/usr/bin/env python3
"""
mRNA Vaccine Construct Designer

Takes ranked neoantigen epitopes and assembles them into an mRNA vaccine construct.

Construct structure:
    5'UTR — Signal Peptide — [Epitope1—Linker—Epitope2—...—EpitopeN] — 3'UTR — PolyA

Usage:
    python design_construct.py --epitopes epitopes.txt --output construct.fasta
"""

import argparse
import os
import sys
from collections import OrderedDict

# Signal peptide: human tPA — routes protein to ER for MHC-I loading
TPA_SIGNAL = "MDAMKRGLCCVLLLCGAVFVSPS"

# PADRE: universal CD4+ T-helper epitope for CD8+ T-cell support
PADRE = "AKFVAAWTLKAAA"

LINKERS = {"GPGPG": "GPGPG", "AAY": "AAY", "EAAAK": "EAAAK"}

CODON_TABLE = {
    "A": "GCC", "R": "CGG", "N": "AAC", "D": "GAC", "C": "TGC",
    "E": "GAG", "Q": "CAG", "G": "GGC", "H": "CAC", "I": "ATC",
    "L": "CTG", "K": "AAG", "M": "ATG", "F": "TTC", "P": "CCC",
    "S": "AGC", "T": "ACC", "W": "TGG", "Y": "TAC", "V": "GTG",
}


def codon_optimise(protein_seq):
    """Convert protein to codon-optimised DNA (most frequent human codons)."""
    return "".join(CODON_TABLE.get(aa, "") for aa in protein_seq.upper()) + "TGA"


def design_construct(epitopes, linker="GPGPG", include_padre=True):
    """Assemble multi-epitope mRNA vaccine construct."""
    parts = OrderedDict()
    parts["signal"] = TPA_SIGNAL

    if include_padre:
        parts["PADRE"] = PADRE
        parts["linker_0"] = linker

    for i, ep in enumerate(epitopes):
        parts[f"epitope_{i+1}"] = ep.upper()
        if i < len(epitopes) - 1:
            parts[f"linker_{i+1}"] = linker

    protein = "".join(parts.values())
    dna = codon_optimise(protein)

    return {
        "protein": protein, "dna": dna,
        "n_epitopes": len(epitopes), "epitopes": epitopes,
        "parts": parts, "linker": linker,
    }


def write_fasta(construct, path):
    with open(path, "w") as f:
        f.write(f">NeoVax_protein epitopes={construct['n_epitopes']}\n")
        p = construct["protein"]
        for i in range(0, len(p), 70):
            f.write(p[i:i+70] + "\n")
        f.write(f"\n>NeoVax_dna codon_optimised=human\n")
        d = construct["dna"]
        for i in range(0, len(d), 70):
            f.write(d[i:i+70] + "\n")


def print_report(c):
    print(f"\n{'='*60}")
    print(f"  mRNA VACCINE CONSTRUCT")
    print(f"{'='*60}")
    print(f"  Epitopes: {c['n_epitopes']}  |  Linker: {c['linker']}")
    print(f"  Protein: {len(c['protein'])} aa  |  CDS: {len(c['dna'])} nt")
    print(f"\n  Architecture: 5'cap—UTR—SP—PADRE—", end="")
    print("—".join(f"E{i+1}" for i in range(c["n_epitopes"])), end="")
    print(f"—UTR—polyA(120)\n")
    for i, ep in enumerate(c["epitopes"], 1):
        print(f"    {i}. {ep}")
    print(f"\n  + N1-methylpseudouridine throughout")
    print(f"  + Cap1 (m7GpppNm)")
    print(f"  + LNP encapsulation for delivery")
    print(f"\n  FOR RESEARCH USE ONLY")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epitopes", required=True)
    parser.add_argument("--output", default="construct.fasta")
    parser.add_argument("--linker", default="GPGPG", choices=LINKERS.keys())
    args = parser.parse_args()

    if os.path.isfile(args.epitopes):
        with open(args.epitopes) as f:
            epitopes = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    else:
        epitopes = [e.strip() for e in args.epitopes.split(",")]

    construct = design_construct(epitopes, linker=args.linker)
    print_report(construct)
    write_fasta(construct, args.output)
    print(f"Written to {args.output}")
