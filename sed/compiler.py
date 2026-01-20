# from typing import Any, TypeAlias, Union
#
# from bsedic.data_structure import ExperimentEntityList
#
#
# class SedCompilerSettings:
#     pass
#
#
# _schema_element = Union[str, list[str], "_schema"]
# _schema: TypeAlias = dict[str, _schema_element]
#
#
# class SedCompiler:
#     # Compiler should not be stateful about what it compiles; only it's settings may be stateful
#     def __init__(self, settings: SedCompilerSettings, shims: Any) -> None:
#         self._settings = settings
#         self._shims = shims
#
#     def compile(self) -> str:
#         raise NotImplementedError()
#
#     def _compile_stage_0(self) -> list[str]:  # Validate Sed2, return list of error messages
#         raise NotImplementedError()
#
#     def _compile_stage_1(self) -> ExperimentEntityList:  # Sed2 -> Abstract Entity List
#         raise NotImplementedError()
#
#     def _compile_stage_2(
#         self, abstract_entity_list: ExperimentEntityList
#     ) -> ExperimentEntityList:  # Abstract Entity List -> Implementation Entity List
#         raise NotImplementedError()
#
#     # TODO: This seems to need some level of processing from stage 2; especially if we're doing true compilation
#     #   The `ExperimentEntityList` should be adjusted as such.
#     def _compile_stage_3(
#         self, implementation_entity_list: ExperimentEntityList
#     ) -> str:  # Implementation Entity List -> Absolute-path PBIF (APPBIF)
#         composition_schema: _schema = {"state": {}, "composition": {}, "bridge": {}, "interface": {}}
#         for node in implementation_entity_list.nodes:
#             composition = composition_schema["composition"]
#             if not isinstance(composition, dict):
#                 raise TypeError()  # should never be reached
#             state = composition_schema["state"]
#             if not isinstance(state, dict):
#                 raise TypeError()  # should never be reached
#             composition[node.id] = {
#                 "_type": "step",
#                 "config": {},
#                 "inputs": "",  # this should be the type of
#                 "outputs": "",
#             }
#             state[node.id] = {
#                 "_type": "step",
#                 "config": {},
#                 "inputs": [],  #
#                 "outputs": [],
#             }
#         return ""
