import matplotlib.pyplot as plt
import scanpy as sc
from anndata.io import read_h5ad


def reduce_dimensions(
    input_path: str, output_path: str, n_pcs: int = 30, n_neighbors: int = 15, seed: int = 42,
) -> dict:
    """Compute PCA on flagged HVGs, a neighbor graph on the PCs, and a 2D UMAP. Save all three in the output h5ad."""
    adata = read_h5ad(input_path)
    sc.pp.pca(adata, n_comps=n_pcs, mask=adata.var["highly_variable"].to_numpy(), rng=seed)
    sc.pp.neighbors(adata, use="obsm.X_pca", n_neighbors=n_neighbors, rng=seed)
    sc.tl.umap(adata, rng=seed)
    adata.write_h5ad(output_path)
    return {"dataset": output_path, "n_pcs": n_pcs, "n_neighbors": n_neighbors, "seed": seed}


def cluster_cells(input_path: str, output_path: str, plot_path: str, resolution: float, seed: int = 42) -> dict:
    """Cluster the existing neighbor graph with Leiden at the specified resolution and plot labels on the saved UMAP."""
    adata = read_h5ad(input_path)
    sc.tl.leiden(adata, resolution=resolution, flavor="igraph", directed=False, rng=seed)
    axis = sc.pl.legacy.umap(adata, color="leiden", show=False)
    axis.figure.savefig(plot_path, bbox_inches="tight")
    plt.close(axis.figure)
    adata.write_h5ad(output_path)
    return {
        "dataset": output_path, "plot": plot_path, "cluster_column": "leiden",
        "cluster_sizes": adata.obs["leiden"].value_counts().to_dict(), "resolution": resolution, "seed": seed,
    }
