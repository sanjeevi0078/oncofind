import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from oncofind.exceptions import DataNotDownloadedError, ClinicalVariableNotFoundError
from oncofind.config.cancer_types import get_cancer_metadata

logger = logging.getLogger(__name__)


class ClinicalStore:
    """Manages and queries patient clinical metadata."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def get_clinical_path(self, cancer_type: str) -> Path:
        """Get the path to the clinical Parquet file for a cancer type."""
        return self.data_dir / cancer_type.upper() / "clinical_metadata.parquet"

    def is_downloaded(self, cancer_type: str) -> bool:
        """Check if clinical data has been preprocessed and saved."""
        return self.get_clinical_path(cancer_type).exists()

    def save_clinical_data(
        self,
        cancer_type: str,
        clinical_records: List[Dict[str, Any]],
        sample_to_patient: Dict[str, str],
        sample_to_type: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Merge raw clinical records with sample barcodes and save as a Parquet file.
        
        Args:
            cancer_type: TCGA cancer code
            clinical_records: List of dictionaries containing patient clinical info
            sample_to_patient: Dict mapping sample_barcode to patient_barcode
            sample_to_type: Optional dict mapping sample_barcode to sample_type
                            (e.g. "Primary Tumor", "Solid Tissue Normal").
                            Populated automatically by GDCClient.query_files().
        """
        if not clinical_records:
            raise ValueError("No clinical records provided to save.")

        cancer_dir = self.data_dir / cancer_type.upper()
        cancer_dir.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame
        df_clin = pd.DataFrame(clinical_records)
        # Index clinical by patient_barcode
        df_clin = df_clin.set_index("patient_barcode")

        # Map sample barcodes to patient records
        rows = []
        for sample_barcode, patient_barcode in sample_to_patient.items():
            # Standard TCGA patient barcode is the first 12 characters: TCGA-XX-XXXX
            # Standard TCGA sample barcode is: TCGA-XX-XXXX-01A-...
            pat_id = patient_barcode[:12]
            
            record = {"sample_barcode": sample_barcode, "patient_barcode": pat_id}
            
            # Persist sample_type for tumor_vs_normal DEG mode
            if sample_to_type:
                record["sample_type"] = sample_to_type.get(sample_barcode, "Primary Tumor")
            
            # Find patient record
            if pat_id in df_clin.index:
                pat_record = df_clin.loc[pat_id]
                if isinstance(pat_record, pd.DataFrame):
                    pat_record = pat_record.iloc[0]
                # Merge fields
                for col in df_clin.columns:
                    record[col] = pat_record[col]
            else:
                # Fill defaults
                record.update({
                    "gender": "Not Reported",
                    "age_at_index": None,
                    "vital_status": "Alive",
                    "survival_days": None,
                    "censored": 1,
                    "stage": "Not Reported",
                    "primary_diagnosis": ""
                })
            rows.append(record)

        df = pd.DataFrame(rows)
        
        df = self._standardize_clinical_df(df)

        parquet_path = self.get_clinical_path(cancer_type)
        df.to_parquet(parquet_path, index=False)
        logger.info(f"Saved clinical metadata to {parquet_path} ({df.shape[0]} rows)")

    def get_clinical_df(self, cancer_type: str) -> pd.DataFrame:
        """Retrieve clinical metadata DataFrame for a cancer type."""
        path = self.get_clinical_path(cancer_type)
        if not path.exists():
            raise DataNotDownloadedError(f"Clinical metadata for {cancer_type} not found. Run download first.")
        df = pd.read_parquet(path)
        return df

    def get_group_samples(
        self,
        cancer_type: str,
        groupby: str,
        group_a: Optional[str] = None,
        group_b: Optional[str] = None
    ) -> Tuple[List[str], List[str], str, str]:
        """
        Group sample barcodes based on a clinical variable.
        
        Returns:
            Tuple of (group_a_samples, group_b_samples, group_a_val, group_b_val)
        """
        df = self.get_clinical_df(cancer_type)
        
        if groupby not in df.columns:
            # Check standard mappings
            available_cols = [c for c in df.columns if c not in ["sample_barcode", "patient_barcode", "case_id"]]
            raise ClinicalVariableNotFoundError(
                f"Clinical variable '{groupby}' not found for {cancer_type}. "
                f"Available variables: {', '.join(available_cols)}"
            )

        # Filter out NaN/null values
        df_sub = df.dropna(subset=[groupby])
        df_sub = df_sub[df_sub[groupby].astype(str).str.lower() != "not reported"]
        df_sub = df_sub[df_sub[groupby].astype(str).str.lower() != "nan"]

        unique_vals = df_sub[groupby].unique().tolist()
        if len(unique_vals) < 2:
            raise ValueError(
                f"Clinical variable '{groupby}' must have at least 2 distinct groups. "
                f"Found only: {unique_vals}"
            )

        # Auto-detect top 2 groups if not specified
        if not group_a or not group_b:
            counts = df_sub[groupby].value_counts()
            top_groups = counts.index.tolist()
            if len(top_groups) < 2:
                raise ValueError(f"Could not automatically detect 2 comparison groups for variable '{groupby}'.")
            group_a_val = str(top_groups[0])
            group_b_val = str(top_groups[1])
        else:
            group_a_val = group_a
            group_b_val = group_b

            if group_a_val not in unique_vals or group_b_val not in unique_vals:
                raise ValueError(
                    f"Selected groups ({group_a_val}, {group_b_val}) not found in data. "
                    f"Available groups: {unique_vals}"
                )

        samples_a = df_sub[df_sub[groupby] == group_a_val]["sample_barcode"].tolist()
        samples_b = df_sub[df_sub[groupby] == group_b_val]["sample_barcode"].tolist()

        return samples_a, samples_b, group_a_val, group_b_val

    def _standardize_clinical_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize clinical DataFrame without any imputation.
        """
        # Clean stage column if present
        if "stage" in df.columns:
            def clean_stage(s):
                if pd.isna(s) or not isinstance(s, str):
                    return "Not Reported"
                s_lower = s.lower()
                if "stage iv" in s_lower: return "Stage IV"
                if "stage iii" in s_lower: return "Stage III"
                if "stage ii" in s_lower: return "Stage II"
                if "stage i" in s_lower: return "Stage I"
                return "Not Reported"
            
            df["stage"] = df["stage"].apply(clean_stage)

        # Standardize censored indicator if missing
        if "censored" not in df.columns:
            # find vital status / censored column
            vital_col = None
            for col in df.columns:
                col_lower = col.lower().replace(" ", "_").replace("-", "_")
                if col_lower in ["vital_status", "os_status", "status", "death_censored", "patient_status"]:
                    vital_col = col
                    break
            if vital_col:
                def parse_censored(val):
                    if pd.isna(val):
                        return 1
                    val_str = str(val).lower()
                    if val_str in ["dead", "deceased", "0", "event"]:
                        return 0
                    return 1
                df["censored"] = df[vital_col].apply(parse_censored)
            else:
                # Default: all censored
                df["censored"] = 1

        # Standardize survival time if missing
        if "survival_days" not in df.columns:
            # Find death days and follow up days columns
            death_col = None
            follow_col = None
            for col in df.columns:
                col_lower = col.lower().replace(" ", "_").replace("-", "_")
                if col_lower in ["days_to_death", "overall_survival_days", "os_days", "os_time", "survival_time"]:
                    death_col = col
                elif col_lower in ["days_to_last_follow_up", "days_to_last_followup"]:
                    follow_col = col
            
            if death_col and follow_col:
                # We have both: check vital status or censored status to merge them correctly
                vital_col = None
                for col in df.columns:
                    col_lower = col.lower().replace(" ", "_").replace("-", "_")
                    if col_lower in ["vital_status", "os_status", "status", "death_censored", "patient_status"]:
                        vital_col = col
                        break
                
                # Try using vital_status / censored to split
                if vital_col:
                    def get_surv(row):
                        val = row[vital_col]
                        if pd.isna(val):
                            return row[follow_col] if not pd.isna(row[follow_col]) else row[death_col]
                        val_str = str(val).lower()
                        if val_str in ["dead", "deceased", "0", "event"]:
                            return row[death_col]
                        return row[follow_col]
                    df["survival_days"] = df.apply(get_surv, axis=1)
                elif "censored" in df.columns:
                    def get_surv_cens(row):
                        if row["censored"] == 0:  # event occurred (death)
                            return row[death_col]
                        return row[follow_col]
                    df["survival_days"] = df.apply(get_surv_cens, axis=1)
                else:
                    df["survival_days"] = df[death_col].fillna(df[follow_col])
            elif death_col:
                df["survival_days"] = df[death_col]
            elif follow_col:
                df["survival_days"] = df[follow_col]

        # Clean survival_days: ensure numeric
        if "survival_days" in df.columns:
            df["survival_days"] = pd.to_numeric(df["survival_days"], errors="coerce")
            
        return df
