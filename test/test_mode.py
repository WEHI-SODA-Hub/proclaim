from linkml_runtime.utils.schemaview import SchemaView
from proclaim.mode.generator import RoCrateModeGenerator


def test_mode_file_generation(process_run: str, process_run_sv: SchemaView):
    mode = RoCrateModeGenerator(schema=process_run).make_mode()
    mode_classes = set(mode.classes.keys())
    assert len(mode_classes) == len(process_run_sv.all_class(imports=False))
    assert mode_classes == {'ContainerImage', 'DockerImage', 'SIFImage', 'ParameterConnection'}
    assert "Thing" not in mode_classes, "Schema.org classes should not be included in the mode file"
    assert "MediaObject" not in mode_classes, "Schema.org classes should not be included in the mode file"
    for cname, mode_cls in mode.classes.items():
        assert len(mode_cls.inputs) == len(process_run_sv.class_slots(cname))
        assert mode_cls.id is not None and ":" not in mode_cls.id
        for slot in mode_cls.inputs:
            assert slot.id is not None and ":" not in slot.id
            assert slot.help is not None
            assert slot.label is not None
