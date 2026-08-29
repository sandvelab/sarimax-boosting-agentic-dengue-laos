"""The negative binomial this baseline needs: fit its dispersion, take its quantiles.

Both entry points need the same two operations on the same distribution, so they are here
rather than in either of them. The parameterisation is the one the construction is stated
in: mean `mu` and dispersion `r`, with

    P(Y = k) = Gamma(k + r) / (Gamma(r) k!) * (r/(r+mu))^r * (mu/(r+mu))^k

so that Var(Y) = mu + mu^2 / r and `r -> infinity` is Poisson.

**Nothing here is random.** The predictive draws are this distribution's quantile function
evaluated at fixed levels, and the dispersion fit is a deterministic search on a fixed
grid. Two runs are byte-identical, and Rule 6 is satisfied by there being nothing to seed
-- the same property the sibling construction has, and for the same reason.

## The dispersion estimate is bounded, and the bounds are not cosmetic

The construction estimates `r` by maximum likelihood from a short window of recent
observations. On this dataset that likelihood is often **unbounded**: when every
observation in the window is zero, and the mean of each is the floor, the log-likelihood
`sum r * log(r/(r+mu))` increases monotonically as `r -> 0`, where the distribution
becomes a point mass at zero. Symmetrically, a window with no more spread than a Poisson
pushes `r` up without limit. So the estimator does not exist without bounds, and the
bounds are stated here, recorded in the fitted object, and counted -- how many provinces
sit at one of them is a property of the construction on a count series that is half
zeros, and it is reported rather than absorbed.
"""

from __future__ import annotations

import math

import numpy as np

# The bounds on the dispersion. Wide enough that they bind only where the likelihood is
# genuinely unbounded, which is the case they exist for; both are recorded per province.
R_MIN = 0.01
R_MAX = 1000.0

# The search: a log-spaced grid, then golden-section refinement inside the winning
# interval. A fixed number of steps of a deterministic search, so the estimate is a
# function of the data alone and two runs agree to the last bit.
GRID = 401
REFINE_STEPS = 80

# Where the pmf summation gives up. It binds only for a very small `r` beside a large
# mean, and when it does the shortfall is recorded rather than silently truncating the
# distribution.
K_MAX = 4_000_000


def loglik(y: np.ndarray, mu: np.ndarray, r: float) -> float:
    """The negative binomial log-likelihood of `y` at means `mu` and dispersion `r`."""
    lg = np.array([math.lgamma(v + r) for v in y]) - math.lgamma(r)
    lg -= np.array([math.lgamma(v + 1.0) for v in y])
    return float(np.sum(lg + r * np.log(r / (r + mu)) + y * np.log(mu / (r + mu))))


def fit_dispersion(y: list[float], mu: list[float]) -> dict:
    """Maximum-likelihood `r` for the pairs `(mu_t, y_t)`, inside [R_MIN, R_MAX].

    Returned with the evidence: how many pairs it used, whether it sits on a bound, and
    the log-likelihood there. A number at a bound is not an estimate and the file has to
    say so.
    """
    values, means = np.asarray(y, dtype=float), np.asarray(mu, dtype=float)
    grid = np.exp(np.linspace(math.log(R_MIN), math.log(R_MAX), GRID))
    scores = [loglik(values, means, float(r)) for r in grid]
    best = int(np.argmax(scores))

    low = float(grid[max(best - 1, 0)])
    high = float(grid[min(best + 1, GRID - 1)])
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = math.log(low), math.log(high)
    c, d = b - phi * (b - a), a + phi * (b - a)
    fc, fd = loglik(values, means, math.exp(c)), loglik(values, means, math.exp(d))
    for _ in range(REFINE_STEPS):
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - phi * (b - a)
            fc = loglik(values, means, math.exp(c))
        else:
            a, c, fc = c, d, fd
            d = a + phi * (b - a)
            fd = loglik(values, means, math.exp(d))
    r = math.exp((a + b) / 2.0)

    at_bound = ""
    if r <= R_MIN * 1.001:
        r, at_bound = R_MIN, "lower"
    elif r >= R_MAX * 0.999:
        r, at_bound = R_MAX, "upper"
    return {
        "dispersion": r,
        "pairs": int(len(values)),
        "at_bound": at_bound,
        "log_likelihood": loglik(values, means, r),
        "observed_values": [float(v) for v in values],
        "means_used": [float(v) for v in means],
    }


def quantiles(mu: float, r: float, levels: np.ndarray) -> tuple[np.ndarray, bool]:
    """The quantile function of NB(mu, r) at `levels`, and whether the sum was truncated.

    Computed by summing the pmf, which is exact in integers and needs no special function
    beyond a logarithm: the pmf ratio `P(k)/P(k-1) = (k-1+r)/k * mu/(mu+r)` turns the
    whole sequence into one cumulative sum. Nearest-rank quantiles, so every draw is a
    count the distribution actually puts mass on -- the same convention as the sibling
    construction's `method="inverted_cdf"`.
    """
    p = mu / (mu + r)
    highest = float(levels.max())
    size = 256
    while True:
        k = np.arange(1, size + 1, dtype=float)
        log_pmf = np.concatenate((
            [r * math.log(r / (r + mu))],
            r * math.log(r / (r + mu)) + np.cumsum(np.log(k - 1.0 + r) - np.log(k))
            + k * math.log(p)))
        cdf = np.cumsum(np.exp(log_pmf))
        if cdf[-1] >= highest or size >= K_MAX:
            break
        size = min(size * 8, K_MAX)
    truncated = bool(cdf[-1] < highest)
    return np.searchsorted(cdf, levels, side="left").astype(float), truncated
