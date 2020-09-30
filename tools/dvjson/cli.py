import sys

from typing import Dict, Any, List, Iterable
from pathlib import Path
from collections import namedtuple

from core import blueprint, dino, cli
from core.file import load_json, query, validate, dump_json
from core.filter import load_filter
from core.jsonutils import format_json
from .const import DinoData, WHITELISTED_FIELDS
from .filter_ext import FilterDv
from .mwimpl import get_dv_compatible_key, prepare_object


def run():
    obelisk_path = cli.get_path('obelisk', Path('data/obelisk'))
    output_path = cli.get_path('output_path', Path('output/dv.json'))
    filter_path = cli.get_path('filter', Path('filters/dv_filter.yml'))
    flt = load_filter(filter_path)
    assert isinstance(flt, FilterDv)
    main(flt, obelisk_path, output_path)


DataCollection = namedtuple('DataCollection', ('stats', 'extended'))


def main(flt: FilterDv, obelisk_path: Path, output_path: Path):
    data = DataCollection(
        stats=load_json(obelisk_path / 'data/asb/values.json'),
        extended=load_json(obelisk_path / 'data/wiki/species.json'),
    )
    game_version = max(data.extended['version'], data.stats['version'])

    # Sort data arrays
    sort_key = lambda dino_data: dino.get_descriptive_name(flt, dino_data)
    data.stats['species'].sort(key=sort_key)
    data.extended['species'].sort(key=sort_key)

    # Zip up dino data
    for dino1 in data.stats['species']:
        for dino2 in data.extended['species']:
            if dino1['blueprintPath'] == dino2['bp'][:-2]:
                dino1['extra'] = dino2
                break
    species = data.stats['species']
    for dino1 in species:
        if 'extra' not in dino1:
            bp1 = dino1['blueprintPath']
            print(f'Zipping error: {bp1} does not have any extended data.')
            dino1['extra'] = dict()

    results: Dict[str, Dict[str, Any]] = dict()
    for dino_data in query(
            species,
            dict(where=lambda x: dino.should_skip(flt, x), equals=False),
    ):
        lookup_key = get_dv_compatible_key(flt, dino_data)
        out: Dict[str, Any] = dict()

        for field in WHITELISTED_FIELDS:
            value = dino_data.get(field, None) \
                    or dino_data['extra'].get(field, None)
            if value != None:
                out[field] = value

        if lookup_key in results:
            bp1 = results[lookup_key]['bp']
            bp2 = out['bp']
            message = f'Look-up key collision: {lookup_key}\n'
            message += f'\tdino A:\t{bp1}\n'
            message += f'\tdino B:\t{bp2}\n'
            print(message)
            continue
        results[lookup_key] = out

    packed = dict(
        version=game_version,
        species=results,  #prepare_object(results),
    )
    output = format_json(packed, True)
    output_path.write_text(output)