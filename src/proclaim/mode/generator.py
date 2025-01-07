from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, cast
from packaging.version import parse as parse_version
from linkml_runtime.linkml_model.meta import ElementName

import click
from linkml_runtime.linkml_model.meta import (
    ClassDefinition,
)
from linkml_runtime.utils.schemaview import SchemaView

from linkml._version import __version__
from linkml.utils.generator import Generator, shared_arguments
from linkml.generators.jsonldcontextgen import ContextGenerator
import json

import proclaim.mode.schema as mode

def fail_unless[T](x: T | None, msg: str) -> T:
    if x is None:
        raise ValueError(f"{msg} must be specified in the LinkML schema to be compatible with the mode file generator")
    return x

def convert_class(cls: ClassDefinition, sv: SchemaView) -> mode.Class:
    """
    Converts a LinkML class definition into a mode file class definition
    """
    return mode.Class(
        id=sv.get_uri(cast(ElementName, cls.name), expand=True),
        subClassOf=[str(cls) for cls in sv.class_parents(cls.name)],
        hasSubclass=[str(cls) for cls in sv.class_children(cls.name)],
        # At this stage we have no inputs, but this will get filled in by visit_class_slot
        inputs = [ convert_slot(slot_name, sv) for slot_name in sv.class_slots(cls.name) ]
    )

def convert_slot(slot_name: str, sv: SchemaView) -> mode.Input:
    """
    Converts a LinkML slot into a mode file input definition
    """
    from linkml_runtime.utils.metamodelcore import Bool

    slot = sv.get_slot(slot_name)

    if slot.slot_uri is None:
        raise Exception("Each slot must have an IRI in order to convert to a mode file")

    description = slot.description
    if description is None:
        if isinstance(slot.comments, str):
            description = slot.comments
        elif isinstance(slot.comments, list):
            description = "\n".join(slot.comments)

    return mode.Input(
        id=sv.get_uri(cast(ElementName, slot.name), expand=True),
        name=slot.name,
        label=slot.name,
        help=fail_unless(description, "slot description or comments"),
        multiple=Bool(slot.multivalued or False),
        required=Bool(slot.required or False),
        hide=False,
        group=slot.slot_group,
        readonly=slot.readonly is not None,
        type=None if slot.range is None else [str(slot.range)]
    )

@dataclass
class RoCrateModeGenerator(Generator):
    """"
    Converts LinkML schema into a Crate-O compatible mode file
    """
    visit_all_class_slots: ClassVar[bool] = True
    valid_formats: ClassVar[list[str]] = ["crateo-mode"]
    uses_schemaloader: ClassVar[bool] = False
    requires_metamodel: ClassVar[bool] = False

    mode_file_template: Path | None = None

    def make_mode(self) -> mode.ModeFile:
        sv = SchemaView(self.schema)
        # parse version
        version = parse_version(fail_unless(sv.schema.version, "version"))
        return mode.ModeFile(
            metadata=mode.Metadata(
                name=fail_unless(sv.schema.name, "name"),
                description=fail_unless(sv.schema.description, "description"),
                # Approximate the version as a float, e.g. 1.2.3 -> 1.23
                version=float(f"{version.major}.{version.minor}{version.micro}"),
                license=fail_unless(sv.schema.license, "license"),
                author=fail_unless(sv.schema.created_by, "created_by"),
            ),
            classes={
                key: convert_class(value, sv) for key, value in sv.all_classes().items()
            },
            context=json.loads(ContextGenerator(schema=sv.schema).serialize())
        )

    def serialize(self, **kwargs) -> str:
        return self.make_mode().model_dump_json(indent=4)

@shared_arguments(RoCrateModeGenerator)
@click.command(name="crato-mode")
@click.option(
    "--mode-template",
    help=f"JSON mode file to merge with the generated output",
)
@click.version_option(__version__, "-V", "--version")
def cli(yamlfile: str, mode_template: Path, **kwargs: Any):
    print(RoCrateModeGenerator(yamlfile, mode_file_template=mode_template, **kwargs).serialize(**kwargs))

if __name__ == "__main__":
    cli()
