# Claim

What does the plan's fixed backtest scheme (n_periods=3, n_splits=8, stride=3, expanding window ending at the development file's last period) resolve to as concrete train/test month windows?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

Eight splits, expanding window, evaluated span **2008-01 to 2009-12** (24 months), the first
split trained on 1998-01–2007-12 (120 months) and the last on 1998-01–2009-09 (141 months).
Matches the prior project's own reported figures for the same scheme, computed independently
here. `results/split_schedule.csv`.
