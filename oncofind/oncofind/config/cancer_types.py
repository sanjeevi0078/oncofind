"""TCGA Cancer Type Registry with clinical metadata defaults."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CancerMetadata:
    code: str
    name: str
    clinical_variables: List[str] = field(default_factory=list)
    primary_site: str = ""


CANCER_REGISTRY: Dict[str, CancerMetadata] = {
    "BRCA": CancerMetadata(
        code="BRCA",
        name="Breast Invasive Carcinoma",
        clinical_variables=["ER_status", "PR_status", "HER2_status", "stage", "subtype"],
        primary_site="Breast",
    ),
    "LUAD": CancerMetadata(
        code="LUAD",
        name="Lung Adenocarcinoma",
        clinical_variables=["stage", "smoking_status", "subtype"],
        primary_site="Bronchus and lung",
    ),
    "COAD": CancerMetadata(
        code="COAD",
        name="Colon Adenocarcinoma",
        clinical_variables=["stage", "msi_status", "subtype"],
        primary_site="Colon",
    ),
    "STAD": CancerMetadata(
        code="STAD",
        name="Stomach Adenocarcinoma",
        clinical_variables=["stage", "hpylori_status", "subtype"],
        primary_site="Stomach",
    ),
    "OV": CancerMetadata(
        code="OV",
        name="Ovarian Serous Cystadenocarcinoma",
        clinical_variables=["stage", "grade"],
        primary_site="Ovary",
    ),
    "LUSC": CancerMetadata(
        code="LUSC",
        name="Lung Squamous Cell Carcinoma",
        clinical_variables=["stage", "smoking_status"],
        primary_site="Bronchus and lung",
    ),
    "SKCM": CancerMetadata(
        code="SKCM",
        name="Skin Cutaneous Melanoma",
        clinical_variables=["stage", "tumor_thickness", "ulceration"],
        primary_site="Skin",
    ),
    "GBM": CancerMetadata(
        code="GBM",
        name="Glioblastoma Multiforme",
        clinical_variables=["subtype", "mgmt_methylation"],
        primary_site="Brain",
    ),
    "KIRC": CancerMetadata(
        code="KIRC",
        name="Kidney Renal Clear Cell Carcinoma",
        clinical_variables=["stage", "grade"],
        primary_site="Kidney",
    ),
    "LIHC": CancerMetadata(
        code="LIHC",
        name="Liver Hepatocellular Carcinoma",
        clinical_variables=["stage", "grade", "child_pugh_score"],
        primary_site="Liver",
    ),
}


def is_valid_cancer(code: str) -> bool:
    """Check if a cancer code is registered."""
    return code.upper() in CANCER_REGISTRY


def get_cancer_metadata(code: str) -> CancerMetadata:
    """Retrieve metadata for a registered cancer code."""
    if not is_valid_cancer(code):
        raise ValueError(f"Cancer code '{code}' is not supported by oncofind.")
    return CANCER_REGISTRY[code.upper()]
