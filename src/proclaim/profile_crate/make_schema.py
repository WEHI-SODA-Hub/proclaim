"""
Script to generate the LinkML models using only the relevant subset of Schema.org models needed to create a profile crate.
"""

from linkml_runtime import SchemaView
from linkml.utils.schema_builder import SchemaBuilder
from dataclasses import dataclass, field, replace
from linkml.generators.pydanticgen import PydanticGenerator
from pathlib import Path
from linkml_runtime.dumpers import YAMLDumper


@dataclass
class ImportSpec:
    schema: str
    classes: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)
    types: list[str] = field(default_factory=list)


def compile_schema(builder: SchemaBuilder, specs: list[ImportSpec]):
    """
    Compile the LinkML schema from the given list of ImportSpec objects.
    """
    for spec in specs:
        sv = SchemaView(spec.schema)
        for typename in spec.types:
            builder.add_type(sv.get_type(typename, strict=True))
        for classname in spec.classes:
            cls = sv.get_class(classname, strict=True)
            if cls.is_a not in spec.classes:
                cls.is_a = None
            # for parent in sv.class_parents(classname):
            #     if parent not in spec.classes:
            #         implicit_classes.add(parent)
            builder.add_class(replace(
                cls,
                # Only use slots that we are interested in
                slots = list(set(cls.slots).intersection(set(spec.properties)))
            ))
        for prop in spec.properties:
            builder.add_slot(sv.get_slot(prop, strict=True))


sb = SchemaBuilder(name="RoCrateProfile")
compile_schema(
    sb,
    [
        ImportSpec(
            # schema="https://multimeric.github.io/cordful/models/sdo/schemaorg-current-https.yaml",
            schema="/Users/milton.m/Programming/ProfLinkMl/models/sdo/schemaorg-current-https.yaml",
            classes=[
                # CreativeWork Profile
                "CreativeWork",
                "Dataset",
                "MediaObject",
                "DataDownload",
                # "DefinedTerm", "ResourceRole",
                "DefinedTerm",
                "SoftwareApplication",
                "DefinedTermSet",
                "Thing"
            ],
            properties=[
                "about",
                "name",
                "version",
                "hasPart",
                "encodingFormat",
                "distribution",
                "url",
                "termCode",
            ],
            types=[
                "Text",
                "URL"
            ]
        ),
        ImportSpec(
            schema="https://multimeric.github.io/cordful/models/prof/prof.yaml",
            classes=["Profile", "ResourceDescriptor", "ResourceRole", "Standard", "Concept"],
            properties=[
                "hasResource",
                "isProfileOf",
                "hasArtifact",
                "hasRole",
            ],
        ),
        ImportSpec(
            schema="https://multimeric.github.io/cordful/models/dc/dublin_core_terms.yaml",
            properties=["conformsTo"],
        ),
        ImportSpec(
            schema="https://multimeric.github.io/cordful/models/pcdm/models.yaml",
            classes=["Collection"],
        ),
    ],
)

# Add the RO-Crate File alias
sb.add_class(
    replace(sb.schema.classes["MediaObject"], name="File")
)
x = YAMLDumper().dumps(sb.schema)

sb.schema
(Path(__file__).parent / "schema.py").write_text(
    PydanticGenerator(sb.schema).serialize()
)
