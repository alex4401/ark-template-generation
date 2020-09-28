import sys

from typing import Dict, Any, List, Iterable

from core import blueprint, dino
from core.file import load_json, query, validate, dump_json
from core.filter import load_filter
from .const import DinoData, CLONING_SECTION, \
                   BASE_COST, LEVEL_COST, BASE_TIME, LEVEL_TIME


def run(source_filename: str, filter_filename: str):
    species = load_json(source_filename)
    
    flt = load_filter(filter_filename)

    game_version = species['version']
    species = species['species']
    
    species.sort(key=lambda dino_data: dino.get_descriptive_name(flt, dino_data))
    
    if flt.dinoClasses:
        validate(species, contains_range=flt.dinoClasses, of=blueprint.get_class_name)
        conditions = [dict(where=blueprint.get_class_name, contained_in=flt.dinoClasses)]
    else:
        conditions = [dict(where=lambda x: dino.should_skip(flt, x), equals=True)]

    results = dict()
    for dino_data in query(species,
                           *conditions,
                           dict(where=CLONING_SECTION, not_null=True)):
        cloning = dino_data[CLONING_SECTION]
        cost_base = cloning[BASE_COST]
        cost_level = cloning[LEVEL_COST]
        time_base = cloning[BASE_TIME]
        time_level = cloning[LEVEL_TIME]
        
        out = (cost_base, cost_level, time_base, time_level)
        name = dino.get_descriptive_name(flt, dino_data)
        
        if not flt.includeCloningTimes:
            out = out[:2]
        
        results[name] = out

    print('// Version:', game_version)
    print(dump_json(flt, results))

