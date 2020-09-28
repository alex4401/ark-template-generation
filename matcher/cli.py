import sys
import re

from typing import Dict, Any, List, Iterable, Tuple
from difflib import SequenceMatcher

from core import blueprint, dino
from core.file import load_json, query, dump_json, JsonData

STARTING_THRESHOLD = 0.90
THRESHOLD_DROP = 0.05
THRESHOLD_MIN = 0.49
EXT_SIMILARITY = 'x-name-similarity'
VARIANT_MAP = {
    'Alpha': 'Hard',
    'Beta': 'Medium',
    'Gamma': 'Easy',
}

RE_CLEAN = r'\((Beta|Medium|Easy|Gamma|Alpha|Hard)\)'
CLEAN_WEIGHT = 0.3


def is_dino_name_similar(a: JsonData, b: str) -> float:
    name = dino.get_descriptive_name(None, a)
    class_name = blueprint.get_class_name(a)

    ratio_name = SequenceMatcher(None, name, b).ratio()
    penalty = 0.0

    if '(' in b and ')' in b:
        ratio_name *= (1.0 - CLEAN_WEIGHT)
        ratio_name += SequenceMatcher(None, name, re.sub(
            RE_CLEAN, '', b)).ratio() * CLEAN_WEIGHT

    for variant in a.get('variants', []):
        if variant in b or VARIANT_MAP.get(variant, variant) in b:
            penalty -= 0.064
        else:
            penalty += 0.025

    a[EXT_SIMILARITY] = min(1.0, ratio_name - penalty)
    return a[EXT_SIMILARITY]


def run(source_filename: str, list_filename: str):
    species = load_json(source_filename)
    name_list = load_json(list_filename)

    species = species['species']

    species.sort(
        key=lambda dino_data: dino.get_descriptive_name(None, dino_data))

    for dino_name in name_list:
        print()
        print(dino_name)

        THRESHOLD = STARTING_THRESHOLD

        results: List[Tuple[str, ...]] = list()
        while not results and THRESHOLD >= THRESHOLD_MIN:
            for dino_data in query(
                    species,
                    dict(where=lambda x: is_dino_name_similar(x, dino_name),
                         greater_than=THRESHOLD)):
                ratio = dino_data[EXT_SIMILARITY]
                name = dino.get_descriptive_name(None, dino_data)
                class_name = blueprint.get_class_name(dino_data)
                results.append((f'{round(ratio, 2) * 100}%', name, class_name))
            THRESHOLD -= THRESHOLD_DROP

        for result in results:
            print('-', result[1], f'({result[2]})', result[0])
