import torch
from torch import nn
from torch.distributions import NegativeBinomial
from torch.nn import functional as F
from torch.utils.data import DataLoader


RANDOM_SEED = 42


class VAE(nn.Module):
    def __init__(self, input_dim, latent_dim=4, hidden_dim=256):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 2 * latent_dim),
        )

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )

        last_layer = self.encoder[-1]
        with torch.no_grad():
            last_layer.weight[latent_dim:].zero_()
            last_layer.bias[latent_dim:].zero_()

    def encode(self, x):
        mu, logvar = self.encoder(x).chunk(2, dim=-1)
        return mu, logvar

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x):
        mu, logvar = self.encode(x)
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + std * eps
        return self.decode(z), mu, logvar

    @staticmethod
    def reconstruction_loss(reconstruction, expression, gene_weights=1.0):
        squared_error = (reconstruction - expression).square()
        return 0.5 * (gene_weights * squared_error).sum(dim=1)


class CellLabelVAE(VAE):
    def __init__(self, input_dim, n_types, n_subtypes, latent_dim=4, hidden_dim=256):
        super().__init__(input_dim, latent_dim, hidden_dim)
        self.type_head = nn.Linear(hidden_dim, n_types)
        self.subtype_head = nn.Linear(hidden_dim, n_subtypes)

    def _decoder_hidden(self, z):
        projection, activation, _ = self.decoder
        return activation(projection(z))

    def label_logits(self, z):
        hidden = self._decoder_hidden(z)
        return self.type_head(hidden), self.subtype_head(hidden)

    def decode(self, z):
        hidden = self._decoder_hidden(z)
        reconstruction = self.decoder[-1](hidden)
        return reconstruction, self.type_head(hidden), self.subtype_head(hidden)


class NBVAE(nn.Module):
    def __init__(self, input_dim, latent_dim=4, hidden_dim=256):
        super().__init__()

        encoder_output = nn.Linear(hidden_dim, 2 * latent_dim)

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            encoder_output,
        )

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )

        self.raw_theta = nn.Parameter(torch.zeros(input_dim))

        with torch.no_grad():
            encoder_output.weight[latent_dim:].zero_()
            encoder_output.bias[latent_dim:].zero_()

    def encode(self, x):
        mu, logvar = self.encoder(x).chunk(2, dim=-1)
        return mu, logvar

    def decode(self, z):
        mean_counts = F.softplus(self.decoder(z)) + 1e-6

        theta = F.softplus(self.raw_theta) + 1e-6

        return NegativeBinomial(
            total_count=theta,
            logits=mean_counts.log() - theta.log(),
        )

    def forward(self, x):
        mu, logvar = self.encode(x)
        std = torch.exp(0.5 * logvar)
        z = mu + std * torch.randn_like(std)

        count_dist = self.decode(z)
        return count_dist, mu, logvar

    @staticmethod
    def reconstruction_loss(count_distribution, counts, gene_weights=1.0):
        return -(gene_weights * count_distribution.log_prob(counts)).sum(dim=1)


def train_vae(model_class, adata, input_layer, checkpoint_path, epochs=30, *, gene_weights=1.0):
    if epochs < 1:
        raise ValueError("Training requires at least one epoch.")
    torch.manual_seed(RANDOM_SEED)
    shuffle_generator = torch.Generator().manual_seed(RANDOM_SEED)
    inputs = torch.as_tensor(adata.layers[input_layer], dtype=torch.float32)
    if not torch.isfinite(inputs).all():
        raise ValueError(f"Non-finite values in expression layer {input_layer!r}.")

    loader = DataLoader(inputs, batch_size=128, shuffle=True, generator=shuffle_generator)
    config = {"input_dim": inputs.shape[1], "latent_dim": 4, "hidden_dim": 256}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    gene_weights = torch.as_tensor(gene_weights, dtype=inputs.dtype, device=device)
    if gene_weights.ndim and gene_weights.shape != (inputs.shape[1],):
        raise ValueError("Expected one reconstruction weight per gene.")
    model = model_class(**config).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        for batch_index, expression in enumerate(loader, start=1):
            expression = expression.to(device)
            optimizer.zero_grad()
            reconstruction, mean, log_variance = model(expression)
            reconstruction_loss = model.reconstruction_loss(reconstruction, expression, gene_weights)
            kl_loss = 0.5 * (mean.square() + log_variance.exp() - 1 - log_variance).sum(dim=1)
            loss = (reconstruction_loss + kl_loss).mean()
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Non-finite loss at epoch {epoch}, batch {batch_index}.")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0, error_if_nonfinite=True)
            optimizer.step()
            total_loss += loss.item() * len(expression)

    torch.save(
        {
            "model_config": config,
            "model_state_dict": model.state_dict(),
            "gene_names": adata.var_names.tolist(),
            "input_layer": input_layer,
            "epoch": epochs,
            "seed": RANDOM_SEED,
        },
        checkpoint_path,
    )
    print(f"{model_class.__name__} | {epochs} epochs | final mean loss {total_loss / len(inputs):.2f}")


@torch.inference_mode()
def load_latent_means(model_class, checkpoint_path, expression):
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    model = model_class(**checkpoint["model_config"])
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    inputs = torch.as_tensor(expression, dtype=torch.float32)
    latent_batches = []
    for batch in inputs.split(128):
        means, _ = model.encode(batch)
        latent_batches.append(means)
    return torch.cat(latent_batches).numpy()
