from pathlib import Path
from typing import Literal, NotRequired, TypedDict

import matplotlib.pyplot as plt
import pandas as pd
import scanpy as sc
from anndata.io import read_h5ad


class QcRule(TypedDict):
    metric: Literal["total_counts", "n_genes_by_counts", "pct_counts_mt"]
    minimum: NotRequired[float]
    maximum: NotRequired[float]
    sample: NotRequired[str]


def qc_report(
    input_path: str, output_dir: str, count_layer: str | None = None,
    sample_column: str | None = None, gene_symbol_column: str | None = None,
    mitochondrial_prefix: str = "MT-",
) -> dict:
    """Report QC on raw counts (X or count_layer). Save cells with QC metrics, per-sample quantiles, and boxplots."""
    adata = read_h5ad(input_path)
    if count_layer is None and "log1p" in adata.uns:
        raise ValueError("X is marked as log-transformed. Supply the raw count layer.")
    symbols = adata.var_names if gene_symbol_column is None else adata.var[gene_symbol_column]
    mt = symbols.str.upper().str.startswith(mitochondrial_prefix.upper(), na=False)
    qc_vars = []
    columns = ["total_counts", "n_genes_by_counts"]
    if mt.any():
        adata.var["mt"] = mt
        qc_vars.append("mt")
        columns.append("pct_counts_mt")
    metrics = sc.pp.calculate_qc_metrics(
        adata, use="X" if count_layer is None else f"layers.{count_layer}",
        qc_vars=qc_vars, percent_top=None, log1p=False, out=True,
    ).obs[columns]
    adata.obs[columns] = metrics
    samples = adata.obs[sample_column] if sample_column is not None else pd.Series("all", index=metrics.index)
    groups = metrics.groupby(samples, observed=True, dropna=False)
    adata.uns["qc_report"] = {"metrics": columns, "count_source": count_layer or "X"}
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    summary = groups.quantile([0, 0.25, 0.5, 0.75, 1]).rename_axis(["sample", "quantile"])
    summary["cells"] = summary.index.get_level_values("sample").map(groups.size())
    summary.to_csv(directory / "qc_summary.csv")
    figure, axes = plt.subplots(len(columns), 1, figsize=(8, 3 * len(columns)), layout="constrained")
    for metric, axis in zip(columns, axes):
        axis.boxplot([rows[metric].dropna() for _, rows in groups], tick_labels=[str(sample) for sample, _ in groups])
        axis.set_ylabel(metric)
    figure.savefig(directory / "qc.png")
    plt.close(figure)
    adata.write_h5ad(directory / "qc.h5ad")
    return {
        "dataset": str(directory / "qc.h5ad"), "summary": str(directory / "qc_summary.csv"),
        "plot": str(directory / "qc.png"), "cells": adata.n_obs, "mitochondrial_genes_matched": int(mt.sum()),
    }


def apply_qc_filters(
    input_path: str, output_path: str, rules: list[QcRule], sample_column: str | None = None,
) -> dict:
    """Apply explicit inclusive QC bounds to qc_report output. Each rule can target one sample in sample_column."""
    adata = read_h5ad(input_path)
    keep = pd.Series(True, index=adata.obs_names)
    counts = []
    for rule in rules:
        if rule["metric"] not in adata.uns["qc_report"]["metrics"]:
            raise ValueError(f"Metric unavailable in this QC report: {rule['metric']}")
        values = adata.obs[rule["metric"]]
        minimum, maximum = rule.get("minimum"), rule.get("maximum")
        if minimum is None and maximum is None:
            raise ValueError("Each QC rule needs a minimum or maximum.")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("The minimum exceeds the maximum.")
        lower = -float("inf") if minimum is None else minimum
        upper = float("inf") if maximum is None else maximum
        flagged = ~values.between(lower, upper).fillna(False)
        if "sample" in rule:
            if sample_column is None:
                raise ValueError("A sample-specific rule requires sample_column.")
            selected = adata.obs[sample_column].astype("string").eq(rule["sample"]).fillna(False)
            if not selected.any():
                raise ValueError(f"Unknown sample: {rule['sample']}")
            flagged &= selected
        counts.append({**rule, "flagged": int(flagged.sum())})
        keep &= ~flagged
    adata[keep].write_h5ad(output_path)
    return {"dataset": output_path, "before": adata.n_obs, "retained": int(keep.sum()), "rules": counts}
