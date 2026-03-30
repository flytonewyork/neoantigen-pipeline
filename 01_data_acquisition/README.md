# 01 — Data Acquisition

## Overview

We need three types of data from the same patient:

1. **Tumor WES/WGS** — whole exome or genome sequencing of the tumor
2. **Normal WES/WGS** — matched normal (usually blood) from the same patient
3. **Tumor RNA-seq** — gene expression data to validate which mutations are actually expressed

## Data Source: TCGA (The Cancer Genome Atlas)

We use **TCGA-SKCM** (Skin Cutaneous Melanoma) because:
- Moderna/Merck mRNA-4157 Phase 3 trial is in melanoma → clinical ground truth
- Melanoma has high tumour mutational burden → more neoantigen candidates → richer learning
- Well-annotated with clinical outcomes (immunotherapy response data available)

## How to Access

### Option A: Full BAM files (recommended for complete pipeline experience)

1. Register at https://portal.gdc.cancer.gov/
2. Apply for dbGaP access (controlled data — takes days to weeks)
3. Search: Project = TCGA-SKCM, Data Type = Aligned Reads, Experimental Strategy = WXS
4. Find a case with BOTH tumor and matched normal WXS + tumor RNA-seq
5. Download using GDC Data Transfer Tool:
   ```bash
   gdc-client download -m manifest.txt -t token.txt
   ```

### Option B: Pre-processed MAF files (fast-track — start here)

Open-access somatic mutation data (no dbGaP required):

```bash
# Download TCGA-SKCM MAF from GDC
# Go to: https://portal.gdc.cancer.gov/repository
# Filter: Project = TCGA-SKCM, Data Category = Simple Nucleotide Variation
# Download the MAF file (Mutect2 calls, open access)
```

This skips alignment and variant calling (Weeks 2-4) but lets you jump straight to annotation and neoantigen prediction. Circle back to the full pipeline later.

### Option C: Use a published benchmark dataset

The TESLA consortium (Tumor nEoantigen SeLection Alliance) published matched genomic + immunogenicity data — mutations paired with experimental T-cell response data. This is gold-standard validation data:

- Paper: Wells et al., Cell 2020
- Data available through dbGaP

This is ideal for later phases when you want to evaluate your neoantigen scoring against ground truth.

## Selecting a Case

Look for:
- **High TMB** (>10 mutations/Mb) — more candidates to work with
- **Known driver mutations** (BRAF V600E is in ~50% of melanoma) — sanity check
- **Clinical response data** — ideally a patient who received immunotherapy
- **All three data types available** — tumor WES, normal WES, tumor RNA-seq

Document your chosen case ID in this README once selected.

## Selected Case

**Case ID:** [TO BE FILLED]
**Rationale:** [TO BE FILLED]
**Data downloaded:** [TO BE FILLED]
