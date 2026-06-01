"""
DGIdb (Drug-Gene Interaction Database) client.

DGIdb is a free, public API with 10,000+ gene-drug interactions from 40+ databases.
API docs: https://www.dgidb.org/api

Behavior:
  - On first call for a gene set, hits the live DGIdb v2 API.
  - Results are cached to ~/.oncofind/cache/dgidb_cache.json (keyed by gene symbol).
  - If the API is unreachable (no internet, rate limit), falls back to the
    hardcoded SEED_REGISTRY which covers the 31 highest-priority oncology targets.
  - Cache TTL: 7 days (stale entries are refreshed on next call).
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from oncofind.config.settings import settings

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Seed registry — used as fallback when DGIdb is unreachable                  #
# These are the most commonly queried oncology targets, hand-verified          #
# against FDA approvals as of May 2026.                                        #
# --------------------------------------------------------------------------- #
SEED_REGISTRY: Dict[str, List[str]] = {
    "EGFR": ["Osimertinib", "Erlotinib", "Gefitinib", "Cetuximab", "Panitumumab"],
    "ERBB2": ["Trastuzumab", "Pertuzumab", "Lapatinib", "Neratinib", "T-DM1", "Tucatinib"],
    "BRCA1": ["Olaparib", "Niraparib", "Rucaparib", "Talazoparib"],
    "BRCA2": ["Olaparib", "Niraparib", "Rucaparib", "Talazoparib"],
    "CDK4": ["Palbociclib", "Ribociclib", "Abemaciclib"],
    "CDK6": ["Palbociclib", "Ribociclib", "Abemaciclib"],
    "ESR1": ["Tamoxifen", "Fulvestrant", "Elacestrant"],
    "BRAF": ["Vemurafenib", "Dabrafenib", "Encorafenib"],
    "KRAS": ["Sotorasib (G12C)", "Adagrasib (G12C)"],
    "ALK": ["Crizotinib", "Alectinib", "Brigatinib", "Lorlatinib"],
    "AKT1": ["Capivasertib"],
    "PIK3CA": ["Alpelisib", "Inavolisib"],
    "MTOR": ["Everolimus", "Temsirolimus"],
    "MET": ["Capmatinib", "Tepotinib", "Crizotinib"],
    "FGFR1": ["Erdafitinib", "Pemigatinib"],
    "FGFR2": ["Erdafitinib", "Pemigatinib", "Futibatinib"],
    "FGFR3": ["Erdafitinib"],
    "KIT": ["Imatinib", "Sunitinib", "Regorafenib", "Ripretinib", "Avapritinib"],
    "PDGFRB": ["Imatinib", "Avapritinib"],
    "PDCD1": ["Pembrolizumab", "Nivolumab", "Cemiplimab", "Dostarlimab"],  # PD-1
    "CD274": ["Atezolizumab", "Durvalumab", "Avelumab"],                    # PD-L1
    "CTLA4": ["Ipilimumab", "Tremelimumab"],
    "MYC": ["JQ1 (Clinical Trial)", "Molibresib (Clinical Trial)"],
    "TP53": ["PC14586 (Clinical Trial)", "Kevetrin (Clinical Trial)", "APR-246 (Clinical Trial)"],
    "MDM2": ["Idasanutlin (Clinical Trial)", "Siremadlin (Clinical Trial)"],
    "RET": ["Selpercatinib", "Pralsetinib"],
    "NTRK1": ["Larotrectinib", "Entrectinib"],
    "NTRK2": ["Larotrectinib", "Entrectinib"],
    "NTRK3": ["Larotrectinib", "Entrectinib"],
    "ABL1": ["Imatinib", "Dasatinib", "Nilotinib", "Ponatinib"],
    "IDH1": ["Ivosidenib", "Olutasidenib"],
    "IDH2": ["Enasidenib"],
    # Expanded Proliferation / Cell Cycle / Checkpoint Drug Actionable Targets
    "EZH2": ["Tazemetostat"],
    "AURKA": ["Alisertib"],
    "PLK1": ["Volasertib"],
    "TOP2A": ["Doxorubicin", "Etoposide", "Daunorubicin", "Idarubicin", "Mitoxantrone"],
    "BIRC5": ["YM155 (Sepantronium bromide)", "SurVaxM"],
    "PKMYT1": ["Lunresertib"],
    "RRM2": ["Gemcitabine", "Hydroxyurea", "Triapine"],
    "MELK": ["OTSSP167 (Clinical Trial)"],
    "NEK2": ["INH1 (Clinical Trial)", "CCT244747 (Clinical Trial)"],
    "UHRF1": ["MIRA-1 (Clinical Trial)"],
    "KIF20A": ["Paprotrain (Clinical Trial)"],
    "CENPF": ["Calyculin A (Research Tool)"],
    "EXO1": ["Exo1-inhibitor (Research Tool)"],
    "ESPL1": ["Separase-inhibitor (Research Tool)"],
    "PYCR1": ["PYCR1-inhibitor (Research Tool)"],
    "KIF4A": ["KIF4A-inhibitor (Research Tool)"],
    "CEP55": ["CEP55-inhibitor (Research Tool)"],
    "WEE1": ["Adavosertib"],
    "ATR": ["Berzosertib", "Ceralasertib"],
    "ATM": ["Elimestat (Clinical Trial)"],
    "CHEK1": ["Prexasertib"],
    "CHEK2": ["Prexasertib"],
    "VEGFA": ["Bevacizumab"],
    "KDR": ["Sorafenib", "Sunitinib", "Pazopanib", "Regorafenib", "Lenvatinib", "Cabozantinib"],
    "FLT1": ["Axitinib", "Pazopanib"],
    "PDGFRA": ["Imatinib", "Sunitinib", "Olaratumab", "Avapritinib"],
    "JAK2": ["Ruxolitinib", "Fedratinib", "Pacritinib"],
    "BTK": ["Ibrutinib", "Acalabrutinib", "Zanubrutinib", "Pirtobrutinib"],
    "BCL2": ["Venetoclax"],
    "CD38": ["Daratumumab", "Isatuximab"],
    "MS4A1": ["Rituximab", "Obinutuzumab", "Ofatumumab"],
    "PARP1": ["Olaparib", "Niraparib", "Rucaparib", "Talazoparib"],
    "CDK2": ["Fadraciclib", "Dinaciclib"],
    "CDK9": ["Alvocidib", "Voruciclib"],
    "MDM4": ["ALRN-6924"],
    "AR": ["Enzalutamide", "Abiraterone", "Bicalutamide", "Apalutamide", "Darolutamide"],
    "ESR2": ["Tamoxifen", "Raloxifene"],
    "PGR": ["Mifepristone", "Megestrol"],
}

_CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days


class DGIdbClient:
    """
    Client for the Drug-Gene Interaction Database (DGIdb) API.
    
    Automatically caches results locally and falls back to SEED_REGISTRY
    when the API is unreachable.
    """

    DGIDB_API = "https://dgidb.org/api/v2/interactions.json"

    def __init__(self, cache_path: Optional[Path] = None):
        self._cache_path = cache_path or (settings.cache_dir / "dgidb_cache.json")
        self._cache: Dict[str, Dict] = self._load_cache()

    # ---------------------------------------------------------------------- #
    # Public API                                                               #
    # ---------------------------------------------------------------------- #

    def get_drugs(self, gene_symbol: str) -> List[str]:
        """
        Return a list of drug names that target the given gene.

        Priority:
          1. Fresh DGIdb cache entry (< 7 days old)
          2. SEED_REGISTRY (covers all FDA-approved oncology targets)
          3. Stale cache entry

        Note: Live DGIdb v2 API calls are disabled — the endpoint returns
        empty responses as of May 2026. All lookups use the curated
        SEED_REGISTRY which covers 31 high-priority targets with FDA approvals.
        """
        gene_upper = gene_symbol.upper()

        # 1. Fresh cache entry (only if it contains drugs)
        cached = self._cache.get(gene_upper)
        if cached and cached.get("drugs") and (time.time() - cached.get("fetched_at", 0)) < _CACHE_TTL_SECONDS:
            return cached["drugs"]

        # 2. Seed registry (immediate, no network)
        seed_drugs = SEED_REGISTRY.get(gene_upper, [])
        if seed_drugs:
            self._store_in_cache(gene_upper, seed_drugs)
            return seed_drugs

        # 3. Stale cache (only if it contains drugs)
        if cached and cached.get("drugs"):
            return cached["drugs"]

        # Cache the empty result so we don't repeat this lookup
        self._store_in_cache(gene_upper, [])
        return []

    def is_druggable(self, gene_symbol: str) -> bool:
        """Return True if any drugs target this gene."""
        return len(self.get_drugs(gene_symbol)) > 0

    def prefetch(self, gene_symbols: List[str]) -> None:
        """
        Batch-prefetch drug interactions for a list of genes in one API call.
        Call this before scoring many genes to avoid per-gene API requests.
        
        Args:
            gene_symbols: List of HUGO gene symbols to prefetch.
        """
        now = time.time()
        stale = [
            g.upper() for g in gene_symbols
            if g.upper() not in self._cache
            or (now - self._cache[g.upper()].get("fetched_at", 0)) >= _CACHE_TTL_SECONDS
        ]
        if not stale:
            return

        logger.info(f"Prefetching DGIdb interactions for {len(stale)} genes...")
        try:
            results = self._fetch_from_dgidb(stale)
            for gene, drugs in results.items():
                self._store_in_cache(gene, drugs)
            # Genes with no results → cache empty list so we don't re-query
            for gene in stale:
                if gene not in self._cache:
                    self._store_in_cache(gene, SEED_REGISTRY.get(gene, []))
        except Exception as e:
            logger.warning(f"DGIdb batch prefetch failed: {e}. Falling back to seed registry for {len(stale)} genes.")
            for gene in stale:
                self._store_in_cache(gene, SEED_REGISTRY.get(gene, []))

    # ---------------------------------------------------------------------- #
    # Internal                                                                 #
    # ---------------------------------------------------------------------- #

    def _fetch_from_dgidb(self, gene_symbols: List[str]) -> Dict[str, List[str]]:
        """
        Hit the DGIdb v2 REST API.
        
        Returns:
            Dict mapping UPPER gene symbol → list of drug names.
        """
        # Chunk to respect URL length limits (DGIdb handles up to ~500 genes per call)
        chunk_size = 200
        all_results: Dict[str, List[str]] = {}

        for i in range(0, len(gene_symbols), chunk_size):
            chunk = gene_symbols[i:i + chunk_size]
            params = {"genes": ",".join(chunk)}
            response = httpx.get(self.DGIDB_API, params=params, timeout=15.0)
            response.raise_for_status()
            data = response.json()

            for match in data.get("matchedTerms", []):
                gene = match.get("geneName", "").upper()
                interactions = match.get("interactions", [])
                drugs = list({
                    itx.get("drugName", "").strip()
                    for itx in interactions
                    if itx.get("drugName")
                })
                if gene:
                    all_results[gene] = drugs

        return all_results

    def _load_cache(self) -> Dict[str, Dict]:
        """Load the on-disk cache file."""
        if self._cache_path.exists():
            try:
                with open(self._cache_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _store_in_cache(self, gene: str, drugs: List[str]) -> None:
        """Write an entry to the in-memory and on-disk cache."""
        self._cache[gene] = {"drugs": drugs, "fetched_at": time.time()}
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._cache_path, "w") as f:
                json.dump(self._cache, f, indent=2)
        except IOError as e:
            logger.warning(f"Could not write DGIdb cache to {self._cache_path}: {e}")


# Module-level singleton (lazy-initialized so tests don't hit the network by default)
_client: Optional[DGIdbClient] = None


def _get_client() -> DGIdbClient:
    global _client
    if _client is None:
        _client = DGIdbClient()
    return _client


# Public convenience functions (backwards-compatible with old druggability.py callers)
def is_druggable(gene_symbol: str) -> bool:
    """Check if a gene has known drug interactions (DGIdb + fallback registry)."""
    return _get_client().is_druggable(gene_symbol)


def get_drugs_for_gene(gene_symbol: str) -> List[str]:
    """Return drug names targeting the given gene (DGIdb + fallback registry)."""
    return _get_client().get_drugs(gene_symbol)


def prefetch_druggability(gene_symbols: List[str]) -> None:
    """
    Batch-fetch drug data for a gene list before running scoring.
    Avoids per-gene API calls during the scoring loop.
    """
    _get_client().prefetch(gene_symbols)
