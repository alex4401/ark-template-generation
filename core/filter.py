import yaml
import copy
from pathlib import Path
from typing import List, Dict, Optional, Type, Any, cast, Union

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
            if value != None:
                setattr(self, field_name, copy.deepcopy(value))

    def get_fields(self):
        # Yields all type annotations from this object.
        yield from self.__annotations__.keys()

        for base in type(self).__bases__:
            if getattr(base, '__annotations__', None):
                yield from base.__annotations__.keys()

    def update(self, source: Any, override=False):
        for field_name in self.get_fields():
            field = source.get(field_name, None)

            if field != None:
                existing = getattr(self, field_name, None)
                if not override and existing:
                    # Pass data to a Deserializable object
                    if isinstance(existing, Deserializable):
                        existing.update(field, override)
                        continue
                    # Join lists and dicts
                    elif isinstance(existing, list):
                        existing += field
                        continue
                    elif isinstance(existing, dict):
                        existing = {**existing, **field}
                        continue

                # Set field list
                setattr(self, field_name, field)


BPTree = List[Union[str, Dict[str, Any]]]


class CreatureBPList(Deserializable):
    values: List[Path] = list()

    def update(self, source: Any, override=False):
        source = cast(BPTree, source)
        if override:
            self.values = list()

        self.update_slice(source)

    def clean_node(self, node: str) -> str:
        return node.strip('/ ')

    def update_slice(self, source: Union[str, BPTree], path: List[str] = ['']):
        if isinstance(source, str):
            result = Path('/'.join([*path, self.clean_node(source)]))
            self.values.append(result)
            return

        if isinstance(source, list):
            for node in source:
                self.update_slice(node, path)  # type:ignore
            return

        if isinstance(source, dict):
            for node, sub in source.items():
                node = self.clean_node(node)
                self.update_slice(sub, [*path, node])
            return

        raise ValueError('Unknown field type when updating CreatureBPList')

    def __contains__(self, item: str):
        # End if list is empty
        if not self.values:
            return False

        itemp = Path(item)
        for node in self.values:
            # Check if the node is the same as item or a parent of itemp
            if node == itemp or node in itemp.parents:
                return True

        return False


class CreatureSelectors(Deserializable):
    matchRegex: Dict[str, str] = dict()
    includeClasses: List[str] = list()
    ignoreClasses: List[str] = list()
    includeBPs: CreatureBPList = CreatureBPList()
    ignoreBPs: CreatureBPList = CreatureBPList()
    ignoreVariants: List[str] = list()


@namespace('default')
class Filter(Deserializable):
    path: str
    modId: str = CORE_GAME
    modNameOverride: Optional[str] = None

    selectors: CreatureSelectors = CreatureSelectors()
    displayVariants: Dict[str, str] = dict()
    dinoNameOverrides: Dict[str, str] = dict()

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
