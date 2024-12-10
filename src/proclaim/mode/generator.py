from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union, ClassVar

import click
from linkml_runtime.linkml_model.meta import (
    ClassDefinition,
    SlotDefinition,
)
from linkml_runtime.utils.schemaview import SchemaView

from linkml._version import __version__
from linkml.utils.generator import Generator, shared_arguments

import proclaim.mode.schema as mode

def fail_unless[T](x: T | None, msg: str) -> T:
    if x is None:
        raise ValueError(f"{msg} must be specified to be compatible with the mode file generator")
    return x

def convert_class(cls: ClassDefinition, sv: SchemaView) -> mode.Class:
    """
    Converts a LinkML class definition into a mode file class definition
    """
    parents: list[str] = []
    if isinstance(cls.subclass_of, str):
        parents.append(cls.subclass_of)
    elif isinstance(cls.subclass_of, list):
        parents += cls.subclass_of

    return mode.Class(
        id=cls.class_uri,
        subClassOf=parents,
        hasSubclass=None,
        # At this stage we have no inputs, but this will get filled in by visit_class_slot
        inputs = [ convert_slot(sv.get_slot(slot_name)) for slot_name in sv.class_slots() ]
    )

def convert_slot(slot: SlotDefinition) -> mode.Input:
    """
    Converts a LinkML slot into a mode file input definition
    """
    from linkml_runtime.utils.metamodelcore import Bool

    if slot.slot_uri is None:
        raise Exception("Each slot must have an IRI in order to convert to a mode file")
    return mode.Input(
        id=slot.slot_uri,
        name=slot.name,
        label=slot.title,
        multiple=Bool(slot.multivalued or False),
        required=Bool(slot.required or False),
        group=slot.slot_group,
        readonly=slot.readonly is not None,
        type=None if slot.range is None else [str(slot.range)]
    )

@dataclass
class RoCrateModeGenerator(Generator):
    visit_all_class_slots: ClassVar[bool] = True
    valid_formats: ClassVar[list[str]] = ["crateo-mode"]
    uses_schemaloader: ClassVar[bool] = False
    requires_metamodel: ClassVar[bool] = False

    mode_file_template: Path | None = None
    # mode_file: mode.ModeFile | None = None
    # name: str | None = None
    # description: str | None = None
    # version: float | None = None
    # classes: mode.Classes = field(default_factory=dict)
    # lookup: mode.Lookups = None
    # context: mode.Context = None
    # input_groups: mode.InputGroups = None
    # resolve: mode.Resolve = None

    # def __post_init__(self) -> None:
    #     self.schemaview = SchemaView(self.schema)

    def serialize(self, **kwargs) -> str:
        sv = SchemaView(self.schema)
        mode_file = mode.ModeFile(
            metadata=mode.Metadata(
                name=fail_unless(sv.schema.name, "name"),
                description=fail_unless(sv.schema.description, "description"),
                version=float(fail_unless(sv.schema.version, "version"))
            ),
            classes={
                key: convert_class(value, sv) for key, value in sv.all_classes().items()
            },
        )
        return mode_file.model_dump_json()


    # def visit_schema(self, **kwargs) -> Optional[str]:
    #     """Visited once at the beginning of generation

    #     @param kwargs: Arguments passed through from CLI -- implementation dependent
    #     """
    #     self.schema
    #     if self.name is None:
    #         raise Exception("The name field, which is mandatory, is missing")
    #     if self.version is None:
    #         raise Exception("The version field is mandatory")
    #     if self.description is None:
    #         raise Exception("The description field is mandatory")

    #     self.mode_file = mode.ModeFile(metadata=mode.Metadata(name=self.name, description=self.description, version=self.version), classes=self.classes, lookup=self.lookup, context=self.context, inputGroups=self.input_groups, resolve=self.resolve)

    # def end_schema(self, **kwargs) -> Optional[str]:
    #     """Visited once at the end of generation

    #     @param kwargs: Arguments passed through from CLI -- implementation dependent
    #     """
    #     if self.mode_file is not None:
    #         return self.mode_file.model_dump_json()


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
