import pytest
from typer.testing import CliRunner
from oncofind.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_env(mock_data_dir):
    """Override oncofind settings to use the mock TCGA data directory."""
    from oncofind.config.settings import settings
    settings.data_dir = mock_data_dir


def test_deg_help():
    """Verify that help text displays successfully."""
    result = runner.invoke(app, ["deg", "--help"])
    assert result.exit_code == 0
    assert "Run DEG analysis using PyDESeq2 or t-test fallback" in result.output


def test_deg_validation_errors():
    """Verify that input validators raise appropriate error codes and suggestions."""
    # Invalid cancer type
    result = runner.invoke(app, ["deg", "--cancer", "INVALID", "--groupby", "ER_status"])
    assert result.exit_code == 1
    assert "is not supported" in result.output
    
    # Missing clinical variable
    result = runner.invoke(app, ["deg", "--cancer", "BRCA", "--groupby", "non_existent_column"])
    assert result.exit_code == 1
    assert "Clinical variable 'non_existent_column' not found" in result.output


def test_deg_execution_success(tmp_path):
    """Verify that a standard DEG run generates expected CSV and Plotly outputs."""
    out_dir = tmp_path / "deg_results"
    
    result = runner.invoke(app, [
        "deg",
        "--cancer", "BRCA",
        "--groupby", "ER_status",
        "--method", "ttest",
        "--output-dir", str(out_dir)
    ])
    
    assert result.exit_code == 0
    assert "DEG Analysis: BRCA" in result.output
    assert "Significant DEGs" in result.output
    
    # Check outputs were created
    assert (out_dir / "BRCA_ER_status_deg_results.csv").exists()
    assert (out_dir / "BRCA_ER_status_volcano.html").exists()
    assert (out_dir / "BRCA_ER_status_heatmap.html").exists()
