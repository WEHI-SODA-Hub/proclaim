from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any, ClassVar, cast, TypeVar
from packaging.version import parse as parse_version
from linkml_runtime.linkml_model.meta import ElementName

import click
from linkml_runtime.linkml_model.meta import (
    ClassDefinition,
)
from linkml_runtime.utils.schemaview import SchemaView
from linkml_runtime.dumpers.yaml_dumper import YAMLDumper

from linkml._version import __version__
from linkml.utils.generator import Generator, shared_arguments
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.generators.docgen import DocGenerator
from linkml.generators.shaclgen import ShaclGenerator
from proclaim.profile_crate import schema
from rdflib import Graph, Literal, Namespace, RDF, PROF, URIRef, DC, DCTERMS, BNode
from proclaim.mode.generator import RoCrateModeGenerator
from rdfcrate import AttachedCrate, uris, spec_version

# HTTP version of Schema.org
SDO = Namespace("http://schema.org/")

PROF_ROLES = Namespace("http://www.w3.org/ns/dx/prof/role/")

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

    def make_graph(self, directory: Path, sv: SchemaView):
        crate = AttachedCrate(
            path=directory,
            name=mandatory(sv.schema.name, "A LinkML schema must have a `name` field to be converted to an RO-Crate Profile"),
            description=mandatory(sv.schema.description, "A LinkML schema must have a `description` field to be converted to an RO-Crate Profile"),
            license=mandatory(sv.schema.license, "A LinkML schema must have a `license` field to be converted to an RO-Crate Profile"),
            version=spec_version.ROCrate1_1
        )

        index = crate.register_file("index.html", attrs=[
            (uris.name, Literal(f"Human readable profile description"))
        ])
        crate.add_entity(BNode(), [PROF.ResourceDescriptor], attrs=[
            (uris.hasRole, PROF_ROLES["specification"]),
            (uris.hasArtifact, index)
        ])

        shacl = crate.register_file("shapes.ttl", attrs=[
            (uris.name, Literal("SHACL Shapes")),
            (uris.description, Literal("Provide validation of compliant crates")),
            (uris.conformsTo, URIRef("https://www.w3.org/TR/shacl/"))
        ])
        crate.add_entity(BNode(), [PROF.ResourceDescriptor], attrs=[
            (PROF.hasRole, PROF_ROLES["validation"]),
            (PROF.hasArtifact, shacl)
        ])

        linkml = crate.register_file("linkml.yml", attrs=[
            (uris.name, Literal("LinkML Schema"))
        ])
        crate.add_entity(BNode(), [PROF.ResourceDescriptor], attrs=[
            (PROF.hasRole, PROF_ROLES["schema"]),
            (PROF.hasArtifact, linkml)
        ])

        mode = crate.register_file("mode.json", attrs=[
            (uris.name, Literal("Crate-O Mode File"))
        ])
        crate.add_entity(BNode(), [PROF.ResourceDescriptor], attrs=[
            (PROF.hasRole, PROF_ROLES["mode"]),
            (PROF.hasArtifact, mode)
        ])

        crate.write()

    def make_html(self, directory: str) -> str:
        # Build markdown into docs directory
        gen = DocGenerator(schema=self.schema, directory=directory)
        gen.serialize()

        

    def serialize(self, directory: str, **kwargs) -> None:
        dir_path = Path(directory)
        crate_path = dir_path / "crate"

        # Docs
        DocGenerator(schema=self.schema, directory=directory).serialize()
        # TODO: Compile to HTML

        # SHACL
        shacl = dir_path / "shapes.ttl"
        shacl.write_text(ShaclGenerator(schema=self.schema).serialize())

        # LinkML
        sv = SchemaView(self.schema)
        linkml_schema = dir_path / "linkml.yml"
        YAMLDumper().dump(sv.schema, linkml_schema)

        # Mode File
        mode = dir_path / "mode.json"
        mode.write_text(RoCrateModeGenerator(schema=self.schema).serialize())

        # RO-Crate Profile
        self.make_graph(dir_path, sv)

@shared_arguments(ProfileCrateGenerator)
@click.command(name="rocrate-profile")
@click.version_option(__version__, "-V", "--version")
@click.option(
    "--output-dir",
    help=f"Directory into which the RO-Crate Profile will be written",
)
def cli(yamlfile: str, output_dir: Path, **kwargs: Any):
    print(ProfileCrateGenerator(yamlfile).serialize(str(output_dir), **kwargs))

if __name__ == "__main__":
    cli()
