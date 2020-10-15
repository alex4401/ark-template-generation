from typing import List
from core.filter import Filter, namespace


@namespace('WildCreatureStats')
class FilterWildStatCalc(Filter):
    linkMods: List[str] = list()
    prettifyOutput: bool = False