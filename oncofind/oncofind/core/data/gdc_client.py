import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from tqdm.asyncio import tqdm

from oncofind.config.settings import settings
from oncofind.exceptions import APIError

logger = logging.getLogger(__name__)


class GDCClient:
    """Asynchronous client for interacting with the NIH Genomic Data Commons (GDC) API."""

    def __init__(self, base_url: str = settings.gdc_api_url):
        self.base_url = base_url.rstrip("/")
        # Separate connect/read timeouts — GDC file downloads can be slow (4–8 MB/s)
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=15.0, read=300.0, write=30.0, pool=15.0),
            follow_redirects=True,
            headers={"Accept": "application/json"},
        )

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        await self.client.aclose()

    async def _post_query(self, endpoint: str, query_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a POST request to a GDC API endpoint."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = await self.client.post(url, json=query_payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise APIError(f"GDC API query failed with status {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise APIError(f"Failed to connect to GDC API: {e}")

    async def query_files(self, cancer_type: str, n_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query the GDC files endpoint for STAR-Counts RNA-seq data for a given TCGA cohort.
        
        Returns:
            List of dicts containing file_id, file_name, case_id, and sample_barcode.
        """
        endpoint = "files"
        project_id = f"TCGA-{cancer_type.upper()}"
        
        # Build query filters for STAR - Counts
        filters = {
            "op": "and",
            "content": [
                {"op": "in", "content": {"field": "cases.project.project_id", "value": [project_id]}},
                {"op": "in", "content": {"field": "files.experimental_strategy", "value": ["RNA-Seq"]}},
                {"op": "in", "content": {"field": "files.data_type", "value": ["Gene Expression Quantification"]}},
                {"op": "in", "content": {"field": "files.analysis.workflow_type", "value": ["STAR - Counts"]}},
                {"op": "in", "content": {"field": "files.data_format", "value": ["tsv"]}}
            ]
        }
        
        fields = [
            "file_id",
            "file_name",
            "file_size",
            "cases.case_id",
            "cases.submitter_id",
            "cases.samples.submitter_id",
            "cases.samples.sample_type",
        ]
        
        # Determine paging sizes
        size = n_samples if n_samples is not None else 10000
        
        payload = {
            "filters": filters,
            "fields": ",".join(fields),
            "format": "JSON",
            "size": size
        }
        
        data = await self._post_query(endpoint, payload)
        hits = data.get("data", {}).get("hits", [])
        
        parsed_files = []
        for hit in hits:
            # GDC cases structure is nested
            cases = hit.get("cases", [])
            if not cases:
                continue
            case = cases[0]
            case_id = case.get("case_id")
            patient_barcode = case.get("submitter_id")
            
            samples = case.get("samples", [])
            if not samples:
                continue
            
            # Use the first sample barcode (usually primary tumor 01A or solid tissue normal 11A)
            sample_barcode = samples[0].get("submitter_id")
            sample_type = samples[0].get("sample_type", "Primary Tumor")
            
            parsed_files.append({
                "file_id": hit["file_id"],
                "file_name": hit["file_name"],
                "file_size": hit["file_size"],
                "case_id": case_id,
                "patient_barcode": patient_barcode,
                "sample_barcode": sample_barcode,
                "sample_type": sample_type,   # ← Primary Tumor / Solid Tissue Normal / etc.
            })
            
        return parsed_files

    async def query_clinical(self, case_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Query GDC cases endpoint to retrieve clinical metadata.
        
        Returns:
            List of clinical dictionaries.
        """
        if not case_ids:
            return []
            
        endpoint = "cases"
        
        # Batch requests if there are too many cases (GDC POST handles large batches but let's chunk in groups of 500)
        chunk_size = 500
        all_clinical = []
        
        fields = [
            "case_id",
            "submitter_id",
            "demographic.gender",
            "demographic.age_at_index",
            "demographic.vital_status",
            "demographic.days_to_death",
            "diagnoses.days_to_last_follow_up",
            "diagnoses.ajcc_pathologic_stage",
            "diagnoses.primary_diagnosis",
        ]
        
        for i in range(0, len(case_ids), chunk_size):
            chunk = case_ids[i:i+chunk_size]
            filters = {
                "op": "in",
                "content": {"field": "cases.case_id", "value": chunk}
            }
            
            payload = {
                "filters": filters,
                "fields": ",".join(fields),
                "format": "JSON",
                "size": len(chunk)
            }
            
            data = await self._post_query(endpoint, payload)
            hits = data.get("data", {}).get("hits", [])
            
            for hit in hits:
                demo = hit.get("demographic", {})
                diag_list = hit.get("diagnoses", [])
                diag = diag_list[0] if diag_list else {}
                
                # Deduce stage
                stage = diag.get("ajcc_pathologic_stage", "Not Reported")
                
                # Survival analysis fields
                vital_status = demo.get("vital_status", "Alive")
                days_to_death = demo.get("days_to_death")
                days_to_follow_up = diag.get("days_to_last_follow_up")
                
                # Standard TCGA survival metric: overall survival time is days to death if dead, or last follow up if alive
                survival_days = None
                censored = 1  # default: censored / alive
                
                if vital_status and vital_status.lower() == "dead":
                    survival_days = days_to_death
                    censored = 0  # event occurred
                else:
                    survival_days = days_to_follow_up
                    
                all_clinical.append({
                    "case_id": hit["case_id"],
                    "patient_barcode": hit["submitter_id"],
                    "gender": demo.get("gender", "Not Reported"),
                    "age_at_index": demo.get("age_at_index"),
                    "vital_status": vital_status,
                    "days_to_death": days_to_death,
                    "days_to_last_follow_up": days_to_follow_up,
                    "survival_days": survival_days,
                    "censored": censored,
                    "stage": stage,
                    "primary_diagnosis": diag.get("primary_diagnosis", "")
                })
                
        return all_clinical

    async def download_file(self, file_id: str, dest_path: Path, semaphore: asyncio.Semaphore) -> None:
        """Download a single file from GDC by UUID, with concurrency limiting."""
        url = f"{self.base_url}/data/{file_id}"
        async with semaphore:
            temp_path = dest_path.parent / (dest_path.name + ".tmp")
            async with self.client.stream(
                "GET", url,
                timeout=httpx.Timeout(connect=15.0, read=300.0, write=30.0, pool=15.0),
                follow_redirects=True,
            ) as response:
                if response.status_code != 200:
                    raise APIError(
                        f"GDC returned HTTP {response.status_code} for file {file_id}"
                    )
                with open(temp_path, "wb") as f:
                    # aiter_bytes() is the async iterator — iter_bytes() is sync only
                    async for chunk in response.aiter_bytes(chunk_size=65536):
                        f.write(chunk)
            temp_path.rename(dest_path)

    async def download_files_batch(self, file_infos: List[Dict[str, Any]], dest_dir: Path, max_concurrency: int = 5) -> List[Tuple[str, Path]]:
        """Download multiple files in parallel with a progress bar."""
        dest_dir.mkdir(parents=True, exist_ok=True)
        semaphore = asyncio.Semaphore(max_concurrency)
        
        tasks = []
        downloaded = []
        
        for info in file_infos:
            file_id = info["file_id"]
            file_name = info["file_name"]
            path = dest_dir / f"{file_id}_{file_name}"
            
            # Check cache/existence
            if path.exists() and path.stat().st_size > 0:
                downloaded.append((info["sample_barcode"], path))
                continue
                
            tasks.append((info["sample_barcode"], file_id, path))
            
        if not tasks:
            return downloaded
            
        # Execute tasks asynchronously — await each future so exceptions propagate
        # tqdm wraps asyncio.as_completed for a live progress bar
        async_tasks = [
            (sample_barcode, file_id, path,
             self.download_file(file_id, path, semaphore))
            for sample_barcode, file_id, path in tasks
        ]
        
        futures = [coro for _, _, _, coro in async_tasks]
        task_meta = [(sb, fid, p) for sb, fid, p, _ in async_tasks]
        
        failed = []
        for i, future in enumerate(
            tqdm(asyncio.as_completed(futures), total=len(futures), desc="Downloading RNA-seq files")
        ):
            try:
                await future
            except Exception as e:  # noqa: BLE001
                sample_barcode, file_id, path = task_meta[i]
                logger.error(f"Failed to download {file_id} ({sample_barcode}): {e}")
                failed.append(file_id)
                
        if failed:
            logger.warning(f"{len(failed)} file(s) failed to download: {failed}")
            
        for sample_barcode, file_id, path in task_meta:
            if path.exists() and path.stat().st_size > 0:
                downloaded.append((sample_barcode, path))
                
        return downloaded
