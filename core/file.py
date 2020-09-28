import json
import re

from typing import Dict, Any, List, Iterable
from .filter import Filter

JsonData = Dict[str, Any]

# Reduce 2-12 numbers in an array onto a single line
JOIN_MULTIPLE_NUMBERS_REGEX = re.compile(
    r'(\n\s+)[-+.\de]+,(?:\n\s+(?:[-+.\de"]|null)+,?){1,12}')

# Reduce arrays with only a single line of content (including previously joined multiple fields) to a single line
COLLAPSE_SINGLE_LINE_ARRAY_REGEX = re.compile(r'\[\s+(.+)\s+\]')


def load_json(filename: str) -> JsonData:
    with open(filename, 'rt') as fp:
        return json.load(fp)


def _flatten_re_result(match):
    txt = match[0]
    txt = re.sub(r'\s*\n\s+', '', txt)
    txt = txt.replace(',', ', ')
    return f'{match[1]}{txt}'


def dump_json(flt: Filter, data: JsonData) -> str:
    if flt.prettifyOutput:
        result = json.dumps(data, indent='  ')
        result = re.sub(JOIN_MULTIPLE_NUMBERS_REGEX, _flatten_re_result,
                        result)
        result = re.sub(COLLAPSE_SINGLE_LINE_ARRAY_REGEX, r"[ \1 ]", result)
        return result
    else:
        return json.dumps(data, indent=None)


def load_strml(filename: str) -> List[str]:
    with open(filename, 'rt') as fp:
        lines = fp.read().split('\n')
        return [line for line in lines if not line.startswith('#')]


def query(data: List[JsonData], *conditions) -> Iterable[JsonData]:
    for entry in data:
        for args in conditions:
            where = args['where']
            contained_in = args.get('contained_in', None)
            equals = args.get('equals', None)
            not_null = args.get('not_null', None)
            greater_than = args.get('greater_than', None)

            if callable(where):
                val = where(entry)
            else:
                val = entry.get(where, None)

            if not ( (contained_in and val in contained_in) \
                or   (equals != None and val == equals) \
                or   (not_null and val) \
                or   (greater_than and val > greater_than) ):
                break
        else:
            yield entry


def validate(data: List[JsonData], contains_range=None, of=None):
    tracker = set()

    for entry in data:
        if callable(of):
            val = of(entry)
        else:
            val = entry.get(of, None)
        tracker.add(val)

    diff = set(contains_range) - tracker
    if diff:
        message = 'This data cannot be used to cover the filter: following entries could not be satisfied.\n\n' \
                  + ', '.join(diff)
        raise ValueError(message)
