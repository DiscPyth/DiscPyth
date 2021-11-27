"""Implementation of JSONDecoder
"""
import re
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union

from . import scanner
from .struct import Struct, get_field, is_struct_class

try:
    from _json import scanstring as c_scanstring
except ImportError:
    c_scanstring = None  # type: ignore

__all__ = ["JSONDecoder", "JSONDecodeError"]

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL

NaN = float("nan")
PosInf = float("inf")
NegInf = float("-inf")

S = TypeVar("S", bound=Type[Struct])


class JSONDecodeError(ValueError):
    """Subclass of ValueError with the following additional properties:

    msg: The unformatted error message
    doc: The JSON document being parsed
    pos: The start index of doc where parsing failed
    lineno: The line corresponding to pos
    colno: The column corresponding to pos

    """

    # Note that this exception is used from _json
    def __init__(self, msg, doc, pos) -> None:
        lineno = doc.count("\n", 0, pos) + 1
        colno = pos - doc.rfind("\n", 0, pos)
        errmsg = "%s: line %d column %d (char %d)" % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):
        return self.__class__, (self.msg, self.doc, self.pos)


_CONSTANTS = {
    "-Infinity": NegInf,
    "Infinity": PosInf,
    "NaN": NaN,
}


STRINGCHUNK = re.compile(r'(.*?)(["\\\x00-\x1f])', FLAGS)
BACKSLASH = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}


def _decode_uXXXX(s, pos) -> int:  # noqa: N802
    esc = s[pos + 1 : pos + 5]
    if len(esc) == 4 and esc[1] not in "xX":
        try:
            return int(esc, 16)
        except ValueError:
            pass
    msg = "Invalid \\uXXXX escape"
    raise JSONDecodeError(msg, s, pos)


def py_scanstring(  # pylint: disable=dangerous-default-value, too-many-branches;
    s, end, strict=True, _b=BACKSLASH, _m=STRINGCHUNK.match
) -> Tuple[str, int]:
    """Scan the string s for a JSON string. End is the index of the
    character in s after the quote that started the JSON string.
    Unescapes all valid JSON string escape sequences and raises ValueError
    on attempt to decode an invalid string. If strict is False then literal
    control characters are allowed in the string.

    Returns a tuple of the decoded string and the index of the character in s
    after the end quote."""
    chunks: List[Any] = []
    _append = chunks.append
    begin = end - 1
    while 1:
        chunk = _m(s, end)
        if chunk is None:
            raise JSONDecodeError("Unterminated string starting at", s, begin)
        end = chunk.end()
        content, terminator = chunk.groups()
        # Content is contains zero or more unescaped string characters
        if content:
            _append(content)
        # Terminator is the end of string, a literal control character,
        # or a backslash denoting that an escape sequence follows
        if terminator == '"':  # pylint: disable=no-else-break
            break
        elif terminator != "\\":
            if strict:  # pylint: disable=no-else-raise
                # msg = "Invalid control character %r at" % (terminator,)
                msg = "Invalid control character {0!r} at".format(terminator)
                raise JSONDecodeError(msg, s, end)
            else:
                _append(terminator)
                continue
        try:
            esc = s[end]
        except IndexError:
            raise JSONDecodeError(
                "Unterminated string starting at", s, begin
            ) from None
        # If not a unicode escape sequence, must be in the lookup table
        if esc != "u":
            try:
                char = _b[esc]
            except KeyError:
                msg = "Invalid \\escape: {0!r}".format(esc)
                raise JSONDecodeError(  # pylint: disable=raise-missing-from
                    msg, s, end
                )
            end += 1
        else:
            uni = _decode_uXXXX(s, end)
            end += 5
            if 0xD800 <= uni <= 0xDBFF and s[end : end + 2] == "\\u":
                uni2 = _decode_uXXXX(s, end + 1)
                if 0xDC00 <= uni2 <= 0xDFFF:
                    uni = 0x10000 + (((uni - 0xD800) << 10) | (uni2 - 0xDC00))
                    end += 6
            char = chr(uni)
        _append(char)
    return "".join(chunks), end


# Use speedup if available
scanstring = c_scanstring or py_scanstring

WHITESPACE = re.compile(r"[ \t\n\r]*", FLAGS)
WHITESPACE_STR = " \t\n\r"


def JSONObject(  # pylint: disable=too-many-arguments, too-many-locals, too-many-branches; # noqa: N802
    s_and_end,
    strict,
    scan_once,
    object_hook,
    object_pairs_hook,
    object_: S = None,
    lock=False,
    raw=False,
    memo=None,
    _w=WHITESPACE.match,
    _ws=WHITESPACE_STR,
):
    # pylint: disable=too-many-statements
    if not raw:
        if not is_struct_class(object_):
            object_ = None
        else:
            object_ = object_()  # type: ignore
    s, end = s_and_end
    i_end = end-1
    pairs: Union[List[Any], Dict[Any, Any], S, str] = []
    pairs_append = pairs.append  # type: ignore
    # Backwards compatibility
    if memo is None:
        memo = {}
    memo_get = memo.setdefault
    # Use a slice to prevent IndexError from being raised, the following
    # check will raise a more specific ValueError if the string is empty
    nextchar = s[end : end + 1]
    # Normally we expect nextchar == '"'
    if nextchar != '"':
        if nextchar in _ws:
            end = _w(s, end).end()
            nextchar = s[end : end + 1]
        # Trivial empty object
        if nextchar == "}":  # pylint: disable=no-else-return
            if not raw:
                if object_pairs_hook is not None:
                    result = object_pairs_hook(pairs)
                    return result, end + 1
                pairs = {}
            else:
                pairs = "{}"
            if object_hook is not None:
                pairs = object_hook(pairs)
            return pairs, end + 1
        elif nextchar != '"':
            raise JSONDecodeError(
                "Expecting property name enclosed in double quotes", s, end
            )
    end += 1
    while True:
        key, end = scanstring(s, end, strict)
        key = memo_get(key, key)
        if not raw:
            field = get_field(object_, key)  # type: ignore
        # To skip some function call overhead we optimize the fast paths where
        # the JSON key separator is ": " or just ":".
        if s[end : end + 1] != ":":
            end = _w(s, end).end()
            if s[end : end + 1] != ":":
                raise JSONDecodeError("Expecting ':' delimiter", s, end)
        end += 1

        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

        try:
            if not raw:
                value, end = scan_once(s, end, field.object, field.lock, field.raw)
            else:
                _, end = scan_once(s, end, None, False, True)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        if not raw:
            if object_ is not None:
                try:
                    if field.hook is not None and callable(field.hook):
                        setattr(object_, object_.__mapping__[1][key], field.hook(value))
                    else:
                        setattr(object_, object_.__mapping__[1][key], value)
                except KeyError:
                    pass
            pairs_append((key, value))
        try:
            nextchar = s[end]
            if nextchar in _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        except IndexError:
            nextchar = ""
        end += 1
        if nextchar == "}":  # pylint: disable=no-else-break
            break
        elif nextchar != ",":
            raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        end = _w(s, end).end()
        nextchar = s[end : end + 1]
        end += 1
        if nextchar != '"':
            raise JSONDecodeError(
                "Expecting property name enclosed in double quotes", s, end - 1
            )
    if not raw:
        if object_pairs_hook is not None:
            result = object_pairs_hook(pairs)
            return result, end
        if object_ is not None:
            if lock:
                object_.lock()  # type: ignore
            pairs = object_
        else:
            pairs = dict(pairs)  # type: ignore
    else:
        pairs = s[i_end:end]
    if object_hook is not None:
        pairs = object_hook(pairs)
    return pairs, end


def JSONArray(  # noqa: N802
    s_and_end,
    scan_once,
    object_: S,
    lock=False,
    raw=False,
    _w=WHITESPACE.match,
    _ws=WHITESPACE_STR,
):
    s, end = s_and_end
    i_end = end-1
    values: List[Any] = []
    nextchar = s[end : end + 1]
    if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end : end + 1]
    # Look-ahead for trivial empty array
    if nextchar == "]":
        if raw:
            values = "[]"  # type: ignore
        return values, end + 1
    _append = values.append
    while True:
        try:
            value, end = scan_once(s, end, object_, lock, raw)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        if not raw:
            _append(value)
        nextchar = s[end : end + 1]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end : end + 1]
        end += 1
        if nextchar == "]":  # pylint: disable=no-else-break
            break
        elif nextchar != ",":
            raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

    if raw:
        values = s[i_end:end]

    return values, end


class JSONDecoder:  # pylint: disable=too-many-instance-attributes;
    r"""Simple JSON <http://json.org> decoder

    Performs the following translations in decoding by default:

    +---------------+-------------------+
    | JSON          | Python            |
    +===============+===================+
    | object        | dict, Struct, str |
    +---------------+-------------------+
    | array         | list, str         |
    +---------------+-------------------+
    | string        | str               |
    +---------------+-------------------+
    | number (int)  | int, str          |
    +---------------+-------------------+
    | number (real) | float, str        |
    +---------------+-------------------+
    | true          | True, str         |
    +---------------+-------------------+
    | false         | False, str        |
    +---------------+-------------------+
    | null          | None, str         |
    +---------------+-------------------+

    It also understands ``NaN``, ``Infinity``, and ``-Infinity`` as
    their corresponding ``float`` values, which is outside the JSON spec.

    """

    def __init__(
        self,
        *,
        object_hook=None,
        parse_float=None,
        parse_int=None,
        parse_constant=None,
        strict=True,
        object_pairs_hook=None
    ) -> None:
        r"""``object_hook``, if specified, will be called with the result
        of every JSON object decoded and its return value will be used in
        place of the given ``dict``.  This can be used to provide custom
        deserializations (e.g. to support JSON-RPC class hinting).

        ``object_pairs_hook``, if specified will be called with the result of
        every JSON object decoded with an ordered list of pairs.  The return
        value of ``object_pairs_hook`` will be used instead of the ``dict``.
        This feature can be used to implement custom decoders.
        If ``object_hook`` is also defined, the ``object_pairs_hook`` takes
        priority.

        ``parse_float``, if specified, will be called with the string
        of every JSON float to be decoded. By default this is equivalent to
        float(num_str). This can be used to use another datatype or parser
        for JSON floats (e.g. decimal.Decimal).

        ``parse_int``, if specified, will be called with the string
        of every JSON int to be decoded. By default this is equivalent to
        int(num_str). This can be used to use another datatype or parser
        for JSON integers (e.g. float).

        ``parse_constant``, if specified, will be called with one of the
        following strings: -Infinity, Infinity, NaN.
        This can be used to raise an exception if invalid JSON numbers
        are encountered.

        If ``strict`` is false (true is the default), then control
        characters will be allowed inside strings.  Control characters in
        this context are those with character codes in the 0-31 range,
        including ``'\\t'`` (tab), ``'\\n'``, ``'\\r'`` and ``'\\0'``.
        """
        self.object_hook = object_hook
        self.parse_float = parse_float or float
        self.parse_int = parse_int or int
        self.parse_constant = parse_constant or _CONSTANTS.__getitem__
        self.strict = strict
        self.object_pairs_hook = object_pairs_hook
        self.parse_object = JSONObject
        self.parse_array = JSONArray
        self.parse_string = scanstring
        self.memo: Dict[Any, Any] = {}
        self.scan_once = scanner.make_scanner(self)

    def decode(
        self, s, object_: S, lock=False, _w=WHITESPACE.match
    ):
        r"""Return the Python representation of ``s`` (a ``str`` instance
        containing a JSON document).

        May return the following:
        - List
        - Dict
        - Struct Object (instance)
        - Boolean
        - String
        - Integer/Float

        """
        obj, end = self.raw_decode(s, object_, lock, idx=_w(s, 0).end())
        end: int = _w(s, end).end()  # type: ignore
        if end != len(s):
            raise JSONDecodeError("Extra data", s, end)
        return obj

    def raw_decode(
        self, s, object_: S, lock=False, idx=0
    ):
        r"""Decode a JSON document from ``s`` (a ``str`` beginning with
        a JSON document) and return a 2-tuple of the Python
        representation and the index in ``s`` where the document ended.

        This can be used to decode a JSON document from a string that may
        have extraneous data at the end.

        """
        try:
            obj, end = self.scan_once(s, idx, object_, lock)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        return obj, end
