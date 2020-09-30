import sys

from typing import Dict, Any, List, Iterable, Tuple, Union, Callable

from core import blueprint, dino, cli
from core.file import load_json, query, validate, dump_json
from core.filter import load_filter, Filter
from .const import DinoData, CLONING_SECTION, \
                   BASE_COST, LEVEL_COST, BASE_TIME, LEVEL_TIME
from .filter_ext import FilterCloning
from pathlib import Path

OutputTupleCCTT = Tuple[float, float, float, float]
OutputTupleCC = Tuple[float, float]
DinoCloningValues = Union[OutputTupleCC, OutputTupleCCTT]


def run():
    obelisk_path = cli.get_path('obelisk', Path('data/obelisk'))
    filter_path = cli.get_path('filter', Path('filters/cloning_filter.yml'))
    flt = load_filter(filter_path)
    assert isinstance(flt, FilterCloning)
    main(flt, obelisk_path)


def sort_dinos_by_name(flt: Filter) -> Callable[[DinoData], str]:
    def _key_(data: DinoData):
        return dino.get_descriptive_name(flt, data)

    return _key_


def main(flt: FilterCloning, obelisk_path: Path):
    species = load_json(obelisk_path /
                        'data/wiki/species.json')  # TODO: allow mods

    game_version = species['version']
    species = species['species']
    species.sort(key=sort_dinos_by_name(flt))

    if flt.dinoClasses:
        validate(species,
                 contains_range=flt.dinoClasses,
                 of=blueprint.get_class_name)
        conditions = [
            dict(where=blueprint.get_class_name, contained_in=flt.dinoClasses)
        ]
    else:
        conditions = [
            dict(where=lambda x: dino.should_skip(flt, x), equals=True)
        ]

    results: Dict[str, DinoCloningValues] = dict()
    for dino_data in query(species, *conditions,
                           dict(where=CLONING_SECTION, not_null=True)):
        cloning = dino_data[CLONING_SECTION]
        cost_base = cloning[BASE_COST]
        cost_level = cloning[LEVEL_COST]
        time_base = cloning[BASE_TIME]
        time_level = cloning[LEVEL_TIME]

        out: DinoCloningValues = (cost_base, cost_level, time_base, time_level)
        name = dino.get_descriptive_name(flt, dino_data)

        if not flt.includeCloningTimes:
            out = out[:2]

        results[name] = out

    print('// Version:', game_version)
    print(dump_json(flt, results))
