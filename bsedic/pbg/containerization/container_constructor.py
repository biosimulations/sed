import re
from typing import Optional

from bsedic.pbif.containerization.container_file import (
    get_generic_dockerfile_template,
    pull_substitution_keys_from_document,
)
from bsedic.utils.input_types import (
    ContainerizationFileRepr,
    ExperimentPrimaryDependencies,
    ProgramArguments,
)


def formulate_dockerfile_for_necessary_env(
    program_arguments: ProgramArguments,
) -> tuple[ContainerizationFileRepr, ExperimentPrimaryDependencies]:
    docker_template: str = get_generic_dockerfile_template()
    pb_document_str: str
    with open(program_arguments.input_file_path) as pb_document_file:
        pb_document_str = pb_document_file.read()
    experiment_deps, updated_document_str = determine_dependencies(pb_document_str, program_arguments.passlist_entries)
    if updated_document_str != pb_document_str:  # we need to update file
        with open(program_arguments.input_file_path, "w") as pb_document_file:
            pb_document_file.write(updated_document_str)
    for desired_field in generate_necessary_values():
        match_target: str = "$${#" + desired_field + "}"
        if desired_field == "PYPI_DEPENDENCIES":
            if len(experiment_deps.get_pypi_dependencies()) == 0:
                docker_template = docker_template.replace(match_target, "# No PyPI dependencies!")
                continue
            pypi_section = """
RUN python3 -m pip install $${#DEPENDENCIES}
""".strip()
            dependency_str = convert_dependencies_to_installation_string_representation(
                experiment_deps.get_pypi_dependencies()
            )
            filled_section = pypi_section.replace("$${#DEPENDENCIES}", dependency_str)
            docker_template = docker_template.replace(match_target, filled_section)
        elif desired_field == "CONDA_FORGE_DEPENDENCIES":
            if len(experiment_deps.get_conda_dependencies()) == 0:
                docker_template = docker_template.replace(match_target, "# No conda dependencies!")
                continue
            conda_section = """
RUN mkdir /micromamba
RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
RUN mv bin/micromamba /usr/local/bin/
RUN micromamba create -y -p /opt/conda -c conda-forge $${#DEPENDENCIES} python=3.12
ENV PATH=/opt/conda/bin:$PATH
""".strip()
            dependency_str = " ".join(experiment_deps.get_conda_dependencies())
            filled_section = conda_section.replace("$${#DEPENDENCIES}", dependency_str)
            docker_template = docker_template.replace(match_target, filled_section)
        else:
            err_msg = f"unknown field in template dockerfile: {desired_field}"
            raise ValueError(err_msg)

    return ContainerizationFileRepr(representation=docker_template), experiment_deps


def generate_necessary_values() -> list[str]:
    return pull_substitution_keys_from_document()


# Due to an assumption that we can not have all dependencies included
# in the same python environment, we need a solid address protocol to assume.
# going with: `python:{source}<{package_name}>[{version_statement}]@{python_module_path_to_class_def}`
#         ex: "python: pypi<copasi-basico[~0.8]>@basico.model_io.load_model" (if this was a class, and not a function)
def determine_dependencies(  # noqa: C901
    string_to_search: str, whitelist_entries: Optional[list[str]] = None
) -> tuple[ExperimentPrimaryDependencies, str]:
    whitelist_mapping: dict[str, set[str]] | None
    if whitelist_entries is not None:
        whitelist_mapping = {}
        for whitelist_entry in whitelist_entries:
            entry = whitelist_entry.split("::")
            if len(entry) != 2:
                err_msg = f"invalid whitelist entry: {whitelist_entry}"
                raise ValueError(err_msg)
            source, package = (entry[0], entry[1])
            if source not in whitelist_mapping:
                whitelist_mapping[source] = set()
            whitelist_mapping[source].add(package)
    else:
        whitelist_mapping = None
    source_name_legal_syntax = r"[\w\-]+"
    package_name_legal_syntax = r"[\w\-._~:/?#[\]@!$&'()*+,;=%]+"  # package or git-http repo name
    version_string_legal_syntax = (
        r"\[([\w><=~!*\-.]+)]"  # hard brackets around alphanumeric plus standard python version constraint characters
    )
    # stricter pattern of only legal python module names
    # (letters and underscore first character, alphanumeric and underscore for remainder); must be at least 1 char long
    import_name_legal_syntax = r"[A-Za-z_]\w*(\.[A-Za-z_]\w*)*"
    known_sources = ["pypi", "conda"]
    approved_dependencies: dict[str, list[str]] = {source: [] for source in known_sources}
    regex_pattern = f"python:({source_name_legal_syntax})<({package_name_legal_syntax})({version_string_legal_syntax})?>@({import_name_legal_syntax})"
    adjusted_search_string = str(string_to_search)
    matches = re.findall(regex_pattern, string_to_search)
    if len(matches) == 0:
        local_protocol_matches = re.findall(f"local:{import_name_legal_syntax}", string_to_search)
        if len(local_protocol_matches) == 0:
            err_msg = "No dependencies found in document; unable to generate environment."
            raise ValueError(err_msg)
        match_str_list: str = ",".join([str(match) for match in matches])
        if len(match_str_list) != 0:  # For some reason, we can get a single "match" that's empty...
            err_msg = f"Document is using the following local protocols: `{match_str_list}`; unable to determine needed environment."
            raise ValueError(err_msg)
    for match in matches:
        source_name = match[0]
        package_name = match[1]
        package_version = match[3]
        if source_name not in known_sources:
            err_msg = f"Unknown source `{source_name}` used; can not determine dependencies"
            raise ValueError(err_msg)
        dependency_str = f"{package_name}{package_version}".strip()
        if dependency_str in approved_dependencies[source_name]:
            continue  # We've already accounted for this dependency
        if whitelist_mapping is not None:
            # We need to validate against whitelist!
            if source_name not in whitelist_mapping:
                err_msg = f"Unapproved source `{source_name}` used; can not trust document"
                raise ValueError(err_msg)
            if package_name not in whitelist_mapping[source_name]:
                err_msg = f"`{package_name}` from `{source_name}` is not a trusted package; can not trust document"
                raise ValueError(err_msg)
        approved_dependencies[source_name].append(dependency_str)
        version_str = match[2] if package_version != "" else ""
        complete_match = f"python:{source_name}<{package_name}{version_str}>@{match[4]}"
        adjusted_search_string = adjusted_search_string.replace(complete_match, f"local:{match[4]}")
    return ExperimentPrimaryDependencies(
        approved_dependencies["pypi"], approved_dependencies["conda"]
    ), adjusted_search_string.strip()


def convert_dependencies_to_installation_string_representation(dependencies: list[str]) -> str:
    return "'" + "' '".join(dependencies) + "'"
