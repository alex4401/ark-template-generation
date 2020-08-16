from typing import Union

from .file import JsonData

EXT_BP_CLASS = 'x-bp-class'

def get_path(blueprint: JsonData) -> str:
    out = blueprint.get('bp', None)
    if not out:
        out = blueprint['blueprintPath']
    return out

def get_class_name(blueprint: Union[JsonData, str]) -> str:
    if isinstance(blueprint, str):
        index = blueprint.index('.')
        return blueprint[index + 1:]
    else:
        cached = blueprint.get(EXT_BP_CLASS, None)
        if cached:
            return cached
           
        blueprint[EXT_BP_CLASS] = get_class_name(get_path(blueprint))
        return blueprint[EXT_BP_CLASS]

