<!-- ARCHIVED — DO NOT CODE FROM THIS FILE -->

> **⚠️ ARCHIVED / HISTORICAL — NOT AUTHORITATIVE.** Frozen on 2026-08-08. This is a pre-SDD
> Release 1–5 document, kept as an immutable record of what was decided at the time. It does **not**
> describe the code today and it is **not** a set of instructions to execute. Paths inside predate the
> `notebooks/` → `sdd/` rename and are deliberately left unrewritten.
>
> **Authoritative sources:** `sdd/specs/vision.md` (what this project is) ·
> `sdd/specs/constitution.md` (the rules) · `sdd/specs/F<n>_<slug>/spec.md` (what a feature must do) ·
> `sdd/specs/F0_code_map/spec.md` (what the code currently looks like). See `sdd/archive/README.md`.

---

# **📘 Investment AI Agent — Full System Documentation**

# ***Version 1 - 2026/Jan/31***

## **1. Introduction**

### **1.1 Framing the Personal Investment Problem**

This project reframes personal investing as an **AI‑driven decision system**:

- The AI processes market data every day
- Predicts short‑term (1‑week) stock performance
- Selects the best opportunities
- Manages risk and portfolio turnover
- Produces clear BUY / SELL / HOLD recommendations

The goal is to replace intuition with **systematic, data‑driven discipline**.

---

### **1.2 Training Data**

This AI Agent is trained based on a focused set of **30 large‑cap technology and market‑leading stocks**.
**Cash** is treated as the 31st "virtual stock", to determine when no stock is worth holding.
This choice is intentional:

- High liquidity → easy execution
- Strong fundamentals → fewer anomalies
- Rich historical data → better ML training
- High volatility → more exploitable short‑term signals
- Manageable universe size → reduces noise and overfitting

A small, high‑quality universe improves:

- Model stability
- Signal strength
- Backtest reliability
- Interpretability

---

### **1.3 Why Cash Is Treated as a Stock**

Cash is modeled as a “virtual stock” with:

- Zero return
- Zero volatility
- Zero risk

This allows the SlotSelector to choose:

- **1–3 stocks**, or
- **Cash**, when no stock meets the opportunity threshold

This is essential for:

- Bear markets
- High‑volatility periods
- Low‑confidence days

---

### **1.4 Why a 3‑Slot Maximum Portfolio**

The portfolio is intentionally limited to **3 positions**:

- Concentration increases expected return
- Reduces over‑diversification
- Keeps transaction costs manageable
- Matches the model’s ability to rank top opportunities
- Simplifies execution and interpretation

This is a **high‑conviction, low‑churn** strategy.

---

### **1.5 Why only 1‑week Horizon in Version-1?**
It gives the fastest feedback loop, the most training samples, and the simplest policy logic.

---

## **2. AI Models**

This 1st-version uses **3 independent ML models**, each capturing a different dimension of market behavior.

---

### **2.1 Ranker Model (Cross‑Sectional Ranking)**

**Purpose:**
Identify which stocks are likely to outperform others over the next week.
- It uses lgb.LGBMRanker with objective="lambdarank".
- It constructs group sizes based on dates (X.groupby("date").size()). This is critical for ranking because the model needs to know which stocks compete against each other on the same day.

**Input:**
- Technical indicators
- Momentum features
- Volatility features
- Trend features
- Market regime features

**Output:**
- `rank_score` (continuous value)
Higher = better expected relative performance.

**Why Needed:**
Ranking models excel in **cross‑sectional selection**, where the goal is to pick the best stocks *relative to each other*.

---

### **2.2 Regressor Model (1‑Week Return Prediction)**

**Purpose:**
Estimate the **magnitude** of the expected return.
- This provides the "magnitude" signal. Even if the Ranker says "Stock A is \#1", the Regressor might say "Stock A will only return 0.01%". This helps you decide if the trade is worth the transaction cost.
- It uses lgb.LGBMRegressor trained on y_reg (the raw float return).

**Input:**
Same feature set as Ranker.

**Output:**
- `pred_return` (float)
Example: `0.012` = +1.2% expected return next week.

**Why Needed:**
Ranker tells *who is better*, but not *by how much*.
Magnitude helps distinguish:

- Strong opportunities
- Weak but positive opportunities
- False positives

---

### **2.3 Classifier Model (Up/Down Probability)**

**Purpose:**
Estimate the **probability** that the stock will be positive next week.
- It uses lgb.LGBMClassifier with objective="binary".
- This acts as a filter. If the Ranker picks a stock but the Classifier says "40% chance of being positive," you can block the trade.

**Input:**
Same feature set.

**Output:**
- `prob_up` (0–1)

**Why Needed:**
Acts as a **quality filter**:

- High prob_up → stable, reliable signals
- Low prob_up → volatile or noisy stocks

This prevents the system from selecting stocks with high predicted return but low confidence.

---

### **2.4 Why Three Models?**

Each model captures a different dimension:

| Model      | Captures               | Strength                           |
|------------|------------------------|------------------------------------|
| Ranker     | Relative performance   | Best for cross‑sectional selection |
| Regressor  | Magnitude of return    | Helps size opportunities           |
| Classifier | Confidence / stability | Reduces false positives            |

These 3 models form your **voting ensemble**.
The **SlotSelector** combines all 3 ML outputs into a single **opportunity score**,
and provide recommendation of buy/sell/hold daily.

---

### **2.5 Why Independently Training 3 Models instead of Sequential (Stacking)?**

This is a deliberate architectural choice called **Parallel Ensembling (Bagging-style)** vs. **Sequential Stacking**.

**Reason 1: Error Independence (Robustness)**
If we feed the Regressor's output into the Ranker, you create a "Chain of Failure."
- Sequential Risk: If the Regressor has a bug or encounters a market anomaly (e.g., predicts +500% return due to a data glitch), the Ranker will "trust" that feature and likely rank it #1 erroneously.
- Parallel Strength: By keeping them separate, they act as independent voters. If the Regressor hallucinates a +500% return but the Classifier sees "Low Probability," the system can detect the conflict and abstain from trading.


**Reason 2: Different Mathematical Objectives**
The models are looking at the data through different "lenses":
- The Ranker minimizes NDCG (listwise error). It doesn't care if the market is crashing; it just wants to find the stock that crashes the least.
- The Regressor minimizes MSE (pointwise error). It cares deeply about the absolute value.
- The Classifier minimizes LogLoss (probability error). It cares about the boundary between profit and loss.

If you feed Model 1 into Model 2, you force Model 2 to inherit the specific biases of Model 1's objective function. Keeping them separate preserves the diversity of signals.


**Reason 3: Data Leakage Prevention**
"Stacking" (feeding model outputs into other models) is notoriously difficult to do correctly in time-series finance. To do it right, you need Out-of-Fold (OOF) predictions. You cannot simply train Model 1 on 2015-2023 and feed its predictions to Model 2 on 2015-2023, or Model 2 will just learn to trust Model 1 perfectly (overfitting). You would need complex "expanding window" training schemes which significantly complicate your pipeline for a V1 project.

---

## **3. Data Pipeline**

### **3.1 Raw Data Ingested**

Using yfinance:

- Daily OHLCV
- Adjusted close
- Market index proxies
- Volume and liquidity metrics

---

### **3.2 Engineered Features**

The system generates:

#### **Momentum Features**
- 1‑day, 5‑day, 20‑day returns
- Relative strength vs universe
- Price acceleration

#### **Volatility Features**
- 5‑day, 20‑day rolling volatility
- ATR (Average True Range)
- High‑low range ratios

#### **Trend Features**
- SMA (5, 20)
- EMA (5, 20)
- Trend slope

#### **Market Regime Features**
- SPY volatility
- VIX proxy
- Market breadth

#### **Why These Features?**

They capture:

- Short‑term momentum
- Trend continuation
- Volatility clustering
- Market risk regime
- Cross‑sectional dispersion

These are the core drivers of 1‑week stock behavior.

---

## **4. Project Architecture**

### **4.1 Object‑Oriented Components**

| Component                | Purpose                                      |
|--------------------------|----------------------------------------------|
| **DataLoader**           | Fetches raw price data, incremental updates  |
| **OhlcvFeatureEngineer** | Builds technical features                    |
| **ModelManager**         | Saves/loads model versions                   |
| **RankerModel**          | Trains LightGBM ranker                       |
| **RegressorModel**       | Trains LightGBM regressor                    |
| **ClassifierModel**      | Trains LightGBM classifier                   |
| **SlotSelector**         | Combines model outputs → portfolio decisions |
| **Backtester**           | Simulates historical performance             |
| **main_train.py**        | Full training pipeline                       |
| **main_inference.py**    | Daily inference engine                       |

---

## **4.2 SlotSelector — Core Logic**

### **Inputs:**
- `rank_score`
- `pred_return`
- `prob_up`
- `current_positions`

### **Opportunity Score Formula**

```
opportunity =
    c_rank * norm_rank
  + c_ret  * (pred_return * 10)
  + c_prob * (prob_up - 0.5)
```

Where:

- `c_rank`, `c_ret`, `c_prob` are optimized coefficients (by SlotSelector::optimize_coefficients())
- `pred_return * 10` scales returns to match rank magnitude
- `(prob_up - 0.5)` centers confidence around zero

### **Coefficient Optimization**

`c_rank`, `c_ret`, `c_prob` are determined by brute‑force grid search:

- rank coefficient: 0.5–0.7
- return coefficient: 0.3–0.4
- prob coefficient: 0.0–0.2

Backtester evaluates Sharpe ratio for each combination.

The best coefficients are saved to `policy_params.json`.

---

## **4.3 Challenger vs Incumbent Logic (Hysteresis)**

A new stock (***challenger***) replaces an existing one (***incumbent***) only after penalized twice:

```
1. _turnover_penalty() {
    # Makes it harder for a new stock to enter the "Top 3" list
    adj_opportunity(new) = opportunity(new) - turnover_penalty_bps
}

2. _apply_hysteresis() {
    # The "Top 3" list has to be better than Incumbent by swap_buffer
    adj_opportunity(new) > adj_opportunity(old) + swap_buffer
}
```

Where:

- `turnover_penalty_bps = 0.10`
- `swap_buffer = 0.005`
- Prevents unnecessary churn (excessive trading)
- Ensures only meaningful improvements trigger trades

This ensures:

- Stability
- Lower transaction costs
- Higher signal quality

---

## **4.4 Rolling‑Window Backtesting (1‑Week Horizon)**

The problem with Backtest horizon is that Agent's recommendations are all based on 1-week signals.
However, in reality, portfolio fluctuates daily, and stocks can be bought/sold at any trading day.
To solve this horizon-mismatch, BackTester applies the industry's standard Rolling-Window (Staggered Portfolio) method:

- Capital is split into **5 buckets**, each holding 1/5 of total capital
- Each bucket is rebalanced once every 5 days (staggered by 1 day)
- Each stock is held for exactly 5 days per bucket
- Daily PnL is aggregated across all active buckets

This fixes the **horizon mismatch** between:

- 1‑week model predictions
- 1‑day backtest evaluation

This is the correct institutional approach for multi‑day signals.

---

### **Correct Implementation Details**

#### Step 1 — One Shared Daily Target (no incumbent bias)

The AI models (Ranker, Regressor, Classifier) run **once per day** across all 30 stocks.
SlotSelector produces **one shared target** — the global "best ≤ 3 stocks today" — with `current_positions={}` so that no single bucket's historical holdings can bias the selection.

This enforces the **3-slot constraint globally**: regardless of how many buckets are active, the shared target always contains ≤ 3 stocks.

#### Step 2 — Per-Bucket Reconciliation (active bucket only)

Only the **active bucket** is rebalanced today. Its current holdings are compared against the shared target:

- **SELL** — ticker held by bucket but not in target → fee charged
- **BUY** — ticker in target but not held by bucket → fee charged
- **HOLD** — ticker in both → no fee

Transaction costs are charged to the active bucket only. All other buckets are untouched.

#### Step 3 — Daily PnL (all buckets, opening positions)

**Before** reconciliation, each bucket earns today's market return on its **opening positions**.
This ordering is critical: the active bucket earns today's return on what it held at market open, not on the new positions it will hold tomorrow. Reconciliation (and fee deduction) happens at **end of day**.

#### Daily Execution Order

```
Market open   →  PnL computed on opening positions (ALL buckets)
Market close  →  Active bucket reconciled against shared target
After close   →  Fees deducted from active bucket
End of day    →  total_capital = sum of all bucket capitals
```

#### Convergence Behaviour

Over time, each bucket converges to the same 3-stock portfolio — just with staggered entry dates.
This averages out the arbitrary-start-date bias and produces a smooth, high-resolution daily equity curve (~252 points/year vs ~52 for a naive weekly rebalance).

---

## **5. Results & Report Interpretation**

The backtester outputs:

### **5.1 Equity Curve**
Shows cumulative capital over time.

### **5.2 Daily Returns**
Used to compute:

- Sharpe ratio
- Volatility
- Drawdown

### **5.3 Metrics**
Key values:

| Metric           | Meaning                     |
|------------------|-----------------------------|
| **Sharpe Ratio** | Risk‑adjusted return        |
| **Max Drawdown** | Worst peak‑to‑trough loss   |
| **Win Rate**     | % of profitable days        |
| **Turnover**     | How often portfolio changes |
| **Hit Rate**     | % of correct stock picks    |

### **5.4 Debug Log**
Includes:

- rank_score
- pred_return
- prob_up
- next_day_ret
- weight assigned
- whether selected

This allows full transparency into model behavior.

---

## **6. Version‑2 Recommendations**

### **6.1 Multi‑Horizon Ensemble**
Add:

- 1‑week
- 1‑month

Signals for a richer ensemble.

---

### **6.2 Feature Importance Dashboard**
ML Models finetuning:

- XAI/SHAP values: Understand most important features
- Feature drift
- Model degradation

---

### **6.3 Regime‑Aware SlotSelector**
Adjust thresholds based on:

- VIX
- Market volatility
- Trend regime

---

### **6.4 Go Online**
Remotely accessible through Android phone.

---


# **Conclusion**

This Investment AI Agent is a fully engineered, end‑to‑end system that:

- Converts personal investing into a disciplined AI workflow
- Uses 3 complementary ML models
- Applies a robust SlotSelector policy
- Uses horizon‑aligned rolling‑window backtesting
- Produces interpretable, actionable daily recommendations

It is modular, extensible, and ready for Version‑2 enhancements.
