from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
import contextlib

from linkml_runtime.utils.schemaview import SchemaView

from linkml._version import __version__
from linkml.utils.generator import Generator
import tempfile
from mkdocs.commands.build import build
from mkdocs.config import load_config
from jinja2 import Environment, PackageLoader, select_autoescape

from proclaim.util import mandatory, description

@dataclass
class ProfileHtmlGenerator(Generator):
    """"
    Converts LinkML schema into a single page HTML document for use in an RO-Crate Profile crate.
    """
    valid_formats: ClassVar[list[str]] = ["html"]
    # mkdocs_config: MkDocsConfig = field(default_factory=lambda: load_config())

    def to_markdown(self) -> str:
        env = Environment(
            loader=PackageLoader(__name__),
            autoescape=select_autoescape(),
            trim_blocks=True,
            keep_trailing_newline=False,
            lstrip_blocks=True
        )
        env.filters["mandatory"] = mandatory
        env.filters["description"] = description
        template = env.get_template("profile.jinja2")
        sv = SchemaView(self.schema)
        return template.render(sv=sv)

    def serialize(self, directory: str, *, config: dict = {}, **kwargs) -> None:
        with tempfile.TemporaryDirectory() as _build_dir:
            with contextlib.chdir(_build_dir):
                build_dir = Path(_build_dir)
                (build_dir / "mkdocs.yml").touch()
                docs = build_dir / "docs"
                docs.mkdir()
                (docs / "index.md").write_text(self.to_markdown())
                build(load_config(**config, site_name=self.schema.name, markdown_extensions=["tables"], site_dir=directory))
