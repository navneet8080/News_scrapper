import os
import pandas as pd
from datetime import datetime
import shutil

def combine_all_outputs():
    output_dir = "output"
    archive_dir = "archive"
    combined_dir = "combined"

    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(combined_dir, exist_ok=True)

    xlsx_files = [f for f in os.listdir(output_dir) if f.endswith(".xlsx")]
    dfs = []

    for f in xlsx_files:
        try:
            df = pd.read_excel(os.path.join(output_dir, f))

            if "aajtak" in f.lower():
                df = df.iloc[:, :2]
                df.columns = ["time", "news"]
                df["description"] = "0"
                df.insert(0, "source", "AajTak")

            elif "latestly" in f.lower():
                df = df.iloc[:, :1]
                df.columns = ["news"]
                df["time"] = "0"
                df["description"] = "0"
                df.insert(0, "source", "Latestly")

            elif "ani" in f.lower():
                df = df.iloc[:, :3]
                df.columns = ["time", "news", "description"]
                df.insert(0, "source", "ANI")

            elif "google" in f.lower():
                df = df.iloc[:, :1]
                df.columns = ["news"]
                df["time"] = "0"
                df["description"] = "0"
                df.insert(0, "source", "Google News")

            elif "hindusthan" in f.lower():
                df = df.iloc[:, :2]
                df.columns = ["news", "description"]
                df["time"] = "0"
                df.insert(0, "source", "Hindusthan")

            else:
                continue

            # Ensure consistent column order
            df = df[["source", "time", "news", "description"]]
            dfs.append(df)

        except Exception as err:
            print(f"⚠️ Skipping file '{f}' due to error: {err}")
            continue

    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        filename = f"combined_news_{datetime.now():%d_%b_%Y_%H%M}.xlsx"
        final_path = os.path.join(combined_dir, filename)
        combined_df.to_excel(final_path, index=False)

        # Archive old files with overwrite protection
        for f in xlsx_files:
            src = os.path.join(output_dir, f)
            dst = os.path.join(archive_dir, f)
            if os.path.exists(dst):
                os.remove(dst)
            shutil.move(src, dst)

        return final_path

    return None