from linkml_runtime.utils.schemaview import SchemaView
from proclaim.mode.generator import RoCrateModeGenerator

def test_mode_file_generation(process_run: str, process_run_sv: SchemaView):
    mode = RoCrateModeGenerator(schema=process_run).make_mode()
    assert len(mode.classes) == len(process_run_sv.all_class())
    for cname, mode_cls in mode.classes.items():
        assert len(mode_cls.inputs) == len(process_run_sv.class_slots(cname))
