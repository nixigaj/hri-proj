import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import warnings
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Suppress FutureWarnings from seaborn/matplotlib
warnings.filterwarnings("ignore", category=FutureWarning)

# Configure pandas display options
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# Get data type from command line argument or default to real
if len(sys.argv) > 1:
    data_type = sys.argv[1].lower()
else:
    data_type = "real"

if data_type not in ["real", "dummy"]:
    print(f"Error: Invalid data type '{data_type}'. Use 'real' or 'dummy'")
    sys.exit(1)

# Set directories and files (v2 format)
output_dir = f"output_{data_type}"
input_file = f"{output_dir}/responses_cleaned_v2_{data_type}.csv"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print(f"Analyzing {data_type.upper()} data (v2 format)")
print(f"Input: {input_file}")
print(f"Output directory: {output_dir}/")
print()

# Check if input file exists
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found. Did you run handle_data.py {data_type} first?")
    sys.exit(1)

# Load cleaned responses
merged_df = pd.read_csv(input_file)

print("="*60)
print("EXPLORATORY DATA ANALYSIS")
print("="*60)

# Survey questions (Likert scale)
survey_questions = [
    "trustworthiness",
    "competence",
    "likeability",
    "warmth",
    "interact_again",
]

print("\n=== Overall Survey Statistics ===")
for question in survey_questions:
    print(f"\n{question.upper()}:")
    print(f"  Mean: {merged_df[question].mean():.2f}")
    print(f"  Std:  {merged_df[question].std():.2f}")
    print(f"  Range: {merged_df[question].min()}-{merged_df[question].max()}")

print("\n=== Analysis by Condition ===")
condition_stats = merged_df.groupby("condition")[survey_questions].agg(["mean", "std", "count"])
print(condition_stats.to_string())

print("\n=== Analysis by Group ===")
group_stats = merged_df.groupby("group")[survey_questions].agg(["mean", "std", "count"])
print(group_stats.to_string())

print("\n=== Analysis by Perceived Dialect ===")
perceived_dialect_stats = merged_df.groupby("percieved_dialect")[survey_questions].agg(["mean", "std", "count"])
print(perceived_dialect_stats.to_string())

print("\n=== Analysis by Actual Dialect (from group_keys) ===")
actual_dialect_stats = merged_df.groupby("actual_dialect")[survey_questions].agg(["mean", "std", "count"])
print(actual_dialect_stats.to_string())

print("\n" + "="*60)
print("STATISTICAL TESTING PREPARATION")
print("="*60)

# Check normality (Shapiro-Wilk test)
print("\n=== Normality Tests (Shapiro-Wilk) ===")
print("p > 0.05 indicates normal distribution\n")
for question in survey_questions:
    stat, p_value = stats.shapiro(merged_df[question])
    print(f"{question}: p = {p_value:.4f} {'✓ Normal' if p_value > 0.05 else '✗ Not normal'}")

# Check homogeneity of variance (Levene's test) for each condition
print("\n=== Homogeneity of Variance (Levene's Test) by Condition ===")
print("p > 0.05 indicates equal variances\n")
for question in survey_questions:
    groups = [group[question].values for name, group in merged_df.groupby("condition")]
    stat, p_value = stats.levene(*groups)
    print(f"{question}: p = {p_value:.4f} {'✓ Equal var' if p_value > 0.05 else '✗ Unequal var'}")

# One-way ANOVA for each survey question by condition
print("\n=== One-Way ANOVA: Survey Questions by Condition ===")
print("p < 0.05 indicates significant difference between conditions\n")
for question in survey_questions:
    groups = [group[question].values for name, group in merged_df.groupby("condition")]
    f_stat, p_value = stats.f_oneway(*groups)
    print(f"{question}:")
    print(f"  F = {f_stat:.4f}, p = {p_value:.4f} {'✓ Significant' if p_value < 0.05 else '  Not significant'}")

# One-way ANOVA by group
print("\n=== One-Way ANOVA: Survey Questions by Group ===")
n_groups = merged_df['group'].nunique()
if n_groups < 2:
    print(f"⚠ Cannot perform ANOVA: Only {n_groups} group(s) in dataset")
else:
    print("p < 0.05 indicates significant difference between groups\n")
    for question in survey_questions:
        groups = [group[question].values for name, group in merged_df.groupby("group")]
        f_stat, p_value = stats.f_oneway(*groups)
        print(f"{question}:")
        print(f"  F = {f_stat:.4f}, p = {p_value:.4f} {'✓ Significant' if p_value < 0.05 else '  Not significant'}")

# Non-parametric alternative: Kruskal-Wallis test (for non-normal data)
print("\n" + "="*60)
print("KRUSKAL-WALLIS TEST (Non-Parametric Alternative)")
print("="*60)
print("\nRecommended for ordinal data or non-normal distributions")
print("p < 0.05 indicates significant difference between conditions\n")

for question in survey_questions:
    groups = [group[question].values for name, group in merged_df.groupby("condition")]
    h_stat, p_value = stats.kruskal(*groups)
    print(f"{question}:")
    print(f"  H = {h_stat:.4f}, p = {p_value:.4f} {'✓ Significant' if p_value < 0.05 else '  Not significant'}")

print("\n" + "="*60)
print("REPEATED-MEASURES ANALYSIS (GEE)")
print("="*60)

# Ensure categorical variables
merged_df["condition"] = merged_df["condition"].astype("category")
merged_df["scenario"] = merged_df["scenario"].astype("category")
merged_df["participant_id"] = merged_df["participant_id"].astype("category")

# Optional:
# Set reference categories
merged_df["condition"] = merged_df["condition"].cat.reorder_categories(
    ["c1", "c2", "c3"],
    ordered=True
)

for question in survey_questions:

    print(f"\n=== {question.upper()} ===")

    try:
        # GEE model with participant clustering
        model = smf.gee(
            f"{question} ~ C(condition) + C(scenario)",
            groups="participant_id",
            data=merged_df,
            family=sm.families.Gaussian(),
            cov_struct=sm.cov_struct.Exchangeable()
        )

        result = model.fit()

        print(result.summary())

    except Exception as e:
        print(f"Error analyzing {question}: {e}")

merged_df["overall_score"] = merged_df[survey_questions].mean(axis=1)
try:
    # GEE model with participant clustering
    model = smf.gee(
        f"{merged_df['overall_score'].name} ~ C(condition) + C(scenario)",
        groups="participant_id",
        data=merged_df,
        family=sm.families.Gaussian(),
        cov_struct=sm.cov_struct.Exchangeable()
    )
    result = model.fit()
    print(result.summary())
except Exception as e:
    print(f"Error analyzing {merged_df['overall_score'].name}: {e}")

def cronbach_alpha(df):
    df_corr = df.corr()
    n = len(df.columns)

    mean_corr = df_corr.values[np.triu_indices(n, 1)].mean()

    return (n * mean_corr) / (1 + (n - 1) * mean_corr)

alpha = cronbach_alpha(merged_df[survey_questions])

print("\n=== Cronbach's Alpha ===")
print(f"Alpha: {alpha:.3f}")

# Summary statistics for analysis
print("\n=== Data Structure for Analysis ===")
print(f"Total responses (scenario-level): {len(merged_df)}")
print(f"Conditions: {sorted([c for c in merged_df['condition'].unique() if pd.notna(c)])}")
print(f"Groups: {sorted(merged_df['group'].unique())}")
print(f"Scenarios: {sorted(merged_df['scenario'].unique())}")
print(f"Actual dialects: {sorted([d for d in merged_df['actual_dialect'].unique() if pd.notna(d)])}")
print(f"Perceived dialects: {sorted(merged_df['percieved_dialect'].unique())}")

print("\n=== Condition Distribution ===")
print(merged_df['condition'].value_counts().sort_index())

print("\n=== Group Distribution ===")
print(merged_df['group'].value_counts().sort_index())

print("\n=== Scenario Distribution ===")
print(merged_df['scenario'].value_counts().sort_index())

# Visualizations
print("\n" + "="*60)
print("GENERATING VISUALIZATIONS")
print("="*60)

condition_label_map = {
    'c1': 'TTS',
    'c2': 'Rikssvenska',
    'c3': 'Skånska',
}
merged_df['condition_label'] = merged_df['condition'].map(condition_label_map).fillna(merged_df['condition'])

sns.set_style("whitegrid")
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle("Survey Responses by Condition", fontsize=16, fontweight='bold')

for idx, question in enumerate(survey_questions):
    row = idx // 3
    col = idx % 3
    ax = axes[row, col]

    sns.boxplot(data=merged_df, x='condition_label', y=question, ax=ax, palette='Set2')
    ax.set_title(question.replace('_', ' ').title(), fontweight='bold')
    ax.set_ylabel('Rating')
    ax.set_ylim(0, 6)
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_dir}/boxplots_by_condition_{data_type}.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: boxplots_by_condition_{data_type}.png")
plt.close()

# Heatmap of mean ratings by condition
fig, ax = plt.subplots(figsize=(10, 4))
condition_means = merged_df.groupby('condition_label')[survey_questions].mean()
sns.heatmap(condition_means, annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=1, vmax=5, cbar_kws={'label': 'Mean Rating'}, ax=ax)
ax.set_title('Mean Ratings by Condition', fontweight='bold', fontsize=14)
ax.set_ylabel('Condition')
ax.set_xlabel('Survey Question')
plt.tight_layout()
plt.savefig(f'{output_dir}/heatmap_condition_means_{data_type}.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: heatmap_condition_means_{data_type}.png")
plt.close()

# Heatmap by perceived dialect
fig, ax = plt.subplots(figsize=(10, 6))
dialect_means = merged_df.groupby('percieved_dialect')[survey_questions].mean()
sns.heatmap(dialect_means, annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=1, vmax=5, cbar_kws={'label': 'Mean Rating'}, ax=ax)
ax.set_title('Mean Ratings by Perceived Dialect', fontweight='bold', fontsize=14)
ax.set_ylabel('Perceived Dialect')
ax.set_xlabel('Survey Question')
plt.tight_layout()
plt.savefig(f'{output_dir}/heatmap_perceived_dialect_means_{data_type}.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: heatmap_perceived_dialect_means_{data_type}.png")
plt.close()

# Distribution plots for each question
fig, axes = plt.subplots(1, 5, figsize=(16, 4))
for idx, question in enumerate(survey_questions):
    axes[idx].hist(merged_df[question], bins=5, color='steelblue', edgecolor='black', alpha=0.7)
    axes[idx].set_title(question.replace('_', ' ').title(), fontweight='bold')
    axes[idx].set_xlabel('Rating')
    axes[idx].set_ylabel('Frequency')
    axes[idx].set_xlim(0, 6)

plt.tight_layout()
plt.savefig(f'{output_dir}/distribution_all_questions_{data_type}.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: distribution_all_questions_{data_type}.png")
plt.close()

# Violin plots for better distribution visualization by condition
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Distribution of Responses by Condition (Violin Plots)', fontsize=16, fontweight='bold')

for idx, question in enumerate(survey_questions):
    row = idx // 3
    col = idx % 3
    ax = axes[row, col]

    sns.violinplot(data=merged_df, x='condition_label', y=question, ax=ax, palette='muted')
    ax.set_title(question.replace('_', ' ').title(), fontweight='bold')
    ax.set_ylabel('Rating')
    ax.set_ylim(0, 6)

plt.tight_layout()
plt.savefig(f'{output_dir}/violin_plots_by_condition_{data_type}.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: violin_plots_by_condition_{data_type}.png")
plt.close()

# Save merged data for further analysis
merged_df.to_csv(f"{output_dir}/responses_analyzed_v2_{data_type}.csv", index=False)
print(f"\n✓ Analyzed data saved to responses_analyzed_v2_{data_type}.csv")
print("\nAnalysis complete!")
