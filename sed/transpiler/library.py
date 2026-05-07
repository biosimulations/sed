import math


def parse_hash(var_hash):
    return var_hash[1:].split(":")[1:]


def python_literal(value):
    """Return a string that, when used as a Python expression, evaluates to
    `value`.  This walks lists/tuples/dicts recursively and emits the special
    forms `float('nan')`, `float('inf')`, and `float('-inf')` for non-finite
    floats, since Python's repr for those is bare `nan`/`inf`/`-inf`, which
    are not valid Python literals at runtime.
    """
    if isinstance(value, bool):
        return repr(value)
    if isinstance(value, float):
        if math.isnan(value):
            return "float('nan')"
        if math.isinf(value):
            return "float('inf')" if value > 0 else "float('-inf')"
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(python_literal(v) for v in value) + "]"
    if isinstance(value, tuple):
        inner = ", ".join(python_literal(v) for v in value)
        if len(value) == 1:
            inner += ","
        return "(" + inner + ")"
    if isinstance(value, dict):
        return "{" + ", ".join(
            f"{python_literal(k)}: {python_literal(v)}" for k, v in value.items()
        ) + "}"
    return repr(value)


# Keys here are lower-cased; lookups should lower-case the candidate string
# first.  All the usual aliases for non-finite floats are accepted.
_SPECIAL_FLOAT_STRINGS = {
    "nan":       float("nan"),
    "inf":       float("inf"),
    "-inf":      float("-inf"),
    "infinity":  float("inf"),
    "-infinity": float("-inf"),
}


def _special_value(s):
    """If `s` is a string spelling of NaN/Inf (any letter case), return the
    corresponding float.  Otherwise return None.
    """
    if isinstance(s, str):
        return _SPECIAL_FLOAT_STRINGS.get(s.lower())
    return None


def interpret_special_strings(value):
    """Recursively walk a JSON-loaded value and convert "NaN"/"Inf"/"-Inf"
    strings (any letter case, plus the longer "Infinity"/"-Infinity" forms)
    to the corresponding floats when context indicates numeric intent.
    JSON booleans (true/false) load as Python bools, which are an int
    subclass and are therefore treated numerically here.

    Per-list classification:
      * Numbers (ints, floats, booleans) alongside special strings -> the
        special strings become floats.
      * Only special strings -> all become floats (numeric reading
        preferred when ambiguous).
      * Non-special strings and no numbers -> specials stay as strings.
      * Numbers and non-special strings in the same list -> ValueError.

    Dict values are recursed; dict keys are left untouched.  Nested lists
    are classified independently of their parent.
    """
    if isinstance(value, dict):
        return {k: interpret_special_strings(v) for k, v in value.items()}

    if isinstance(value, list):
        items = [
            interpret_special_strings(v) if isinstance(v, (list, dict)) else v
            for v in value
        ]

        has_number = any(isinstance(v, (int, float)) for v in items)
        has_plain_string = any(
            isinstance(v, str) and _special_value(v) is None
            for v in items
        )
        if has_number and has_plain_string:
            raise ValueError(
                "List contains a mix of numbers and strings, which is not "
                f"allowed: {items!r}"
            )

        special_idxs = {i for i, v in enumerate(items)
                        if isinstance(v, str) and _special_value(v) is not None}
        if not special_idxs:
            return items

        non_special = [v for i, v in enumerate(items) if i not in special_idxs]

        if not non_special:
            return [_special_value(v) for v in items]

        if all(isinstance(v, (int, float)) for v in non_special):
            return [_special_value(v) if (isinstance(v, str)
                                           and _special_value(v) is not None)
                    else v
                    for v in items]

        return items

    return value
