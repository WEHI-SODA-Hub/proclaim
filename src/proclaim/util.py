from typing import TypeVar
from linkml_runtime.linkml_model import Element


T = TypeVar("T")
def mandatory(x: T | None, message: str) -> T:
    if x is None:
        raise ValueError(message)
    return x

def description(el: Element) -> str:
    """
    Get a string that describes the element, either from the description field or the comments field.
    See https://github.com/linkml/linkml/issues/2507
    """
    if el.description is not None:
        return el.description
    elif el.comments is not None:
        if isinstance(el.comments, list):
            return "\n".join(el.comments)
        else:
            return el.comments
    else:
        raise ValueError(f"Element {el.name} must have a description or comments field to be converted to an RO-Crate Profile")
