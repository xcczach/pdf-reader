from typing import TypedDict
import pymupdf
from PIL import Image


class PDFMetadata(TypedDict):
    producer: str
    format: str
    encryption: str | None
    author: str | None
    mod_data: str
    keywords: str
    title: str
    creation_date: str
    creator: str
    subject: str


class PDFReader:
    def __init__(self, path: str) -> None:
        self.doc = pymupdf.open(path)

    @property
    def metadata(self) -> PDFMetadata:
        pass

    @property
    def text(self) -> str:
        return self._get_or_compute("_text", lambda: self.doc.get_text())

    @property
    def images(self) -> list[Image.Image]:
        def _get_images():
            images = []
            for page in self.doc:
                images.extend(page.get_images())
            result = []
            for img in images:
                xref = img[0]
                pix = pymupdf.Pixmap(self.doc, xref)
                if pix.n - pix.alpha > 3:
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                result.append(
                    Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                )
            return result

        return self._get_or_compute("_images", _get_images)

    @property
    def tables(self) -> list:
        def _get_tables():
            tables = []
            for page in self.doc:
                tables.extend(map(lambda x: x.to_pandas(), page.find_tables().tables))
            return tables

        return self._get_or_compute("_tables", _get_tables)

    @property
    def links(self) -> list:
        def _get_links():
            links = []
            for page in self.doc:
                link = page.first_link
                while link:
                    links.append(link)
                    link = link.next
            return links

        return self._get_or_compute("_links", _get_links)

    @property
    def annotations(self) -> list:
        def _get_annotations():
            annotations = []
            for page in self.doc:
                annotations.extend(page.annots())
            return annotations

        return self._get_or_compute("_annotations", _get_annotations)

    def _get_or_compute(self, attr: str, method):
        if hasattr(self, attr):
            return getattr(self, attr)
        result = method()
        setattr(self, attr, result)
        return result
