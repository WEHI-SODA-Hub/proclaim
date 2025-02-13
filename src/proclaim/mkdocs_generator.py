from abc import abstractmethod, ABC
from dataclasses import dataclass, fields, asdict
from importlib.abc import Traversable
from pathlib import Path
from typing import Any, Callable, ClassVar
import contextlib

from linkml._version import __version__
from linkml.utils.generator import Generator
import tempfile
from mkdocs.commands.build import build
from mkdocs.config import load_config
from jinja2 import Environment, PackageLoader, Template, select_autoescape
from jinja2.environment import get_spontaneous_environment
from shutil import copytree, copy
from linkml_runtime import SchemaView

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

    # Without this, the relative imports are broken
    uses_schemaloader: ClassVar[bool] = False

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
        # env = Environment(
        #     loader=PackageLoader(self.__module__),
        #     autoescape=select_autoescape(),
        #     trim_blocks=True,
        #     keep_trailing_newline=False,
        #     lstrip_blocks=True
        # )
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
        root = Path(directory)
        root.mkdir(parents=True, exist_ok=True)
        sv = self.schemaview
        if sv is None:
            raise Exception("Missing schema")
        (root / "mkdocs.yml").touch()
        markdown_dir = Path(directory) / self.markdown_dir
        markdown_dir.mkdir(exist_ok=True)
        self.make_markdown(markdown_dir, sv)
        html_dir = Path(directory) / self.html_dir
        html_dir.mkdir(exist_ok=True)
        with contextlib.chdir(directory):
            build(load_config(**config, site_name=self.schema.name, markdown_extensions=["tables"], site_dir=str(html_dir), docs_dir=str(markdown_dir)))
