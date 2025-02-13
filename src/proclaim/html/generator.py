from dataclasses import dataclass
from importlib.resources.abc import Traversable
from pathlib import Path
from importlib.resources import files
from typing import Callable
from linkml_runtime import SchemaView

from linkml._version import __version__
from rdflib import Graph

from proclaim.mkdocs_generator import MkDocsGenerator
from proclaim.util import file_description


@dataclass
class ProfileHtmlGenerator(MkDocsGenerator):
    """"
    Converts LinkML schema into a single page HTML document that describes the profile
    """
    graph: Graph = Graph()
    template_path: Traversable = files(__name__) / "profile.jinja2"

    def get_filters(self) -> dict[str, Callable]:
        return {
            **super().get_filters(),
            "file_description": file_description,
        }

    def make_markdown(self, markdown_dir: Path, sv: SchemaView) -> None:
        self.write_markdown(markdown_dir / "index.md", self.template_path)
