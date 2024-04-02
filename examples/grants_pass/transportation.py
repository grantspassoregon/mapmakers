import mapmakers as m
import copy
from examples.grants_pass.refs import *

gis = GIS_CONN

TEST = "2bc59679ad4040f4b7eb9ebec358152b"
t = m.Templates.from_workbook("examples/grants_pass/workbooks/workbook.csv")


def transportation_old():
    fixtures = t.template["transportation_wv"].into_items()
    fixtures.items = fixtures.items[13:18]
    fixtures = fixtures.group("Fixtures")
    bike = t.template["transportation_wv"].into_items()
    bike.items = bike.items[8:13]
    bike = bike.group("Bike | Walk | Ride")
    streets = t.template["transportation_wv"].into_items()
    streets_county = streets.items[5]
    streets_county.url = "https://gis.ecso911.com/server/rest/services/Hosted/RoadCenterlines_View/FeatureServer/0"
    streets_county = copy.deepcopy(streets.items[5])
    streets_county.title = "Streets by Owner"
    streets.items = streets.items[1:7]
    streets.items.insert(5, streets_county)
    street_adoption = (
        t.template["transportation_editing"]
        .items["transportation_editing_0"]
        .into_item()
    )
    streets.append(street_adoption)
    streets = streets.group("Streets Group")
    traffic = t.template["traffic"].into_items().group("Traffic")

    transportation = t.template["transportation_wv"].into_items()
    transportation.items = [transportation.items[0]]
    transportation = transportation.layers()
    transportation.extend([traffic, streets, bike, fixtures])

    transportation = transportation.group("Transportation")
    return transportation


def parking():
    return t.template["parking"].into_items().group("Parking")


def fixtures(public=False):
    fixtures_public = t.template["transport"].into_items()
    fixtures_public.items = fixtures_public.items[16:21]
    if public:
        return fixtures_public.group("Fixtures")
    else:
        fixtures = t.template["transportation_editing"].into_items()
        fixtures.items = fixtures.items[1:4]
        fixtures.items.insert(2, fixtures_public.items[2])
        fixtures.items.insert(4, fixtures_public.items[4])
        return fixtures.group("Fixtures")


def bike():
    bike = t.template["transport"].into_items()
    bike.items = bike.items[11:16]
    return bike.group("Bike | Walk | Ride")


def streets(public=False):
    streets = t.template["transport"].into_items()
    streets_public = copy.deepcopy(streets)
    streets_public.items = streets.items[3:11]
    streets.items = streets.items[3:10]
    street_adoption = (
        t.template["transportation_editing"]
        .items["transportation_editing_0"]
        .into_item()
    )
    streets.append(street_adoption)
    streets_public = streets_public.group("Streets Group")
    streets = streets.group("Streets Group")
    if public:
        return streets_public
    else:
        return streets


def traffic():
    return t.template["traffic"].into_items().group("Traffic")


def transportation(public=False):
    transportation = t.template["transport"].into_items()
    transportation.items = [transportation.items[0]]
    transportation = transportation.layers()
    transportation.extend([parking(), traffic(), streets(public), bike(), fixtures()])

    transportation = transportation.group("Transportation")
    return transportation


def build(target=TEST, public=False):
    mp = m.Map(
        target,
        [transportation()],
        gis,
    )
    mp.build()
    logging.info("Target map updated.")
