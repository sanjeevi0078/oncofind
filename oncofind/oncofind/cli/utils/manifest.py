"""
Run manifest — records every analysis run for reproducibility.

After every CLI command completes, call write_manifest() to save a JSON
file alongside the results. This provides an audit trail of:
  - Which version of oncofind produced the results
  - Every parameter used
  - SHA-256 hashes of the input data files
  - A timestamp

Format:
    {output_dir}/{command}_manifest.json

Usage:
    from oncofind.cli.utils.manifest import write_manifest
    write_manifest(out_dir, "deg", params={...}, data_files=[path1, path2])
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import oncofind  # for version

logger = logging.getLogger(__name__)


def _sha256(path: Path, chunk: int = 1 << 20) -> str:
    """Return the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                block = f.read(chunk)
                if not block:
                    break
                h.update(block)
        return h.hexdigest()
    except OSError as e:
        logger.warning(f"Could not hash {path}: {e}")
        return "unavailable"


def write_manifest(
    output_dir: Path,
    command: str,
    params: Dict[str, Any],
    data_files: Optional[List[Path]] = None,
    result_summary: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Write a JSON run manifest to output_dir.

    Args:
        output_dir: Directory where results are saved (manifest goes here too).
        command: CLI command name (e.g. "deg", "score", "pancancer").
        params: Dict of all CLI parameter names and their values.
        data_files: List of input data file paths to hash for traceability.
        result_summary: Optional dict of key result statistics to embed
                        (e.g. {"n_sig_genes": 2847, "top_gene": "TP53"}).

    Returns:
        Path to the written manifest file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest: Dict[str, Any] = {
        "oncofind_version": getattr(oncofind, "__version__", "unknown"),
        "command": command,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "parameters": _serialise(params),
    }

    if data_files:
        manifest["input_data_hashes"] = {
            str(p): _sha256(p) for p in data_files if p is not None
        }

    if result_summary:
        manifest["result_summary"] = _serialise(result_summary)

    manifest_path = output_dir / f"{command}_manifest.json"
    try:
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        logger.info(f"Run manifest written to {manifest_path}")
    except OSError as e:
        logger.warning(f"Could not write run manifest: {e}")

    return manifest_path


# ------------------------------------------------------------------ #
# Internal helpers                                                     #
# ------------------------------------------------------------------ #

def _serialise(obj: Any) -> Any:
    """Recursively convert non-JSON-serialisable types to strings."""
    if isinstance(obj, dict):
        return {k: _serialise(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialise(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, (int, float, bool, str)) or obj is None:
        return obj
    return str(obj)
