# NeoVax Pipeline — 10-Week Execution Checklist

> Every day: write code, run a pipeline step, or document what you learned.
> No theorising without building. The theory develops when the pipeline breaks.

---

## WEEK 1: Environment & Foundations

- [ ] Install mambaforge
- [ ] Create environment: `mamba env create -f environment.yml`
- [ ] Install BWA, samtools, GATK, VEP, pVACtools
- [ ] Verify all tools with `--version`
- [ ] Init git repo, push to GitHub (public from day 1)
- [ ] Understand file formats: FASTQ (reads), BAM (aligned), VCF (variants)
- [ ] First entry in `docs/learning_log.md`
- [ ] First entry in `CLINICAL_NOTES.md`: What is a neoantigen? (from memory, no looking up)

## WEEK 2: Data Acquisition

- [ ] Register at GDC Data Portal (portal.gdc.cancer.gov)
- [ ] Find a TCGA-SKCM (melanoma) case with: tumor-normal WES + RNA-seq + clinical data
- [ ] Download via GDC Transfer Tool
- [ ] Organise in `01_data_acquisition/data/`
- [ ] Document case ID and rationale
- [ ] **Fast-track option:** download pre-processed MAF files to skip to Week 4

Why melanoma: Moderna's mRNA-4157 Phase 3 is melanoma. High TMB = more candidates = richer learning.

## WEEK 3: Alignment

From raw FASTQ:
- [ ] Download + index GRCh38 reference genome
- [ ] Align tumor: `bwa mem ref.fa tumor_R1.fq tumor_R2.fq | samtools sort -o tumor.bam`
- [ ] Align normal: same
- [ ] Mark duplicates: `gatk MarkDuplicates`
- [ ] Index BAMs: `samtools index`
- [ ] QC: `samtools flagstat`, `samtools coverage`
- [ ] Clinical note: germline vs somatic mutations, why matched tumor-normal

## WEEK 4: Variant Calling

- [ ] Run Mutect2: `gatk Mutect2 -I tumor.bam -I normal.bam -normal SAMPLE -O raw.vcf`
- [ ] Filter: `gatk FilterMutectCalls -V raw.vcf -O filtered.vcf`
- [ ] Count variants, check types (SNV, indel)
- [ ] Sanity check: known melanoma drivers present? (BRAF V600E, NRAS Q61, KIT)
- [ ] Clinical note: TMB, driver vs passenger mutations

## WEEK 5: Annotation

- [ ] Run VEP with Wildtype + Frameshift plugins
- [ ] Parse: missense, nonsense, frameshift counts
- [ ] Filter to protein-coding consequences
- [ ] Clinical note: why missense > synonymous for neoantigens, frameshift immunogenicity

## WEEK 6: Neoantigen Prediction ← CRITICAL STEP

- [ ] Determine HLA type (TCGA clinical data or OptiType)
- [ ] Run pVACseq with NetMHCpan (epitope lengths 8-11)
- [ ] Examine: candidate count, binding affinity distribution
- [ ] Filter: affinity < 500nM, fold change > 1
- [ ] Create `notebooks/02_neoantigen_analysis.ipynb` with visualisations
- [ ] **Document the signal-to-noise problem.** How many candidates? How many are real?
- [ ] Clinical note: HLA/MHC biology, class I vs II presentation

## WEEK 7: RNA Validation

- [ ] Align RNA-seq with STAR
- [ ] Quantify with featureCounts (TPM)
- [ ] Filter neoantigens to only those with RNA expression
- [ ] Calculate: what fraction survive validation?
- [ ] Clinical note: DNA mutation ≠ protein ≠ immune target

## WEEK 8: Vaccine Construct Design

- [ ] Rank top 7-10 candidates
- [ ] Design construct: epitopes + linkers (GPGPG/AAY) + signal peptide + UTRs
- [ ] Codon-optimise for human expression
- [ ] Output `07_construct_design/final_construct.fasta`
- [ ] Clinical note: mRNA vaccine mechanism (LNP → cell → ribosome → MHC → T-cell)

## WEEK 9: Treatment Protocol ← YOUR MD IS LOAD-BEARING

- [ ] Design combination protocol: vaccine + anti-PD-1 + targeted therapy
- [ ] Specify timing and sequencing with pharmacological rationale
- [ ] Address drug interactions and contraindications
- [ ] Write `08_protocol_design/protocol_report.md`

## WEEK 10: Automation & Publication

- [ ] Write Snakemake/bash master pipeline
- [ ] Test reproducibility
- [ ] Write essay: `docs/essay_draft.md`
- [ ] Publish (Substack, X, bioinformatics communities)

---

## Daily Rhythm

| When | What | Duration |
|------|------|----------|
| Morning (non-clinical days) | Execute current week's tasks | 2 hours |
| Evening (every day) | `docs/learning_log.md` entry | 10 min |
| Sunday | Review week, update checklist, plan ahead | 30 min |
