"""JSON token scanner
"""
import re

__all__ = ["make_scanner"]

NUMBER_RE = re.compile(
    r"(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?",
    (re.VERBOSE | re.MULTILINE | re.DOTALL),
)


def py_make_scanner(context):  # pylint: disable=too-many-locals;
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = NUMBER_RE.match
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    def _scan_once(string, idx, obj=None, lock=False, raw=False):
        # pylint: disable=too-many-branches, too-many-return-statements, no-else-return
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration(idx) from None

        if nextchar == '"':
            return parse_string(string, idx + 1, strict)
        elif nextchar == "{":
            return parse_object(
                (string, idx + 1),
                strict,
                _scan_once,
                object_hook,
                object_pairs_hook,
                obj,
                lock,
                raw,
                memo,
            )
        elif nextchar == "[":
            return parse_array((string, idx + 1), _scan_once, obj, lock, raw)
        elif nextchar == "n" and string[idx : idx + 4] == "null":
            if raw:
                return string[idx : idx + 4], idx + 4
            return None, idx + 4
        elif nextchar == "t" and string[idx : idx + 4] == "true":
            if raw:
                return string[idx : idx + 4], idx + 4
            return True, idx + 4
        elif nextchar == "f" and string[idx : idx + 5] == "false":
            if raw:
                return string[idx : idx + 5], idx + 5
            return False, idx + 5

        m = match_number(string, idx)  # pylint: disable=invalid-name
        if m is not None:
            integer, frac, exp = m.groups()
            if frac or exp:
                res = parse_float(integer + (frac or "") + (exp or ""))
            else:
                res = parse_int(integer)
            if raw:
                res = str(res)
            return res, m.end()
        elif nextchar == "N" and string[idx : idx + 3] == "NaN":
            if raw:
                return string[idx : idx + 3], idx + 3
            return parse_constant("NaN"), idx + 3
        elif nextchar == "I" and string[idx : idx + 8] == "Infinity":
            if raw:
                return string[idx : idx + 8], idx + 8
            return parse_constant("Infinity"), idx + 8
        elif nextchar == "-" and string[idx : idx + 9] == "-Infinity":
            if raw:
                return string[idx : idx + 9], idx + 9
            return parse_constant("-Infinity"), idx + 9
        else:
            raise StopIteration(idx)

    def scan_once(string, idx, obj, lock=False):
        try:
            return _scan_once(string, idx, obj, lock)
        finally:
            memo.clear()

    return scan_once


make_scanner = py_make_scanner