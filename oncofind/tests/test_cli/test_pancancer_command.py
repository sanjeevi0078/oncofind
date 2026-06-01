import pytest
from typer.testing import CliRunner
from oncofind.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_env(mock_data_dir):
    """Override oncofind settings to use the mock TCGA data directory."""
    from oncofind.config.settings import settings
    settings.data_dir = mock_data_dir


def test_pancancer_help():
    """Verify that help text displays successfully."""
    result = runner.invoke(app, ["pancancer", "--help"])
    assert result.exit_code == 0
    assert "Run cross-cancer consistency analysis" in result.output


def test_pancancer_success(tmp_path):
    """Verify successful flagship pancancer comparison run."""
    out_dir = tmp_path / "pancancer_results"
    
    result = runner.invoke(app, [
        "pancancer",
        "--gene", "TP53",
        "--cancers", "BRCA,LUAD,COAD",
        "--output-dir", str(out_dir)
    ])
    
    assert result.exit_code == 0
    assert "Pan-Cancer Analysis: TP53" in result.output
    assert "Cross-Cancer Consistency Score (CCCS)" in result.output
    
    # Check outputs
    assert (out_dir / "pancancer_TP53_comparison.html").exists()
    assert (out_dir / "pancancer_TP53_data.csv").exists()


def test_score_success(tmp_path):
    """Verify ranking genes using CCCS."""
    out_dir = tmp_path / "score_results"
    
    result = runner.invoke(app, [
        "score",
        "--cancers", "BRCA LUAD COAD",
        "--top-n", "10",
        "--min-cancers", "1",  # Set to 1 because mock dataset is small
        "--output-dir", str(out_dir)
    ])
    
    assert result.exit_code == 0, f"Command failed. Output:\n{result.output}\nException: {result.exception}"
    assert "Top Biomarker Candidates Ranked by CCCS" in result.output
    assert (out_dir / "pancancer_cccs_rankings.csv").exists()


def test_report_success(tmp_path):
    """Verify report generation command."""
    out_file = tmp_path / "custom_report.html"
    
    result = runner.invoke(app, [
        "report",
        "--cancer", "BRCA",
        "--output", str(out_file)
    ])
    
    assert result.exit_code == 0
    assert "Successfully compiled report for TCGA-BRCA" in result.output
    assert out_file.exists()
    
    # Check that it contains expected template blocks
    content = out_file.read_text(encoding="utf-8")
    assert "Oncofind Analysis Report" in content
    assert "TCGA-BRCA" in content
    assert "Top Differentially Expressed Genes" in content
