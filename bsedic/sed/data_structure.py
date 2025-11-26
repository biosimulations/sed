import re
import typing

import pydantic

_ID_TYPE: typing.TypeAlias = typing.Annotated[str, pydantic.Field(pattern=re.compile(r"^[_a-zA-Z]+\w*$"))]
_SOURCE_TYPE: typing.TypeAlias = typing.Annotated[str, pydantic.Field(pattern=re.compile(r"^[_a-zA-Z]+[\w\-]*$"))]
_TYPE_TYPE: typing.TypeAlias = typing.Annotated[str, pydantic.Field(pattern=re.compile(r"^[_a-zA-Z]+[\w\-]*$"))]


class ExperimentDefinition(pydantic.BaseModel):
    id: _ID_TYPE
    source: str


# class AbstractHeader(pydantic.BaseModel):
#     pass


class ExperimentNode(pydantic.BaseModel):
    id: _ID_TYPE
    definition: _ID_TYPE
    inputs: set[_ID_TYPE]
    outputs: set[_ID_TYPE]


class ExperimentNodeImplementation(ExperimentNode):
    address: _SOURCE_TYPE


class ExperimentWiring(pydantic.BaseModel):
    id: _ID_TYPE
    output: _ID_TYPE
    input: _ID_TYPE
    protocol: _TYPE_TYPE  # The type of the port


class ExperimentEntityList(pydantic.BaseModel):
    # TODO: Determine if we need multiple models in one AEL

    # header: AbstractHeader
    definitions: dict[_ID_TYPE, _SOURCE_TYPE]
    nodes: list[ExperimentNode]
    wirings: list[ExperimentWiring]
