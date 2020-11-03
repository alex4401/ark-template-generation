import sys

from typing import Dict, Any, List, Iterable, Callable, Tuple
from pathlib import Path
from collections import namedtuple
from tabulate import tabulate
from dataclasses import dataclass

from core import blueprint, dino, cli
from core.file import load_json, query, validate, dump_json
from core.filter import load_filter, Filter
from tools.dvjson.filter_ext import FilterDv
from tools.dvjson.mwimpl import get_dv_compatible_key


def run():
    obelisk_path = cli.get_path('obelisk', Path('data/obelisk'))
    filter_path = cli.get_path('filter', Path('filters/dv_filter.yml'))
    output_path = cli.get_path('output_path',
                               Path('output/selector-test-report.txt'))
    flt = load_filter(filter_path)
    main(flt, obelisk_path, output_path)


DinoData = Dict[str, Any]


def sort_dinos_by_name(flt: Filter) -> Callable[[DinoData], str]:
    def _key_(data: DinoData):
        return dino.get_descriptive_name(flt, data)

    return _key_


def get_asset_path(bp_path) -> str:
    return bp_path[:bp_path.rindex('.')]


@dataclass
class ToolResults:
    included: List[Tuple[str, str, str]]
    ignored: List[Tuple[str, str]]
    dv_conflicts: List[Tuple[str, str, str]]
    name_conflicts: List[Tuple[str, str, str]]


def main(flt: Filter, obelisk_path: Path, output_path: Path):
    species = load_json(obelisk_path /
                        'data/wiki/species.json')  # TODO: allow mods

    game_version = species['version']
    species = species['species']
    species.sort(key=sort_dinos_by_name(flt))

    results = ToolResults(
        included=[],
        ignored=[],
        dv_conflicts=[],
        name_conflicts=[],
    )
    should_output_dv = isinstance(flt, FilterDv)
    dvset: Dict[str, str] = dict()
    nameset: Dict[str, str] = dict()

    for dino_data in species:
        info: Tuple[str, ...]
        descriptive_name = dino.get_descriptive_name(flt, dino_data)

        if dino.should_skip(flt, dino_data):
            info = (
                # BP path
                get_asset_path(dino_data['bp']),
                # Name
                descriptive_name,
            )
            results.ignored.append(info)
            continue

        dv_key = get_dv_compatible_key(
            flt, dino_data) if should_output_dv else 'N/A'
        info = (
            # BP path
            get_asset_path(dino_data['bp']),
            # Name
            descriptive_name,
            # Dv key
            dv_key,
        )
        results.included.append(info)

        if descriptive_name in nameset:
            results.name_conflicts.append((
                # BP path 1
                get_asset_path(nameset[descriptive_name]),
                # BP path 2
                get_asset_path(dino_data['bp']),
                # Name
                descriptive_name,
            ))
            continue

        if dv_key in dvset and should_output_dv:
            results.dv_conflicts.append((
                # BP path 1
                get_asset_path(nameset[descriptive_name]),
                # BP path 2
                get_asset_path(dino_data['bp']),
                # Key
                dv_key,
            ))
            continue

        nameset[descriptive_name] = dino_data['bp']
        dvset[dv_key] = dino_data['bp']

    text = '\n'.join([
        '=== INCLUDED CREATURES ===',
        '',
        tabulate(results.included, ('Blueprint Path', 'Name', 'Dv ID')),
        '',
        '',
        '=== NAME CONFLICTS ===',
        '',
        tabulate(results.name_conflicts,
                 ('Blueprint Path A', 'Blueprint Path B', 'Name')),
        '',
        '',
        '=== DV CONFLICTS ===',
        '',
        tabulate(results.dv_conflicts,
                 ('Blueprint Path A', 'Blueprint Path B', 'Dv ID')),
        '',
        '',
        '=== SKIPPED CREATURES ===',
        '',
        tabulate(results.ignored, ('Blueprint Path', 'Name')),
    ])
    output_path.write_text(text)