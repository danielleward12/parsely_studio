import asyncio
import csv
import os
import time
from typing import Any, Dict, List, Type

from herbarium_processor.config import ROOT_DIR, TMP_DIR
from herbarium_processor.core.inference.label_extractor import LabelExtractor
from herbarium_processor.core.inference.llm_api import BaseLLMAPI, OpenRouterAPI


class LabelExtractionBatchRunner:
    """
    Async batch runner for extracting structured label data using an LLM-based extractor.

    Usage (async preferred):
        await LabelExtractionBatchRunner(...).run_async()

    Legacy sync:
        LabelExtractionBatchRunner(...).run()  # wraps the async path
    """

    def __init__(
        self,
        output_csv_path: str | None = None,
        system_instructions_path: str = "prompts/system_instructions_no_ocr.md",
        output_dir: str | None = None,
        prompt_builder=None,
        targets: List[Any] | None = None,
        llm_api_cls: Type[BaseLLMAPI] = OpenRouterAPI,
        *,
        max_inflight: int = 60,  # cap concurrent LLM calls per container
        rpm_limit: int = 140,  # safety below 150 RPM provider cap
        llm_api_key: str | None = None,
    ):
        self.output_csv_path = (
            ROOT_DIR / output_csv_path if output_csv_path else TMP_DIR / "results.csv"
        )
        self.system_instructions_path = ROOT_DIR / system_instructions_path
        self.output_dir = ROOT_DIR / output_dir if output_dir else TMP_DIR

        self.prompt_builder = prompt_builder
        self.targets = targets or []
        self.results: List[Dict[str, Any]] = []
        self.llm_api_cls = llm_api_cls
        self.llm_api_key = llm_api_key

        # concurrency + rate limiting
        self._sem = asyncio.Semaphore(max_inflight)
        self._rpm = max(1, rpm_limit)
        self._tokens = self._rpm
        self._last_refill = time.monotonic()

    # ---------------- internal helpers ----------------

    def load_prompts(self) -> None:
        with open(self.system_instructions_path, "r", encoding="utf-8") as f:
            self.sys_instr = f.read()

    def _make_extractor(self) -> LabelExtractor:
        api_client = self.llm_api_cls(
            system_instructions=self.sys_instr,
            api_key=self.llm_api_key,
        )
        return LabelExtractor(
            llm_api=api_client,
            prompt_builder=self.prompt_builder,
            output_dir=self.output_dir,
        )

    def _refill_tokens(self) -> None:
        # token-bucket refill based on elapsed time
        now = time.monotonic()
        per_sec = self._rpm / 60.0
        add = int((now - self._last_refill) * per_sec)
        if add > 0:
            self._tokens = min(self._rpm, self._tokens + add)
            self._last_refill = now

    async def _acquire_rpm_token(self) -> None:
        while True:
            self._refill_tokens()
            if self._tokens > 0:
                self._tokens -= 1
                return
            await asyncio.sleep(0.2)

    # ---------------- async extraction ----------------

    async def run_extraction_async(self) -> None:
        extractor = self._make_extractor()

        async def classify_one(target):
            async with self._sem:
                await self._acquire_rpm_token()
                # LabelExtractor.classify is async now
                res = await extractor.classify(target)
                res["imagename"] = os.path.splitext(os.path.basename(target.img_path))[
                    0
                ]
                return res

        if not self.targets:
            self.results = []
            return

        self.results = await asyncio.gather(*(classify_one(t) for t in self.targets))

    # ---------------- CSV save (sync is fine) ----------------

    def save_csv(self) -> None:
        all_keys: set[str] = set()
        for r in self.results:
            all_keys.update(r.keys())

        ordered = ["imagename"]
        if self.prompt_builder is not None and getattr(
            self.prompt_builder, "field_list", None
        ):
            ordered += [f for f in self.prompt_builder.field_list if f not in ordered]

        remaining = [k for k in all_keys if k not in ordered]
        fieldnames = ordered + sorted(remaining)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.results:
                writer.writerow(row)
        print(f"Saved CSV to {self.output_csv_path}")

    # ---------------- public entry points ----------------

    async def run_async(self) -> None:
        self.load_prompts()
        await self.run_extraction_async()
        self.save_csv()

    def run(self) -> None:
        """Backward-compatible sync wrapper."""
        self.load_prompts()
        asyncio.run(self.run_extraction_async())
        self.save_csv()
