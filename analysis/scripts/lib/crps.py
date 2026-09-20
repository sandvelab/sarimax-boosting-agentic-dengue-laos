"""The project's own CRPS implementation (plan §4: evaluation is native, not Chap's).

Every model in this project produces a Gaussian predictive distribution (mean, standard
deviation) per forecast cell -- what a SARIMAX fit yields directly, and what stage 2's
correction is added to. `crps_gaussian` is the closed-form CRPS of a normal distribution
against a scalar observation. It must be verified against an independent implementation
before anything downstream trusts it (`verify_crps.py`, in this same directory's sibling
node) -- Rule 1 makes an unverified metric the single most likely way this project ends up
dishonest.

Formula: Gneiting & Raftery (2007), eq. 5 (CRPS of N(mu, sigma) against y):

    z = (y - mu) / sigma
    CRPS = sigma * [ z * (2*Phi(z) - 1) + 2*phi(z) - 1/sqrt(pi) ]
"""
from __future__ import annotations

import math

from scipy.stats import norm


def crps_gaussian(y: float, mu: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError(f"sigma must be positive, got {sigma}")
    z = (y - mu) / sigma
    return sigma * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / math.sqrt(math.pi))


def mean_crps(cells: list[tuple[float, float, float]]) -> float:
    """Mean CRPS over (y, mu, sigma) triples -- one per scored cell."""
    return sum(crps_gaussian(y, mu, sigma) for y, mu, sigma in cells) / len(cells)
