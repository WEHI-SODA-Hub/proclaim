from pathlib import Path
from typing import TypeVar
from linkml_runtime.linkml_model import Element, SlotDefinition, SlotDefinitionName
from rdflib import Graph, URIRef
from rdfcrate import uris


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

def domain(slot: SlotDefinition) -> set[SlotDefinitionName]:
    """
    Returns a set of all domains of a slot
    """
    ret = set()
    if slot.domain is not None:
        ret.add(slot.domain)
    if slot.domain_of is not None:
        if isinstance(slot.domain_of, str):
            ret.add(slot.domain_of)
        elif isinstance(slot.domain_of, list):
            ret.update(slot.domain_of)
    return ret

def remove_newlines(s: str) -> str:
    return s.replace("\n", " ")
