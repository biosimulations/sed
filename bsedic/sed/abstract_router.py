from abc import ABC, abstractmethod

from bsedic.sed.data_structure import ExperimentNode, ExperimentNodeImplementation

# Need to create a datasource of implementations with proper tags that tie back to their abstract concepts.
# With all of the groups gathered covering all abstract concept, in each group pick one implementation based on
# criteria that can be feed in (pick from the set).

# ruff: noqa: TRY003


class AbstractRouter(ABC):
    @abstractmethod
    def abstract_entity_to_implementation(
        self, abstract_representation: ExperimentNode
    ) -> ExperimentNodeImplementation:
        pass

    @abstractmethod
    def _get_implementations(self, abstract_representation: ExperimentNode) -> set[ExperimentNodeImplementation]:
        pass


class LocalRouter(AbstractRouter):
    def abstract_entity_to_implementation(
        self, abstract_representation: ExperimentNode
    ) -> ExperimentNodeImplementation:
        input_constraint = abstract_representation.inputs
        output_constraint = abstract_representation.outputs
        node_implementations_for_abstract: set[ExperimentNodeImplementation] = self._get_implementations(
            abstract_representation
        )

        # Sift through the set, simple for now but will need retouch when what's being sifted for is better understood
        for n in node_implementations_for_abstract:
            if n.inputs == input_constraint and n.outputs == output_constraint:
                return n

        raise NotImplementedError("No implementation for abstract entity to implement")
