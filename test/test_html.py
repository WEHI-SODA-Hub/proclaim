from proclaim.html.generator import ProfileHtmlGenerator
import tempfile
from pathlib import Path
import contextlib

def test_html_generator(process_run: str):
    with tempfile.TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)
        # with contextlib.chdir("test"):
        ProfileHtmlGenerator(schema=process_run).serialize(directory=_tmp)
        assert (tmp / "index.html").exists()
