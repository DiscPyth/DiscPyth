# flake8: noqa

import re
from typing import Generator, List, Tuple

STRUCT_REGEX = re.compile(r"type (?P<name>\w*) struct {", flags=re.DOTALL)
ATTR_REGEX = re.compile(r'(?P<name>.*)#(?P<type>.*)#`json:"(?P<options>.*)"`')

CASE_REGEX_A = re.compile(r"(.)([A-Z][a-z]+)")
CASE_REGEX_B = re.compile(r"([a-z0-9])([A-Z])")

OPTIONS_REGEX = re.compile(
    r"(?P<name>\w*),{0,1}(?P<option_a>omitempty){0,1},{0,1}(?P<option_b>string){0,1}"
)
TYPE_REGEX = re.compile(r"\w*\W*$")


def clean_var_name(name: str) -> str:
    name = CASE_REGEX_A.sub(r"\1_\2", name)
    return CASE_REGEX_B.sub(r"\1_\2", name).lower()


def get_type(typ: str) -> str:
    typ = TYPE_REGEX.findall(typ)[0]
    if typ == "string":
        return "str"
    if typ in (
        "int",
        "int8",
        "int16",
        "int32",
        "int64",
        "uint",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
    ):
        return "int"
    if typ in ("float32", "float64"):
        return "float"
    if typ == "bool":
        return "bool"
    return typ


def get_annotation(name: str, options: str, typ: str) -> str:
    typ = get_type(typ)
    options_m = OPTIONS_REGEX.match(options)
    options = options_m.groupdict()
    ops = "{"
    if options.get("name", name) != name:
        ops += f'"name": "{options["name"]}",'  # type: ignore
    if options.get("option_a") is not None:
        ops += f'"optional": True,'
    if options.get("option_b") is not None:
        ops += '"string": True,'
    if typ not in ("int", "str", "bool", "float"):
        ops += f'"object": {typ},'
    ops += "}"
    if ops == "{}":
        return typ
    else:
        return f"Annotated[{typ}, {ops[:-2]+'}'}]"


def match_struct_ends(inp: str, idx: int) -> Tuple[str, int]:
    s_idx = idx
    while True:
        nextchar = inp[idx]
        if nextchar == "{":
            _, idx = match_struct_ends(inp, idx + 1)
        if nextchar == "}":
            break
        idx += 1
    return inp[s_idx:idx], idx


def match_structs(inp: str) -> Generator[Tuple[str, List[str]], None, None]:
    inp = inp.replace("\n", "\\n").replace(r"\t", "")
    for m in STRUCT_REGEX.finditer(inp):
        _, idx = m.span()
        yld = m.group("name"), match_struct_ends(inp, idx)[0].split("\\n")
        yield yld


def make_class(match: Generator[str, None, None]):
    class_def = "class {0}(Struct):\n"
    attr_def = "    {0}: {1}\n"
    for struct in match:
        s_class_def = class_def.format(struct[0])
        for attr in struct[1]:
            attr = re.sub(r"\s+", "#", attr.strip())
            attr = ATTR_REGEX.match(attr)  # type: ignore
            if attr is not None:
                name, typ, options = attr.groups()  # type: ignore
                name = clean_var_name(name)
                s_class_def += attr_def.format(
                    name, get_annotation(name, options, typ)
                )
        yield s_class_def


def make(inp: str) -> Generator[str, None, None]:
    return make_class(match_structs(inp))
