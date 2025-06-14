from code_chunker import extract_code_chunks
from tqdm import tqdm

from pathlib import Path
repo_root = Path("/Users/matthew.flood/workspace/airflow-datawarehouse")
python_files = list(repo_root.rglob("*.py"))

for file in tqdm(python_files, desc="🔍 Extracting chunks"):
    for chunk in extract_code_chunks(file):
        print(chunk.code[:80])
        print(chunk)
