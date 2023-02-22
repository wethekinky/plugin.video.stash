import json


def parse(criterions):
    _filter = {}

    for json_criterion in criterions:
        criterion = json.loads(json_criterion)

        _filter[criterion["type"]] = parse_criterion(criterion)

    return _filter


def parse_criterion(criterion):
    _filter = {}

    _filter["modifier"] = criterion["modifier"]

    if isinstance(criterion["value"], dict) and "depth" in criterion["value"]:
        _filter["value"] = list(map(lambda v: v["id"], criterion["value"]["items"]))
        _filter["depth"] = criterion["value"]["depth"]
    elif isinstance(criterion["value"], dict) and not criterion["value"].keys() - [
        "value",
        "value2",
    ]:
        _filter.update(criterion["value"])
    elif isinstance(criterion["value"], list):
        _filter["value"] = list(map(lambda v: v["id"], criterion["value"]))
    else:
        _filter["value"] = criterion["value"]

    return _filter
