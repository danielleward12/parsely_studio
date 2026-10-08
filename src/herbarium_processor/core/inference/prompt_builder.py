import json
import os
import re
from typing import Dict, List, Tuple

from jinja2 import Environment, FileSystemLoader
import pandas as pd

from herbarium_processor.config import ROOT_DIR
from herbarium_processor.core.types.specimen_label import SpecimenLabel


class PromptBuilder:
    """
    PromptBuilder

    This module defines a PromptBuilder class that loads example data from a CSV file and a Jinja2 template,
    then renders few-shot prompts for use with a language model (e.g., Gemini).
    It supports generating both plain prompt strings and multimodal prompt content with embedded images and OCR data.

    Key Features:
    -------------
    - Loads specimen label data from a CSV file.
    - Uses a Jinja2 template to render prompts with few-shot examples and a target sample.
    - Supports multimodal prompt generation: produces content parts with images for Gemini's API.
    - Provides methods for generating debug prompts and for extracting output fields.

    Usage Example:
    --------------
    from prompt_builder import PromptBuilder, SpecimenLabel

    labels = [
        SpecimenLabel(id="1", img_path="/path/to/image1.jpg", ocr_path="/path/to/ocr1.json"),
        SpecimenLabel(id="2", img_path="/path/to/image2.jpg", ocr_path="/path/to/ocr2.json")
    ]

    target_example = SpecimenLabel(id="3", img_path="/path/to/image3.jpg", ocr_path="/path/to/ocr3.json")

    builder = PromptBuilder(
        csv_path="data/labels.csv",
        field_list=["scientific_name", "field_collectors", "sources"],
        shot_data=labels,
        template_path="templates/prompt_template.j2"
    )

    # Generate a prompt string and list of image paths for the target example
    prompt_str, image_paths = builder.generate(target_example)

    # Generate a list of content parts (text and images) for multimodal model input
    contents = builder.generate_contents(target_example)

    # `prompt_str` is a string containing the rendered prompt
    # `image_paths` is a list of image file paths referenced in the prompt
    # `contents` is a list of text and image parts suitable for Gemini's API
    """

    def __init__(
        self,
        csv_path: str,
        field_list: List[str],
        shot_data: List[SpecimenLabel],
        template_path: str,
    ):
        self.csv_path = ROOT_DIR / csv_path
        self.field_list = field_list
        self.shot_data = shot_data
        self.template_path = ROOT_DIR / template_path

        self.df = pd.read_csv(self.csv_path, dtype={"id": str})
        self.id_column = "imagename" if "imagename" in self.df.columns else "id"
        template_dir, template_file = os.path.split(self.template_path)
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template(template_file)

    def _load_ocr_json(self, path: str) -> Dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_output_json(self, id_: str) -> Dict:
        matching_rows = self.df[self.df[self.id_column].astype(str) == str(id_)]
        row = matching_rows.iloc[0].to_dict()
        output = {}
        for key in self.field_list:
            if key == "sources":
                output["sources"] = (
                    json.loads(row["sources"]) if row.get("sources") else {}
                )
            else:
                output[key] = row.get(key, None)
        return output

    def generate_prompt(self, target_data) -> Tuple[str, List[str]]:
        shots = [
            {
                "image_path": shot.img_path,
                "ocr_json": self._load_ocr_json(shot.ocr_path),
                "output_json": self._load_output_json(shot.id),
            }
            for shot in self.shot_data
        ]

        target = {
            "image_path": target_data.img_path,
            "ocr_json": self._load_ocr_json(target_data.ocr_path),
        }

        prompt = self.template.render(
            field_list=self.field_list, shots=shots, target=target
        )

        return prompt

    def generate_debug_prompt(self) -> str:
        """
        Generate a prompt using only the few-shot examples, without inserting a target sample.
        Useful for debugging or printing the base prompt template.

        Returns:
            str: The rendered prompt string with only the few-shot examples.
        """
        shots = [
            {
                "image_path": shot.img_path,
                "ocr_json": self._load_ocr_json(shot.ocr_path),
                "output_json": self._load_output_json(shot.id),
            }
            for shot in self.shot_data
        ]

        # Provide an empty or dummy target
        target = {
            "image_path": "",
            "ocr_json": {},
        }

        prompt = self.template.render(
            field_list=self.field_list, shots=shots, target=target
        )
        return prompt

    def generate(self, target_data) -> Tuple[str, List[str]]:
        image_paths = [shot.img_path for shot in self.shot_data]
        image_paths.append(target_data.img_path)

        return self.generate_prompt(target_data), image_paths

    def generate_contents(self, target_data):
        """Return content parts with images inserted where <|image_N|> is referenced."""
        prompt_text, image_paths = self.generate(target_data)
        image_parts = [self._make_image_part(p) for p in image_paths]
        parts = []
        pattern = re.compile(r"<\|image_(\d+)\|>")

        pos = 0
        for match in pattern.finditer(prompt_text):
            start, end = match.span()
            if start > pos:
                parts.append(prompt_text[pos:start])
            idx = int(match.group(1))
            if idx >= len(image_parts):
                raise ValueError(
                    f"Image index {idx} out of range for {len(image_parts)} image parts"
                )
            parts.append(image_parts[idx])
            pos = end
        if pos < len(prompt_text):
            parts.append(prompt_text[pos:])
        return parts

    def _make_image_part(self, image_path):
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
        return {
            "mime_type": "image/jpeg",
            "data": img_bytes,
        }
