### File that collects the abstract headers
import importlib.metadata
import pkgutil
import re


def load_local_modules() -> None:
    print("Loading local registry...")
    for package in importlib.metadata.distributions():
        if not does_package_require_bsail(package):
            continue
        # If a package requires BSail, it probably has abstractions for us; worth importing.
        recursive_dynamic_import(package.name)


def does_package_require_bsail(package: importlib.metadata.Distribution) -> bool:
    for key in package.metadata:
        if key != "Requires-Dist":
            continue
        if not re.match(r"bsail \([=><\d.]+,?[=><\d.]+\)", package.metadata[key]):
            continue
        return True
    return False


def recursive_dynamic_import(package_name: str) -> list[str]:
    classes_to_import = []
    adjusted_package_name = package_name.replace("-", "_")
    try:
        module = importlib.import_module(adjusted_package_name)
    except ModuleNotFoundError as mnfe:
        # TODO: Add code to try and find correct module name via accessing `top_level.txt`,
        #  and getting the correct module name
        # find top-level.txt
        # find correct module name
        # return recursive_dynamic_import(correct_module_name)
        err_msg = f"module {adjusted_package_name} not found"
        raise ModuleNotFoundError(err_msg) from mnfe
    # class_members = inspect.getmembers(module, inspect.isclass)
    # for class_name, clazz in class_members:
    #     if not (issubclass(clazz, Process) or issubclass(clazz, Step)) or (clazz in [Process, Step, Composite]):
    #         continue
    #     classes_to_import.append((class_name, clazz))

    modules_to_check = pkgutil.iter_modules(module.__path__) if hasattr(module, "__path__") else []
    for _module_loader, subname, _isPkg in modules_to_check:
        # if not isPkg: continue
        classes_to_import += recursive_dynamic_import(f"{adjusted_package_name}.{subname}")

    return classes_to_import
