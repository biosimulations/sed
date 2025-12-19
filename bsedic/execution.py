import os
import shutil

from spython.main.parse.parsers import DockerParser  # type: ignore[import-untyped]
from spython.main.parse.writers import SingularityWriter  # type: ignore[import-untyped]

from bsedic.pbg.containerization.container_constructor import (
    formulate_dockerfile_for_necessary_env,
)
from bsedic.pbg.local_registry import load_local_modules
from bsedic.utils.experiment_archive import extract_archive_returning_pbg_path
from bsedic.utils.input_types import (
    ContainerizationEngine,
    ContainerizationFileRepr,
    ContainerizationTypes,
    ExperimentPrimaryDependencies,
    ProgramArguments,
)


def execute_bsedic(
    original_program_arguments: ProgramArguments,
) -> tuple[ContainerizationFileRepr, ExperimentPrimaryDependencies]:
    new_input_file_path: str
    input_is_archive = original_program_arguments.input_file_path.endswith(
        ".zip"
    ) or original_program_arguments.input_file_path.endswith(".omex")
    required_program_arguments: ProgramArguments
    if input_is_archive:
        new_input_file_path = extract_archive_returning_pbg_path(
            original_program_arguments.input_file_path, str(original_program_arguments.output_dir)
        )
    else:
        new_input_file_path = os.path.join(
            str(original_program_arguments.output_dir), os.path.basename(original_program_arguments.input_file_path)
        )
        print(f"file copied to `{shutil.copy(original_program_arguments.input_file_path, new_input_file_path)}`")
    required_program_arguments = ProgramArguments(
        new_input_file_path,
        original_program_arguments.output_dir,
        original_program_arguments.passlist_entries,
        original_program_arguments.containerization_type,
        original_program_arguments.containerization_engine,
    )

    load_local_modules()  # Collect Abstracts
    # TODO: Add feature - resolve abstracts

    # Determine Dependencies
    docker_template: ContainerizationFileRepr
    returned_template: ContainerizationFileRepr
    primary_dependencies: ExperimentPrimaryDependencies
    docker_template, primary_dependencies = formulate_dockerfile_for_necessary_env(required_program_arguments)
    returned_template = docker_template
    if required_program_arguments.containerization_type != ContainerizationTypes.NONE:
        if required_program_arguments.containerization_type != ContainerizationTypes.SINGLE:
            raise NotImplementedError("Only single containerization is currently supported")
        container_file_path: str
        container_file_path = os.path.join(str(original_program_arguments.output_dir), "Dockerfile")
        with open(container_file_path, "w") as docker_file:
            docker_file.write(docker_template.representation)
        if (
            required_program_arguments.containerization_engine == ContainerizationEngine.APPTAINER
            or required_program_arguments.containerization_engine == ContainerizationEngine.BOTH
        ):
            dockerfile_path = container_file_path
            container_file_path = os.path.join(str(original_program_arguments.output_dir), "singularity.def")
            dockerfile_parser = DockerParser(dockerfile_path)
            singularity_writer = SingularityWriter(dockerfile_parser.recipe)
            results = singularity_writer.convert()
            returned_template = ContainerizationFileRepr(representation=results)
            with open(container_file_path, "w") as container_file:
                container_file.write(results)
            if required_program_arguments.containerization_engine != ContainerizationEngine.BOTH:
                os.remove(dockerfile_path)
        print(f"Container build file located at '{container_file_path}'")

    # Reconstitute if archive
    if input_is_archive:
        base_name = os.path.basename(original_program_arguments.input_file_path)
        output_dir: str = (
            os.path.dirname(original_program_arguments.input_file_path)
            if original_program_arguments.output_dir is None
            else str(original_program_arguments.output_dir)
        )
        new_archive_path = os.path.join(output_dir, base_name)
        # Note: If no output dir is provided (dir is `None`), then input file WILL BE OVERWRITTEN
        target_dir = os.path.join(str(original_program_arguments.output_dir), base_name.split(".")[0])
        shutil.make_archive(new_archive_path, "zip", target_dir)
        shutil.move(new_archive_path + ".zip", new_archive_path)  # get rid of extra suffix
    return returned_template, primary_dependencies
