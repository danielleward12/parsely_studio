"""
Herbarium Processor Notebook
========================

This notebook is designed to process herbarium specimen images and generate labels using a prompt-based approach.
It includes steps for image processing, prompt configuration, and generating specimen labels.
It is structured to be run in a Jupyter notebook environment.

Configuration: select what images to sample from.

You should edit this section each time you run the code to:
  * select the images you want to process
  * set the path to the output CSV file.
"""

from utils.notebook_setup import setup_project

setup_project()

image_path = "data/img/bucket"
output_csv_path = "tmp/an_output.csv"













"""import argparse
import asyncio
import csv
import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from herbarium_processor.config import ROOT_DIR
from herbarium_processor.core.inference.llm_api import GoogleGeminiAPI, OpenRouterAPI


DEFAULT_CONFIG = ROOT_DIR / "prompts/configs/default_prompt.yaml"
DEFAULT_SYSTEM_INSTRUCTIONS = Path(
    "/Users/danielleward/Documents/Projects/parsely_studio/prompts/ai_only_system_instructions.md"
)
IMAGE_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
SYSTEM_INSTRUCTIONS = """You are an expert assistant for transcribing herbarium specimen labels.
Read each label directly from its image and extract the requested fields.
Use only information visible in the image. Preserve label wording where the
field calls for verbatim text. Return null when a value is absent or illegible.
Never invent or infer missing values. Return only valid JSON with the requested
keys and no explanation or Markdown fences."""


def resolve_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT_DIR / path


def load_config(config_path: Path) -> tuple[list[str], list[dict[str, Any]], pd.DataFrame]:
    with config_path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    fields = [str(field).strip() for field in config["field_list"]]
    shots = config.get("shot_data", [])
    csv_path = resolve_path(config["csv_path"])
    labels = pd.read_csv(csv_path, dtype={"id": str})
    labels.columns = [str(column).strip() for column in labels.columns]
    return fields, shots, labels


def json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def load_example_output(
    example_id: str, fields: list[str], labels: pd.DataFrame
) -> dict[str, Any]:
    matches = labels[labels["id"].astype(str) == str(example_id)]
    if matches.empty:
        raise ValueError(f"Few-shot example ID {example_id!r} is missing from the labels CSV")
    row = matches.iloc[0].to_dict()
    return {field: json_value(row.get(field)) for field in fields}


def build_prompt(
    fields: list[str], examples: list[tuple[str, dict[str, Any]]], target_name: str
) -> str:
    field_list = "\n".join(f"- {field}" for field in fields)
    sections = [
        "Extract the following fields from the herbarium specimen label image.",
        "Return a single JSON object with exactly these keys:",
        field_list,
        "Use the examples to match the requested field meanings and output format.",
    ]
    for index, (example_name, output) in enumerate(examples, start=1):
        sections.extend(
            [
                f"\nExample {index}: {example_name}",
                f"Image: <|image_{index - 1}|>",
                "Correct output:",
                json.dumps(output, ensure_ascii=False, indent=2),
            ]
        )
    sections.extend(
        [
            f"\nNow extract the fields from this image ({target_name}):",
            f"Image: <|image_{len(examples)}|>",
            "Return only one valid JSON object. Do not include extra keys or text.",
        ]
    )
    return "\n".join(sections)


def parse_model_json(raw_text: str, fields: list[str]) -> dict[str, Any]:
    text = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", raw_text.strip())
    result = json.loads(text)
    if not isinstance(result, dict):
        raise ValueError("Model response must be a JSON object")
    return {field: result.get(field) for field in fields}


def build_contents(
    fields: list[str],
    examples: list[tuple[str, dict[str, Any]]],
    target_path: Path,
    example_images: list[Path],
) -> list[str | dict[str, Any]]:
    """Interleave prompt text and image parts in the same order as the markers."""
    prompt = build_prompt(fields, examples, target_path.name)
    image_paths = [*example_images, target_path]
    parts: list[str | dict[str, Any]] = []
    cursor = 0
    for match in re.finditer(r"<\|image_(\d+)\|>", prompt):
        if match.start() > cursor:
            parts.append(prompt[cursor : match.start()])
        index = int(match.group(1))
        image_path = image_paths[index]
        parts.append(
            {
                "data": image_path.read_bytes(),
                "mime_type": IMAGE_MIME_TYPES[image_path.suffix.lower()],
            }
        )
        cursor = match.end()
    if cursor < len(prompt):
        parts.append(prompt[cursor:])
    return parts


async def run(
    images_dir: Path,
    output_csv: Path,
    config_path: Path,
    provider: str,
    model_name: str | None,
    system_instructions_path: Path | None,
) -> None:
    fields, shot_configs, labels = load_config(config_path)
    examples: list[tuple[str, dict[str, Any]]] = []
    example_images: list[Path] = []
    for shot in shot_configs:
        image_path = resolve_path(shot["img_path"])
        if not image_path.is_file():
            raise FileNotFoundError(f"Few-shot image not found: {image_path}")
        example_images.append(image_path)
        examples.append(
            (image_path.name, load_example_output(shot["id"], fields, labels))
        )

    if not images_dir.is_dir():
        raise NotADirectoryError(f"Image directory not found: {images_dir}")
    image_paths = sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_MIME_TYPES
    )
    if not image_paths:
        raise FileNotFoundError(f"No supported image files found in {images_dir}")

    api_class = GoogleGeminiAPI if provider == "google" else OpenRouterAPI
    instructions = (
        system_instructions_path.read_text(encoding="utf-8")
        if system_instructions_path
        else SYSTEM_INSTRUCTIONS
    )
    llm = api_class(system_instructions=instructions, model_name=model_name)
    rows = []
    for image_path in image_paths:
        contents = build_contents(fields, examples, image_path, example_images)
        print(f"Processing {image_path.name}")
        raw_response = await llm.generate_content(contents)
        row = parse_model_json(raw_response, fields)
        row["id"] = image_path.stem
        rows.append(row)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["id", *fields])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} records to {output_csv}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract specimen label data from images using a vision LLM without OCR."
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=ROOT_DIR / "data/img/bucket",
        help="Directory of specimen images (use the same cropped images as the OCR run).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT_DIR / "tmp/llm_only_results.csv",
        help="Path for the output CSV.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Prompt YAML containing the field list and few-shot examples.",
    )
    parser.add_argument(
        "--provider",
        choices=("openrouter", "google"),
        default="openrouter",
        help="LLM API provider; defaults to OpenRouter like the standard local runner.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override for the selected provider.",
    )
    parser.add_argument(
        "--system-instructions",
        type=Path,
        default=DEFAULT_SYSTEM_INSTRUCTIONS,
        DEFAULT_SYSTEM_INSTRUCTIONS = Path(
    "/Users/danielleward/Documents/Projects/parsely_studio/prompts/ai_only_system_instructions.md")

IMAGE_MIME_TYPES = {
    args = parser.parse_args()
    asyncio.run(
        run(
            resolve_path(args.images),
            resolve_path(args.output),
            resolve_path(args.config),
            args.provider,
            args.model,
            resolve_path(args.system_instructions),
        )
    )


if __name__ == "__main__":
    main()"""
