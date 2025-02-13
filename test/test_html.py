from proclaim.html.generator import ProfileHtmlGenerator
import tempfile
from pathlib import Path

def test_profile_html_default(process_run: str):
    """
    Checks that a default profile template renders
    """
    with tempfile.TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)
        ProfileHtmlGenerator(schema=process_run).serialize(directory=_tmp)
        assert (tmp / "html" / "index.html").exists()

def test_profile_html_custom_template(process_run: str):
    """
    Checks that a custom template with dynamic content, located outside of the package can be used to define the profile.
    """
    with tempfile.TemporaryDirectory() as _tmp:
        tmp = Path(_tmp)
        ProfileHtmlGenerator(schema=process_run, template_path=Path(__file__).parent / "test_template.jinja2").serialize(directory=_tmp)
        assert (tmp / "markdown" / "index.md").read_text() == "2"
