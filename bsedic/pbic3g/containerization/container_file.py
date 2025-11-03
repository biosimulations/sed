import re


def get_generic_dockerfile_template() -> str:
    return """
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

RUN apt update
RUN apt upgrade -y
RUN apt install -y git curl

## Dependency Installs
### Conda
$${#CONDA_FORGE_DEPENDENCIES}

### PyPI
$${#PYPI_DEPENDENCIES}

##
RUN mkdir /runtime
WORKDIR /runtime
RUN git clone https://github.com/biosimulators/bsew.git  /runtime
RUN python3 -m pip install -e /runtime

ENTRYPOINT ["python3", "/runtime/main.py"]
""".strip()


# Note the capture group; that's what re.findall will return!
_sub_keys: set[str] = {match for match in re.findall(r"\$\${#(\w+)}", get_generic_dockerfile_template())}  # noqa: C416


def pull_substitution_keys_from_document() -> list[str]:
    return list(_sub_keys)
