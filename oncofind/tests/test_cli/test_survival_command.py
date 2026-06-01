import pytest
from typer.testing import CliRunner
from oncofind.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_env(mock_data_dir):
    """Override oncofind settings to use the mock TCGA data directory."""
    from oncofind.config.settings import settings
    settings.data_dir = mock_data_dir


def test_survival_help():
    """Verify that help text displays successfully."""
    result = runner.invoke(app, ["survival", "--help"])
    assert result.exit_code == 0
    assert "Run survival analysis" in result.output


def test_survival_validation_errors():
    """Verify validation on cancer types and gene names."""
    # Gene symbol spelling suggestion warning
    result = runner.invoke(app, ["survival", "--cancer", "BRCA", "--gene", "TP53_SPELLED_WRONG"])
    assert result.exit_code == 1
    assert "Gene 'TP53_SPELLED_WRONG' not found" in result.output


def test_survival_success(tmp_path):
    """Verify successful execution of Kaplan-Meier analysis and outputs."""
    out_dir = tmp_path / "survival_results"
    
    result = runner.invoke(app, [
        "survival",
        "--cancer", "BRCA",
        "--gene", "TP53",
        "--split", "median",
        "--output-dir", str(out_dir)
    ])
    
    assert result.exit_code == 0, f"Command output: {result.output}"
    assert "Kaplan-Meier Analysis: TP53 in TCGA-BRCA" in result.output
    assert "Median Survival" in result.output
    assert "Log-rank p-value" in result.output
    
    # Check outputs were created
    assert (out_dir / "BRCA_TP53_survival.html").exists()
    assert (out_dir / "BRCA_TP53_survival_groups.csv").exists()
