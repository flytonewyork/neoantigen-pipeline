#!/bin/bash
# NeoVax Pipeline - Environment Setup
# Prerequisites: mambaforge installed, ~20GB disk space
# Usage: bash 00_setup/install_tools.sh

set -euo pipefail

echo "========================================"
echo "  NeoVax Pipeline - Setup"
echo "========================================"

# 1. Conda environment
echo "[1/4] Creating conda environment..."
if conda env list | grep -q "neovax"; then
    echo "  Updating existing environment..."
    mamba env update -f environment.yml
else
    mamba env create -f environment.yml
fi

# 2. Reference genome
echo "[2/4] Reference genome (GRCh38)..."
mkdir -p reference
if [ ! -f "reference/GRCh38.fa" ]; then
    wget -q -O reference/GRCh38.fa.gz \
        "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna.gz"
    gunzip reference/GRCh38.fa.gz
fi

# 3. Index reference
echo "[3/4] Indexing reference..."
[ ! -f "reference/GRCh38.fa.bwt" ] && bwa index reference/GRCh38.fa
[ ! -f "reference/GRCh38.fa.fai" ] && samtools faidx reference/GRCh38.fa
[ ! -f "reference/GRCh38.dict" ] && gatk CreateSequenceDictionary -R reference/GRCh38.fa

# 4. VEP cache
echo "[4/4] VEP cache..."
mkdir -p ~/.vep
if [ ! -d "$HOME/.vep/homo_sapiens" ]; then
    vep_install --AUTO cf --SPECIES homo_sapiens --ASSEMBLY GRCh38 \
        --DESTDIR "$HOME/.vep" --CACHEDIR "$HOME/.vep"
fi

# Verify
echo ""
echo "Verifying installations:"
for tool in bwa samtools gatk vep pvacseq STAR featureCounts; do
    command -v "$tool" &>/dev/null && echo "  ✓ $tool" || echo "  ✗ $tool NOT FOUND"
done

echo ""
echo "Setup complete. Next: conda activate neovax"
