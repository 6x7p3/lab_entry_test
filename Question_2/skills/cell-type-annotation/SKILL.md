---
name: cell-type-annotation
description: Interpret cluster markers in the relevant organism and tissue, assign supported cell type labels, and record conflicting evidence.
---

Start with the clustered h5ad, the cluster column, and the marker table from `identify_markers`. Confirm the organism, tissue, gene identifiers, and reference marker panel or atlas. Record the reference name and version or source. If a suitable reference is unavailable, return an evidence table with provisional or unresolved labels and say what information is needed.

For each cluster, compare several markers with plausible candidate types. Inspect fold changes and expression fractions inside and outside the cluster. Use log-normalized expression across all genes to examine reference markers missing from the top-ranked table. Where samples are available, check whether the pattern is consistent across them. Consider conflicting lineage markers, sparse expression, and possible mixed clusters.

For a contested subtype, identify the closest plausible alternative and the marker pattern that would distinguish them. Record a measured comparison from the dataset alongside the reference evidence. When the observed markers support both candidates equally, keep the supported broad type and mark the subtype unresolved.

Assign the narrowest label supported by the evidence. A broad type can be supported while the subtype remains unresolved. Record one row per cluster in `/workspace/annotations.csv` with the cluster ID, cell count, proposed label, supporting genes, conflicting or ambiguous evidence, and reference. Use `unresolved` for clusters lacking a defensible assignment.

Use Python to map this table back to a new `obs["predicted_cell_type"]` column by cluster ID, aligning IDs as strings. Verify that every observed cluster has a row, including unresolved clusters. Save a new annotated h5ad and a UMAP colored by predicted type. Preserve supplied annotation columns; if they serve as evaluation labels, compare them only after deriving the predictions. Report the artifact paths and the remaining uncertainties.
