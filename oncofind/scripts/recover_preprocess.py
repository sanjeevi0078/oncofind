#!/usr/bin/env python3
"""
Recover: preprocess already-downloaded BRCA raw count files into Parquet.
Run this once after the rename fix.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from oncofind.core.data.expression_store import ExpressionStore
from oncofind.core.data.gdc_client import GDCClient
from oncofind.config.settings import settings
import asyncio

DATA_DIR = settings.data_dir
CANCER = "BRCA"
RAW_DIR = DATA_DIR / CANCER / "raw_counts"

# Build (sample_barcode, path) tuples from the clinical parquet we already have
import pandas as pd

clin_path = DATA_DIR / CANCER / "clinical_metadata.parquet"
clin_df = pd.read_parquet(clin_path)
print(f"Clinical records: {len(clin_df)}")
print(f"Columns: {list(clin_df.columns)}")

# Map file_id back from filename
downloaded = []
for p in sorted(RAW_DIR.iterdir()):
    if p.name.endswith(".tmp"):
        continue
    # filename format: {file_id}_{original_filename}
    file_id = p.name.split("_")[0]
    # match to clinical by trying to find sample_barcode 
    downloaded.append(("UNKNOWN", p))

print(f"Raw count files found: {len(downloaded)}")

# Better: match file_id to sample from the GDC query
# Re-query GDC to rebuild the mapping
async def get_mapping():
    client = GDCClient()
    try:
        hits = await client.query_files(CANCER, n_samples=100)
        return {hit["file_id"]: hit["sample_barcode"] for hit in hits}
    finally:
        await client.close()

print("Re-querying GDC to get file_id -> sample_barcode mapping...")
mapping = asyncio.run(get_mapping())
print(f"Got mapping for {len(mapping)} files")

# Build proper (sample_barcode, path) list
proper_downloaded = []
for p in sorted(RAW_DIR.iterdir()):
    if p.name.endswith(".tmp"):
        continue
    file_id = p.name.split("_")[0]
    sample_barcode = mapping.get(file_id, f"SAMPLE_{file_id[:8]}")
    proper_downloaded.append((sample_barcode, p))

print(f"Matched: {len(proper_downloaded)} files with barcodes")

# Preprocess
store = ExpressionStore(DATA_DIR)
print("Preprocessing expression matrix...")
store.preprocess_files(CANCER, proper_downloaded)
print(f"Done. Parquet saved to: {store.get_expression_path(CANCER)}")

# Verify
import duckdb
conn = duckdb.connect(":memory:")
result = conn.execute(f"SELECT COUNT(*) FROM '{store.get_expression_path(CANCER)}'").fetchone()
conn.close()
print(f"Matrix shape: {result[0]} samples")
