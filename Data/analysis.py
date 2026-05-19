"""Statistical analysis of HRI dialect-study survey responses.

Primary tests (pre-registered):
  1. Friedman on composite voice rating (3 voices, within-subjects)
  2. Wilcoxon signed-rank pairwise post-hoc (Bonferroni)
  3. Friedman on scenario position (S1/S2/S3) — confound check
  4. Cochran's Q on dialect-identification accuracy

Secondary (exploratory):
  5. Per-item Friedman
  6. Spearman: prior experience vs composite

Effect sizes: Cronbach's alpha (composite), Kendall's W (Friedman),
r = Z/sqrt(N) (Wilcoxon).
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

CSV = Path(__file__).parent / "responses_raw_v2 - Formulärsvar 1.csv"
PLOT_DIR = Path(__file__).parent / "plots"

VOICE_ORDER = ["tts", "rikssvenska", "skanska"]
VOICE_LABEL = {"tts": "TTS", "rikssvenska": "Rikssvenska", "skanska": "Skånska"}
VOICE_COLOR = {"tts": "#888888", "rikssvenska": "#4C7FBE", "skanska": "#D9534F"}

# group -> voice played in (S1, S2, S3); see ordning.md
GROUP_ORDER = {
    "g1": ("tts", "rikssvenska", "skanska"),
    "g2": ("skanska", "tts", "rikssvenska"),
    "g3": ("rikssvenska", "skanska", "tts"),
}

DIMS = ["trust", "competence", "sympathy", "warmth", "reuse"]

# Map dialect-ID free-choice option -> "what voice was actually played" for hit-coding.
# Rikssvenska is ambiguously perceived; count Stockholm/"ingen specifik" as hits too.
DIALECT_ID_MAP = {
    "tts": {"Syntetisk/TTS-röst"},
    "skanska": {"Skånsk"},
    "rikssvenska": {"Rikssvenska", "Stockholmsdialekt", "Ingen specifik dialekt"},
}


def load_long(csv_path: Path) -> pd.DataFrame:
    raw = pd.read_csv(csv_path)
    # 5 Likert columns per scenario, indexed 1..3 in header
    rows = []
    for _, r in raw.iterrows():
        pid = r["participant_id"]
        grp = r["group"]
        voices = GROUP_ORDER[grp]
        for s_idx, voice in enumerate(voices, start=1):
            # columns are "1. 1 - ..." for S1 item 1, "1.2 - ..." for S1 item 2 etc.
            base = [c for c in raw.columns if c.startswith(f"{s_idx}.")]
            assert len(base) == 5, f"want 5 items for S{s_idx}, got {base}"
            ratings = [int(r[c]) for c in base]
            dialect_guess = r[f"{s_idx} - Vilken dialekt upplevde du att roboten hade i Scenario {s_idx}?"]
            rows.append(dict(
                pid=pid, group=grp, scenario=s_idx, voice=voice,
                **dict(zip(DIMS, ratings)),
                composite=float(np.mean(ratings)),
                dialect_guess=dialect_guess,
                dialect_hit=int(dialect_guess in DIALECT_ID_MAP[voice]),
            ))
    return pd.DataFrame(rows)


def cronbach_alpha(items: np.ndarray) -> float:
    """items: (n_subjects, k_items)."""
    k = items.shape[1]
    item_vars = items.var(axis=0, ddof=1)
    total_var = items.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var)


def kendall_w(chi2: float, n: int, k: int) -> float:
    return chi2 / (n * (k - 1))


def wilcoxon_r(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Wilcoxon signed-rank with effect size r = Z / sqrt(N_nonzero)."""
    diff = x - y
    nz = diff[diff != 0]
    n = len(nz)
    res = stats.wilcoxon(x, y, zero_method="wilcox", method="approx")
    # method="approx" exposes z-statistic via .zstatistic in modern scipy
    z = getattr(res, "zstatistic", None)
    if z is None:
        # fallback: derive from p (two-sided)
        z = stats.norm.isf(res.pvalue / 2) * np.sign(np.median(nz))
    r = abs(z) / np.sqrt(n)
    return res.statistic, res.pvalue, r


def cochrans_q(hits: np.ndarray) -> tuple[float, float, int, int]:
    """hits: (n_subjects, k_conditions) of 0/1. Returns Q, p, df, n."""
    n, k = hits.shape
    col_totals = hits.sum(axis=0)
    row_totals = hits.sum(axis=1)
    num = (k - 1) * (k * (col_totals ** 2).sum() - col_totals.sum() ** 2)
    denom = k * row_totals.sum() - (row_totals ** 2).sum()
    if denom == 0:
        return float("nan"), float("nan"), k - 1, n
    q = num / denom
    p = stats.chi2.sf(q, df=k - 1)
    return q, p, k - 1, n


def widen(df: pd.DataFrame, value: str, by: str) -> pd.DataFrame:
    """pid × {by} -> value. Sorted by pid for matrix ops."""
    w = df.pivot(index="pid", columns=by, values=value).sort_index()
    return w


def report_friedman(name: str, wide: pd.DataFrame) -> None:
    cols = list(wide.columns)
    arrs = [wide[c].values for c in cols]
    stat, p = stats.friedmanchisquare(*arrs)
    n, k = wide.shape
    w = kendall_w(stat, n, k)
    print(f"\n[{name}] Friedman  chi2={stat:.3f}  df={k-1}  p={p:.4f}  "
          f"Kendall's W={w:.3f}  n={n}")
    medians = wide.median().to_dict()
    print(f"  medians: {medians}")


def report_wilcoxon_posthoc(wide: pd.DataFrame, alpha: float = 0.05) -> None:
    cols = list(wide.columns)
    pairs = [(a, b) for i, a in enumerate(cols) for b in cols[i + 1:]]
    bonf = alpha / len(pairs)
    print(f"  Wilcoxon post-hoc (Bonferroni alpha={bonf:.4f}):")
    for a, b in pairs:
        W, p, r = wilcoxon_r(wide[a].values, wide[b].values)
        flag = " *" if p < bonf else ""
        print(f"    {a:>12} vs {b:<12}  W={W:6.1f}  p={p:.4f}  r={r:.3f}{flag}")


def plot_composite_by_voice(df: pd.DataFrame, friedman_p: float, w: float) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    data = [df[df.voice == v].composite.values for v in VOICE_ORDER]
    bp = ax.boxplot(data, patch_artist=True, widths=0.5,
                    medianprops=dict(color="black", lw=2))
    for patch, v in zip(bp["boxes"], VOICE_ORDER):
        patch.set_facecolor(VOICE_COLOR[v])
        patch.set_alpha(0.7)
    # jittered points
    rng = np.random.default_rng(0)
    for i, v in enumerate(VOICE_ORDER, start=1):
        xs = rng.normal(i, 0.05, size=len(data[i - 1]))
        ax.scatter(xs, data[i - 1], color="black", alpha=0.5, s=18, zorder=3)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels([VOICE_LABEL[v] for v in VOICE_ORDER])
    ax.set_ylabel("Composite robot perception (1–5)")
    ax.set_ylim(0.8, 5.2)
    ax.set_title(f"Composite rating per voice\nFriedman p={friedman_p:.4f}, Kendall's W={w:.2f}, n={df.pid.nunique()}")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "01_composite_by_voice.png", dpi=150)
    plt.close(fig)


def plot_per_item(df: pd.DataFrame, results: dict[str, tuple[float, float, float]]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(DIMS))
    width = 0.27
    for i, v in enumerate(VOICE_ORDER):
        means = [df[df.voice == v][dim].mean() for dim in DIMS]
        sems = [df[df.voice == v][dim].sem() for dim in DIMS]
        ax.bar(x + (i - 1) * width, means, width, yerr=sems, capsize=3,
               label=VOICE_LABEL[v], color=VOICE_COLOR[v], alpha=0.85)
    # significance stars under x-labels
    labels = []
    for dim in DIMS:
        _, p, _ = results[dim]
        star = " *" if p < 0.05 else ""
        labels.append(f"{dim}{star}\np={p:.3f}")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Mean rating (1–5)")
    ax.set_ylim(0, 5.5)
    ax.set_title("Per-item ratings by voice (mean ± SEM, Friedman per item)")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "02_per_item_by_voice.png", dpi=150)
    plt.close(fig)


def plot_position(df: pd.DataFrame, p_value: float) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    data = [df[df.scenario == s].composite.values for s in (1, 2, 3)]
    bp = ax.boxplot(data, patch_artist=True, widths=0.5,
                    medianprops=dict(color="black", lw=2))
    for patch in bp["boxes"]:
        patch.set_facecolor("#999999")
        patch.set_alpha(0.6)
    rng = np.random.default_rng(1)
    for i, arr in enumerate(data, start=1):
        xs = rng.normal(i, 0.05, size=len(arr))
        ax.scatter(xs, arr, color="black", alpha=0.5, s=18, zorder=3)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["S1 Retur", "S2 Orderfråga", "S3 Reklamation"])
    ax.set_ylabel("Composite rating (1–5)")
    ax.set_ylim(0.8, 5.2)
    ax.set_title(f"Confound check: composite by scenario position\nFriedman p={p_value:.3f} (n.s. → no order effect)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "03_position_confound.png", dpi=150)
    plt.close(fig)


def plot_dialect_id(df: pd.DataFrame, q: float, p_value: float) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    hit_rates = [df[df.voice == v].dialect_hit.mean() for v in VOICE_ORDER]
    bars = ax.bar([VOICE_LABEL[v] for v in VOICE_ORDER], hit_rates,
                  color=[VOICE_COLOR[v] for v in VOICE_ORDER], alpha=0.85)
    for bar, rate in zip(bars, hit_rates):
        ax.text(bar.get_x() + bar.get_width() / 2, rate + 0.02,
                f"{rate:.0%}", ha="center", fontsize=11)
    ax.set_ylabel("Dialect-ID hit rate")
    ax.set_ylim(0, 1.1)
    ax.axhline(1.0, color="black", lw=0.5, ls="--", alpha=0.5)
    ax.set_title(f"Manipulation check: dialect identification\nCochran's Q={q:.2f}, p={p_value:.3f} (n.s.)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "04_dialect_id.png", dpi=150)
    plt.close(fig)


def main() -> int:
    if not CSV.exists():
        print(f"missing CSV: {CSV}", file=sys.stderr)
        return 1
    PLOT_DIR.mkdir(exist_ok=True)
    df = load_long(CSV)
    print(f"loaded n_participants={df.pid.nunique()}  n_rows={len(df)}")
    print(f"voices: {sorted(df.voice.unique())}")
    print(f"groups: {df.groupby('group').pid.nunique().to_dict()}")

    # --- Cronbach's alpha on 5 items (pooled across voices) ---
    alpha = cronbach_alpha(df[DIMS].values)
    print(f"\nCronbach's alpha (5 items, pooled): {alpha:.3f}")
    if alpha < 0.7:
        print("  WARN: alpha < .7, composite weak — report per-item too.")

    # --- 1. Friedman on composite voice rating ---
    wide_voice = widen(df, "composite", "voice")
    report_friedman("composite × voice", wide_voice)
    report_wilcoxon_posthoc(wide_voice)
    chi2_v, p_v = stats.friedmanchisquare(*[wide_voice[c].values for c in wide_voice.columns])
    plot_composite_by_voice(df, p_v, kendall_w(chi2_v, *wide_voice.shape))

    # --- 3. Friedman on scenario position (confound check) ---
    wide_pos = widen(df, "composite", "scenario")
    wide_pos.columns = [f"S{c}" for c in wide_pos.columns]
    report_friedman("composite × scenario-position (confound)", wide_pos)
    _, p_pos = stats.friedmanchisquare(*[wide_pos[c].values for c in wide_pos.columns])
    plot_position(df, p_pos)

    # --- 4. Cochran's Q on dialect-ID hit ---
    wide_hit = widen(df, "dialect_hit", "voice").astype(int)
    Q, p_q, ddof, n = cochrans_q(wide_hit.values)
    print(f"\n[dialect-ID × voice] Cochran's Q={Q:.3f}  df={ddof}  p={p_q:.4f}  n={n}")
    print(f"  hit rate per voice: {wide_hit.mean().to_dict()}")
    plot_dialect_id(df, Q, p_q)

    # --- 5. Per-item Friedman (exploratory) ---
    print("\n--- exploratory: per-item Friedman ---")
    per_item: dict[str, tuple[float, float, float]] = {}
    for dim in DIMS:
        w = widen(df, dim, "voice")
        stat, p = stats.friedmanchisquare(*[w[c].values for c in w.columns])
        kw = kendall_w(stat, w.shape[0], w.shape[1])
        per_item[dim] = (stat, p, kw)
        flag = " *" if p < 0.05 else ""
        print(f"  {dim:<12} chi2={stat:6.3f}  p={p:.4f}  W={kw:.3f}{flag}")
    plot_per_item(df, per_item)

    # --- 6. Spearman: prior experience × composite ---
    raw = pd.read_csv(CSV)
    exp = raw.set_index("participant_id")["Vad har du för tidigare erfarenhet av att interagera med röstrobotar?"]
    per_p = df.groupby("pid").composite.mean()
    rho, p = stats.spearmanr(exp.reindex(per_p.index).values, per_p.values)
    print(f"\n[prior-exp × mean composite] Spearman rho={rho:.3f}  p={p:.4f}  n={len(per_p)}")

    print(f"\nplots saved → {PLOT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
