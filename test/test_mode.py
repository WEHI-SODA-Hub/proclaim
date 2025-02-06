from pathlib import Path
from linkml_runtime.utils.schemaview import SchemaView
from proclaim.mode.generator import RoCrateModeGenerator
import tempfile
import rdflib

from proclaim.profile_crate.generator import ProfileCrateGenerator

def test_mode_file_generation(process_run: str, process_run_sv: SchemaView):
    mode = RoCrateModeGenerator(schema=process_run).make_mode()
    mode_classes = set(mode.classes.keys())
    assert len(mode_classes) == len(process_run_sv.all_class(imports=False))
    assert mode_classes == {'ContainerImage', 'DockerImage', 'SIFImage', 'ParameterConnection'}
    assert "Thing" not in mode_classes, "Schema.org classes should not be included in the mode file"
    assert "MediaObject" not in mode_classes, "Schema.org classes should not be included in the mode file"
    for cname, mode_cls in mode.classes.items():
        assert len(mode_cls.inputs) == len(process_run_sv.class_slots(cname))

def test_profile_generator(process_run: str):
    with tempfile.TemporaryDirectory() as tmpdirname:
        ProfileCrateGenerator(schema=process_run).serialize(directory=tmpdirname)
        tmp_path = Path(tmpdirname)

        # Check that markdown files were generated
        md = list(tmp_path.glob("*.md"))
        assert len(md) > 0

        # Check that SHACL shapes were generated and are parsable
        shacl = tmp_path / "shapes.ttl"
        assert shacl.exists()
        rdflib.Graph().parse(str(shacl), format="turtle")

        # Check that the RO-Crate metadata was generated and is parsable
        metadata_path = tmp_path / "ro-crate-metadata.json"
        assert metadata_path.exists()
        metadata = rdflib.Graph()
        metadata.parse(metadata_path, format="json-ld")
        print(metadata)
