This is a good question to ask, and the answer is genuinely teachable. I'll build it from the ground up. Everything below is the actual mathematics from the spec — nothing is simplified away, but I'll motivate each piece before using it.

---

# Part 0 — What the system is trying to do

You have ~130 stocks. Every day you want to nominate **one** to buy. To do that you need to rank them by how attractive they are, and to rank them you need a model that predicts something about each stock's future.

The immediate question: **predict its future over what period?** Five days? Twenty-one? Sixty-three? This sounds like a minor implementation detail. It is not. It changes the mathematics of almost everything else, and that is what the entire discussion has been about.

**Notation.** Write the price of stock *i* at time *t* as `P[i,t]`. The **return over the next h days** is

```
R[i,t,h] = P[i,t+h] / P[i,t] − 1
```

We call `h` the **horizon**, measured in trading days. There are 252 trading days in a year, so:

| Name | h |
|---|---|
| 1 week | 5 |
| 1 month | 21 |
| 1 quarter | 63 |

---

# Part 1 — Why the horizon changes everything

## 1.1 Noise grows like the square root of time

Start with the simplest possible model of a stock price: each day it moves by a random amount, and the days are independent. Call the daily move `ε[t]`, with mean zero and standard deviation `σ` (this is "daily volatility").

The return over `h` days is roughly the sum of `h` daily moves:

```
R[h] ≈ ε[1] + ε[2] + ... + ε[h]
```

Now the key fact from probability: **for independent random variables, variances add.** Not standard deviations — variances.

```
Var(R[h]) = Var(ε[1]) + ... + Var(ε[h]) = h·σ²
sd(R[h])  = σ·√h
```

**Layman version.** Flip a fair coin 100 times, counting +1 for heads and −1 for tails. Your total isn't going to be 100 or −100. It'll typically be somewhere around ±10 — the square root of 100. Flip it 10,000 times and you'll typically land around ±100, not ±10,000. Randomness accumulates, but *slowly* — like √n, not n.

Concretely, for a stock with 30% annualised volatility:

```
σ_daily = 0.30 / √252 = 1.89%
sd over 5 days  = 0.30·√(5/252)  = 4.23%
sd over 21 days = 0.30·√(21/252) = 8.66%
sd over 63 days = 0.30·√(63/252) = 15.0%
```

So the 1-quarter label is about **3.5× noisier** than the 1-week label. That alone tells you the two prediction problems are not the same problem.

## 1.2 Signal does *not* grow like √h — and that's the whole story

Suppose your model has found something real: stock *i* has a genuine expected drift of `μ` per day. If that drift persisted forever, the cumulative expected return over `h` days would be `μ·h`.

Then the **signal-to-noise ratio** would be:

```
SNR(h) = μ·h / (σ·√h) = (μ/σ)·√h
```

which *grows* with h. Longer horizon, better. That would mean you should always predict as far out as possible.

But real market signals don't persist forever. They **decay**. If a stock looks cheap today, that cheapness gets arbitraged away over days or weeks. Model this as exponential decay with a **time constant τ** (Greek "tau"), so the drift on day *s* into the future is:

```
μ(s) = μ₀ · e^(−s/τ)
```

**Layman version of τ.** Think of a hot cup of coffee cooling. It doesn't cool by a fixed number of degrees per minute; it cools faster when it's hotter, and the temperature gap shrinks exponentially. τ is the "cooling time" — after τ minutes the gap has fallen to 1/e ≈ 37% of what it was. For a trading signal, τ is how long the edge survives before the market erases it.

The **half-life** is the more intuitive cousin: `t½ = τ·ln2 ≈ 0.693·τ`. That's the time for the edge to fall to half strength.

Now integrate the decaying drift to get the cumulative expected return over h days:

```
∫₀ʰ μ₀·e^(−s/τ) ds = μ₀·τ·(1 − e^(−h/τ))
```

Notice what this does: as `h → ∞`, the bracket goes to 1 and the total **saturates** at `μ₀τ`. You can't harvest more than the signal contains, no matter how long you wait. But the noise keeps growing as √h. So:

```
                    μ₀τ·(1 − e^(−h/τ))          (1 − e^(−h/τ))
    SNR(h)  =  ─────────────────────────  ∝  ──────────────────
                        σ·√h                        √h
```

This is the central equation of the whole discussion. It **rises then falls**. Short horizons: not enough signal accumulated yet. Long horizons: signal is exhausted but noise keeps piling up.

> ## 📐 Lecture 1 — Finding the peak
>
> This is a standard first-year calculus optimisation, worth doing in full because the answer is used repeatedly.
>
> Let `f(h) = (1 − e^(−h/τ)) · h^(−1/2)`. Use the product rule:
>
> ```
> f′(h) = (1/τ)·e^(−h/τ)·h^(−1/2)  −  (1/2)·(1 − e^(−h/τ))·h^(−3/2)
> ```
>
> Set `f′(h) = 0` and multiply through by `h^(3/2)` (legal, since h > 0):
>
> ```
> (h/τ)·e^(−h/τ) − (1/2)·(1 − e^(−h/τ)) = 0
> ```
>
> Substitute `u = h/τ` to make it dimensionless:
>
> ```
> u·e^(−u) = (1/2)·(1 − e^(−u))
> 2u·e^(−u) = 1 − e^(−u)
> ```
>
> Multiply both sides by `e^u`:
>
> ```
>     e^u = 2u + 1
> ```
>
> This is **transcendental** — no closed-form solution. You solve it numerically (Newton's method, or just bisection). `u = 0` is one root but it's the trivial one; the meaningful root is:
>
> ```
> u* ≈ 1.2564        check: e^1.2564 = 3.5128,  2(1.2564)+1 = 3.5128 ✓
> ```
>
> So **h\* = 1.2564·τ**, or in half-life terms, `h* = 1.2564/0.693 = 1.813 × half-life`.

**What this means in practice.** Every feature you feed the model — a 5-day momentum, an RSI, a volume spike, a 200-day moving average — has its own τ. A 5-day momentum signal might have τ ≈ 5 days and therefore be best exploited at a ~6-day horizon. A valuation signal might have τ ≈ 120 days and be best at ~150 days.

**This is why a model trained at one horizon doesn't transfer to another.** It isn't a scaling bug. When you train at h = 5, gradient descent finds the features whose τ makes them useful at 5 days and effectively discards the rest. Retrain at h = 63 and it finds a *different set of features*. You haven't rescaled a model; you've solved a different problem.

---

# Part 2 — How you know whether the model works at all

## 2.1 IC: the metric

The **Information Coefficient** is the correlation between what you predicted and what happened. Specifically, on each date, rank your 130 stocks by predicted attractiveness, rank them again by what actually happened, and compute the correlation between the two rankings (Spearman rank correlation).

- IC = 1: perfect ranking
- IC = 0: no better than random
- IC = −1: perfectly wrong

**What's a good IC?** This is where intuition from other engineering fields misleads badly. In equity prediction, a **sustained IC of 0.03 is a real, valuable edge.** Not 0.3. Not 0.8. Three percent correlation.

> ## 📐 Lecture 2 — Why 0.03 isn't pathetic
>
> Grinold's **Fundamental Law of Active Management**:
>
> ```
> IR = IC · √BR
> ```
>
> `IR` is the Information Ratio (roughly: annual excess return divided by its standard deviation — a quality-of-strategy score). `BR` is **breadth**: the number of genuinely independent bets you make per year.
>
> The insight: a tiny edge, applied many times independently, compounds into a good strategy. This is the casino's business model. A roulette wheel gives the house a 2.7% edge — an "IC" of essentially nothing — and casinos are extremely profitable because they play *millions* of independent rounds.
>
> With IC = 0.03 and 500 independent bets a year: `IR = 0.03 × √500 = 0.67`. That's a decent hedge fund. The edge per decision is negligible; the *aggregate* is not.
>
> This also explains why breadth appears everywhere in the discussion. Both terms matter, and √BR means quadrupling your bets only doubles your IR.

## 2.2 Can you even measure an IC of 0.03? — statistical power

Here's the problem nobody thinks about until it bites. You compute a rank IC on each date and average over your history. But **the average of noisy numbers is itself noisy.** How noisy?

Under the null hypothesis (your model is worthless, true IC = 0), the rank correlation on a single date across `n` stocks has:

```
sd(IC on one date) = 1/√(n − 1)
```

With n = 130, that's `1/√129 = 0.088`. So on any given day, a *worthless* model will show an IC of ±0.088 just by chance — **three times larger than the real edge you're hunting.**

You beat this by averaging over many dates. If you had `T̃` genuinely independent dates:

```
SE(mean IC) = 1 / √((n−1)·T̃)
```

But — and this is the trap — **your dates are not independent.**

> ## 📐 Lecture 3 — Overlapping labels
>
> Suppose you have 1,915 trading days of history and you're predicting 63-day forward returns. You compute a label on every single day. That gives you 1,915 labels. How much information is that?
>
> The label on Monday covers days 1–63. The label on Tuesday covers days 2–64. **They share 62 of their 63 days.** They are almost the same number.
>
> **Layman version.** You want to know the average monthly rainfall in Ottawa. You go outside every day and record the total rainfall over the *previous 30 days*. After a year you have 365 numbers. Do you have 365 measurements of monthly rainfall? No — you have roughly 12. Each consecutive pair of your 365 numbers differs by only one day in and one day out.
>
> The effective number of independent observations is:
>
> ```
> T̃ ≈ T / h
> ```
>
> | Horizon | T = 1,915 days | independent observations |
> |---|---|---|
> | 1w (h=5) | 1,915 labels | ~383 |
> | 1m (h=21) | 1,915 labels | ~91 |
> | 1q (h=63) | 1,915 labels | **~30** |
>
> If you ignore this and treat all 1,915 as independent, your standard errors are too small by a factor of `√h` — **8× at the quarterly horizon.** Your model will look statistically significant when it is noise. This is the single most common way backtests lie.

Putting it together, the t-statistic for "is my IC really above zero?" is:

```
t = IC · √( (n−1)·T / h )
```

And inverting: the **Minimum Detectable Effect** — the smallest IC you could prove exists at confidence level `t*`:

```
MDE(t*) = t* · √( h / ((n−1)·T) )
```

For n = 130, T = 1,915:

| Horizon | MDE at t > 2 | MDE at t > 3 |
|---|---|---|
| 1w | 0.0090 | 0.0135 |
| 1m | 0.0184 | **0.0277** |
| 1q | 0.0319 | **0.0479** |

Read the bottom-right cell carefully. **At the quarterly horizon, on this data, an IC below 0.048 is statistically invisible.** Not "weak" — invisible. You cannot distinguish it from zero. Any quarterly backtest showing something smaller is reporting noise, no matter how good the equity curve looks.

Notice that `n` and `T` enter the formula **identically**. You can buy statistical power with more *history* (wait longer) or more *stocks* (widen the universe). Going from 130 names to 500 multiplies your t-statistic by `√(499/129) = 1.97` — the same effect as quadrupling your history, available today.

---

# Part 3 — Making the labels comparable: volatility normalisation

## 3.1 The problem

You want one model to handle multiple horizons, and you want it to handle both a sleepy utility (15% annual vol) and a semiconductor stock (60% annual vol).

If you train on raw returns, the loss function is dominated by whichever labels happen to be numerically largest — the long horizons and the volatile names. A squared-error loss `Σ(R − R̂)²` doesn't care *why* a number is big; it just chases the big numbers.

**Layman version.** You're grading students across two classes. Class A's test scores range 70–80. Class B's range 20–95. If you rank everyone by raw score, Class B fills both the top and the bottom, and Class A vanishes into the middle — not because those students are average, but because their *scale* is compressed.

## 3.2 The fix

Divide by the expected size of the move:

```
Z[i,t,h] = R[i,t,h] / ( σ̂[i,t] · √h )
```

where `σ̂[i,t]` is an estimate of stock *i*'s daily volatility as of time *t*. The `√h` handles the horizon; the `σ̂[i,t]` handles the stock. Now every label is measured in "how many standard deviations did it move," and all labels — across every stock and every horizon — are on the same scale.

**Where σ̂ comes from.** You could use the standard deviation of past closing prices, but that throws away information you already have. OHLCV data gives you the high and low of each day, which tells you far more about how much the stock moved than the close alone. The **Yang–Zhang estimator** combines overnight gaps, open-to-close range, and intraday high-low, and achieves roughly **14× the statistical efficiency** of close-to-close for the same amount of data. That's free precision — use it.

## 3.3 The subtle part: this also fixes a bias you didn't know you had

This is the deepest point in the whole discussion, so I'll go slowly.

**Every regularised model shrinks its predictions toward the mean.** This is not a bug — it's what regularisation *is*. If a feature's relationship to the target looks strong but the target is noisy, the model correctly hedges: it says "probably +2%, but I'm not confident, so I'll predict +0.8%."

Formally, if the true expected return is `μ[i]` and the model attenuates by a factor `κ[i]`:

```
prediction ≈ κ[i] · μ[i]        where 0 < κ[i] < 1
```

And **κ depends on the local signal-to-noise ratio.** Where the label is noisy, the model shrinks harder.

Now: if you train on **raw returns**, the noise in the label for stock *i* is `σ[i]·√h` — it varies by stock. High-volatility stocks have noisier labels. So the model shrinks their predictions **more**:

```
κ[i] is a decreasing function of σ[i]
```

The consequence: **high-volatility stocks get systematically pushed toward the middle of your ranking.** They don't get ranked low because they're unattractive — they get ranked low because the model is less sure about them. Your ranker has acquired a hidden preference for boring stocks, and nothing in your code says so.

**Layman version.** Two students. Alice scores 78, 79, 77, 78 — dead consistent. Bob scores 45, 95, 30, 98 — wildly erratic, same average. If you're asked "who will score higher on the next test?", a cautious predictor says "Alice, 78; Bob, probably around 68" — hedging Bob toward the class average precisely *because* he's unpredictable. That hedge is statistically correct for guessing Bob's score. But if you now use those predictions to *rank* students, you've systematically demoted every erratic student. That's a different question, and you've answered it wrong.

**Now watch what normalisation does.** If you train on `Z = R/(σ̂√h)`, the noise in every label is the same size by construction — about 1. Homoskedastic. So the shrinkage factor is **uniform**:

```
Ẑ[i] ≈ λ · μ[i] / (σ̂[i]·√h)        one single λ for all stocks
```

Multiply back by `σ̂[i]·√h` to return to return units:

```
Ẑ[i] · σ̂[i]·√h ≈ λ · μ[i]
```

Every stock's true expected return, scaled by **the same constant λ**. A uniform rescaling doesn't change the ordering. The bias is gone.

## 3.4 But rank on the *de-normalised* value

Here's the trap on the other side. Having fitted on `Z`, it's tempting to just rank on `Ẑ` directly. **Don't.** `Z` is return divided by volatility — that's a **Sharpe ratio**. Ranking by predicted Sharpe systematically favours low-volatility stocks, which is a well-documented factor exposure (the "low-volatility anomaly"). Your backtest would look great for a reason that has nothing to do with your features.

So the rule, which the spec calls QA-58:

> **Normalise for the loss. De-normalise for the decision.**
> Fit on `Z = R/(σ̂√h)`. Rank on `Ẑ · σ̂√h`.

The normalisation earns its keep during fitting — comparable scales, uniform shrinkage — and then gets undone before it can contaminate the decision.

---

# Part 4 — Units: how a factor-of-385 error hides in plain sight

The system combines three model outputs into a single score:

```
opportunity = 0.5·z(rank_score) + 0.3·z(pred_return) + 0.2·z(prob_up)
```

Each `z(·)` is a **z-score** — standardised to mean 0, standard deviation 1. So `opportunity` is **dimensionless**. It's a score, not a return.

Now the system wants to discourage churn: if you already hold stock A and stock B looks slightly better, don't switch unless B is better by enough to cover the trading cost. So it subtracts a penalty:

```
adjusted_opportunity = opportunity − penalty
```

The code sets `penalty = 10 bps / 10⁴ = 0.001`.

**This is a dimensional error.** You are subtracting a *return* from a *score*. It's `5 metres − 3 seconds`. The number 0.001 happens to be small, so nothing crashes — the penalty just quietly does nothing (it's 0.1% of one standard deviation of opportunity).

To fix it you need a **conversion factor**: how much expected return is one unit of opportunity worth?

That's a regression slope. Regress realised forward return on opportunity:

```
β = Cov(R, opp) / Var(opp) = ρ · sd(R) / sd(opp)
```

With ρ = IC = 0.03, `sd(R₂₁) = 8.66%`, `sd(opp) = 1`:

```
β = 0.03 × 0.0866 = 0.0026
```

**One unit of opportunity is worth 26 basis points of expected return.** So a round-trip cost of `rt` requires:

```
penalty_z = rt / β
```

At rt = 32 bps: `penalty_z = 0.0032 / 0.0026 = 1.23`. The code has 0.001. The error factor is `1/β ≈ 385×`.

> ## 📐 Lecture 4 — Why the direction of the regression matters
>
> This is where both AI agents got it wrong, in opposite directions, and it's a classic.
>
> For two variables *x* and *y* with correlation ρ, there are **two different regression lines**:
>
> ```
> slope of y on x:   β_{y|x} = ρ · σ_y / σ_x
> slope of x on y:   β_{x|y} = ρ · σ_x / σ_y
> ```
>
> These are **not reciprocals.** Their product is:
>
> ```
> β_{y|x} · β_{x|y} = ρ²
> ```
>
> They're only reciprocal when ρ = 1 — a perfect relationship. The weaker the correlation, the further apart the two lines.

Here is what that looks like geometrically:**Layman version — Galton's heights.** Francis Galton measured fathers and sons. Two facts, both true:

- Tall fathers have sons who are, on average, *shorter* than them (closer to the population mean).
- Tall sons have fathers who are, on average, *shorter* than them.

That sounds contradictory until you realise these are two different regression lines. Predicting sons from fathers is not the inverse of predicting fathers from sons. Both lines pass through the mean, but they have different slopes, and the weaker the correlation the more they splay apart.

Applied here, with ρ = 0.03:

| Recipe | Value | Verdict |
|---|---|---|
| `penalty = rt` (current code) | 0.001 | wrong units — off by `1/β ≈ 385×` |
| `penalty = rt / sd(pred_return)` | 0.11 – 0.21 | assumes the model is perfect (`ρ = 1`) |
| `penalty = rt × slope(opp on R)` | 0.0011 | **wrong regression** — off by a further `1/ρ² ≈ 1111×` |
| **`penalty = rt / β`** | **1.23** | correct |

**And the economic reading is the most important result in the whole thread.** The correct penalty is about *one full standard deviation* of opportunity. In plain language: **a model with IC = 0.03 barely distinguishes one stock from another, so it should almost never pay a guaranteed 32 bps to chase an uncertain 26 bps.** The right behaviour is to hold what you have. That conclusion falls out of the arithmetic alone, with no reference to the mandate — and the mandate independently says "hold winners, trim rather than exit." When your model and your policy agree for independent reasons, you've probably got both right.

---

# Part 5 — Trading costs and why they pick the horizon

## 5.1 Cost scales inversely with horizon

If you hold a position for `h` days, you trade `252/h` times per year. Each round trip costs some fraction `c` of the position. So the annual drag is:

```
drag(h) = c · 252 / h
```

At c = 32 bps: `1w → 16.1%/yr`, `1m → 3.8%`, `1q → 1.3%`. **A 5-day strategy has to overcome a 16% annual headwind that a 21-day strategy doesn't.**

## 5.2 But gross returns favour *short* horizons

Recall the Fundamental Law, `IR = IC·√BR`. Trading every 5 days gives you `252/5 = 50.4` rebalances a year; every 21 days gives 12. So `BR ∝ 252/h`. Combining with the decay law:

```
IR(h) ∝ IC(h) · √BR  ∝  (1−e^(−h/τ))/√h · √(252/h)  ∝  (1 − e^(−h/τ)) / h
```

Is this increasing or decreasing in h? Setting the derivative to zero gives `u = e^u − 1`, whose only root is `u = 0`. Since `e^u − 1 > u` for all `u > 0`, the derivative is always negative. So:

> **Gross information ratio is monotonically decreasing in horizon.** Before costs, shorter is always better.

That's a genuinely important structural result: **cost is the *only* thing that stops you from trading as fast as possible.** There is no interior optimum without it.

## 5.3 Where the two forces balance

`net(h) = [A·(1−e^(−h/τ)) − 252c] / h`. Maximising numerically:

| τ | optimal h | net at 21d as % of the optimum |
|---|---|---|
| 15 d | 20 days | 99.8% |
| 30 d | 25 days | 98.4% |
| 50 d | 31 days | 94.9% |

The optimum barely moves across the plausible range of τ, because the *cost* term pins its location, not the decay term. **Roughly 21 days is right whatever the signal turns out to be.** That robustness is why the production horizon could be settled before measuring τ.

*(An important caveat that came out of the review: the actual cost model in your repository charges a flat $10/trade, not a percentage, and spread and slippage aren't modelled at all. So `c` is currently unknown, and this argument is suspended until it's measured. The horizon decision now rests mainly on the tax/regulatory constraint, not on this arithmetic.)*

---

# Part 6 — The conclusion: how to train the model

Here is the complete recipe, with the reason for each step.

### 1. Fix the validation protocol first

You cannot measure anything until measurement is honest.

- **Purge and embargo.** Drop any training sample whose label window overlaps a test sample, plus `h` days of buffer on each side. Otherwise the model sees the future.
- **Uniqueness weighting.** Weight each observation by `1/c_t`, averaged over its label span, where `c_t` counts labels concurrently open at time `t`. This stops overlapping labels from counting as independent evidence.
- **Deflated Sharpe.** You're testing across horizons and hyperparameters; correct for the number of trials.

Expect your existing numbers to drop when you do this. That drop is the measurement, not a regression.

### 2. Fix the target

```
Z[i,t,h] = R[i,t,h] / ( σ̂[i,t] · √h )
```

Estimate `σ̂` with Yang–Zhang from OHLC. This buys comparable scales across horizons and names, and uniform shrinkage.

### 3. Build multi-scale features, then measure decay

Compute each indicator at lookbacks of roughly 1×, 4×, and 16× the shortest horizon. Then — and only then — measure `IC(h)` for every feature across a grid of h, and fit `τ` per feature. Do this *before* the power calculation, because the power calculation needs `IC(h)`.

### 4. Check you have the statistical power

```
MDE(t*) = t* · √( h / ((n−1)·T) )
```

If the MDE at your chosen horizon exceeds the IC you could plausibly achieve, stop — you cannot validate a model there no matter how good it is. If the number is uncomfortable, remember `n` and `T` enter identically: widening from 130 to 500 names buys the same power as quadrupling your history.

### 5. Train one model across horizons, with the horizon as an input

Rather than three separate models, stack your training rows so each `(stock, date)` appears once per horizon, with `h` as a feature. This lets the 21-day head borrow statistical strength from the 5-day rows, which carry far more effective evidence. Weight the stacked copies deliberately — the default uniqueness weighting gives 1-week rows about 12.6× the influence of 1-quarter rows, which is a decision, not a side effect.

Use **pinball (quantile) loss** at several quantiles rather than squared error. This gives you a prediction *interval*, not just a point — P10/P50/P90 — which is what a stop-loss and a target price actually need. And the median (α = 0.5) is more robust to the fat tails that dominate an L2 fit.

### 6. Rank on the de-normalised prediction

```
score[i] = Ẑ[i] · σ̂[i] · √h
```

Never rank on `Ẑ` itself — that ranks Sharpe ratios and buys you the low-volatility anomaly by accident. Then verify: report IC conditional on volatility decile and confirm no tilt has leaked in either direction.

### 7. Separate selection from timing

The two decisions have different natural horizons and should not share a model:

- **Selection** (which stock) at 21 days — a cross-sectional ranking problem.
- **Timing** (when to enter, when to exit) at 5 days — a barrier problem, better served by triple-barrier labels than by return prediction.

### 8. Size the turnover penalty correctly

```
penalty_z = rt / β,     β = slope of realised return regressed ON opportunity
```

Measure β empirically. At realistic IC this lands near 1σ of opportunity, meaning the system holds rather than churns — which is both statistically and economically correct.

---

## The one-paragraph version

Longer horizons have more accumulated signal but proportionally more noise, and far fewer independent observations — so a model trained at one horizon is solving a genuinely different problem than the same model at another, and cannot be transferred. The fix is not a bigger network. It is: normalise the labels so all horizons and all stocks live on one scale, train a single model with the horizon supplied as an input so the data-rich horizons subsidise the data-poor ones, validate with purging and uniqueness weighting so overlapping labels don't manufacture false confidence, convert the predictions back to return units before making any decision, and size every cost and penalty in the units of the thing it's subtracted from. Then choose your production horizon based on where costs and signal decay balance — which, for retail equity with realistic trading frictions, is around a month almost regardless of what the signal turns out to be.
