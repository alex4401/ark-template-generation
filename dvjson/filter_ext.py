from core.filter import Filter, namespace
from typing import Dict


@namespace('DvJson')
class FilterDv(Filter):
    idOverrides: Dict[str, str] = dict()