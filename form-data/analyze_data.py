import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Load cleaned responses and master list
responses_df = pd.read_csv("responses_cleaned.csv")
master_df = pd.read_csv("master_list.csv")

# Merge responses with master list metadata
merged_df = responses_df.merge(
    master_df[["participant_ID", "dialekt"]],
    left_on="participant_id",
    right_on="participant_ID",
    how="left"
)

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
print(condition_stats)

print("\n=== Analysis by Group ===")
group_stats = merged_df.groupby("group")[survey_questions].agg(["mean", "std", "count"])
print(group_stats)

print("\n=== Analysis by Perceived Dialect ===")
perceived_dialect_stats = merged_df.groupby("percieved_dialect")[survey_questions].agg(["mean", "std", "count"])
print(perceived_dialect_stats)

print("\n=== Analysis by Actual Dialect (from master list) ===")
actual_dialect_stats = merged_df.groupby("dialekt")[survey_questions].agg(["mean", "std", "count"])
print(actual_dialect_stats)

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

# Summary statistics for analysis
print("\n=== Data Structure for Analysis ===")
print(f"Total responses: {len(merged_df)}")
print(f"Conditions: {merged_df['condition'].unique()}")
print(f"Groups: {merged_df['group'].unique()}")
print(f"Scenarios: {merged_df['scenario'].unique()}")
print(f"Actual dialects: {merged_df['dialekt'].unique()}")
print(f"Perceived dialects: {merged_df['percieved_dialect'].unique()}")

print("\n=== Condition Distribution ===")
print(merged_df['condition'].value_counts().sort_index())

print("\n=== Group Distribution ===")
print(merged_df['group'].value_counts().sort_index())

# Visualizations
print("\n" + "="*60)
print("GENERATING VISUALIZATIONS")
print("="*60)

sns.set_style("whitegrid")
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle("Survey Responses by Condition", fontsize=16, fontweight='bold')

for idx, question in enumerate(survey_questions):
    row = idx // 3
    col = idx % 3
    ax = axes[row, col]

    sns.boxplot(data=merged_df, x='condition', y=question, ax=ax, palette='Set2')
    ax.set_title(question.replace('_', ' ').title(), fontweight='bold')
    ax.set_ylabel('Rating')
    ax.set_ylim(0, 6)
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('boxplots_by_condition.png', dpi=300, bbox_inches='tight')
print("✓ Saved: boxplots_by_condition.png")
plt.close()

# Heatmap of mean ratings by condition
fig, ax = plt.subplots(figsize=(10, 4))
condition_means = merged_df.groupby('condition')[survey_questions].mean()
sns.heatmap(condition_means, annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=1, vmax=5, cbar_kws={'label': 'Mean Rating'}, ax=ax)
ax.set_title('Mean Ratings by Condition', fontweight='bold', fontsize=14)
ax.set_ylabel('Condition')
ax.set_xlabel('Survey Question')
plt.tight_layout()
plt.savefig('heatmap_condition_means.png', dpi=300, bbox_inches='tight')
print("✓ Saved: heatmap_condition_means.png")
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
plt.savefig('heatmap_perceived_dialect_means.png', dpi=300, bbox_inches='tight')
print("✓ Saved: heatmap_perceived_dialect_means.png")
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
plt.savefig('distribution_all_questions.png', dpi=300, bbox_inches='tight')
print("✓ Saved: distribution_all_questions.png")
plt.close()

# Violin plots for better distribution visualization by condition
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Distribution of Responses by Condition (Violin Plots)', fontsize=16, fontweight='bold')

for idx, question in enumerate(survey_questions):
    row = idx // 3
    col = idx % 3
    ax = axes[row, col]

    sns.violinplot(data=merged_df, x='condition', y=question, ax=ax, palette='muted')
    ax.set_title(question.replace('_', ' ').title(), fontweight='bold')
    ax.set_ylabel('Rating')
    ax.set_ylim(0, 6)

plt.tight_layout()
plt.savefig('violin_plots_by_condition.png', dpi=300, bbox_inches='tight')
print("✓ Saved: violin_plots_by_condition.png")
plt.close()

# Save merged data for further analysis
merged_df.to_csv("responses_merged.csv", index=False)
print("\n✓ Merged data saved to responses_merged.csv")
print("\nAnalysis complete!")
