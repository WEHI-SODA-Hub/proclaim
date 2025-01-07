# generated by datamodel-codegen:
#   filename:  ro-crate-editor-profile-schema.json
#   timestamp: 2024-11-29T06:39:35+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypeAlias, Union, Annotated

from pydantic import BaseModel, Field, StringConstraints


class Metadata(BaseModel):
    class Config:
        extra = "allow"

    name: str
    description: str
    version: float


class ResolveItem(BaseModel):
    types: Optional[List] = None
    properties: Optional[List] = None


class Type(Enum):
    Select = 'Select'
    MultiSelect = 'MultiSelect'
    Value = 'Value'


class Input(BaseModel):
    class Config:
        extra = "allow"

    id: str
    name: str
    label: Optional[str] = None
    multiple: Optional[bool] = None
    required: Optional[bool] = None
    hide: Optional[bool] = None
    readonly: Optional[bool] = None
    group: Optional[str] = None
    type: Optional[Union[List[str], Type]] = None


class Class(BaseModel):
    class Config:
        extra = "forbid"

    id: Optional[str] = None
    hasSubclass: Optional[List[str]] = None
    subClassOf: Optional[List[str]] = None
    inputs: List[Input]


class Lookup(BaseModel):
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
Context: TypeAlias = Optional[Union[List, str, Dict[str, Any]]]
InputGroups: TypeAlias = Optional[List[Dict[str, Any]]]
Resolve: TypeAlias = Optional[List[ResolveItem]]
Lookups: TypeAlias = Optional[Dict[Annotated[str, StringConstraints(pattern=r'^[A-Z,a-z]*')], Lookup]]

class ModeFile(BaseModel):
    class Config:
        extra = "allow"

    metadata: Annotated[Metadata, Field(description='Profile Metadata')]
    classes: Annotated[Classes, Field(
        description='Class definitions'
    )]
    context: Context = None
    #: Groups inputs together into logical categories
    #: A list of dicts where each dict is a group that has a name 
    inputGroups: Annotated[InputGroups,Field(
        description='Definitions for the top-level groups of inputs (properties)'
    )] = None
    resolve: Annotated[Resolve, Field(
        None, description='Configuration to resolve property associations'
    )] = None
    lookup: Annotated[Lookups, Field(
        description='Lookup definitions'
    )] = None
