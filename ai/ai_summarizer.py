# import os
# import shutil
# import pandas as pd
# from pathlib import Path
# from datetime import datetime
# from llama_cpp import Llama

# # Directory configuration
# combined_dir = Path("combined")
# archive_dir = Path("/archive")
# model_path = "models/Meta-Llama-3-8B.Q2_K.gguf"
# summary_output_path = Path("output/summary.txt")

# def get_combined_xlsx_files():
#     return sorted(combined_dir.glob("*.xlsx"), key=os.path.getmtime, reverse=True)

# def load_excel(file_path: Path):
#     return pd.read_excel(file_path)

# def build_prompt(df, limit=50):
#     prompt = "निम्नलिखित समाचार शीर्षकों में से 50 सबसे महत्वपूर्ण चुनें और उन्हें सारांशित करें:\n\n"
#     for i, row in df.head(limit).iterrows():
#         news = str(row.get("news", "")).strip()
#         if news:
#             prompt += f"{i+1}. {news}\n"
#     return prompt

# def run_llama_summary(prompt: str):
#     llm = Llama(model_path=model_path, n_ctx=4096)
#     response = llm(prompt, max_tokens=1024, stop=["</s>"])
#     return response["choices"][0]["text"]

# def archive_files(files):
#     archive_dir.mkdir(parents=True, exist_ok=True)
#     for f in files:
#         dest = archive_dir / f.name
#         if dest.exists():
#             dest.unlink()
#         shutil.move(str(f), str(dest))

# def main():
#     xlsx_files = get_combined_xlsx_files()
#     if not xlsx_files:
#         raise FileNotFoundError("❌ No Excel files found in '/combined' folder.")

#     latest_file = xlsx_files[0]
#     df = load_excel(latest_file)

#     prompt = build_prompt(df)
#     summary = run_llama_summary(prompt)

#     # Print and save
#     print("\n🧠 Generated Summary:\n")
#     print(summary)

#     summary_output_path.parent.mkdir(parents=True, exist_ok=True)
#     with summary_output_path.open("w", encoding="utf-8") as f:
#         f.write(summary)

#     # Move all combined Excel files to archive
#     archive_files(xlsx_files)

# if __name__ == "__main__":
#     main()






from transformers import T5ForConditionalGeneration, T5Tokenizer
import pandas as pd
from pathlib import Path
from datetime import datetime
import os, shutil

# Load model
model_name = "google/flan-t5-base"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

def get_combined_files():
    combined_dir = Path("combined")
    return sorted(combined_dir.glob("*.xlsx"), key=os.path.getmtime, reverse=True)

def summarize_title(title: str) -> str:
    prompt = f"एक लाइन न्यूज़ हेडलाइन लिखें: {title.strip()}"
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    output = model.generate(input_ids, max_new_tokens=16)
    return tokenizer.decode(output[0], skip_special_tokens=True)

def main():
    combined_files = get_combined_files()
    if not combined_files:
        raise FileNotFoundError("❌ No Excel files found in combined folder.")

    df = pd.read_excel(combined_files[0])
    summaries = []

    for i, row in df.head(50).iterrows():
        title = str(row.get("news", "")).strip()
        if title:
            result = summarize_title(title)
            summaries.append(f"{i+1}. {result}")

    output_file = Path("output/summary.txt")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(summaries), encoding="utf-8")

    # Move processed files to archive
    archive_dir = Path("archive")
    archive_dir.mkdir(exist_ok=True)
    for f in combined_files:
        shutil.move(str(f), archive_dir / f.name)

    print("✅ News Summary Saved to output/summary.txt")

if __name__ == "__main__":
    main()
