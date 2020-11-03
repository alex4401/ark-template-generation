import re
from .filter_ext import FilterDv
from typing import Dict, Any
from core.dino import get_descriptive_name
from core.blueprint import get_class_name

R_NON_WORD = r'[^\w]'


def get_dv_compatible_key(flt: FilterDv, dino: Dict[str, Any]):
    class_name = get_class_name(dino)
    desc_name = get_descriptive_name(flt, dino)
    
    if class_name in flt.idOverrides:
        return flt.idOverrides[class_name]
    
    if desc_name in flt.idOverrides:
        return flt.idOverrides[desc_name]

    return re.sub(R_NON_WORD, '', desc_name).lower()


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
