# cortex.h5ad analysis

## Input and interpretation

`/data/cortex.h5ad`: 3,005 cells × 19,972 features. `X` is the sole distinct expression matrix: finite, nonnegative integers with varying library sizes and no recorded transformation, consistent with counts but raw-count provenance and assay are unconfirmed. `var['genes']` contains mouse-style gene symbols; `var_names` are numeric identifiers. Two symbols, `Mar-01` and `Mar-02`, are duplicated. Organism and tissue are not explicitly documented; mouse and cortical/hippocampal tissue are inferred from gene nomenclature and supplied labels, respectively. The existing `obs['label']` and `obs['label2']` annotations are preserved, not used for predictions or evaluated. Biological sample, donor, and batch identity are unknown; cell-ID prefixes are not assumed to be batches.

## QC and preprocessing

- Count totals: median 12,089, IQR 7,361–18,186, range 2,508–61,982. Detected genes: median 3,630, IQR 2,459–4,907, range 770–8,146.
- No genes match the mouse `mt-` prefix; mitochondrial fraction is unavailable, not zero. This prevents mitochondrial-based filtering.
- No cells were removed. Low-count distributions differ markedly across supplied broad groups (e.g., median totals 4,496 endothelial-mural vs 16,267 pyramidal CA1), and no validated sample-specific thresholds or clear failure population were established. 106 cells exceed the upper 1.5-IQR count fence of 34,423.5; this flags possible high-library outliers, not confirmed doublets. No doublet detection was performed.
- Counts were normalized to 10,000 per cell and log1p transformed, retaining counts in `layers['counts']`. Seurat flavor selected 2,000 HVGs without batching; all 19,972 genes were retained. PCA used 30 PCs, neighbor graph 15 neighbors, UMAP and Leiden seed 42, Leiden resolution 0.7. The observed clustering contains 18 clusters and sums to all 3,005 retained cells. Resolution is an exploratory choice, not evidence of biological resolution.
- Wilcoxon cluster-versus-rest markers are exploratory, not donor-aware differential expression. Only the top 30 per cluster are in the marker table; full-expression panel metrics were also calculated for annotation.

## Provisional annotation

Labels are based on several literature-informed gene panels and cluster-versus-rest expression, not a reference transfer. Species, sampled regions, and reference match remain unverified. Sample-level reproducibility could not be evaluated. See `cortex_annotation_evidence.md` for citations, detection fractions, effect sizes and alternative interpretations.

| Predicted type | Cells |
|---|---:|
| Excitatory neuron | 1,060 |
| Oligodendrocyte | 720 |
| Astrocyte | 267 |
| Inhibitory neuron | 249 |
| Endothelial cell | 244 |
| Border-associated macrophage-like | 122 |
| Vascular mural cell | 90 |
| Microglia | 49 |
| unresolved | 204 |

Unresolved cluster 1 (76 cells) contains distinct inhibitory-like and astrocyte-like subsets; 13 (80 cells) co-detects endothelial and oligodendrocyte panels, and 15 (48 cells) co-detects astrocyte and oligodendrocyte panels. These may reflect mixed cells, contamination, clustering, or biology; no mechanism is established. The annotation table covers every observed cluster once; all 3,005 cells map to a prediction. Supplied labels remain in the h5ad.

## Outputs

- Annotated dataset: `/workspace/cortex_annotated.h5ad`
- Cluster annotations: `/workspace/annotations.csv`
- Detailed marker evidence and references: `/workspace/cortex_annotation_evidence.md`
- Reference-panel metrics: `/workspace/cortex_reference_panel_metrics.csv`
- Top markers: `/workspace/cortex_markers.csv`
- Cell type UMAP: `/workspace/cortex_cell_types_umap.png`
- Leiden UMAP: `/workspace/cortex_leiden_umap.png`
- QC metrics, quantiles and plot: `/workspace/cortex_qc/qc.h5ad`, `/workspace/cortex_qc/qc_summary.csv`, `/workspace/cortex_qc/qc.png`

Next steps: confirm species, anatomical source, count matrix provenance and donor/batch metadata; obtain mitochondrial annotation if available; assess doublets and ambient RNA and revisit unresolved clusters. Use sample-aware methods for any biological condition comparisons.
