---
name: summarize-data
description: Inspect an unfamiliar h5ad file, identify count and annotation fields, and summarize the dataset before choosing an analysis.
---

Use Python in the sandbox. Open the requested h5ad with `anndata.io.read_h5ad(path, backed="r")` for the initial inspection. Report the cell and gene counts, available layers, and relevant `obs` and `var` columns. Check `raw`, `obsm`, `obsp`, and preprocessing metadata when the user asks to analyze or resume a processed dataset. Close the backed file after inspection.

For a cell-count or gene-count question, report the requested dimensions and stop. For an annotation question, inspect representative entries, missing values, and distinct counts in plausible columns. If two columns could represent broad types and subtypes, compare their values and cross-tabulate them to check the proposed relationship. Use a dataset note when its filename and fields match. If the interpretation remains ambiguous, show the evidence and ask which annotation the user intended.

Name the source column in your answer. With few categories, show all observed labels and counts. With many, give the full distinct count and identify any preview as partial. Report missing values and unassigned placeholders separately from named types.

Determine whether `var_names` holds gene symbols or feature IDs and identify any sample and batch fields. Inspect candidate expression matrices, their values, and preprocessing metadata. When a single plausible matrix contains finite, nonnegative, integer-valued expression with varying library sizes and no evidence of a transformation, use it as counts and report that inference. If the evidence conflicts, ask the specific question that would resolve it.

For a general description, return the file path, dimensions, relevant fields, and any unresolved questions. Identify which labels were supplied with the dataset.
