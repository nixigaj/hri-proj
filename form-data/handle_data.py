import pandas as pd
import numpy as np

df = pd.read_csv("responses_raw.csv")
master_df = pd.read_csv("master_list.csv")

# Drop timestamp columns
df = df.drop(columns=[col for col in df.columns if "Tidstämpel" in col])

# Rename Swedish columns to English
df.rename(
    columns={
        "Hur pålitlig upplevde du roboten?": "trustworthiness",
        "Hur kompetent upplevde du roboten?": "competence",
        "Hur sympatisk upplevde du roboten?": "likeability",
        "Hur varm/uppmuntrande upplevde du roboten?": "warmth",
        "Hur troligt är att du skulle vilja interagera med denna robot igen?": "interact_again",
        "Vilken dialekt upplevde du att roboten hade?": "percieved_dialect",
        "Vad anser du vara din hemregion?": "home_region",
        "Vad anser du dig ha för dialektal bakgrund?": "dialectal_background",
        "Vad är din ålder?": "age",
        "Vilket kön har du?": "gender",
        "Vad har du för tidigare erfarenhet av att interagera med röstrobotar?": "previous_experience",
    },
    inplace=True,
)

# Standardize participant_id column name
if "participant_id" not in df.columns and "participant_ID" not in df.columns:
    print("Warning: No participant ID column found")
else:
    id_col = "participant_ID" if "participant_ID" in df.columns else "participant_id"
    if id_col != "participant_id":
        df.rename(columns={id_col: "participant_id"}, inplace=True)

# Validate group, scenario, condition against master_list
print("=== Validating group, scenario, condition ===")
mismatches = []

for idx, row in df.iterrows():
    participant_id = row["participant_id"]
    master_rows = master_df[master_df["participant_ID"] == participant_id]

    if len(master_rows) == 0:
        print(f"Warning: Participant {participant_id} not in master list")
        continue

    master_row = master_rows[
        (master_rows["scenario"] == row["scenario"]) &
        (master_rows["condition"] == row["condition"])
    ]

    if len(master_row) == 0:
        mismatch = {
            "participant_id": participant_id,
            "response_group": row.get("group", "N/A"),
            "response_scenario": row["scenario"],
            "response_condition": row["condition"],
            "master_group": master_rows.iloc[0]["group"],
            "master_scenario": master_rows.iloc[0]["scenario"],
            "master_condition": master_rows.iloc[0]["condition"],
        }
        mismatches.append(mismatch)

if mismatches:
    print(f"\nFound {len(mismatches)} mismatches:")
    for m in mismatches:
        print(m)
else:
    print("✓ All group/scenario/condition values match master list")

# Convert non-numeric entries to lowercase
print("\n=== Converting non-numeric entries to lowercase ===")
for col in df.columns:
    if col in ["participant_id", "group", "scenario", "condition"]:
        continue

    try:
        df[col] = pd.to_numeric(df[col])
    except (ValueError, TypeError):
        original_unique = df[col].unique()
        df[col] = df[col].astype(str).str.lower()
        new_unique = df[col].unique()
        if len(original_unique) != len(new_unique):
            print(f"  {col}: {len(original_unique)} → {len(new_unique)} unique values")

print("\n=== Data summary ===")
print(f"Total responses: {len(df)}")
print(f"Participants: {df['participant_id'].nunique()}")
print(f"\nData types:")
print(df.dtypes)

df.to_csv("responses_cleaned.csv", index=False)
print("\n✓ Cleaned data saved to responses_cleaned.csv")
