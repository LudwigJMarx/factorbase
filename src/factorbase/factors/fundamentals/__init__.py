"""Factors computed from reported accounts.

── THE SHAPE OF THE INPUT ──────────────────────────────────────────────────

One frame, one instrument, indexed by period end and ordered by it. A `period`
column says which basis each row is on: annual, quarterly or ttm. Rows of
different bases live side by side, and every function here selects the basis it
needs rather than assuming the caller filtered first. Assuming would mean a
frame of quarterly rows silently producing annual-looking ratios.

── THE ONE DESIGN DECISION ─────────────────────────────────────────────────

The trailing, annual and multi-year-average readings of a ratio are the same
factor with different parameters, not different factors. A catalogue with
separate entries for "return on equity", "return on equity (TTM)" and "average
return on equity" has three places to fix one formula. Here there is one entry
with `period` and `average_years`, and the entry says which combinations its
source data has to support.
"""

from __future__ import annotations
