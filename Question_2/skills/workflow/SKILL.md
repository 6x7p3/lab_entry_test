---
name: workflow
description: Guide an end-to-end single-cell RNA-seq analysis from a count matrix to a cluster annotation report, or resume an existing analysis.
---

Start with the user's question and the dataset path. For a request such as “describe this file”, finish after inspection. For a full analysis, follow the stages below. To resume an analysis, inspect the saved representation and its provenance, then continue from the first stage needed for the request. Reuse existing results when their cell set and parameters match.

1. Use the `summarize-data` skill to identify the expression representation, gene identifiers, and available organism, tissue, and sample metadata. Proceed with the count matrix supported by the evidence. If competing interpretations would change preprocessing, ask which matrix contains raw counts.
2. Use the `quality-control` skill. Inspect the QC report and record the reason for each filtering rule. Carry the retained cells forward.
3. Use `normalize_expression` on raw counts. It preserves counts in `layers["counts"]` and writes library-size-normalized, log-transformed expression to `X`. If the input already contains suitable log-normalized expression, use it directly.
4. Use `select_hvgs` on log-normalized `X`. Record the flavor, number of genes, and batch column if used. Keep all genes in the dataset so marker analysis can use the full expression matrix.
5. Use `reduce_dimensions` to build PCA, the cell-neighbor graph, and UMAP. Choose fewer PCs than the smaller of the cell count and HVG count. Use `cluster_cells` on the saved graph. Inspect cluster sizes and the UMAP; if a different resolution is warranted, reuse the graph.
6. Use `identify_markers` with the grouping column and comparison of interest. It ranks genes on log-normalized expression and saves effect sizes, adjusted p-values, and detection fractions. Treat these as exploratory cluster markers. A condition comparison across donors needs a separate sample-aware analysis.
7. Use the `cell-type-annotation` skill to assign evidence-backed labels and retain unresolved clusters.

Use new output paths under `/workspace` for each stage and pass the returned dataset path to the next tool. Before reporting a full run, reconcile the retained cell count with the sum of cluster sizes and check that the annotation table covers each observed cluster once. Report the cell and cluster counts, the evidence behind material choices, unresolved annotations, and the paths to the annotated h5ad, QC outputs, UMAP, and tables actually produced.
