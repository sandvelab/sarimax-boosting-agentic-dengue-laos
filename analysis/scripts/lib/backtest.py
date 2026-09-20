"""The project's fixed backtest scheme (plan §4: n_periods=3, n_splits=8, stride=3).

Expanding-window, refit-every-split (n_retrain=1 in Chap's vocabulary), with the evaluated
span always ending at the last period of the file being backtested -- the same arithmetic
convention the prior project in this repository verified against Chap's own splitter and
reused here, applied by our own code since evaluation is native this time (plan §4).
"""
from __future__ import annotations


def rolling_splits(
    months: list[str], n_periods: int = 3, n_splits: int = 8, stride: int = 3
) -> list[dict]:
    """Rolling-origin splits over a sorted list of "YYYY-MM" period strings.

    Each split trains on every month up to and including `train_end`, and forecasts the
    `n_periods` months immediately after it. The last split's test window ends at the last
    month in `months`; earlier splits step back by `stride` months at a time.
    """
    n = len(months)
    splits = []
    for i in range(n_splits):
        offset = (n_splits - 1 - i) * stride
        test_end_idx = n - 1 - offset
        test_start_idx = test_end_idx - n_periods + 1
        train_end_idx = test_start_idx - 1
        if train_end_idx < 0 or test_start_idx < 0:
            raise ValueError(
                f"split {i}: not enough months ({n}) for n_periods={n_periods}, "
                f"n_splits={n_splits}, stride={stride}"
            )
        splits.append({
            "split": i,
            "train_months": months[: train_end_idx + 1],
            "test_months": months[test_start_idx: test_end_idx + 1],
        })
    return splits
