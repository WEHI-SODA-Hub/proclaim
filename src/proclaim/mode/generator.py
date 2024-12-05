from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union, ClassVar

import click
from jsonasobj2 import as_json, items, loads
from linkml_runtime.linkml_model.meta import (
    ClassDefinition,
    ClassDefinitionName,
    ElementName,
    SchemaDefinition,
    SlotDefinition,
    SlotDefinitionName,
    SubsetDefinition,
    SubsetDefinitionName,
    TypeDefinition,
    TypeDefinitionName,
)
from linkml_runtime.utils.formatutils import camelcase, underscore
from linkml_runtime.utils.yamlutils import YAMLRoot

from linkml import METAMODEL_CONTEXT_URI
from linkml._version import __version__
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml.utils.generator import Generator, shared_arguments

import proclaim.mode.schema as mode

@dataclass
class RoCrateModeGenerator(Generator):
    visit_all_class_slots: ClassVar[bool] = True

    mode_file_template: Path | None = None
    mode_file: mode.ModeFile | None = None
    name: str | None = None
    description: str | None = None
    version: float | None = None
    classes: mode.Classes = {}
    lookup: mode.Lookups = {}
    context: mode.Context=[]
    input_groups: mode.InputGroups=[]
    resolve: mode.Resolve = []

    def visit_schema(self, **kwargs) -> Optional[str]:
        """Visited once at the beginning of generation

        @param kwargs: Arguments passed through from CLI -- implementation dependent
        """
        if self.name is None:
            raise Exception()
        if self.version is None:
            raise Exception()
        if self.description is None:
            raise Exception()

        self.mode_file = mode.ModeFile(metadata=mode.Metadata(name=self.name, description=self.description, version=self.version), classes=self.classes, lookup=self.lookup, context=self.context, inputGroups=self.input_groups, resolve=self.resolve)

    def end_schema(self, **kwargs) -> Optional[str]:
        """Visited once at the end of generation

        @param kwargs: Arguments passed through from CLI -- implementation dependent
        """
        if self.mode_file is not None:
            return self.mode_file.model_dump_json()

    def visit_class(self, cls: ClassDefinition) -> Optional[Union[str, bool]]:
        """Visited once per schema class

        @param cls: class being visited
        @return: Visit slots and end class.  False means skip and go on
        """
        parents: list[str] = []
        if isinstance(cls.subclass_of, str):
            parents.append(cls.subclass_of)
        elif isinstance(cls.subclass_of, list):
            parents += cls.subclass_of

        self.classes[cls.name] = mode.Class(
            id=cls.class_uri,
            subClassOf=parents,
            hasSubclass=None,
            # At this stage we have no inputs, but this will get filled in by visit_class_slot
            inputs = []
        )
        return True

    def visit_class_slot(self, cls: ClassDefinition, aliased_slot_name: str, slot: SlotDefinition) -> Optional[str]:
        """Visited for each slot in a class.  If class level visit_all_slots is true, this is visited once
        for any class that is inherited (class itself, is_a, mixin, apply_to).  Otherwise, just the own slots.

        @param cls: containing class
        @param aliased_slot_name: Aliased slot name.  May not be unique across all class slots
        @param slot: being visited
        """
        from linkml_runtime.utils.metamodelcore import Bool

        current_class = self.classes[cls.name]
        if slot.slot_uri is None:
            raise Exception("Each slot must have an IRI in order to convert to a mode file")
        current_class.inputs.append(mode.Input(
            id=slot.slot_uri,
            name=slot.name,
            label=slot.title,
            multiple=Bool(slot.multivalued or False),
            required=Bool(slot.required or False),
            group=slot.slot_group,
            readonly=slot.readonly is not None,
            type=None if slot.range is None else [str(slot.range)]
        ))
