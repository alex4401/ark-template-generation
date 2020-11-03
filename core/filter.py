import yaml
import copy
from typing import List, Dict, Optional, Type, Any

from .const import CORE_GAME

_FILTERS_: Dict[str, Type] = dict()


def namespace(name):
    def _ns_filter_(kls):
        _FILTERS_[name] = kls
        return kls

    return _ns_filter_


class Deserializable:
    def __init__(self):
        for field_name in self.get_fields():
            value = getattr(self, field_name, None)
            if value:
                setattr(self, field_name, copy.deepcopy(value))

    def get_fields(self):
        # Yields all type annotations from this object.
        yield from self.__annotations__.keys()

        for base in type(self).__bases__:
            if getattr(base, '__annotations__', None):
                yield from base.__annotations__.keys()

    def update(self, source: Dict[str, Any], override=False):
        for field_name in self.get_fields():
            field = source.get(field_name, None)

            if field != None:
                existing = getattr(self, field_name, None)
                if not override and existing:
                    # Pass data to a Deserializable object
                    if isinstance(existing, Deserializable):
                        existing.update(field, override)
                    # Join lists and dicts
                    elif isinstance(existing, list):
                        existing += field
                        continue
                    elif isinstance(existing, dict):
                        existing = {**existing, **field}
                        continue

                # Set field list
                setattr(self, field_name, field)


@namespace('default')
class Filter(Deserializable):
    path: str
    modId: str = CORE_GAME
    modNameOverride: Optional[str] = None

    displayVariants: Dict[str, str] = dict()

    dinoNameOverrides: Dict[str, str] = dict()
    matchRegex: Dict[str, str] = dict()
    includeDinoClasses: List[str] = list()
    ignoreDinoClasses: List[str] = list()
    ignoreDinoBPs: List[str] = list()
    ignoreDinosWithVariants: List[str] = list()

    skipMaps: List[str] = list()
    worldNameOverrides: Dict[str, str] = dict()
    worldNamesCSV: List[str] = list()

    debugNames: bool = False


def load_filter(filename: str) -> Filter:
    with open(filename, 'rt') as fp:
        doc = yaml.safe_load(fp)

    nsname = doc.get('namespace', 'default')
    fltcls = _FILTERS_[nsname]

    if 'import' in doc:
        out = load_filter(doc['import'])
        assert isinstance(out, fltcls)
    else:
        out = fltcls()

    flt_data = doc['filter']
    out.path = filename
    out.update(flt_data)

    overrides = doc.get('overrides', None)
    if overrides:
        out.update(overrides, override=True)

    return out
