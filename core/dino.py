from .blueprint import get_class_name, get_path
from .file import JsonData
from .filter import Filter
from typing import Optional


def get_descriptive_name(flt: Optional[Filter], blueprint: JsonData) -> str:
    def _get_name() -> str:
        if not flt or not flt.dinoNameOverrides:
            return blueprint['name']

        class_name = get_class_name(blueprint)
        override = flt.dinoNameOverrides.get(class_name, None)
        if not override:
            override = flt.dinoNameOverrides.get(blueprint['name'], None)
        if override:
            return override

        return blueprint['name']

    name = _get_name()
    if flt and flt.debugNames:
        return f'{name} ({get_class_name(blueprint)})'
    return name


def should_skip(flt: Filter, blueprint: JsonData) -> bool:
    blueprint_path = get_path(blueprint)
    class_name = get_class_name(blueprint)

    if any(blueprint_path.startswith(prefix) for prefix in flt.ignoreDinoBPs):
        return True
    if flt.ignoreDinoClasses and class_name in flt.ignoreDinoClasses:
        return True
    if not flt.ignoreDinoClasses and class_name not in flt.dinoClasses:
        return True
    return False
