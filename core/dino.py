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

        variants = blueprint.get('variants', None)
        if variants:
            for variant, suffix in flt.displayVariants.items():
                if not suffix:
                    suffix = variant

                if variant in variants:
                    return f'{blueprint["name"]} ({suffix})'

        return blueprint['name']

    name = _get_name()
    if flt and flt.debugNames:
        return f'{name} ({get_class_name(blueprint)})'
    return name


def should_skip(flt: Filter, blueprint: JsonData) -> bool:
    blueprint_path = get_path(blueprint)
    class_name = get_class_name(blueprint)

    # Check if dino is in the ignore list.
    if flt.ignoreDinoBPs and any(
        blueprint_path.startswith(prefix)
        for prefix in flt.ignoreDinoBPs):
        return True

    # Branch off if the ignore options are used
    if flt.ignoreDinoClasses or flt.ignoreDinosWithVariants:
        # Force include a dino if it's in includeDinoClasses
        if class_name in flt.includeDinoClasses:
            return False

        # Ignore it if it's listed on one of the lists
        if class_name in flt.ignoreDinoClasses:
            return True
        elif any(variant in flt.ignoreDinosWithVariants
                 for variant in blueprint.get('variants', [])):
            return True
    elif flt.includeDinoClasses:
        if class_name not in flt.includeDinoClasses:
            return True

    return False
