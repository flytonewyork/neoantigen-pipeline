# NeoVax Pipeline: AI-Driven Personalised Neoantigen Vaccine Design

> **Mission:** Reproduce and systematise the computational pipeline behind the Rosie mRNA cancer vaccine — turning raw sequencing data into a ranked neoantigen vaccine construct — then improve it.

> **Author:** Thomas (MD, MBBS) — building at the intersection of clinical medicine and biological AI.

## What This Project Does

Given matched tumor-normal sequencing data (and optionally RNA-seq), this pipeline:

1. **Aligns** raw reads to the reference genome (BWA-MEM)
2. **Calls somatic variants** — mutations in tumor but not germline (GATK Mutect2)
3. **Annotates** variants with functional impact (Ensembl VEP)
4. **Predicts neoantigens** — mutant peptides that bind patient HLA molecules (pVACseq + NetMHCpan-4.1)
5. **Validates** against RNA expression (only expressed mutations retained)
6. **Designs** an mRNA vaccine construct (epitope selection, linkers, UTRs, codon optimisation)
7. **Recommends** a combination treatment protocol with clinical rationale

Each step includes clinical reasoning — not just *what* the pipeline does, but *why* each step matters immunologically.

## Project Structure

```
neoantigen-pipeline/
├── README.md              # This file
├── CHECKLIST.md           # 10-week execution plan
├── CLINICAL_NOTES.md      # Clinical reasoning journal
├── environment.yml        # Conda environment
├── 00_setup/              # Environment setup
├── 01_data_acquisition/   # TCGA data download
├── 02_alignment/          # BWA-MEM read alignment
├── 03_variant_calling/    # GATK Mutect2
├── 04_annotation/         # Ensembl VEP
├── 05_neoantigen_prediction/  # pVACseq + NetMHCpan
├── 06_rna_validation/     # RNA expression filtering
├── 07_construct_design/   # mRNA vaccine construct
├── 08_protocol_design/    # Treatment protocol
├── notebooks/             # Jupyter exploration
├── docs/                  # Learning log, failure log, essay
└── tests/                 # Validation
```

## Background

In March 2026, Paul Conyngham used AI chatbots to help design a personalised mRNA cancer vaccine for his dog Rosie. This project reproduces that pipeline using publicly available human cancer data (TCGA), adding:

1. **Clinical reasoning at every step** — written from a physician's perspective
2. **A foundation for improvement** — exposing where current neoantigen prediction fails

## Getting Started

```bash
# 1. Clone
git clone https://github.com/[username]/neoantigen-pipeline.git
cd neoantigen-pipeline

# 2. Create environment
mamba env create -f environment.yml
conda activate neovax

# 3. Follow the checklist
cat CHECKLIST.md
```

## Status

- [ ] Phase 0: Environment setup
- [ ] Phase 1: Data acquisition
- [ ] Phase 2: Alignment
- [ ] Phase 3: Variant calling
- [ ] Phase 4: Annotation
- [ ] Phase 5: Neoantigen prediction
- [ ] Phase 6: RNA validation
- [ ] Phase 7: Construct design
- [ ] Phase 8: Protocol design
- [ ] Phase 9: Automation & publication

## License

MIT
