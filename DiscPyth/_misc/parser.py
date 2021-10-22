from typing import List, Tuple


def parse(loc: str):
    fname = []
    fval = []
    typs = []
    with open(loc, "r") as data:
        for ln in data:
            name, typ = ln.split("|")
            tp = typ.strip()
            ns = name.strip()
            if ns[-1:] == "?":
                fname.append(ns[:-1])
                fval.append(f'gpj.field("{ns[:-1]}", optional=True)')
            else:
                fname.append(ns)
                fval.append(f'gpj.field("{ns}")')

            typs.append(tp[1:] if tp[:1] == "?" else tp)

    return fname, fval, typs


def convert(name: str, docstr: str, data: Tuple[List[str], List[str], List[str]]):
    body = f"""class {name}(metaclass=gpj.Struct):
    \"\"\"
    {docstr}
    \"\"\""""
    names, values, types = data
    for lsts in data:
        if len(names) != len(lsts):
            return ""
        if len(values) != len(lsts):
            return ""
        if len(types) != len(lsts):
            return ""

    for idx, nm in enumerate(names):
        body += "\n    " + nm + ": " + types[idx] + " = " + values[idx]

    return body


if __name__ == "__main__":
    print(
        convert(
            "Ready",
            "Received after Identifying, contains information such as the gateway version used by DiscPyth and much more\n    https://discord.com/developers/docs/topics/gateway#ready",
            parse("DDocsParser/toparse.md"),
        )
    )
