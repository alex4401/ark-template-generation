import yaml
from typing import List, Dict, Optional, Type
from .const import CORE_GAME

_FILTERS_: Dict[str, Type] = dict()


def namespace(name):
    def _ns_filter_(kls):
        _FILTERS_[name] = kls
        return kls

    return _ns_filter_


@namespace('default')
class Filter:
    path: str
    modId: str = CORE_GAME
    modNameOverride: Optional[str] = None

    dinoNameOverrides: Dict[str, str] = dict()
    includeDinoClasses: List[str] = list()
    ignoreDinoClasses: List[str] = list()
    ignoreDinoBPs: List[str] = list()
    ignoreDinosWithVariants: List[str] = list()

    skipMaps: List[str] = list()
    worldNameOverrides: Dict[str, str] = dict()
    worldNamesCSV: List[str] = list()

    debugNames: bool = False


def load_filter(filename: str) -> Filter:
    def _set_fields(source, override=False):
        # Get all type annotations from the filter class
        # and all its parents.
        field_names = list(out.__annotations__.keys())
        for base in type(out).__bases__:
            if getattr(base, '__annotations__', None):
                field_names += base.__annotations__.keys()

        for field_name in field_names:
            field = source.get(field_name, None)

            if field != None:
                existing = getattr(out, field_name, None)
                if not override and existing:
                    # Join lists and dicts
                    if isinstance(existing, list):
                        existing += field
                        continue
                    elif isinstance(existing, dict):
                        existing = {**existing, **field}
                        continue

                # Set field list
                setattr(out, field_name, field)

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
    _set_fields(flt_data)
    if 'override' in flt_data:
        _set_fields(flt_data['override'], True)

    return out
