import asyncio
import csv
from types import SimpleNamespace

from herbarium_processor.core.inference.label_extraction_batch_runner import (
    LabelExtractionBatchRunner,
)
from herbarium_processor.core.types.specimen_label import SpecimenLabel


def test_load_prompts(tmp_path):
    sys_path = tmp_path / "sys.txt"
    sys_path.write_text("SYS")
    runner = LabelExtractionBatchRunner(
        output_csv_path="out.csv",
        system_instructions_path=str(sys_path),
        prompt_builder=None,
        targets=[],
    )
    runner.load_prompts()
    assert runner.sys_instr == "SYS"


def test_run_extraction(monkeypatch, tmp_path):
    calls = []

    created_clients = []

    class FakeExtractor:
        def __init__(self, llm_api, prompt_builder, output_dir):
            self.llm_api = llm_api
            self.prompt_builder = prompt_builder
            self.output_dir = output_dir
            created_clients.append(llm_api)

        async def classify(self, target):
            calls.append(target)
            return {"value": target.img_path}

    class FakeAPI:
        def __init__(self, system_instructions, model_name="m", api_key=None):
            self.system_instructions = system_instructions
            self.api_key = api_key

    monkeypatch.setattr(
        "herbarium_processor.core.inference.label_extraction_batch_runner.LabelExtractor",
        FakeExtractor,
    )

    runner = LabelExtractionBatchRunner(
        output_csv_path="out.csv",
        output_dir=str(tmp_path),
        prompt_builder="PB",
        targets=[],
        llm_api_cls=FakeAPI,
        llm_api_key="abc123",
    )
    t1 = SpecimenLabel(id="a", img_path=str(tmp_path / "a.jpg"), ocr_path="x")
    t2 = SpecimenLabel(id="b", img_path=str(tmp_path / "b.jpg"), ocr_path="y")
    runner.targets = [t1, t2]
    runner.sys_instr = "SYS"
    asyncio.run(runner.run_extraction_async())

    assert calls == [t1, t2]
    assert created_clients[0].api_key == "abc123"
    assert [r["value"] for r in runner.results] == [t1.img_path, t2.img_path]
    assert [r["imagename"] for r in runner.results] == ["a", "b"]


def test_make_extractor_receives_api_key(monkeypatch, tmp_path):
    captured = {}

    class RecordingAPI:
        def __init__(self, system_instructions, api_key=None):
            captured["system_instructions"] = system_instructions
            captured["api_key"] = api_key

    class FakeExtractor:
        def __init__(self, llm_api, prompt_builder, output_dir):
            captured["llm_api"] = llm_api
            captured["prompt_builder"] = prompt_builder
            captured["output_dir"] = output_dir
            captured["extractor"] = self

        async def classify(self, target):
            return {}

    monkeypatch.setattr(
        "herbarium_processor.core.inference.label_extraction_batch_runner.LabelExtractor",
        FakeExtractor,
    )

    runner = LabelExtractionBatchRunner(
        output_csv_path="out.csv",
        output_dir=str(tmp_path),
        prompt_builder="builder",
        targets=[],
        llm_api_cls=RecordingAPI,
        llm_api_key="secret",  # new functionality should pass this through
    )
    runner.sys_instr = "SYS"

    extractor = runner._make_extractor()

    assert captured["system_instructions"] == "SYS"
    assert captured["api_key"] == "secret"
    assert extractor is captured["extractor"]
    assert captured["prompt_builder"] == "builder"
    assert captured["output_dir"] == tmp_path


def test_save_csv(tmp_path):
    csv_path = tmp_path / "out.csv"
    dummy_builder = SimpleNamespace(field_list=["a", "b"])
    runner = LabelExtractionBatchRunner(
        output_csv_path=str(csv_path), prompt_builder=dummy_builder, targets=[]
    )
    runner.results = [{"imagename": "1", "a": "x"}, {"imagename": "2", "b": "y"}]
    runner.save_csv()

    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    imagenames = {row["imagename"] for row in rows}
    assert imagenames == {"1", "2"}
    assert list(rows[0].keys()) == ["imagename", "a", "b"]


def test_run_calls_all_methods(monkeypatch):
    order = []
    runner = LabelExtractionBatchRunner(
        output_csv_path="out.csv", prompt_builder=None, targets=[]
    )
    monkeypatch.setattr(runner, "load_prompts", lambda: order.append("load"))

    async def fake_run_extraction_async():
        order.append("extract")

    monkeypatch.setattr(runner, "run_extraction_async", fake_run_extraction_async)
    monkeypatch.setattr(runner, "save_csv", lambda: order.append("save"))
    runner.run()
    assert order == ["load", "extract", "save"]
