from core.filter import Filter, namespace


@namespace('Cloning')
class FilterCloning(Filter):
    includeCloningTimes: bool = True
    prettifyOutput: bool = False