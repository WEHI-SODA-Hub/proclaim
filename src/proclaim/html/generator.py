from dataclasses import dataclass
from importlib.abc import Traversable
from pathlib import Path
from importlib.resources import files
from typing import Any
from linkml_runtime import SchemaView

from linkml._version import __version__
from rdflib import Graph

from proclaim.mkdocs_generator import MkDocsGenerator
from rdfcrate import uris
import rdflib


@dataclass
class ProfileHtmlGenerator(MkDocsGenerator):
    """"
    Converts LinkML schema into a single page HTML document that describes the profile
    """
    graph: Graph = Graph()
    template_path: Traversable = files("proclaim.html") / "profile.jinja2"

    def get_globals(self) -> dict[str, Any]:
        return {
            **super().get_globals(),
            "uris": uris,
            "rdflib": rdflib
        }

    def make_markdown(self, markdown_dir: Path, sv: SchemaView) -> None:
        self.write_markdown(markdown_dir / "index.md", self.template_path)
