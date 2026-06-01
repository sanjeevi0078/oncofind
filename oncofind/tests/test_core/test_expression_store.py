import pytest
import pandas as pd
from oncofind.core.data.expression_store import ExpressionStore
from oncofind.exceptions import GeneNotFoundError, DataNotDownloadedError


def test_expression_store_queries(mock_data_dir):
    """Test that ExpressionStore can load and query mock expression data."""
    store = ExpressionStore(mock_data_dir)
    
    # Check download status
    assert store.is_downloaded("BRCA") is True
    assert store.is_downloaded("LUAD") is True
    assert store.is_downloaded("COAD") is True
    assert store.is_downloaded("READ") is False  # not in mock registry
    
    # Query single gene
    tp53_expr = store.query_expression("BRCA", ["TP53"])
    assert isinstance(tp53_expr, pd.DataFrame)
    assert tp53_expr.shape == (40, 1)
    assert "TP53" in tp53_expr.columns
    assert tp53_expr.index.name == "sample_barcode"
    
    # Query multiple genes
    multi_expr = store.query_expression("BRCA", ["TP53", "ESR1", "MYC"])
    assert multi_expr.shape == (40, 3)
    assert list(multi_expr.columns) == ["TP53", "ESR1", "MYC"]
    
    # Query with specific samples
    samples = store.get_all_samples("BRCA")
    assert len(samples) == 40
    sub_samples = samples[:10]
    sub_expr = store.query_expression("BRCA", ["TP53"], sample_barcodes=sub_samples)
    assert sub_expr.shape == (10, 1)
    assert list(sub_expr.index) == sub_samples


def test_expression_store_missing_gene(mock_data_dir):
    """Test that querying a missing gene raises GeneNotFoundError and offers suggestions."""
    store = ExpressionStore(mock_data_dir)
    
    with pytest.raises(GeneNotFoundError) as exc_info:
        store.query_expression("BRCA", ["TP54"])  # TP54 is close to TP53
        
    assert "Did you mean: TP53?" in str(exc_info.value)
    
    with pytest.raises(GeneNotFoundError):
        store.query_expression("BRCA", ["NONEXISTENTGENE"])


def test_expression_store_missing_cancer(tmp_path):
    """Test that querying an undownloaded cancer raises DataNotDownloadedError."""
    store = ExpressionStore(tmp_path)
    
    with pytest.raises(DataNotDownloadedError):
        store.query_expression("BRCA", ["TP53"])
