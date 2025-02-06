import json
from pathlib import Path
import tempfile
from proclaim.profile_crate.generator import ProfileCrateGenerator


def test_crate(process_run: str):
    with tempfile.TemporaryDirectory() as _output_dir:
        output_dir = Path(_output_dir)
        ProfileCrateGenerator(process_run).serialize(str(output_dir))

        assert (output_dir / "ro-crate-metadata.json").exists()
        assert (output_dir / "index.html").exists()
        assert (output_dir / "shapes.ttl").exists()
        assert (output_dir / "mode.json").exists()

        parsed_crate = json.loads((output_dir / "ro-crate-metadata.json").read_text())

        # There should be a ResourceDescriptor in the graph, and its type should be shortened to just "ResourceDescriptor"
        found_resource_descriptor = False
        for entity in parsed_crate["@graph"]:
            if entity["@type"] == "ResourceDescriptor":
                found_resource_descriptor = True
                break
        assert found_resource_descriptor
