## Findings

The analysis identified **18 clusters among 3,005 cells**. Marker-based annotations suggest neuronal, oligodendrocyte, astrocyte, vascular and immune populations. **Three clusters—204 cells total—remain unresolved** because they contain mixed or conflicting lineage signatures.

| Provisional annotation | Cells |
|---|---:|
| Excitatory neuron | 1,060 |
| Oligodendrocyte | 720 |
| Astrocyte | 267 |
| Inhibitory neuron | 249 |
| Endothelial cell | 244 |
| Border-associated macrophage-like | 122 |
| Vascular mural cell | 90 |
| Microglia | 49 |
| Unresolved | 204 |

These labels are provisional: gene names and supplied annotations suggest mouse cortical/hippocampal tissue, but the file does not explicitly document species or anatomical provenance.

## Analysis and limitations

All cells were retained. Median counts were **12,089 per cell**, with a median of **3,630 detected genes**. No mitochondrial genes matched the expected prefix, so mitochondrial QC was unavailable. High-count cells were retained; they warrant doublet assessment rather than automatic exclusion.

The sole expression matrix was consistent with counts, although its provenance is unconfirmed. Analysis used 2,000 highly variable genes, 30 PCs, 15 neighbors and Leiden resolution 0.7. Donor and batch identities were unavailable, and cluster markers are exploratory rather than donor-aware differential expression results. Existing dataset labels were preserved but not used to assign the predictions.

## Outputs

- [Analysis report](sandbox:/workspace/cortex_analysis_report.md)
- [Annotated dataset](sandbox:/workspace/cortex_annotated.h5ad)
- [Cluster annotations](sandbox:/workspace/annotations.csv)
- [Cell-type UMAP](sandbox:/workspace/cortex_cell_types_umap.png)
- [Marker table](sandbox:/workspace/cortex_markers.csv)
- [Detailed annotation evidence](sandbox:/workspace/cortex_annotation_evidence.md)
- [QC summary](sandbox:/workspace/cortex_qc/qc_summary.csv) and [QC plot](sandbox:/workspace/cortex_qc/qc.png)

The most useful follow-up is to confirm the organism, tissue, count provenance and sample identities, then assess doublets and ambient RNA—particularly in the unresolved clusters.
