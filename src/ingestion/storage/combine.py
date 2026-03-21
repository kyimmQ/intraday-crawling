import os
import glob
from datetime import datetime
import pandas as pd

MORNING_DIR = "./data/morning"
AFTERNOON_DIR = "./data/afternoon"
COMBINED_DIR = "./data/combined"

def get_latest_fea_file(symbol_dir):
    """Find the latest .fea file in the given symbol directory."""
    files = glob.glob(os.path.join(symbol_dir, "*.fea"))
    if not files:
        return None
    # Sort files; since filenames are YYYY-MM-DD.fea, sorting alphabetically gives chronological order
    files.sort()
    return files[-1]

def combine_files():
    # Find all datatypes in morning and afternoon directories
    datatypes = set()
    for base_dir in [MORNING_DIR, AFTERNOON_DIR]:
        if os.path.exists(base_dir):
            for entry in os.listdir(base_dir):
                if os.path.isdir(os.path.join(base_dir, entry)):
                    datatypes.add(entry)

    if not datatypes:
        print("No datatypes found to combine.")
        return

    date_str = datetime.now().strftime("%Y-%m-%d")

    for datatype in datatypes:
        print(f"\nProcessing datatype: {datatype}")
        symbols = set()

        # Find all symbols for this datatype
        for base_dir in [MORNING_DIR, AFTERNOON_DIR]:
            datatype_dir = os.path.join(base_dir, datatype)
            if os.path.exists(datatype_dir):
                for entry in os.listdir(datatype_dir):
                    if os.path.isdir(os.path.join(datatype_dir, entry)):
                        symbols.add(entry)

        if not symbols:
            print(f"No symbols found for datatype {datatype}.")
            continue

        for symbol in symbols:
            dfs = []

            # Check morning directory
            morning_symbol_dir = os.path.join(MORNING_DIR, datatype, symbol)
            if os.path.exists(morning_symbol_dir):
                latest_morning = get_latest_fea_file(morning_symbol_dir)
                if latest_morning:
                    try:
                        df = pd.read_feather(latest_morning)
                        dfs.append(df)
                        print(f"Loaded {latest_morning} for {datatype}/{symbol} ({len(df)} rows)")
                    except Exception as e:
                        print(f"Error reading {latest_morning}: {e}")

            # Check afternoon directory
            afternoon_symbol_dir = os.path.join(AFTERNOON_DIR, datatype, symbol)
            if os.path.exists(afternoon_symbol_dir):
                latest_afternoon = get_latest_fea_file(afternoon_symbol_dir)
                if latest_afternoon:
                    try:
                        df = pd.read_feather(latest_afternoon)
                        dfs.append(df)
                        print(f"Loaded {latest_afternoon} for {datatype}/{symbol} ({len(df)} rows)")
                    except Exception as e:
                        print(f"Error reading {latest_afternoon}: {e}")

            if not dfs:
                print(f"No data to combine for {datatype}/{symbol}")
                continue

            # Combine
            combined_df = pd.concat(dfs, ignore_index=True)

            # Remove duplicates
            initial_len = len(combined_df)
            combined_df = combined_df.drop_duplicates()
            deduped_len = len(combined_df)
            if initial_len != deduped_len:
                print(f"Removed {initial_len - deduped_len} duplicate rows for {datatype}/{symbol}")

            # Sort by timestamp if it exists
            if "timestamp" in combined_df.columns:
                combined_df = combined_df.sort_values("timestamp").reset_index(drop=True)

            # Save to combined directory
            combined_symbol_dir = os.path.join(COMBINED_DIR, datatype, symbol)
            os.makedirs(combined_symbol_dir, exist_ok=True)

            out_file = os.path.join(combined_symbol_dir, f"{date_str}.fea")
            combined_df.to_feather(out_file)
            print(f"Saved combined data for {datatype}/{symbol} to {out_file} ({len(combined_df)} rows)")

if __name__ == "__main__":
    combine_files()
