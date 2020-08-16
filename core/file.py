import json

from typing import Dict, Any, List, Iterable

JsonData = Dict[str, Any]


def load_json(filename: str) -> JsonData:
    with open(filename, 'rt') as fp:
        return json.load(fp)

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
            
            if callable(where):
            	val = where(entry)
            else:
            	val = entry.get(where, None)
            
            if not ( (contained_in and val in contained_in) \
                or   (equals and val == equals) \
                or   (not_null and val) ):
                break
        else:
            yield entry

