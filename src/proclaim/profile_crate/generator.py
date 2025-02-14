from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, ClassVar

import click
from linkml_runtime.utils.schemaview import SchemaView
from linkml_runtime.dumpers.yaml_dumper import YAMLDumper

from linkml._version import __version__
from linkml.utils.generator import Generator, shared_arguments
from linkml.generators.shaclgen import ShaclGenerator
from proclaim.html.generator import ProfileHtmlGenerator
from rdflib import Graph, Literal, Namespace, PROF, URIRef, BNode
from proclaim.mode.generator import RoCrateModeGenerator
from proclaim.vocabulary import VocabularyHtmlGenerator
from rdfcrate import AttachedCrate, uris, spec_version
from shutil import copy
from typing import TypeVar, ParamSpec

from proclaim.util import mandatory
from logging import getLogger

logger = getLogger(__name__)

#: HTTP version of Schema.org
SDO = Namespace("http://schema.org/")
PROF_ROLES = Namespace("http://www.w3.org/ns/dx/prof/role/")

Ret = TypeVar("Ret")
Params = ParamSpec("Params")
Func = Callable[Params, Ret]
def log_start_end(func: Func) -> Func:
    def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Ret:
        logger.info(f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"Finished {func.__name__}")
        return result
    return wrapper

@dataclass
class ProfileCrateGenerator(Generator):
    """"
    Converts LinkML schema into spec-conformant RO-Crate Profile crate.
    See: https://www.researchobject.org/ro-crate/specification/1.2-DRAFT/profiles.html#profile-crate.
    """
    valid_formats: ClassVar[list[str]] = ["rocrate-profile"]
    uses_schemaloader: ClassVar[bool] = False
    requires_metamodel: ClassVar[bool] = False
    directory_output: bool = True

    @property
    def sv(self) -> SchemaView:
        if self.schemaview is None:
            raise ValueError("Missing schemaview")
        return self.schemaview

    @log_start_end
    def make_vocab(self, directory: Path, crate: AttachedCrate):
        vocab_dir = directory / "vocabulary"
        VocabularyHtmlGenerator(schema=self.schema, site_name=f"{self.schema.name} Vocabulary").serialize(directory=vocab_dir)
        vocab = crate.register_dir(vocab_dir, attrs=[
            (uris.name, Literal("Custom Vocabulary")),
            (uris.description, Literal("Contains markdown and HTML subdirectories")),
        ])
        crate.register_dir(vocab_dir / "html", attrs=[
            (uris.name, Literal("Custom Vocabulary in HTML")),
        ])
        crate.register_dir(vocab_dir / "markdown", attrs=[
            (uris.name, Literal("Custom Vocabulary in markdown")),
        ])
        crate.add_entity(BNode(), [PROF.ResourceDescriptor], attrs=[
            (PROF.hasRole, PROF_ROLES["vocabulary"]),
            (PROF.hasArtifact, vocab)
        ])

    @log_start_end
    def make_shacl(self, directory: Path, crate: AttachedCrate):
        logger.info("(this is fairly slow")
        shacl_path = directory / "shapes.ttl"
        shacl_path.write_text(ShaclGenerator(schema=self.schema, base_dir=str(Path(self.schema.source_file).parent)).serialize())
        shacl = crate.register_file(shacl_path, attrs=[
            (uris.name, Literal("SHACL Shapes")),
            (uris.description, Literal("Provide validation of compliant crates")),
            (uris.conformsTo, URIRef("https://www.w3.org/TR/shacl/"))
        ])
        crate.add_entity(BNode(), [PROF.ResourceDescriptor], attrs=[
            (PROF.hasRole, PROF_ROLES["validation"]),
            (PROF.hasArtifact, shacl)
        ])

    @log_start_end
    def make_linkml(self, directory: Path, crate: AttachedCrate):
        dumper = YAMLDumper()
        linkml_dir = directory / "linkml"
        linkml_dir.mkdir()
        # Copy all LinkML source files to the directory
        for schema_name in self.sv.imports_closure():
            schema = self.sv.schema_map[schema_name]
            # The imported schemas could have used relative paths or full URIs that can't be represented in a flat directory
            # We can only approximate this by taking the path that was used to import the schema, expanding the URI and taking the last element
            # e.g. linkml:types -> types.yml
            # e.g. './schemaorg_current' -> schemaorg_current.yml
            schema_path = Path(self.sv.expand_curie(schema_name)).with_suffix(".yml").name
            dumper.dump(schema, linkml_dir / schema_path)
            # copy(schema.source_file, linkml_dir / schema_path)
        # Make a combined schema
        merged_schema_path = linkml_dir / "merged.yml"
        merged_schema = SchemaView(self.sv.schema)
        merged_schema.merge_imports()
        dumper.dump(merged_schema.schema, str(merged_schema_path))
        linkml = crate.register_dir(linkml_dir, attrs=[
            (uris.name, Literal("LinkML Schemas")),
            (uris.description, Literal("Contains copies of the LinkML schema(s) used to generate the profile."))
        ])
        crate.add_entity(BNode(), [PROF.ResourceDescriptor], attrs=[
            (PROF.hasRole, PROF_ROLES["schema"]),
            (PROF.hasArtifact, linkml)
        ])

    @log_start_end
    def make_mode(self, directory: Path, crate: AttachedCrate):
        logger.info(f"Writing Crate-O Mode File")
        mode_path = directory / "mode.json"
        mode_path.write_text(RoCrateModeGenerator(schema=self.schema).serialize())
        mode = crate.register_file(mode_path, attrs=[
            (uris.name, Literal("Crate-O Mode File")),
            (uris.description, Literal("Provides a schema that can power the Crate-O GUI editor"))
        ])
        crate.add_entity(BNode(), [PROF.ResourceDescriptor], attrs=[
            (PROF.hasRole, PROF_ROLES["schema"]),
            (PROF.hasArtifact, mode)
        ])
        logger.info(f"Finished writing Crate-O Mode File")

    @log_start_end
    def make_docs(self, directory: Path, crate: AttachedCrate):
        # We have to document the index.html file before it's actually created
        # so that it appears in the docs
        index = URIRef("index.html")
        crate.graph.add((index, uris.name, Literal(f"Human readable profile description")))
        crate.graph.add((index, uris.description, Literal(f"Describes the profile in terms of classes and constraints, along with the profile crate's contents")))
        crate.add_entity(BNode(), [PROF.ResourceDescriptor], attrs=[
            (uris.hasRole, PROF_ROLES["specification"]),
            (uris.hasArtifact, index)
        ])
        ProfileHtmlGenerator(schema=self.schema, graph=crate.graph, html_dir=Path(""), markdown_dir=Path(""), site_name=f"{self.schema.name} RO-Crate Profile").serialize(directory=directory)
        index = crate.register_file("index.html")

    def serialize(self, directory: str, **kwargs) -> None:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        # Build up a crate as we create files
        crate = AttachedCrate(
            path=directory,
            name=mandatory(self.sv.schema.name, "A LinkML schema must have a `name` field to be converted to an RO-Crate Profile"),
            description=mandatory(self.sv.schema.description, "A LinkML schema must have a `description` field to be converted to an RO-Crate Profile"),
            license=mandatory(self.sv.schema.license, "A LinkML schema must have a `license` field to be converted to an RO-Crate Profile"),
            version=spec_version.ROCrate1_2
        )

        self.make_vocab(dir_path, crate)
        self.make_shacl(dir_path, crate)
        self.make_mode(dir_path, crate)
        self.make_linkml(dir_path, crate)

        # Document ro-crate-metadata.json
        crate.graph.add((crate.metadata_entity, uris.name, Literal("RO-Crate Metadata File")))
        crate.graph.add((crate.metadata_entity, uris.description, Literal("Describes the profile crate as an RO-Crate itself in JSON-LD format.")))

        self.make_docs(dir_path, crate)

        # RO-Crate Profile
        logger.info(f"Writing ro-crate-metadata.json")
        crate.write()
        logger.info(f"Finished writing ro-crate-metadata.json")

@shared_arguments(ProfileCrateGenerator)
@click.command(name="rocrate-profile")
@click.version_option(__version__, "-V", "--version")
@click.option(
    "--output-dir",
    help=f"Directory into which the RO-Crate Profile will be written",
)
def cli(yamlfile: str, output_dir: Path, **kwargs: Any):
    # getLogger("linkml.utils.generator").setLevel("ERROR")
    ProfileCrateGenerator(yamlfile, base_dir=str(Path(yamlfile).parent)).serialize(str(output_dir), **kwargs)

if __name__ == "__main__":
    cli()
