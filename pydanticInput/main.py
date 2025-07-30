import argparse
import platform
import re
from importlib import metadata
from pathlib import Path

import pydantic
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QScrollArea

import pydanticInput


def Input(model: type[pydantic.BaseModel]) -> dict:
    """
    Display a PySide6 form for a Pydantic model and return user input as a dict.

    Args:
        model (type[BaseModel]): The Pydantic model class to generate the
            input form for.

    Returns:
        dict: A dictionary with values entered by the user, keyed by the
            model's fields.

    Notes:
        - The function blocks until the user closes the form.
        - The form includes OK and Cancel buttons.
        - On OK, input values are collected and returned.
        - On Cancel or window close, an empty dictionary is returned.
    """

    vals = {}
    app = QApplication([])
    widget, getter = pydanticInput.type_dispatch(model)(model)
    btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    btns.accepted.connect(lambda: vals.update(getter()))
    btns.accepted.connect(app.quit)
    btns.rejected.connect(app.quit)
    widget.layout().addWidget(btns)
    scroll_area = QScrollArea()
    scroll_area.setWidget(widget)
    scroll_area.show()
    app.exec()
    return vals


def get_dependency_versions(package: str = "pydanticInput") -> dict:
    """
    Retrieves the installed versions of dependencies for a specified Python
    package. This function reads the package's METADATA file to extract its
    dependencies, then attempts to determine the installed version of each
    dependency.

    Args:
        package (str): The name of the package whose dependencies' versions are
        to be retrieved.
        * Defaults to "pydanticInput".

    Returns:
        dict: A dictionary mapping dependency names to their installed versions.
            * If a dependency is not installed, value will be "not installed"
            * If the METADATA file is not found, returns an empty dictionary.
    """

    versions = {}
    # Find METADATA for the current package
    metadata_file = Path(metadata.distribution(package)._path, "METADATA")
    if not metadata_file.is_file():
        return versions
    for match in re.finditer(
        r"^Requires-Dist: (.+)", metadata_file.read_text(encoding="utf-8"), re.M
    ):
        dep = re.split(r"[<>=]", match.group(1))[0].strip()
        try:
            versions[dep] = metadata.version(dep)
        except metadata.PackageNotFoundError:
            versions[dep] = "not installed"
    return versions


def debug_info() -> str:
    """
    Collects and returns a formatted string containing debug information about
    the current environment. The returned string includes:
        - Operating system name, release, and version
        - System architecture
        - Python version
        - Application version (from pydanticInput.__version__)
        - A list of dependencies and their versions

    Returns:
        str: A multi-line string with environment and dependency information.
    """

    info = (
        f"OS: {platform.system()} {platform.release()} ({platform.version()})\n"
        f"Architecture: {platform.machine()}\n"
        f"Python version: {platform.python_version()}\n"
        f"App version: {pydanticInput.__version__}\n"
        "Dependencies:\n"
    )
    for dep, ver in get_dependency_versions().items():
        info += f"* {dep}: {ver}\n"
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description="pydanticInput CLI")
    parser.add_argument(
        "--version", action="store_true", help="show version information"
    )
    parser.add_argument(
        "--debug", action="store_true", help="show debug information"
    )
    args = parser.parse_args()
    if args.version:
        print(pydanticInput.__version__)
    elif args.debug:
        print(debug_info())


if __name__ == "__main__":
    main()
