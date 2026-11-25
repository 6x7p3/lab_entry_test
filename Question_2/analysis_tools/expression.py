from typing import Literal

import scanpy as sc
from anndata.io import read_h5ad


def normalize_expression(
    input_path: str, output_path: str, count_layer: str | None = None, target_sum: float = 10000,
) -> dict:
    """Normalize confirmed raw counts to target_sum per cell, then log1p. Save raw counts in layers['counts'] and log expression in X."""
    adata = read_h5ad(input_path)
    if count_layer is not None:
        adata.X = adata.layers[count_layer].copy()
    elif "log1p" in adata.uns:
        raise ValueError("X is marked as log-transformed. Supply the raw count layer.")
    adata.layers["counts"] = adata.X.copy()
    sc.pp.normalize_total(adata, target_sum=target_sum)
    sc.pp.log1p(adata)
    adata.uns["normalization"] = {"method": "normalize_total_log1p", "target_sum": target_sum, "count_layer": "counts"}
    adata.write_h5ad(output_path)
    return {"dataset": output_path, "count_layer": "counts", "normalized_expression": "X", "target_sum": target_sum}


def select_hvgs(
    input_path: str, output_path: str, n_top_genes: int = 2000,
    flavor: Literal["seurat", "cell_ranger"] = "seurat", batch_column: str | None = None,
) -> dict:
    """Flag highly variable genes using log-normalized X, optionally within batches. Retain all genes for marker analysis."""
    adata = read_h5ad(input_path)
    sc.pp.highly_variable_genes(
        adata, use="X", flavor=flavor, n_top_genes=n_top_genes,
        batch=f"obs.{batch_column}" if batch_column else None, subset=False,
    )
    adata.write_h5ad(output_path)
    return {
        "dataset": output_path, "hvg_column": "highly_variable", "selected": int(adata.var["highly_variable"].sum()),
        "total_genes": adata.n_vars, "flavor": flavor, "batch_column": batch_column,
    }
