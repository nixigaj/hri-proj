import pandas as pd
import sys
import os
import re

# Get data type from command line argument or default to real
if len(sys.argv) > 1:
    data_type = sys.argv[1].lower()
else:
    data_type = "real"

if data_type not in ["real", "dummy"]:
    print(f"Error: Invalid data type '{data_type}'. Use 'real' or 'dummy'")
    sys.exit(1)

# Set file names and directories
input_file = f"responses_raw_v2.csv" if data_type == "real" else "dummy_responses_raw_v2.csv"
output_dir = f"output_{data_type}"
output_file = f"{output_dir}/responses_cleaned_v2_{data_type}.csv"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print(f"Processing {data_type.upper()} data (v2 format)")
print(f"Input: {input_file}")
print(f"Output directory: {output_dir}/")
print()

# Check if input file exists
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found")
    sys.exit(1)

df = pd.read_csv(input_file)
group_keys = pd.read_csv("group_keys.csv")

print("=== Parsing v2 Response Format ===")
print(f"Raw data shape: {df.shape}")
print(f"Participants: {df['participant_id'].nunique()}")

# Keep basic columns
keep_cols = ["Tidstämpel", "participant_id", "group"]
demographic_cols = [
    "Vad anser du vara din hemregion?",
    "Vad anser du dig ha för dialektal bakgrund?",
    "Vad är din ålder?",
    "Vilket kön har du?",
    "Vad har du för tidigare erfarenhet av att interagera med röstrobotar?"
]

# Rename demographic columns
demographic_rename = {
    "Vad anser du vara din hemregion?": "home_region",
    "Vad anser du dig ha för dialektal bakgrund?": "dialectal_background",
    "Vad är din ålder?": "age",
    "Vilket kön har du?": "gender",
    "Vad har du för tidigare erfarenhet av att interagera med röstrobotar?": "previous_experience",
}

# Extract scenario-based responses (3 scenarios)
scenarios = []

for scenario_num in range(1, 4):
    scenario_data = []

    for idx, row in df.iterrows():
        row_data = {
            "participant_id": row["participant_id"],
            "group": row["group"],
            "scenario": f"s{scenario_num}",
        }

        # Extract Likert questions for this scenario
        row_data["trustworthiness"] = row[f"{scenario_num}. 1 - Hur pålitlig upplevde du roboten?"]
        row_data["competence"] = row[f"{scenario_num}.2 - Hur kompetent upplevde du roboten?"]
        row_data["likeability"] = row[f"{scenario_num}.3 - Hur sympatisk upplevde du roboten?"]
        row_data["warmth"] = row[f"{scenario_num}.4 - Hur varm/uppmuntrande upplevde du roboten?"]
        row_data["interact_again"] = row[f"{scenario_num}.5 - Hur troligt är att du skulle vilja interagera med denna robot igen?"]

        # Extract perceived dialect for this scenario
        row_data["percieved_dialect"] = row[f"{scenario_num} - Vilken dialekt upplevde du att roboten hade i Scenario {scenario_num}?"]

        # Add demographics (same for all scenarios) - use original column names
        row_data["home_region"] = row["Vad anser du vara din hemregion?"]
        row_data["dialectal_background"] = row["Vad anser du dig ha för dialektal bakgrund?"]
        row_data["age"] = row["Vad är din ålder?"]
        row_data["gender"] = row["Vilket kön har du?"]
        row_data["previous_experience"] = row["Vad har du för tidigare erfarenhet av att interagera med röstrobotar?"]

        scenario_data.append(row_data)

    scenarios.append(pd.DataFrame(scenario_data))

# Combine all scenario responses
cleaned_df = pd.concat(scenarios, ignore_index=True)

# Add condition and dialect info from group_keys
# group_keys maps: group → scenario → condition → dialect
print("\n=== Adding Condition and Dialect Info ===")

# Forward-fill blank group values in group_keys (they continue from previous row)
group_keys_filled = group_keys.copy()
group_keys_filled["Grupp"] = group_keys_filled["Grupp"].ffill()

# Build lookup table from group_keys
condition_map = {}
dialect_map = {}

for idx, row in group_keys_filled.iterrows():
    group = row["Grupp"]
    scenario = row["Scenario"]
    condition = row["condition"]
    dialect = row["dialekt"]

    if pd.notna(group) and pd.notna(scenario):
        key = (group, scenario)
        condition_map[key] = condition
        dialect_map[key] = dialect

# Apply to cleaned data
cleaned_df["condition"] = cleaned_df.apply(
    lambda row: condition_map.get((row["group"], row["scenario"]), None),
    axis=1
)
cleaned_df["actual_dialect"] = cleaned_df.apply(
    lambda row: dialect_map.get((row["group"], row["scenario"]), None),
    axis=1
)

# Validate that all rows have condition/dialect
missing_conditions = cleaned_df[cleaned_df["condition"].isna()]
if len(missing_conditions) > 0:
    print(f"\nWarning: {len(missing_conditions)} rows missing condition info")
    print("Missing group-scenario combinations:")
    for combo in missing_conditions[["group", "scenario"]].drop_duplicates().values:
        print(f"  {combo}")
else:
    print("✓ All rows have condition info")

# Convert non-numeric entries to lowercase
print("\n=== Converting non-numeric entries to lowercase ===")
for col in cleaned_df.columns:
    if col in ["participant_id", "group", "scenario", "condition"]:
        continue

    try:
        cleaned_df[col] = pd.to_numeric(cleaned_df[col])
    except (ValueError, TypeError):
        original_unique = cleaned_df[col].nunique()
        cleaned_df[col] = cleaned_df[col].astype(str).str.lower()
        new_unique = cleaned_df[col].nunique()
        if original_unique != new_unique:
            print(f"  {col}: {original_unique} → {new_unique} unique values")

# Drop timestamp column
cleaned_df = cleaned_df.drop(columns=["Tidstämpel"], errors="ignore")

print("\n=== Data summary ===")
print(f"Total responses (scenario-level): {len(cleaned_df)}")
print(f"Participants: {cleaned_df['participant_id'].nunique()}")
print(f"Groups: {sorted(cleaned_df['group'].unique())}")
print(f"Scenarios: {sorted(cleaned_df['scenario'].unique())}")
print(f"Conditions: {sorted([c for c in cleaned_df['condition'].unique() if pd.notna(c)])}")
print(f"\nData types:")
print(cleaned_df.dtypes)

cleaned_df.to_csv(output_file, index=False)
print(f"\n✓ Cleaned data saved to {output_file}")
