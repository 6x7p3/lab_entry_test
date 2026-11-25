---
name: quality-control
description: Generate and interpret per-cell and per-sample QC evidence, choose justified filters, and report their effects.
---

1. Identify the raw count source, sample column if available, and the field containing gene symbols. Supply the mitochondrial prefix appropriate to that organism and naming convention.
2. Call `qc_report` with a new output directory. Read the quantile CSV and inspect the boxplots or the per-cell metrics in the returned h5ad. Compare library size, detected genes, and mitochondrial fraction jointly and by sample. If zero mitochondrial genes match, report the metric as unavailable and check the identifiers.
3. For each proposed cutoff, cite the metric, the affected sample, and the observed distribution or protocol detail that supports it. A high library size alone supports flagging a possible doublet. If the evidence supports retaining all cells, say so. For a report-only request, finish with the findings and report paths.
4. When filtering is warranted and consistent with the user's constraints, pass the report's dataset to `apply_qc_filters`. Each rule names a metric and an inclusive minimum, maximum, or both. For a sample-specific rule, supply the sample and its original metadata column. A cell missing a metric used in a rule fails that bound.
5. Report each rule, its rationale, and its flagged count. Report the total cells removed and retained separately because one cell can fail multiple rules. If an entire sample or plausible rare population disappears, examine the flagged cells and reconsider the cutoff before proceeding.
