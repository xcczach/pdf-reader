from typing import TypedDict


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
        pass

    @property
    def metadata(self) -> PDFMetadata:
        pass

    @property
    def text(self) -> str:
        pass

    @property
    def images(self) -> list:
        pass

    @property
    def tables(self) -> list:
        pass

    @property
    def links(self) -> list:
        pass

    @property
    def annotations(self) -> list:
        pass
