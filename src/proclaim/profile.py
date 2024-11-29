from typing import Any, Optional

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

@dataclass
class ProfileGenerator(Generator):
    pass
