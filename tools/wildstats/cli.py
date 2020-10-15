import sys

from typing import Dict, Any, List, Iterable, Tuple, Union, Callable

from core import blueprint, dino, cli
from core.file import load_json, query, validate, dump_json
from core.filter import load_filter, Filter
from .const import DinoData
from .filter_ext import FilterWildStatCalc
from pathlib import Path

DinoStatValues = Dict[str, float]


def run():
    obelisk_path = cli.get_path('obelisk', Path('data/obelisk'))
    filter_path = cli.get_path('filter', Path('filters/wildstats_filter.yml'))
    flt = load_filter(filter_path)
    assert isinstance(flt, FilterWildStatCalc)
    main(flt, obelisk_path)


def sort_dinos_by_name(flt: Filter) -> Callable[[DinoData], str]:
    def _key_(data: DinoData):
        return dino.get_descriptive_name(flt, data)

    return _key_


def main(flt: FilterWildStatCalc, obelisk_path: Path):
    species = load_json(obelisk_path /
                        'data/asb/values.json')  # TODO: allow mods
    
    for official_mod in flt.linkMods:
        extra = load_json(obelisk_path / 'data/asb' / f'{official_mod}-{official_mod}.json')
        species['species'] += extra['species']

    game_version = species['version']
    species = species['species']
    species.sort(key=sort_dinos_by_name(flt))

    if flt.includeDinoClasses:
        validate(species,
                 contains_range=flt.includeDinoClasses,
                 of=blueprint.get_class_name)

    results: Dict[str, DinoStatValues] = dict()
    for dino_data in query(species,
                           dict(where=lambda x: dino.should_skip(flt, x), equals=False),
                           dict(where='fullStatsRaw', not_null=True)):
        name = dino.get_descriptive_name(flt, dino_data)
        stats = dino_data['fullStatsRaw']
        uses_oxygen = not dino_data['doesNotUseOxygen']

        out: DinoStatValues = dict()
        out['health1'] = stats[0][0]
        out['healthInc'] = stats[0][1]
        out['stamina1'] = stats[1][0]
        out['staminaInc'] = stats[1][1]
        if uses_oxygen:
            out['oxygen1'] = stats[3][0]
            out['oxygenInc'] = stats[3][1]
        out['food1'] = stats[4][0]
        out['foodInc'] = stats[4][1]
        out['weight1'] = stats[7][0]
        out['weightInc'] = stats[7][1]
        out['damage1'] = stats[8][0] * 100
        out['damageInc'] = stats[8][1]

        if name in results:
            print('Found a conflict between two dinos:')
            print(f'"{name}" and "{dino_data["blueprintPath"]}"')
        results[name] = out

    print('// Version:', game_version)
    print(dump_json(flt, results))
