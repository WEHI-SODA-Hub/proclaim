from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Self, TypeAlias, Union, Annotated

from pydantic import BaseModel, Field, StringConstraints, model_serializer


class SkipNullBase(BaseModel):
    @model_serializer(mode="wrap")
    def skip_null(self, handler: Callable[[Self], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Modify the result of serialization to skip keys with None values.
        This results in cleaner JSON but also satisfies the Mode JSON schema that doesn't allow null but allows missing keys.
        """
        return {k: v for k, v in handler(self).items() if v is not None}


class Metadata(SkipNullBase):
    class Config:
        extra = "allow"

    name: str
    description: str
    version: float
    author: str
    license: str


class ResolveItem(SkipNullBase):
    types: Optional[List] = None
    properties: Optional[List] = None


class Type(Enum):
    Select = 'Select'
    MultiSelect = 'MultiSelect'
    Value = 'Value'


class Input(SkipNullBase):
    class Config:
        extra = "allow"

    id: str
    name: str
    help: str
    label: Optional[str] = None
    multiple: Optional[bool] = None
    required: Optional[bool] = None
    hide: Optional[bool] = None
    readonly: Optional[bool] = None
    group: Optional[str] = None
    type: Optional[Union[List[str], Type]] = None

class Class(SkipNullBase):
    class Config:
        extra = "forbid"

    id: Optional[str] = None
    hasSubclass: Optional[List[str]] = None
    subClassOf: Optional[List[str]] = None
    inputs: List[Input]


class Lookup(SkipNullBase):
    class Config:
        extra = "forbid"

    fields: Optional[List] = None
    module: Optional[str] = None
    datapacks: Optional[List[str]] = None

class Group(BaseModel, extra="forbid"):
    """
    A logical grouping of inputs
    """
    name: str
    help: str
    #: URIs for inputs to include in this group
    inputs: list[str]


Classes: TypeAlias = Dict[Annotated[str, StringConstraints(pattern=r'^[A-Z,a-z]*')], Class]
Context: TypeAlias = Union[List, str, Dict[str, Any]]
InputGroups: TypeAlias = Optional[List[Dict[str, Any]]]
Resolve: TypeAlias = Optional[List[ResolveItem]]
Lookups: TypeAlias = Optional[Dict[Annotated[str, StringConstraints(pattern=r'^[A-Z,a-z]*')], Lookup]]

class ModeFile(SkipNullBase):
    class Config:
        extra = "allow"

    metadata: Annotated[Metadata, Field(description='Profile Metadata')]
    classes: Annotated[Classes, Field(
        description='Class definitions'
    )]
    context: Context
    #: Groups inputs together into logical categories
    #: A list of dicts where each dict is a group that has a name 
    inputGroups: Annotated[InputGroups, Field(
        description='Definitions for the top-level groups of inputs (properties)'
    )] = None
    resolve: Annotated[Resolve, Field(
        description='Configuration to resolve property associations'
    )] = None
    lookup: Annotated[Lookups, Field(
        description='Lookup definitions'
    )] = None
