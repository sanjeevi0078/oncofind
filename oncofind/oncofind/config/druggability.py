"""
oncofind druggability module.

This is now a thin façade over the DGIdb API client in
``oncofind.core.data.dgidb_client``.

All previous callers (score.py, pancancer.py, report generator, etc.) continue
to work unchanged — they import ``is_druggable`` and ``get_drugs_for_gene``
from this module and get live DGIdb data instead of the old 31-gene dict.
"""

from oncofind.core.data.dgidb_client import (  # noqa: F401  (re-export)
    is_druggable,
    get_drugs_for_gene,
    prefetch_druggability,
    SEED_REGISTRY as DRUGGABLE_REGISTRY,   # backwards-compat alias
)

__all__ = ["is_druggable", "get_drugs_for_gene", "prefetch_druggability", "DRUGGABLE_REGISTRY"]
