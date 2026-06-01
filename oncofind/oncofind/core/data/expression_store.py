import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import pandas as pd
import duckdb
from oncofind.exceptions import DataNotDownloadedError, GeneNotFoundError

logger = logging.getLogger(__name__)


class ExpressionStore:
    """Manages RNA-seq expression matrices using DuckDB and Parquet."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def get_expression_path(self, cancer_type: str) -> Path:
        """Get the path to the expression Parquet file for a cancer type."""
        return self.data_dir / cancer_type.upper() / "expression_matrix.parquet"

    def get_gene_map_path(self, cancer_type: str) -> Path:
        """Get the path to the gene ID mapping file for a cancer type."""
        return self.data_dir / cancer_type.upper() / "gene_map.csv"

    def is_downloaded(self, cancer_type: str) -> bool:
        """Check if expression data has been preprocessed and saved."""
        return self.get_expression_path(cancer_type).exists()

    def preprocess_files(
        self,
        cancer_type: str,
        downloaded_files: List[Tuple[str, Path]],
        value_col: str = "unstranded"
    ) -> None:
        """
        Process downloaded raw STAR-Counts files and save them as a pivoted Parquet matrix.
        Rows = Samples (sample_barcode), Columns = Gene symbols/ids.
        
        Args:
            cancer_type: TCGA cancer code (e.g. BRCA)
            downloaded_files: List of (sample_barcode, file_path) tuples
            value_col: Column from STAR-Counts file to extract ('unstranded', 'tpm_unstranded', etc.)
        """
        if not downloaded_files:
            raise ValueError("No downloaded files to preprocess.")

        cancer_dir = self.data_dir / cancer_type.upper()
        cancer_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Preprocessing {len(downloaded_files)} files for {cancer_type}...")

        # We will load and pivot the files.
        # Since loading all files into pandas at once could be memory intensive,
        # we'll read them iteratively, extract the columns, and merge.
        gene_to_name: Dict[str, str] = {}
        sample_data: Dict[str, pd.Series] = {}

        for i, (sample_barcode, path) in enumerate(downloaded_files):
            try:
                # GDC STAR counts have 4 comment lines at the beginning (N_unmapped, etc.)
                # and then a header line. We can read with pandas and skip the metadata rows.
                df = pd.read_csv(path, sep="\t", skiprows=1)
                
                # Check for standard columns
                if "gene_id" not in df.columns or value_col not in df.columns:
                    # In case the format differs, check if it's the raw count file format without headers
                    df = pd.read_csv(path, sep="\t", header=None)
                    df.columns = ["gene_id", "gene_name", "gene_type", "unstranded", "stranded_first", "stranded_second", "tpm_unstranded", "fpkm_unstranded", "fpkm_uq_unstranded"][:len(df.columns)]
                
                # Clean metadata rows (they typically start with "N_")
                df = df[~df["gene_id"].str.startswith("N_")]
                
                # Strip versions from Ensembl IDs (e.g., ENSG00000141736.13 -> ENSG00000141736)
                df["gene_id_clean"] = df["gene_id"].str.split(".").str[0]
                
                # Keep gene symbol mappings
                if i == 0:
                    for _, row in df.iterrows():
                        gene_id = row["gene_id_clean"]
                        gene_name = str(row.get("gene_name", gene_id))
                        if pd.isna(gene_name) or gene_name == "nan" or gene_name == "":
                            gene_name = gene_id
                        gene_to_name[gene_id] = gene_name
                
                # Save counts
                series = df.set_index("gene_id_clean")[value_col]
                sample_data[sample_barcode] = series
            except Exception as e:
                logger.error(f"Failed to parse count file {path}: {e}")
                continue

        if not sample_data:
            raise ValueError("Failed to parse any RNA-seq count files.")

        # Construct DataFrame — deduplicate sample barcodes (keep first occurrence)
        # This handles the edge case where GDC returns multiple files for one sample
        deduped: Dict[str, pd.Series] = {}
        for barcode, series in sample_data.items():
            if barcode not in deduped:
                deduped[barcode] = series
            else:
                logger.warning(f"Duplicate barcode {barcode} — keeping first file only.")
        
        matrix_df = pd.DataFrame(deduped).T  # Index: sample_barcode, Columns: gene_id_clean
        matrix_df.index.name = "sample_barcode"
        matrix_df = matrix_df.fillna(0)

        # Map gene IDs to friendly unique names (symbol if unique, else symbol_ENSID)
        symbol_counts: Dict[str, int] = {}
        for gene_name in gene_to_name.values():
            symbol_counts[gene_name] = symbol_counts.get(gene_name, 0) + 1

        final_columns = []
        mapping_records = []
        seen_names: Dict[str, int] = {}       # tracks how many times we've used a name

        for gene_id in matrix_df.columns:
            symbol = gene_to_name.get(gene_id, gene_id)
            candidate = f"{symbol}_{gene_id}" if symbol_counts.get(symbol, 0) > 1 else symbol

            # Guarantee global uniqueness with an integer suffix if needed
            if candidate in seen_names:
                seen_names[candidate] += 1
                unique_col_name = f"{candidate}__dup{seen_names[candidate]}"
            else:
                seen_names[candidate] = 0
                unique_col_name = candidate

            final_columns.append(unique_col_name)
            mapping_records.append({
                "gene_id": gene_id,
                "gene_symbol": symbol,
                "column_name": unique_col_name,
            })

        matrix_df.columns = final_columns

        # Save to Parquet
        parquet_path = self.get_expression_path(cancer_type)
        matrix_df.reset_index().to_parquet(parquet_path, index=False)

        # Save gene mapping table for quick lookups
        map_df = pd.DataFrame(mapping_records)
        map_df.to_csv(self.get_gene_map_path(cancer_type), index=False)
        logger.info(f"Saved pivoted expression matrix to {parquet_path} ({matrix_df.shape[0]} samples x {matrix_df.shape[1]} genes)")

    def get_gene_column(self, cancer_type: str, gene_symbol: str) -> str:
        """Resolve a gene symbol to the exact column name in the expression parquet."""
        map_path = self.get_gene_map_path(cancer_type)
        if not map_path.exists():
            raise DataNotDownloadedError(f"Data for {cancer_type} has not been preprocessed. Map file missing.")
        
        cancer_key = cancer_type.upper()
        if not hasattr(self, "_gene_maps"):
            self._gene_maps = {}
            
        if cancer_key not in self._gene_maps:
            df = pd.read_csv(map_path)
            symbol_map = dict(zip(df["gene_symbol"].astype(str).str.upper(), df["column_name"]))
            col_map = dict(zip(df["column_name"].astype(str).str.upper(), df["column_name"]))
            id_map = dict(zip(df["gene_id"].astype(str).str.upper(), df["column_name"]))
            self._gene_maps[cancer_key] = (symbol_map, col_map, id_map, df)
            
        symbol_map, col_map, id_map, df = self._gene_maps[cancer_key]
        gene_upper = gene_symbol.upper()
        if gene_upper in symbol_map:
            return str(symbol_map[gene_upper])
        if gene_upper in col_map:
            return str(col_map[gene_upper])
        if gene_upper in id_map:
            return str(id_map[gene_upper])
            
        # Suggest fuzzy matches
        all_symbols = df["gene_symbol"].dropna().unique().tolist()
        import difflib
        suggestions = difflib.get_close_matches(gene_symbol, all_symbols, n=3, cutoff=0.6)
        sugg_str = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
        raise GeneNotFoundError(f"Gene '{gene_symbol}' not found in {cancer_type} expression dataset.{sugg_str}")

    def query_expression(
        self,
        cancer_type: str,
        genes: List[str],
        sample_barcodes: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Query expression levels of specified genes using DuckDB.
        
        Args:
            cancer_type: TCGA cancer code
            genes: List of gene symbols or Ensembl IDs
            sample_barcodes: Optional list of sample barcodes to filter on
            
        Returns:
            DataFrame with sample_barcode index and queried genes as columns
        """
        parquet_path = self.get_expression_path(cancer_type)
        if not parquet_path.exists():
            raise DataNotDownloadedError(f"Expression matrix for {cancer_type} not found. Run download first.")

        # Resolve gene columns
        column_mappings = {}
        for gene in genes:
            col = self.get_gene_column(cancer_type, gene)
            column_mappings[col] = gene

        # Construct SQL
        select_cols = ["sample_barcode"] + [f'"{col}"' for col in column_mappings.keys()]
        select_str = ", ".join(select_cols)
        
        conn = duckdb.connect(database=":memory:")
        sql = f"SELECT {select_str} FROM '{parquet_path}'"
        
        if sample_barcodes:
            barcodes_str = ", ".join([f"'{b}'" for b in sample_barcodes])
            sql += f" WHERE sample_barcode IN ({barcodes_str})"
            
        res_df = conn.execute(sql).df()
        conn.close()

        # Rename columns back to requested symbols and set index
        res_df = res_df.rename(columns=column_mappings)
        res_df = res_df.set_index("sample_barcode")
        return res_df

    def get_all_samples(self, cancer_type: str) -> List[str]:
        """Get a list of all sample barcodes for a cancer type."""
        parquet_path = self.get_expression_path(cancer_type)
        if not parquet_path.exists():
            raise DataNotDownloadedError(f"Expression matrix for {cancer_type} not found.")
            
        conn = duckdb.connect(database=":memory:")
        res = conn.execute(f"SELECT sample_barcode FROM '{parquet_path}'").fetchall()
        conn.close()
        return [r[0] for r in res]
