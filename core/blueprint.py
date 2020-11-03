from typing import Union

from .file import JsonData

EXT_BP_CLASS = 'x-bp-class'


def get_path(blueprint: JsonData, no_class=False) -> str:
    out = blueprint.get('bp', None)
    if not out:
        out = blueprint['blueprintPath']

    if no_class:
        out = out[:out.index('.')]

    return out


def get_class_name(blueprint: Union[JsonData, str]) -> str:
    if isinstance(blueprint, str):
        index = blueprint.index('.')
        out = blueprint[index + 1:]
        if not out.endswith('_C'):
            return out + '_C'
        return out
    else:
        cached = blueprint.get(EXT_BP_CLASS, None)
        if cached:
            return cached

        blueprint[EXT_BP_CLASS] = get_class_name(get_path(blueprint))
        return blueprint[EXT_BP_CLASS]
