import random
import string


def create_layer_id(layerIndex: int) -> str:
    """
    Generate random ids for layers. Copied verbatim from https://community.esri.com/t5/arcgis-api-for-python-questions/python-api-add-group-layer-to-webmap/td-p/1112126.

    To build a web map from a published service, we generate feature layers pointed to each service. Each feature layer requires a unique layer id, produced by this function.

    :param layerIndex: Layer index number.
    :type layerIndex: int
    :return: A randomized string to serve as a unique id.
    :rtype: str
    """
    return (
        "".join(random.choices(string.ascii_lowercase + string.digits, k=11))
        + "-layer-"
        + str(layerIndex)
    )


def expand_urls(stub: str, rng: range | list[int]) -> list[str]:
    """
    Generate list of urls over range index given a service stub.

    :param stub: Url base string for map service.
    :type stub: str
    :param rng: List of numbers generated by *range()* call.
    :type rng: range
    :return: List of urls beginning in *stub* and ending in *rng* values.
    :rtype: list[str]
    """
    values = []
    match type(rng).__name__:
        case "range":
            values = list(rng)
        case "list":
            values = rng
    urls = []
    if not stub.endswith("/"):
        stub = stub + "/"
    for i in values:
        urls.append(stub + str(i))
    return urls
