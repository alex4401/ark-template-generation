import re
from .filter_ext import FilterDv
from typing import Dict, Any
from core.dino import get_descriptive_name

R_NON_WORD = r'[^\w]'


def get_dv_compatible_key(flt: FilterDv, dino: Dict[str, Any]):
    name = get_descriptive_name(flt, dino)
    if name in flt.idOverrides:
        return flt.idOverrides[name]

    return re.sub(R_NON_WORD, '', name).lower()


def prepare_object(node):
    if node is None:
        return ""

    if isinstance(node, (int, str, float)):
        return node

    if isinstance(node, (list, tuple)):
        return [prepare_object(value) for value in node]

    if isinstance(node, dict):
        return {prepare_object(k): prepare_object(v) for k, v in node.items()}

    raise TypeError(f"Unexpected node type {type(node)}")