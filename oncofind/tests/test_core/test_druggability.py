import pytest
from oncofind.config.druggability import is_druggable, get_drugs_for_gene, DRUGGABLE_REGISTRY


def test_druggability_registry():
    """Verify that known cancer targets are correctly flagged and suggest drugs."""
    assert is_druggable("EGFR")
    assert is_druggable("egfr")  # Case insensitivity check
    assert is_druggable("ERBB2")
    assert is_druggable("TP53")
    
    # Check associated drugs
    egfr_drugs = get_drugs_for_gene("EGFR")
    assert "Osimertinib" in egfr_drugs
    assert "Erlotinib" in egfr_drugs
    
    # Non-druggable gene check
    assert not is_druggable("HOUSEKEEPER_GENE")
    assert get_drugs_for_gene("HOUSEKEEPER_GENE") == []


def test_registry_has_targets():
    """Ensure the registry is populated with precision oncology markers."""
    assert len(DRUGGABLE_REGISTRY) > 10
    for gene, drugs in DRUGGABLE_REGISTRY.items():
        assert isinstance(gene, str)
        assert isinstance(drugs, list)
        assert len(drugs) > 0
