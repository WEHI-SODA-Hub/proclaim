from abc import abstractmethod, ABC
from dataclasses import dataclass, fields
from importlib.abc import Traversable
from pathlib import Path
from typing import Any, Callable, ClassVar

from linkml._version import __version__
from linkml.utils.generator import Generator
import tempfile
from mkdocs.commands.build import build
from mkdocs.config import load_config
from jinja2 import Environment, select_autoescape
from shutil import copytree
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SchemaDefinition
import os

from proclaim.util import mandatory, description, domain, remove_newlines

@dataclass
class MkDocsGenerator(Generator, ABC):
    """"
    Abstract class for generating documentation using MkDocs from a LinkML schema
    """
    markdown_dir: Path  = Path("markdown")
    "A path *relative* to the output directory where the markdown files will be written."
    html_dir: Path = Path("html")
    "A path *relative* to the output directory where the HTML files will be written."
    valid_formats: ClassVar[list[str]] = ["html"]

    site_name: str | None = None

    # Without this, the relative imports are broken
    uses_schemaloader: ClassVar[bool] = False

    def __post_init__(self):
        super().__post_init__()
        if self.site_name is None and isinstance(self.schema, SchemaDefinition):
            self.site_name = self.schema.name

    def to_markdown(self, template_path: Traversable, **kwargs: Any) -> str:
        """
        Params:
            template_path: Path to the Jinja2 template to render
            **kwargs: Additional keyword arguments to pass to `template.render()`
        """
        environment = Environment(
            autoescape=select_autoescape(),
            trim_blocks=True,
            keep_trailing_newline=False,
            lstrip_blocks=True,
        )
        environment.globals.update(self.get_globals())
        environment.shared = True
        environment.filters.update(self.get_filters())
        template = environment.from_string(
            template_path.read_text()
        )
        return template.render(sv=self.schemaview, **kwargs)

    def get_globals(self) -> dict[str, Any]:
        """
        Override this method to add additional global variables to the Jinja2 environment
        """
        return {field.name: getattr(self, field.name) for field in fields(self)}

    def get_filters(self) -> dict[str, Callable]:
        """
        Can be overridden to add additional Jinja2 filters
        """
        return {
            "mandatory": mandatory,
            "description": description,
            "domain": domain,
            "remove_newlines": remove_newlines
        }

    def write_markdown(self, output_path: Path, template_path: Traversable, **kwargs: Any) -> None:
        """
        Renders a template to markdown and writes it to a file
        """
        output_path.write_text(self.to_markdown(template_path, **kwargs))

    @abstractmethod
    def make_markdown(self, markdown_dir: Path, sv: SchemaView) -> None:
        """
        User should implement this method to generate markdown files using `self.write_markdown()`
        """
        ...

    def serialize(self, directory: str, *, config: dict = {}, **kwargs) -> None:
        # Get the schema view
        sv = self.schemaview
        if sv is None:
            raise Exception("Missing schema")

        # Build everything in a temporary directory first
        # This lets the directory layout be more flexible than mkdocs would overwise allow
        with tempfile.TemporaryDirectory() as _tmp:
            tmp = Path(_tmp)
            tmp_markdown_dir = tmp / "docs"
            tmp_markdown_dir.mkdir()
            tmp_html_dir = tmp / "site"

            # Run the build
            (tmp / "mkdocs.yml").touch()
            self.make_markdown(tmp_markdown_dir, sv)
            wd = os.getcwd()
            os.chdir(tmp)
            build(load_config(**config, site_name=self.site_name, markdown_extensions=["tables"], site_dir=str(tmp_html_dir), docs_dir=str(tmp_markdown_dir)))
            os.chdir(wd)

            # Setup result directory
            root = Path(directory)
            root.mkdir(parents=True, exist_ok=True)
            markdown_dir = Path(directory) / self.markdown_dir
            # markdown_dir.mkdir(exist_ok=True)
            html_dir = Path(directory) / self.html_dir
            # html_dir.mkdir(exist_ok=True)

            # Copy results
            copytree(tmp_markdown_dir, markdown_dir, dirs_exist_ok=True)
            copytree(tmp_html_dir, html_dir, dirs_exist_ok=True)
