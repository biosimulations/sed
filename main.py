import argparse
import os
import sys

from bsedic.execution import execute_bsedic
from bsedic.utils.input_types import ContainerizationEngine, ContainerizationTypes, ProgramArguments


def get_program_arguments() -> ProgramArguments:
    parser = _generate_argparse_parser()
    args = parser.parse_args()
    if args.target_containerization is not None and args.containerize is None:
        parser.print_help()
        print("Error: --target-containerization requires --containerize", file=sys.stderr)
        sys.exit(10)
    if args.target_containerization is None and args.containerize is not None:
        args.target_containerization = "docker"  # docker default, because apptainer is only linux

    args.input_file_path = os.path.abspath(os.path.expanduser(args.input_file_path))
    if (
        not os.path.exists(args.input_file_path)
        or not os.path.isfile(args.input_file_path)
        or not (
            args.input_file_path.endswith(".json")
            or args.input_file_path.endswith(".pbif")
            or args.input_file_path.endswith(".zip")
            or args.input_file_path.endswith(".omex")
        )
    ):
        parser.print_help()
        print("error: `input_file_path` must be either JSON/PBIF file, or ZIP/OMEX that exists!", file=sys.stderr)
        sys.exit(11)
    if args.output_directory is not None:
        args.output_directory = os.path.abspath(os.path.expanduser(args.output_directory))
        if not os.path.exists(args.output_directory) or not (
            os.path.isdir(args.output_directory) or os.path.islink(args.output_directory)
        ):
            parser.print_help()
            print("`output_directory` must be a directory that exists!", file=sys.stderr)
            sys.exit(12)
    else:
        args.output_directory = args.input_file_path.parent

    if args.whitelist is not None:
        args.whitelist = os.path.abspath(os.path.expanduser(args.whitelist))
        if not os.path.exists(args.whitelist) or not (os.path.isfile(args.whitelist) or os.path.islink(args.whitelist)):
            parser.print_help()
            print("`whitelist` must be a file that exists!", file=sys.stderr)
            sys.exit(13)
        with args.whitelist.open() as f:
            whitelist_contents = f.read().strip().split("\n")
    else:
        whitelist_contents = None
    containerization_type: ContainerizationTypes = ContainerizationTypes.NONE
    containerization_engine: ContainerizationEngine = ContainerizationEngine.NONE
    if args.containerize is not None:
        containerization_type, containerization_engine = _determine_containerization(args)

    return ProgramArguments(
        input_file_path=args.input_file_path,
        output_dir=args.output_directory,
        passlist_entries=whitelist_contents,
        containerization_type=containerization_type,
        containerization_engine=containerization_engine,
    )


def _generate_argparse_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="BioSimulators Experiment Description Implementation Compiler (BSedic)",
        description="""BSedic is a BioSimulators project designed to allow users to transform their
biological experiments written in Sed into Process-Bigraph simulations.""",
    )
    parser.add_argument("input_file_path", type=str)  # positional argument
    parser.add_argument(
        "-c",
        "--containerize",
        choices=["single", "multiple"],
        help="specifies if a containerized runtime should be initialized. "
        "`single` mode will reject a configuration that results in multiple containers needing to be coordinated together."
        "`multiple` mode will accept a result that is a coordination of multiple containers.",
    )
    parser.add_argument(
        "-t",
        "--target-containerization",
        choices=["docker", "apptainer", "singularity", "both"],
        help="if containerization is specified, selects whether to containerize with `docker` or `apptainer` (formerly Singularity CE)",
    )
    parser.add_argument(
        "-o",
        "--output_directory",
        nargs="?",
        const=".",
        help="specifies output directory; if not provided, no output file will be generated, but validation (and containerization if requested) will occur.",
    )
    parser.add_argument(
        "-w",
        "--whitelist",
        type=str,
        help="path to a whitelist file that if specified, will declare valid packages to create an environment with. ",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def _determine_containerization(args: argparse.Namespace) -> tuple[ContainerizationTypes, ContainerizationEngine]:
    if args.containerize == "single":
        containerization_type = ContainerizationTypes.SINGLE
    elif args.containerize == "multiple":
        containerization_type = ContainerizationTypes.MULTIPLE
    else:  # should never get here
        print("error: `containerize` must be `single` or `multiple` if requested.", file=sys.stderr)
        sys.exit(14)

    if args.target_containerization == "docker":
        containerization_engine = ContainerizationEngine.DOCKER
    elif args.target_containerization == "apptainer" or args.target_containerization == "singularity":
        containerization_engine = ContainerizationEngine.APPTAINER
    elif args.target_containerization == "both":
        containerization_engine = ContainerizationEngine.BOTH
    else:
        print("error: `target-containerization` must be `docker`, `apptainer`, or `both.", file=sys.stderr)
        sys.exit(15)
    return containerization_type, containerization_engine


def main():
    prog_args = get_program_arguments()
    try:
        execute_bsedic(prog_args)
    except Exception as e:
        print(e, file=sys.stderr)


if __name__ == "__main__":
    main()
