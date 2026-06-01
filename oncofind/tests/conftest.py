import os
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import hashlib


def det_hash(s: str) -> int:
    return int(hashlib.sha256(s.encode()).hexdigest(), 16)


@pytest.fixture(scope="session", autouse=True)
def setup_mock_tcga_data():
    """
    Session-wide fixture that generates mock TCGA data for BRCA, LUAD, and COAD.
    This allows local offline testing of expression stores, DEGs, survival, and CCCS.
    """
    # Define directories
    fixture_dir = Path(__file__).parent / "fixtures"
    fixture_dir.mkdir(exist_ok=True)
    
    cancers = ["BRCA", "LUAD", "COAD"]
    genes = ["TP53", "MYC", "EGFR", "ESR1", "BRCA1", "CDK4", "MDM2", "E2F1"] + [f"GENE_{i}" for i in range(100)]
    
    np.random.seed(42)
    
    for cancer in cancers:
        cancer_dir = fixture_dir / cancer
        cancer_dir.mkdir(parents=True, exist_ok=True)
        
        # 40 samples per cancer
        n_samples = 40
        samples = [f"TCGA-{cancer}-{i:03d}-01A" for i in range(n_samples)]
        
        # Generate clinical data and expression profile features
        clinical_rows = []
        expr_rows = []
        
        for i, sample in enumerate(samples):
            patient = sample[:12]
            is_group_a = i < n_samples // 2
            
            # Tie survival days directly to the group status for LUAD/COAD, but make it random in BRCA to decouple ESR1 from survival
            if cancer == "BRCA":
                # Random survival (not aligned to Group A/B)
                vital_status = "Dead" if (i % 2 == 0) else "Alive"
                if vital_status == "Dead":
                    survival_days = int(500 + (det_hash(sample) % 1500))  # 500-2000 days
                    censored = 0
                else:
                    survival_days = int(1000 + (det_hash(sample) % 2000))  # 1000-3000 days
                    censored = 1
            else:
                # Group-aligned survival for LUAD/COAD (Group A = poor survival, Group B = good survival)
                if is_group_a:
                    vital_status = "Dead"
                    survival_days = int(100 + (det_hash(sample) % 400))  # 100-500 days
                    censored = 0
                else:
                    vital_status = "Alive"
                    survival_days = int(2000 + (det_hash(sample) % 1500))  # 2000-3500 days
                    censored = 1
                
            # Clinical groupings based on cancer
            stage = f"Stage {['I', 'II', 'III', 'IV'][i % 4]}"
            gender = "Female" if cancer == "BRCA" else ("Male" if i % 2 == 0 else "Female")
            clin_var_val = "Positive" if is_group_a else "Negative"
            
            record = {
                "sample_barcode": sample,
                "patient_barcode": patient,
                "gender": gender,
                "age_at_index": int(40 + np.random.randint(0, 40)),
                "vital_status": vital_status,
                "survival_days": survival_days,
                "censored": censored,
                "stage": stage,
                "primary_diagnosis": f"{cancer} diagnosis"
            }
            
            if cancer == "BRCA":
                record["ER_status"] = clin_var_val
                record["subtype"] = ["LumA", "LumB", "Her2", "Basal"][i % 4]
            elif cancer == "LUAD":
                record["smoking_status"] = "Smoker" if clin_var_val == "Positive" else "Non-smoker"
                record["subtype"] = ["TRU", "PP", "PI"][i % 3]
            elif cancer == "COAD":
                record["msi_status"] = "MSI-H" if clin_var_val == "Positive" else "MSS"
                record["subtype"] = ["CMS1", "CMS2", "CMS3", "CMS4"][i % 4]
                
            clinical_rows.append(record)
            
            # Generate expression profile for this sample
            expr_profile = {}
            for gene in genes:
                expr_profile[gene] = float(np.random.poisson(100))
                
            # TP53: Low in Group A, High in Group B (100% aligned with Group A/B)
            if is_group_a:
                expr_profile["TP53"] = float(np.random.poisson(20))
            else:
                expr_profile["TP53"] = float(np.random.poisson(250))
                
            # MYC & EGFR: High in Group A, Low in Group B (100% aligned with Group A/B)
            if is_group_a:
                expr_profile["MYC"] = float(np.random.poisson(250))
                expr_profile["EGFR"] = float(np.random.poisson(240))
            else:
                expr_profile["MYC"] = float(np.random.poisson(30))
                expr_profile["EGFR"] = float(np.random.poisson(25))
                
            # ESR1: BRCA specific signal. 100% aligned to group A/B in BRCA. Extremely low in LUAD/COAD.
            if cancer == "BRCA":
                if is_group_a:
                    expr_profile["ESR1"] = float(np.random.poisson(350))
                else:
                    expr_profile["ESR1"] = float(np.random.poisson(20))
            else:
                expr_profile["ESR1"] = float(np.random.poisson(15))
                
            expr_rows.append((sample, expr_profile))
            
        clinical_df = pd.DataFrame(clinical_rows)
        clinical_df.to_parquet(cancer_dir / "clinical_metadata.parquet", index=False)
        
        if cancer == "BRCA":
            clinical_df.to_csv(fixture_dir / "clinical_sample.csv", index=False)
            
        # Build expression DataFrame
        expr_dict = {sample: profile for sample, profile in expr_rows}
        expr_df = pd.DataFrame(expr_dict).T
        expr_df.index.name = "sample_barcode"
        expr_df = expr_df.reset_index()
        
        expr_df.to_parquet(cancer_dir / "expression_matrix.parquet", index=False)
        
        if cancer == "BRCA":
            expr_df.to_parquet(fixture_dir / "BRCA_sample.parquet", index=False)
            
        # Generate gene map
        gene_map_rows = []
        for idx, gene in enumerate(genes):
            gene_map_rows.append({
                "gene_id": f"ENSG{idx:011d}",
                "gene_symbol": gene,
                "column_name": gene
            })
        gene_map_df = pd.DataFrame(gene_map_rows)
        gene_map_df.to_csv(cancer_dir / "gene_map.csv", index=False)
        
    return fixture_dir


@pytest.fixture
def mock_data_dir(setup_mock_tcga_data):
    """Fixture to retrieve the mock data directory path."""
    return setup_mock_tcga_data
