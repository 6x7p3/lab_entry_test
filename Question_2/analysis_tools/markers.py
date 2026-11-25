import pandas as pd
import scanpy as sc
from anndata.io import read_h5ad


def identify_markers(
    input_path: str, output_csv: str, group_column: str = "leiden", reference: str = "rest",
    expression_layer: str | None = None, gene_symbol_column: str | None = None, top_n: int = 25,
) -> dict:
    """Rank genes by Wilcoxon test on full log-normalized expression, per group versus rest or a named reference group."""
    adata = read_h5ad(input_path)
    adata.var_names_make_unique()
    adata.obs[group_column] = adata.obs[group_column].astype("string").astype("category")
    source = "X" if expression_layer is None else f"layers.{expression_layer}"
    sc.tl.rank_genes_groups(
        adata, groupby=group_column, reference=reference, use=source, method="wilcoxon", pts=True, n_genes=top_n,
    )
    results = adata.uns["rank_genes_groups"]
    tables = []
    for group in results["names"].dtype.names:
        table = sc.get.rank_genes_groups_df(adata, group=group)
        table.insert(0, "group", group)
        table.insert(1, "reference", reference)
        if reference != "rest":
            table["pct_nz_reference"] = table["names"].map(results["pts"][reference])
        if gene_symbol_column is not None:
            table["gene_symbol"] = table["names"].map(adata.var[gene_symbol_column])
        tables.append(table)
    markers = pd.concat(tables, ignore_index=True).rename(columns={
        "names": "gene_id", "pct_nz_group": "fraction_in_group", "pct_nz_reference": "fraction_in_reference",
    })
    markers.to_csv(output_csv, index=False)
    return {"table": output_csv, "groups": len(tables), "rows": len(markers), "expression": source}
