#!/usr/bin/env python3
"""Extract embedded DOCX images and write a reproducible asset manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.oxml.ns import qn
from PIL import Image


VML_IMAGE_DATA = "{urn:schemas-microsoft-com:vml}imagedata"


def natural_media_key(path: str) -> tuple[int, str]:
    match = re.search(r"(\d+)$", Path(path).stem)
    return (int(match.group(1)) if match else 0, path)


def paragraph_image_references(doc: Document) -> dict[str, list[int]]:
    references: dict[str, list[int]] = {}
    for paragraph_index, paragraph in enumerate(doc.paragraphs):
        for element in paragraph._p.iter():
            relationship_id = None
            if element.tag == qn("a:blip"):
                relationship_id = element.get(qn("r:embed")) or element.get(
                    qn("r:link")
                )
            elif element.tag == VML_IMAGE_DATA:
                relationship_id = element.get(qn("r:id"))

            if relationship_id and relationship_id in doc.part.rels:
                target = os.path.basename(doc.part.rels[relationship_id].target_ref)
                references.setdefault(target, []).append(paragraph_index)
    return references


def image_metadata(data: bytes) -> dict[str, object]:
    try:
        with Image.open(BytesIO(data)) as image:
            return {
                "format": image.format,
                "width_px": image.width,
                "height_px": image.height,
            }
    except Exception:
        return {"format": None, "width_px": None, "height_px": None}


def extract(docx_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    doc = Document(docx_path)
    references = paragraph_image_references(doc)

    manifest: dict[str, object] = {
        "source": docx_path.name,
        "assets": [],
    }

    with ZipFile(docx_path) as archive:
        media_paths = sorted(
            (
                name
                for name in archive.namelist()
                if name.startswith("word/media/") and not name.endswith("/")
            ),
            key=natural_media_key,
        )

        for sequence, media_path in enumerate(media_paths, start=1):
            data = archive.read(media_path)
            original_name = Path(media_path).name
            suffix = Path(original_name).suffix.lower()
            output_name = f"source-image-{sequence:03d}{suffix}"
            (output_dir / output_name).write_bytes(data)

            metadata = image_metadata(data)
            manifest["assets"].append(
                {
                    "sequence": sequence,
                    "file": output_name,
                    "docx_media_name": original_name,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data),
                    "paragraph_indices": references.get(original_name, []),
                    **metadata,
                }
            )

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    extension_counts = Counter(
        Path(asset["file"]).suffix for asset in manifest["assets"]
    )
    print(f"Extracted {len(manifest['assets'])} assets to {output_dir}")
    print(f"Formats: {dict(sorted(extension_counts.items()))}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    extract(args.docx.resolve(), args.output_dir.resolve())


if __name__ == "__main__":
    main()
