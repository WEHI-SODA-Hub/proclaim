from proclaim.mode.generator import RoCrateModeGenerator

def test_mode_file_generation():
    RoCrateModeGenerator(schema="test/workflow-ro-crate.yaml").serialize()
