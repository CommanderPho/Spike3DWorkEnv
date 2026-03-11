from rope.base.project import Project
from rope.refactor.extract import ExtractMethod
import re


def convert_call_to_kwargs(source, func_name):
    """
    Convert positional call produced by rope into kwargs call.
    Example:
        compute(a, b, scale)
    becomes
        compute(a=a, b=b, scale=scale)
    """

    pattern = rf"{func_name}\((.*?)\)"

    def repl(match):
        args = [a.strip() for a in match.group(1).split(",") if a.strip()]
        kwargs = ", ".join(f"{a}={a}" for a in args)
        return f"{func_name}({kwargs})"

    return re.sub(pattern, repl, source, count=1)


def extract_function(project_root, filename, start_marker, end_marker, function_name="extracted_function"):
    project = Project(project_root)

    resource = project.get_file(filename)

    with open(filename) as f:
        source = f.read()

    start = source.index(start_marker)
    end = source.index(end_marker) + len(end_marker)

    extractor = ExtractMethod(project, resource, start, end)

    changes = extractor.get_changes(function_name)

    project.do(changes)

    # --- modify call to kwargs style ---
    with open(filename) as f:
        new_source = f.read()

    new_source = convert_call_to_kwargs(new_source, function_name)

    with open(filename, "w") as f:
        f.write(new_source)

    project.close()


if __name__ == "__main__":

    extract_function(
        project_root=".",
        filename="example.py",
        start_marker="c = a + b",
        end_marker="d = c * scale",
        function_name="compute_values",
    )