import typer
from oncofind.cli.commands.download import download
from oncofind.cli.commands.deg import deg
from oncofind.cli.commands.survival import survival
from oncofind.cli.commands.pancancer import pancancer
from oncofind.cli.commands.score import score
from oncofind.cli.commands.report import report
from oncofind.cli.commands.validate import validate

app = typer.Typer(
    name="oncofind",
    help="oncofind — Pan-cancer biomarker discovery from the command line",
    add_completion=False,
)

# Register command callbacks
app.command(name="download")(download)
app.command(name="deg")(deg)
app.command(name="survival")(survival)
app.command(name="pancancer")(pancancer)
app.command(name="score")(score)
app.command(name="report")(report)
app.command(name="validate")(validate)


if __name__ == "__main__":
    app()
