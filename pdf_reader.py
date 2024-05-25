from typing import TypedDict
import pymupdf
from PIL import Image
from io import BytesIO


class PDFMetadata(TypedDict):
    producer: str
    format: str
    encryption: str | None
    author: str | None
    keywords: str
    title: str
    creationDate: str
    modDate: str
    creator: str
    subject: str
    trapped: str


class PDFLink(TypedDict):
    kind: int
    xref: int
    page: int
    to: pymupdf.Point
    zoom: float
    id: str
    rect: pymupdf.Rect
    uri: str


class PDFReader:
    def __init__(self, path: str) -> None:
        self._doc = pymupdf.open(path)

    @property
    def metadata(self) -> PDFMetadata:
        return self._doc.metadata

    @property
    def text(self) -> str:
        def _get_text():
            text = ""
            for page in self._doc:
                text += page.get_text().encode("utf-8").decode("utf-8")
            return text

        return self._get_or_compute("_text", _get_text)

    @property
    def images(self) -> list[Image.Image]:
        def _get_images():
            images = []
            for page in self._doc:
                images.extend(page.get_images())
            result = []
            for img in images:
                xref = img[0]
                pix = self._doc.extract_image(xref)
                pix = pix["image"]
                result.append(Image.open(BytesIO(pix)))
            return result

        return self._get_or_compute("_images", _get_images)

    @property
    def tables(self) -> list:
        def _get_tables():
            tables = []
            for page in self._doc:
                tables.extend(map(lambda x: x.to_pandas(), page.find_tables().tables))
            return tables

        return self._get_or_compute("_tables", _get_tables)

    @property
    def links(self) -> list:
        def _get_links():
            links = []
            for page in self._doc:
                for link in page.links():
                    link["rect"] = link["from"]
                    links.append(link)
            return links

        return self._get_or_compute("_links", _get_links)

    @property
    def annotations(self) -> list:
        def _get_annotations():
            annotations = []
            for page in self._doc:
                annotations.extend(page.annots())
            return annotations

        return self._get_or_compute("_annotations", _get_annotations)

    def _get_or_compute(self, attr: str, method):
        if hasattr(self, attr):
            return getattr(self, attr)
        result = method()
        setattr(self, attr, result)
        return result
