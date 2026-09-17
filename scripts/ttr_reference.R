# Compute the TTR side of the cross-check.
#
# Reads the committed price series and writes one column per mapping in
# catalog/mappings/ttr.yaml. Both sides read the same bytes: regenerating the
# series on each side would make the two disagree before the first indicator.
#
# Column names here are the contract. check_against_ttr.py asserts that every
# mapping names a column that exists and that every column is named by a
# mapping, so a column cannot be added and quietly ignored.
#
# Usage:  Rscript scripts/ttr_reference.R <input.csv> <output.csv>

suppressPackageStartupMessages(library(TTR))

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("usage: ttr_reference.R <input.csv> <output.csv>")

d <- read.csv(args[1])
hlc <- as.matrix(d[, c("high", "low", "close")])
hl <- as.matrix(d[, c("high", "low")])
p <- d$close
v <- d$volume

out <- data.frame(row = seq_len(nrow(d)))

# Agreeing outright.
out$sma <- SMA(p, 20)
out$ema <- EMA(p, 20)
out$wma <- WMA(p, 20)
out$rsi <- RSI(p, 14)
out$rate_of_change <- ROC(p, 12, type = "discrete") * 100
out$cci <- CCI(hlc, 20, c = 0.015)
out$close_location_value <- CLV(hlc)
out$accumulation_distribution_line <- chaikinAD(hlc, v)
out$money_flow_index <- MFI(hlc, v, 14)
out$williams_percent_r <- WPR(hlc, 14) * -100

st <- stoch(hlc, nFastK = 14, nFastD = 3, nSlowD = 3, bounded = TRUE, smooth = 1)
out$stochastic_fast_k <- st[, "fastK"] * 100
out$stochastic_fast_d <- st[, "fastD"] * 100
out$stochastic_slow_d <- st[, "slowD"] * 100

out$macd <- MACD(p, 12, 26, 9, maType = "EMA", percent = FALSE)[, "macd"]
out$bollinger_percent_b <- BBands(p, n = 20, sd = 2)[, "pctB"]

# TTR counts the lookback interval where this catalogue counts the window, so
# its n is one lower for the same measurement.
ar <- aroon(hl, 24)
out$aroon_up <- ar[, "aroonUp"]
out$aroon_down <- ar[, "aroonDn"]

# Agreeing only once the seed has decayed away.
atr <- ATR(hlc, 14)
out$true_range <- atr[, "tr"]
out$atr <- atr[, "atr"]
adx <- ADX(hlc, 14)
out$plus_di <- adx[, "DIp"]
out$minus_di <- adx[, "DIn"]
out$adx <- adx[, "ADX"]

# The traps: the call a reader reaches for first, which is not the one above.
out$trap_bollinger_percent_b_hlc <- BBands(hlc, n = 20, sd = 2)[, "pctB"]
out$trap_macd_percent <- MACD(p, 12, 26, 9, maType = "EMA", percent = TRUE)[, "macd"]
out$trap_rsi_ema <- RSI(p, 14, maType = "EMA")
out$trap_aroon_up_same_n <- aroon(hl, 25)[, "aroonUp"]
out$trap_volatility_close <- volatility(p, n = 250, calc = "close", N = 250) * 100

write.csv(out, args[2], row.names = FALSE, na = "")
cat(sprintf(
  "ttr_reference: TTR %s on R %s, %d columns over %d rows\n",
  as.character(packageVersion("TTR")), getRversion(), ncol(out) - 1L, nrow(out)
))
