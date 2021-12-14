__all__ = ("NamedDict", "NamedDictMeta", "JSONConfig", "decoder")

import json
import re
from json import JSONDecoder, JSONDecodeError, JSONEncoder
from json.decoder import WHITESPACE, WHITESPACE_STR, scanstring  # type: ignore

from .nameddict import (
    is_named_dict_class,
    NamedDictMeta,
    NamedDict,
    _get_key_config,
    JSONConfig,
)

NUMBER_RE = re.compile(
    r"(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?",
    (re.VERBOSE | re.MULTILINE | re.DOTALL),
)


# -------
# SCANNER
# -------
def scanner(context):
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

    def _scan_once(string, idx, obj=None, raw=False):
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
                obj=obj,
                raw=raw,
                memo=memo,
            )
        elif nextchar == "[":
            return parse_array((string, idx + 1), _scan_once, obj=obj, raw=raw)
        elif nextchar == "n" and string[idx : idx + 4] == "null":
            return None, idx + 4
        elif nextchar == "t" and string[idx : idx + 4] == "true":
            return True, idx + 4
        elif nextchar == "f" and string[idx : idx + 5] == "false":
            return False, idx + 5

        m = match_number(string, idx)  # pylint: disable=invalid-name
        if m is not None:
            integer, frac, exp = m.groups()
            if frac or exp:
                res = parse_float(integer + (frac or "") + (exp or ""))
            else:
                res = parse_int(integer)
            return res, m.end()
        elif nextchar == "N" and string[idx : idx + 3] == "NaN":
            return parse_constant("NaN"), idx + 3
        elif nextchar == "I" and string[idx : idx + 8] == "Infinity":
            return parse_constant("Infinity"), idx + 8
        elif nextchar == "-" and string[idx : idx + 9] == "-Infinity":
            return parse_constant("-Infinity"), idx + 9
        else:
            raise StopIteration(idx)

    def scan_once(string, idx, obj=None):
        try:
            return _scan_once(string, idx, obj=obj)
        finally:
            memo.clear()

    return scan_once


def JSONObject(  # pylint: disable=invalid-name;
    s_and_end,
    strict,
    scan_once,
    object_hook,
    object_pairs_hook,
    obj=None,
    raw=False,
    memo=None,
    _w=WHITESPACE.match,
    _ws=WHITESPACE_STR,
):
    s, end = s_and_end  # pylint: disable=invalid-name
    if not raw:
        if obj is not None and is_named_dict_class(obj):
            pairs = obj()
            pairs_append = lambda n_and_v: pairs.__setattr__(  # noqa: E731
                *n_and_v
            )
        else:
            obj = None
            pairs = []
            pairs_append = pairs.append
    else:
        pairs = ""
        i_end = end - 1
    if memo is None:
        memo = {}
    memo_get = memo.setdefault
    nextchar = s[end : end + 1]
    if nextchar != '"':
        if nextchar in _ws:
            end = _w(s, end).end()
            nextchar = s[end : end + 1]
        if nextchar == "}":
            if object_pairs_hook is not None:
                result = object_pairs_hook(pairs)
                return result, end + 1
            if obj is None:
                pairs = {}
            if raw:
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
        conf = _get_key_config(pairs, key)
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
            value, end = scan_once(s, end, obj=conf.object, raw=conf.raw)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        if not raw:
            if obj is not None:
                key = conf.attrname
            if conf.load_hook is not None:
                value = conf.load_hook(value)
            pairs_append((key, value))
        try:
            nextchar = s[end]
            if nextchar in _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        except IndexError:
            nextchar = ""
        end += 1

        if nextchar == "}":
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
    if raw:
        pairs = s[i_end:end]
    if object_pairs_hook is not None:
        result = object_pairs_hook(pairs)
        return result, end
    if obj is None and not raw:
        pairs = dict(pairs)
    if object_hook is not None:
        pairs = object_hook(pairs)
    return pairs, end


def JSONArray(  # pylint: disable=invalid-name;
    s_and_end,
    scan_once,
    obj=None,
    raw=False,
    _w=WHITESPACE.match,
    _ws=WHITESPACE_STR,
):
    s, end = s_and_end  # pylint: disable=invalid-name
    i_end = end - 1
    if not raw:
        values = []
    else:
        values = ""
    nextchar = s[end : end + 1]
    if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end : end + 1]
    # Look-ahead for trivial empty array
    if nextchar == "]":
        values = "[]"
        return values, end + 1
    if not raw:
        _append = values.append
    while True:
        try:
            value, end = scan_once(s, end, obj=obj, raw=raw)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        if not raw:
            _append(value)
        nextchar = s[end : end + 1]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end : end + 1]
        end += 1
        if nextchar == "]":
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


class FurJSON(JSONDecoder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parse_object = JSONObject
        self.parse_array = JSONArray
        self.scan_once = scanner(self)

    def decode(
        self, s, obj=None, _w=WHITESPACE.match
    ):  # pylint: disable=arguments-differ
        """Return the Python representation of ``s`` (a ``str`` instance
        containing a JSON document).
        """
        obj_, end = self.raw_decode(s, obj=obj, idx=_w(s, 0).end())
        end = _w(s, end).end()
        if end != len(s):
            raise JSONDecodeError("Extra data", s, end)
        return obj_

    def raw_decode(
        self, s, obj=None, idx=0
    ):  # pylint: disable=arguments-differ
        """Decode a JSON document from ``s`` (a ``str`` beginning with
        a JSON document) and return a 2-tuple of the Python
        representation and the index in ``s`` where the document ended.
        This can be used to decode a JSON document from a string that may
        have extraneous data at the end.
        """
        try:
            obj_, end = self.scan_once(s, idx, obj=obj)
        except StopIteration as err:
            raise JSONDecodeError("Expecting value", s, err.value) from None
        return obj_, end


decoder = FurJSON()
encoder: JSONEncoder = json._default_encoder  # type: ignore # pylint: disable=protected-access

loads = decoder.decode
dumps = encoder.encode
