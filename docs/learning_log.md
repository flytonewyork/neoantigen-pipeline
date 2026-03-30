# Learning Log

> Daily entries. 3-5 sentences. What did I do, what broke, what did I learn, what's next.

---

## Day 1 — 2026-03-30

**Did:** Set up project scaffold with 8-stage pipeline structure. Initialized git repo. Started conda environment creation with all bioinformatics tools (BWA, GATK, samtools, VEP, pVACtools, STAR, etc.). Reviewed the full pipeline architecture from sequencing through mRNA construct design.

**Broke:** Nothing yet — still in setup phase. The real breakage starts when data meets tools.

**Learned:** The pipeline has a clear sequential dependency chain: raw reads → aligned BAMs → somatic VCF → annotated variants → HLA-typed neoantigen candidates → RNA-validated candidates → mRNA construct. Each stage filters aggressively — the signal-to-noise problem at step 6 (neoantigen prediction) is where most false positives enter.

**Tomorrow:** Finish environment setup, verify all tools with --version, begin TCGA data acquisition for a melanoma case.

---
