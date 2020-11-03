import re
from typing import Optional

from .blueprint import get_class_name, get_path
from .file import JsonData
from .filter import Filter


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
    blueprint_path = get_path(blueprint, no_class=True)
    class_name = get_class_name(blueprint)
    name = get_descriptive_name(flt, blueprint)
    selectors = flt.selectors

    # Execute custom regex checks if any are given
    if selectors.matchRegex:
        re_name = selectors.matchRegex.get('name', None)
        if re_name and not re.match(re_name, name):
            return True

    # Check if dino is in the ignore list.
    if blueprint_path in selectors.ignoreBPs:
        return True

    # Branch off if the ignore options are used
    if selectors.ignoreClasses or selectors.ignoreVariants:
        # Force include a dino if it's in includeDinoClasses
        if class_name in selectors.includeClasses:
            return False

        # Ignore it if it's listed on one of the lists
        if class_name in selectors.ignoreClasses:
            return True
        elif any(variant in selectors.ignoreVariants
                 for variant in blueprint.get('variants', [])):
            return True
    elif selectors.includeBPs.values and blueprint_path not in selectors.includeBPs:
        return True
    elif selectors.includeClasses:
        if class_name not in selectors.includeClasses:
            return True

    return False
