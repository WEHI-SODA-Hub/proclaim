from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
import contextlib

from linkml._version import __version__
from linkml.utils.generator import Generator
import tempfile
from linkml_runtime import SchemaView
from mkdocs.commands.build import build
from mkdocs.config import load_config
from jinja2 import Environment, PackageLoader, select_autoescape

from proclaim.util import mandatory, description, domain, remove_newlines

@dataclass
class ProfileHtmlGenerator(Generator):
    """"
    Converts LinkML schema into a single page HTML document that describes the unique vocabulary terms in the schema
    """
    valid_formats: ClassVar[list[str]] = ["html"]

    # Without this, the relative imports are broken
    uses_schemaloader: ClassVar[bool] = False

    # def __post_init__(self):
    #     # The default schemaview is cooked. It seems to set the wrong base path, so all imports from it fail
    #     # Thus, we replace it with a working SchemaView here
    #     if isinstance(self.schema, (str, Path)):
    #         schema_path = Path(self.schema)
    #     else:
    #         schema_path = Path(self.schema.source_file)
    #     with contextlib.chdir(schema_path.parent):
    #         self.schemaview = SchemaView(self.schema)
    #         self.schemaview.imports_closure()
    #     super().__post_init__()

    def to_markdown(self, template: str, **kwargs) -> str:
        env = Environment(
            loader=PackageLoader(__name__),
            autoescape=select_autoescape(),
            trim_blocks=True,
            keep_trailing_newline=False,
            lstrip_blocks=True
        )
        env.filters.update({
            "mandatory": mandatory,
            "description": description,
            "domain": domain,
            "remove_newlines": remove_newlines
        })
        template = env.get_template(template)
        return template.render(sv=self.schemaview, **kwargs)

    def serialize(self, directory: str, *, config: dict = {}, **kwargs) -> None:
        with tempfile.TemporaryDirectory() as _build_dir:
            build_dir = Path(_build_dir)
            (build_dir / "mkdocs.yml").touch()
            docs = build_dir / "docs"
            docs.mkdir()

            # The index page describes the profile in an RO-Crate way
            (docs / "index.md").write_text(self.to_markdown("profile.jinja2"))

            # The properties and classes pages are more like vocabularies, with the intention that 
            # the respective property and class IRIs should resolve there
            properties = docs / "properties"
            properties.mkdir()
            # Don't render slots that are imported from other schemas
            for sname, slot in self.schemaview.all_slots(imports=False).items():
                md = self.to_markdown("property.jinja2", slot=slot, sname=sname)
                (properties / f"{sname}.md").write_text(md)

            classes = docs / "classes"
            classes.mkdir()
            for cname, cls in self.schemaview.all_classes(imports=False).items():
                md = self.to_markdown("class.jinja2", cls=cls, cname=cname)
                (classes / f"{cname}.md").write_text(md)

            with contextlib.chdir(_build_dir):
                build(load_config(**config, site_name=self.schema.name, markdown_extensions=["tables"], site_dir=directory))
