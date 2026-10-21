from collections import defaultdict
import io
import json
import os

import cv2
from google.cloud import vision
from google.protobuf.json_format import MessageToDict
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from herbarium_processor.config import ROOT_DIR, TMP_DIR

# Prefer Application Default Credentials (ADC).
# Only fall back to ~/.secrets if nothing else is configured.
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    default_path = os.path.expanduser("~/.secrets/vision-key.json")
    if os.path.exists(default_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = default_path


class OcrClient:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        self.preprocessor = ImagePreprocessor()

    def extract_text_json(
        self,
        image_path,
        preprocessed_path=None,
        ocr_annotated_path=None,
        llm_json_path=None,
    ):
        image_path = ROOT_DIR / image_path
        # Get the base name of the file without extension
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        if preprocessed_path is None:
            preprocessed_path = TMP_DIR / f"ocr_preprocessed_{base_name}.jpg"
            preprocessed_path = os.path.normpath(preprocessed_path)
        self.preprocessor.preprocess_and_save(image_path, preprocessed_path)

        with io.open(preprocessed_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # Perform OCR
        # Bound an unavailable Vision API rather than leaving the interactive
        # crop-and-extract request open indefinitely.
        response = self.client.document_text_detection(image=image, timeout=90.0)

        if response.error.message:
            raise Exception(f"Google OCR API error: {response.error.message}")

        lines = self.parse_google_ocr_response(response)
        merged_lines = self.merge_to_lines(lines)
        if ocr_annotated_path is None:
            ocr_annotated_path = TMP_DIR / f"ocr_bounding_{base_name}.jpg"
            ocr_annotated_path = os.path.normpath(ocr_annotated_path)
        self.visualize_bounding_boxes(merged_lines, image_path, ocr_annotated_path)
        if llm_json_path is None:
            llm_json_path = TMP_DIR / f"ocr_ai_input_{base_name}.json"
            llm_json_path = os.path.normpath(llm_json_path)
        print(merged_lines)
        with open(llm_json_path, "w", encoding="utf-8") as f:
            json.dump(merged_lines, f, ensure_ascii=False, indent=2)
        return merged_lines

    def parse_google_ocr_response(self, response):
        response_dict = MessageToDict(response._pb)

        lines = []
        id_counter = 1

        try:
            pages = response_dict["fullTextAnnotation"]["pages"]
        except KeyError:
            return []

        for page_idx, page in enumerate(pages):
            for block_idx, block in enumerate(page.get("blocks", [])):
                for para_idx, para in enumerate(block.get("paragraphs", [])):
                    for word_idx, word in enumerate(para.get("words", [])):
                        word_text = "".join([s["text"] for s in word["symbols"]])
                        bbox = word.get("boundingBox", {}).get("vertices", [])
                        if not bbox or any(
                            "x" not in pt or "y" not in pt for pt in bbox
                        ):
                            continue  # skip this word
                        id_str = f"{page_idx + 1}.{block_idx + 1}.{id_counter}"
                        id_counter += 1

                        lines.append(
                            {
                                "id": id_str,
                                "text": word_text,
                                "bounding_box": bbox,
                                "confidence": word.get("confidence", 1.0),
                            }
                        )
        return lines

    def merge_to_lines(self, words, max_gap=30):
        lines = defaultdict(list)

        for w in words:
            y = round(w["bounding_box"][0]["y"] / max_gap)  # naive line grouping
            lines[y].append(w)

        result = []
        for i, (line_key, word_list) in enumerate(sorted(lines.items())):
            sorted_words = sorted(word_list, key=lambda w: w["bounding_box"][0]["x"])
            text = " ".join(w["text"] for w in sorted_words)

            # Extract all bounding box points from OCR response
            all_pts = [
                (pt["x"], pt["y"])
                for w in sorted_words
                for pt in w["bounding_box"]
                if "x" in pt and "y" in pt
            ]

            # Proceed if we have points
            if all_pts:
                # Merge into one rectangle
                all_x = [pt[0] for pt in all_pts]
                all_y = [pt[1] for pt in all_pts]
                merged_box = [
                    (min(all_x), min(all_y)),
                    (max(all_x), min(all_y)),
                    (max(all_x), max(all_y)),
                    (min(all_x), max(all_y)),
                ]

                # Map merged bounding box back to original image coordinates
                mapped_box = self.preprocessor.map_bbox_to_original(merged_box)

                # Format as list of dicts for output
                merged_box = [{"x": int(x), "y": int(y)} for (x, y) in mapped_box]
            else:
                merged_box = []

            avg_confidence = sum(w["confidence"] for w in sorted_words) / len(
                sorted_words
            )

            result.append(
                {
                    "id": f"1.1.{i + 1}",
                    "text": text,
                    "bounding_box": merged_box,
                    "average_confidence": avg_confidence,
                }
            )
        return result

    def visualize_bounding_boxes(self, words, image_path, output_path):
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        try:
            ImageFont.truetype("arial.ttf", 12)
        except Exception:
            ImageFont.load_default()

        for word in words:
            bbox = word.get("bounding_box", [])
            word.get("id", "")
            if len(bbox) == 4:
                points = [tuple((v.get("x", 0), v.get("y", 0))) for v in bbox]
                draw.line(points + [points[0]], fill="red", width=2)
                # draw.text(points[0], source, fill="blue", font=font)

        image.save(output_path)
        print(
            f"Saved visualized image with bounding boxes and sources to {output_path}"
        )


class ImagePreprocessor:
    """
    Preprocess images for improved OCR accuracy using grayscale conversion,
    perspective correction, sharpening, resizing, contrast stretching,
    denoising, and bounding box remapping support.

    Usage:
        pre = ImagePreprocessor()

        # To get a processed image as an OpenCV array:
        processed = pre.preprocess_for_ocr("input.jpg")

        # To save the processed image to disk:
        pre.preprocess_and_save("input.jpg", "output.jpg")

        # To map OCR bounding boxes (from processed image) back to original image:
        original_pts = pre.map_bbox_to_original([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
    """

    def __init__(self):
        self.last_perspective_transform = None
        self.last_inverse_transform = None
        self.last_resize_fx = 1.0
        self.last_resize_fy = 1.0

    def preprocess_for_ocr(
        self,
        image_path,
    ):
        image_path = ROOT_DIR / image_path
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Unable to load image: {image_path}")

        # img = self._apply_perspective_correction(img)
        # No correction; set identity transforms
        self.last_perspective_transform = np.eye(3, dtype=np.float32)
        self.last_inverse_transform = np.eye(3, dtype=np.float32)
        return img

        # Step 1: Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Step 2: Sharpen image to improve text clarity
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(gray, -1, kernel)

        # Step 3: Resize if resolution is low
        height, width = sharpened.shape
        self.last_resize_fx = self.last_resize_fy = 1.0
        if height < 1000:
            self.last_resize_fx = self.last_resize_fy = 1.5
            sharpened = cv2.resize(
                sharpened, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC
            )

        # Step 4: Light contrast stretch
        processed = cv2.convertScaleAbs(sharpened, alpha=1.2, beta=10)

        # Step 5: Denoise (optional)
        denoised = cv2.fastNlMeansDenoising(processed, h=15)

        return denoised

    def _apply_perspective_correction(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 50, 200)

        contours, _ = cv2.findContours(
            edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                screen_cnt = approx
                break
        else:
            # No correction; set identity transforms
            self.last_perspective_transform = np.eye(3, dtype=np.float32)
            self.last_inverse_transform = np.eye(3, dtype=np.float32)
            return img

        pts = screen_cnt.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        (tl, tr, br, bl) = rect
        width_a = np.linalg.norm(br - bl)
        width_b = np.linalg.norm(tr - tl)
        max_width = max(int(width_a), int(width_b))

        height_a = np.linalg.norm(tr - br)
        height_b = np.linalg.norm(tl - bl)
        max_height = max(int(height_a), int(height_b))

        dst = np.array(
            [
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1],
            ],
            dtype="float32",
        )

        M = cv2.getPerspectiveTransform(rect, dst)
        self.last_perspective_transform = M
        self.last_inverse_transform = cv2.invert(M)[1]

        warped = cv2.warpPerspective(img, M, (max_width, max_height))
        return warped

    def map_bbox_to_original(self, bbox_points):
        if self.last_inverse_transform is None:
            raise ValueError(
                "No perspective transform available. Set correct_perspective=True and run preprocessing first."
            )

        # 1. Unscale the coordinates back to warped image size
        unscaled = np.array(bbox_points, dtype=np.float32).reshape(-1, 2)
        unscaled[:, 0] /= self.last_resize_fx
        unscaled[:, 1] /= self.last_resize_fy

        # 2. Apply inverse perspective transform
        pts = unscaled.reshape(-1, 1, 2)
        mapped = cv2.perspectiveTransform(pts, self.last_inverse_transform)

        return mapped.reshape(-1, 2)

    def save_preprocessed_image(self, image, save_path):
        cv2.imwrite(save_path, image)

    def preprocess_and_save(self, image_path, output_path):
        image = self.preprocess_for_ocr(image_path)
        self.save_preprocessed_image(image, output_path)
        return output_path
