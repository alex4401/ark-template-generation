import json
import sys

from typing import Dict, Any, List, Iterable

from core import blueprint, dino
from core.file import load_json, query
from core.filter import load_filter
from .const import DinoData, CLONING_SECTION, \
                   BASE_COST, LEVEL_COST, BASE_TIME, LEVEL_TIME


def run(source_filename: str, filter_filename: str):
    species = load_json(source_filename)
    
    flt = load_filter(filter_filename)
    limits = flt.dinoClasses

    game_version = species['version']
    species = species['species']
    
    species.sort(key=lambda entry: entry['name'])

    results = dict()
    for dino_data in query(species,
                           dict(where=blueprint.get_class_name, contained_in=limits),
                           dict(where=CLONING_SECTION, not_null=True)):
        cloning = dino_data[CLONING_SECTION]
        cost_base = cloning[BASE_COST]
        cost_level = cloning[LEVEL_COST]
        time_base = cloning[BASE_TIME]
        time_level = cloning[LEVEL_TIME]
        
        out = (cost_base, cost_level, time_base, time_level)
        name = dino.get_descriptive_name(flt, dino_data)
        results[name] = out

    print('// Version:', game_version)
    print(json.dumps(results))

