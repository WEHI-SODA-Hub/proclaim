from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

import click
from linkml_runtime.utils.schemaview import SchemaView
from linkml_runtime.dumpers.yaml_dumper import YAMLDumper

from linkml._version import __version__
from linkml.utils.generator import Generator, shared_arguments
from linkml.generators.shaclgen import ShaclGenerator
from proclaim.html.generator import ProfileHtmlGenerator
from rdflib import Literal, Namespace, PROF, URIRef, BNode
from proclaim.mode.generator import RoCrateModeGenerator
from rdfcrate import AttachedCrate, uris, spec_version

from proclaim.util import mandatory
from logging import getLogger

logger = getLogger(__name__)

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
            version=spec_version.ROCrate1_2
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

    def serialize(self, directory: str, **kwargs) -> None:
        dir_path = Path(directory)
        base_dir = str(Path(self.schema.source_file).parent)

        # Docs
        logger.info(f"Writing HTML")
        ProfileHtmlGenerator(schema=self.schema).serialize(directory=directory)
        logger.info(f"Finished writing HTML")

        # SHACL
        logger.info(f"Writing SHACL (this takes a while)")
        shacl = dir_path / "shapes.ttl"
        shacl.write_text(ShaclGenerator(schema=self.schema, base_dir=base_dir).serialize())
        logger.info(f"Finished writing SHACL")

        # LinkML
        logger.info(f"Writing LinkML")
        sv = SchemaView(self.schema)
        linkml_schema = dir_path / "linkml.yml"
        YAMLDumper().dump(sv.schema, linkml_schema)
        logger.info(f"Finished writing LinkML")

        # Mode File
        logger.info(f"Writing Crate-O Mode File")
        mode = dir_path / "mode.json"
        mode.write_text(RoCrateModeGenerator(schema=self.schema, base_dir=base_dir).serialize())
        logger.info(f"Finished writing Crate-O Mode File")

        # RO-Crate Profile
        logger.info(f"Writing ro-crate-metadata.json")
        self.make_graph(dir_path, sv)
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
