#!/usr/bin/env python3
"""Convert the thesis DOCX body to a complete English Markdown document."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from zipfile import ZipFile

import torch
from lxml import etree
from transformers import MarianMTModel, MarianTokenizer


MODEL_NAME = "Helsinki-NLP/opus-mt-es-en"
NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "v": "urn:schemas-microsoft-com:vml",
}
URL_RE = re.compile(r"https?://\S+")
CODE_PREFIX_RE = re.compile(
    r"^(GET|PUT|POST|DELETE|curl\b|kafka-[\w.-]+|bin/|/etc/|etc/|//|<[^>]+>|"
    r"[@{}\[\]]|input\s*\{|filter\s*\{|output\s*\{)",
    re.IGNORECASE,
)

CHAPTER_TITLES = {
    "INTRODUCCIÓN": "Chapter 1. Introduction",
    "IDEA DE NEGOCIO, INVERSION CON BIG DATA y MACHINE LEARNING": (
        "Chapter 2. Business Case: Investment with Big Data and Machine Learning"
    ),
    "CAPTURA DE DATOS, WEB-CRAWLER": "Chapter 3. Data Capture: Web Crawler",
    "Distribución llegada masiva de eventos, Apache KAKFA": (
        "Chapter 4. High-Volume Event Distribution with Apache Kafka"
    ),
    "Almacenamiento: MongoDB y Elasticsearch": (
        "Chapter 5. Storage: MongoDB and Elasticsearch"
    ),
    "Análisis de Logs, ELK Stack": "Chapter 6. Log Analysis with the Elastic Stack",
    "Visualización de datos, Kibana": "Chapter 7. Data Visualization with Kibana",
    "Machine Learning - X-PACK": "Chapter 8. Machine Learning with X-Pack",
    "CONCLUSIONES Y FUTURAS LÍNEAS DE TRABAJO": (
        "Chapter 9. Conclusions and Future Work"
    ),
    "Referencias": "Chapter 10. References",
    "BIBLIOGRAFÍA": "Bibliography",
}

CAPTION_TRANSLATIONS = {
    1: "Complete project overview",
    2: "Business idea",
    3: "Financial press",
    4: "Author XPath",
    5: "Publication-date XPath",
    6: "Selecting tags",
    7: "Article text",
    8: "From the website to the script",
    9: "Collection of spiders",
    10: "Original point-to-point ingestion",
    11: "Ingestion in a Big Data system",
    12: "Kafka in action",
    13: "Kafka topics",
    14: "Kafka replication",
    15: "Kafka theory summary",
    16: "Creating a topic",
    17: "Producer and consumer",
    18: "Java consumer receiving messages",
    19: "Kafka in the project architecture",
    20: "Elasticsearch and MongoDB integration example",
    21: "Scaling up and scaling out",
    22: "Elasticsearch and MongoDB",
    23: "Using both distributed databases together",
    24: "Data integration with MongoDB",
    25: "Kafka and MongoDB",
    26: "Elastic Stack module",
    27: "OSI model",
    28: "Index and table comparison",
    29: "Checking cluster state in Dev Tools",
    30: "Cluster state",
    31: "Checking cluster health",
    32: "Checking indices",
    33: "SQL insert and Elasticsearch indexing",
    34: "Reading data",
    35: "Deleting and querying data in Kibana",
    36: "Updating data in Kibana",
    37: "Running queries",
    38: "Example collected log",
    39: "Configuring the path to the log files",
    40: "Kibana and Filebeat",
    41: "Metricbeat in Kibana",
    42: "Packetbeat processing sequence",
    43: "Packetbeat execution dashboard",
    44: "Event processing in Logstash",
    45: "Testing and monitoring Logstash",
    46: "Logstash output",
    47: "First Logstash transformation",
    48: "Second Logstash transformation",
    49: "Enabling geolocation",
    50: "Configuring Logstash for the ETL flow",
    51: "Geolocation data arriving correctly",
    52: "Custom template",
    53: "Apache template",
    54: "Apache input logs displayed on a map",
    55: "Elastic Stack and Kibana",
    56: "Viewing logs in Discover",
    57: "Adding a filter to the visualization",
    58: "Bar chart split by response code",
    59: "Donut visualization",
    60: "Table visualization",
    61: "Combined final dashboard",
    62: "Uploading data to Elasticsearch",
    63: "Applying Machine Learning to logs",
    64: "Detailed view of anomalies",
    65: "Applying Machine Learning to user metrics",
}


def image_name_for_media(media_name: str) -> str:
    match = re.search(r"(\d+)", Path(media_name).stem)
    if not match:
        raise ValueError(f"Cannot determine image number: {media_name}")
    return f"source-image-{int(match.group(1)):03d}{Path(media_name).suffix.lower()}"


def read_docx_rows(docx_path: Path) -> list[dict[str, object]]:
    with ZipFile(docx_path) as archive:
        root = etree.fromstring(archive.read("word/document.xml"))
        styles_root = etree.fromstring(archive.read("word/styles.xml"))
        rels_root = etree.fromstring(archive.read("word/_rels/document.xml.rels"))

    style_names = {
        element.get(f"{{{NAMESPACES['w']}}}styleId"): (
            element.xpath("./w:name/@w:val", namespaces=NAMESPACES) or ["Normal"]
        )[0]
        for element in styles_root.xpath(".//w:style", namespaces=NAMESPACES)
    }
    relationships = {
        element.get("Id"): element.get("Target") for element in rels_root
    }
    rows: list[dict[str, object]] = []
    for index, paragraph in enumerate(
        root.xpath(".//w:body//w:p", namespaces=NAMESPACES)
    ):
        text = " ".join(
            "".join(paragraph.xpath(".//w:t/text()", namespaces=NAMESPACES)).split()
        )
        style_id = (
            paragraph.xpath("./w:pPr/w:pStyle/@w:val", namespaces=NAMESPACES)
            or ["Normal"]
        )[0]
        relationship_ids = paragraph.xpath(
            ".//a:blip/@r:embed | .//a:blip/@r:link | .//v:imagedata/@r:id",
            namespaces=NAMESPACES,
        )
        images = [
            image_name_for_media(os.path.basename(relationships[relationship_id]))
            for relationship_id in relationship_ids
            if relationship_id in relationships
        ]
        if text or images:
            rows.append(
                {
                    "index": index,
                    "style": style_names.get(style_id, style_id),
                    "text": text,
                    "images": images,
                }
            )
    return rows


def protect_literals(text: str) -> tuple[str, dict[str, str]]:
    replacements: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        key = f"PLACEHOLDER{len(replacements)}TOKEN"
        replacements[key] = match.group(0)
        return key

    return URL_RE.sub(replace, text), replacements


def restore_literals(text: str, replacements: dict[str, str]) -> str:
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


class Translator:
    def __init__(self, cache_path: Path):
        self.cache_path = cache_path
        self.cache: dict[str, str] = (
            json.loads(cache_path.read_text(encoding="utf-8"))
            if cache_path.exists()
            else {}
        )
        self.tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
        self.model = MarianMTModel.from_pretrained(MODEL_NAME, local_files_only=True)
        self.model.eval()

    def needs_translation(self, text: str) -> bool:
        without_urls = URL_RE.sub("", text).strip()
        return bool(re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", without_urls))

    def translate_batch(self, texts: list[str]) -> list[str]:
        results = [""] * len(texts)
        pending: list[tuple[int, str, str, dict[str, str]]] = []
        for index, original in enumerate(texts):
            if original in self.cache and (
                self.cache[original] != original or not self.needs_translation(original)
            ):
                results[index] = self.cache[original]
            elif not self.needs_translation(original):
                results[index] = original
                self.cache[original] = original
            else:
                protected, replacements = protect_literals(original)
                pending.append((index, original, protected, replacements))

        for offset in range(0, len(pending), 24):
            chunk = pending[offset : offset + 24]
            encoded = self.tokenizer(
                [item[2] for item in chunk],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )
            with torch.no_grad():
                generated = self.model.generate(
                    **encoded,
                    num_beams=1,
                    max_new_tokens=512,
                )
            translated = self.tokenizer.batch_decode(generated, skip_special_tokens=True)
            for item, value in zip(chunk, translated):
                index, original, _, replacements = item
                value = restore_literals(value, replacements).strip()
                results[index] = value
                self.cache[original] = value
            if offset % 80 == 0:
                self.save()
                print(f"Translated {min(offset + len(chunk), len(pending))}/{len(pending)}")
        self.save()
        return results

    def save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()

    all_rows = read_docx_rows(args.docx)
    start = next(
        index for index, row in enumerate(all_rows) if row["text"] == "INTRODUCCIÓN"
    )
    rows = all_rows[start:]

    texts_to_translate = [
        str(row["text"])
        for row in rows
        if row["text"]
        and str(row["text"]) not in CHAPTER_TITLES
        and not re.match(r"^Figura\s*\d+", str(row["text"]), re.IGNORECASE)
        and not CODE_PREFIX_RE.match(str(row["text"]))
    ]
    translator = Translator(args.cache)
    translated = translator.translate_batch(texts_to_translate)
    translation_map = dict(zip(texts_to_translate, translated))

    lines = [
        "# Big Data Architecture: Pipeline and Monitoring - Complete Translation",
        "",
        "> Automatically translated paragraph by paragraph from the body of the original Spanish DOCX and then structurally converted to Markdown. The edited chapter edition is available in the parent directory.",
        "",
    ]
    pending_images: list[str] = []
    image_counter = 0
    in_code = False

    def close_code() -> None:
        nonlocal in_code
        if in_code:
            lines.extend(["```", ""])
            in_code = False

    for row in rows:
        text = str(row["text"])
        style = str(row["style"]).lower()
        images = list(row["images"])
        if images:
            close_code()
            pending_images.extend(images)
            continue
        if not text:
            continue

        caption_match = re.match(r"^Figura\s*(\d+)\s*:", text, re.IGNORECASE)
        if caption_match:
            close_code()
            number = int(caption_match.group(1))
            for image in pending_images:
                if image.endswith((".png", ".jpg", ".gif")):
                    alt = CAPTION_TRANSLATIONS.get(number, f"Figure {number}")
                    lines.extend([f"![{alt}](../assets/figures/{image})", ""])
            pending_images.clear()
            caption = CAPTION_TRANSLATIONS.get(number, translation_map.get(text, text))
            lines.extend([f"*Figure {number}. {caption}.*", ""])
            image_counter += 1
            continue

        if text in CHAPTER_TITLES:
            close_code()
            lines.extend([f"## {CHAPTER_TITLES[text]}", ""])
            continue

        translated_text = translation_map.get(text, text)
        if "heading 2" in style:
            close_code()
            lines.extend([f"### {translated_text}", ""])
        elif "heading 3" in style:
            close_code()
            lines.extend([f"#### {translated_text}", ""])
        elif "heading 4" in style:
            close_code()
            lines.extend([f"##### {translated_text}", ""])
        elif "list paragraph" in style:
            close_code()
            lines.append(f"- {translated_text}")
        elif CODE_PREFIX_RE.match(text):
            if not in_code:
                lines.extend(["```text"])
                in_code = True
            lines.append(text)
        else:
            close_code()
            lines.extend([translated_text, ""])

    close_code()
    lines.extend(["[Back to the English edition](../README.md)", ""])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.output}; paragraphs={len(rows)}; numbered_figures={image_counter}")


if __name__ == "__main__":
    main()
