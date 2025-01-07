import pytest
from pathlib import Path
from linkml_runtime import SchemaView

@pytest.fixture
def process_run() -> str:
    return str((Path(__file__).parent / "process_run.yaml").resolve())

@pytest.fixture
def process_run_sv(process_run: str) -> SchemaView:
    return SchemaView(process_run)
