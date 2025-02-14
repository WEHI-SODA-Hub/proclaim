from proclaim.vocabulary import VocabularyHtmlGenerator
import tempfile
from pathlib import Path

def test_html_generator(process_run: str):
    with tempfile.TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)
        # with contextlib.chdir("test"):
        VocabularyHtmlGenerator(schema=process_run).serialize(directory=_tmp)
        assert (tmp / "html" / "index.html").exists()
        assert (tmp / "html" / "classes" / "SIFImage" / "index.html").exists()
        assert (tmp / "html" / "properties" / "resourceUsage" / "index.html").exists()
        assert not (tmp / "site").exists()
