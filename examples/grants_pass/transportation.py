import mapmakers as m
from mapmakers import expand_urls
from examples.grants_pass.services import Service
import copy
import logging


# transportation
def transport_service():
    county_roads = "https://gis.ecso911.com/server/rest/services/Hosted/RoadCenterlines_View/FeatureServer/0"
    odot_railroad = "https://gis.odot.state.or.us/arcgis1006/rest/services/transgis/catalog/MapServer/143"
    transportation = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/transportation/FeatureServer/"
    url_range = [16, 15, 14, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    agol = expand_urls(transportation, url_range)
    agol.insert(4, county_roads)
    agol.insert(0, odot_railroad)
    transportation = "https://gisserver.grantspassoregon.gov/server/rest/services/transportation/MapServer/"
    gp = expand_urls(transportation, url_range)
    gp.insert(4, county_roads)
    gp.insert(0, odot_railroad)
    return Service("transportation", agol, gp)


def parking(t):
    logging.info("Calling parking.")
    lyrs = t.template["parking"].into_items()
    for lyr in lyrs:
        lyr.visible = True
    return lyrs.group("Parking", False)


def fixtures(t, public=False, portal="agol"):
    logging.info("Calling fixtures.")
    fixtures_public = t.template["transport"].into_items()
    # fixtures are the first five layers in the template
    # so they are the last five on the items vector
    fixtures_public.items = fixtures_public.items[16:21]
    # compared to the service, the url vector has added railroads and county streets, and dropped city streets
    # so the vector index is increased by one, (2 - 1)
    urls = transport_service()
    # subset fixture urls
    urls.agol = urls.agol[13:18]
    urls.gp = urls.gp[13:18]
    logging.info("Calling urls for fixtures.")
    fixtures_public = urls.urls(portal, fixtures_public)
    if public:
        for lyr in fixtures_public:
            lyr.visible = True
        return fixtures_public.group("Fixtures", False)
    else:
        fixtures = t.template["transportation_editing"].into_items()
        fixtures.items.pop(0)
        # add street lights
        fixtures.items.insert(2, fixtures_public.items[2])
        # add traffic signals
        fixtures.items.insert(4, fixtures_public.items[4])
        for lyr in fixtures:
            lyr.visible = True
        return fixtures.group("Fixtures", False)


def bike(t, portal="agol"):
    logging.info("Calling bike.")
    bike = t.template["transport"].into_items()
    bike.items = bike.items[11:16]
    urls = transport_service()
    urls.agol = urls.agol[8:13]
    urls.gp = urls.gp[8:13]
    logging.info("Calling urls for bike.")
    bike = urls.urls(portal, bike)
    bike.items[0].visible = True  # trails
    bike.items[1].visible = True  # bike lane striping
    bike.items[2].visible = True  # paved bike surfaces
    return bike.group("Bike | Walk | Ride", False)


def streets(t, public=False, portal="agol"):
    logging.info("Calling streets.")
    streets = t.template["transport"].into_items()
    streets.items = streets.items[3:11]
    urls = transport_service()
    url_range = [1, 2, 3, 4, 5, 5, 6, 7]
    agol = []
    gp = []
    for i in url_range:
        logging.info("i: %s", i)
        agol.append(urls.agol[i])
        gp.append(urls.gp[i])
    urls.agol = agol
    urls.gp = gp
    logging.info("Calling urls for streets.")
    streets = urls.urls(portal, streets)
    streets.items[4].visible = True  # make streets (county) visible
    streets_public = copy.deepcopy(streets)
    if public:
        return streets_public.group("Streets Group", False)
    else:
        streets.items = streets.items[0:7]
        streets.items[6] = (
            t.template["transportation_editing"]
            .items["transportation_editing_0"]
            .into_item()
        )
        return streets.group("Streets Group", False)


def traffic(t):
    logging.info("Calling traffic.")
    lyrs = t.template["transport"].into_items()
    lyrs.items = lyrs.items[1:3]
    for lyr in lyrs:
        lyr.visible = True
    return lyrs.group("Traffic", False)


def transportation(t, public=False, portal="agol"):
    logging.info("Calling transportation.")
    transportation = t.template["transport"].into_items()
    logging.info("Calling url for transportation.")
    transportation = transport_service().urls(portal, transportation)
    transportation.items = [transportation.items[0]]  # just keep the railroad layer
    transportation = (
        transportation.layers()
    )  # convert to Layers type to extend with more layers
    transportation.extend(
        [  # add sub-groups
            parking(t),
            traffic(t),
            streets(t, public, portal),
            bike(t, portal),
            fixtures(t, public, portal),
        ]
    )

    transportation = transportation.group("Transportation")
    return transportation


if __name__ == "__main__":
    gis = GIS_CONN

    TEST = "2bc59679ad4040f4b7eb9ebec358152b"

    templates = {}
    templates.update({"parking": "70c100fe80df476cad13ab1ca679e31a"})
    templates.update({"transport": "42fdea8a22694cf1bd83452bf594245d"})
    templates.update({"transportation_editing": "951eb2097f2642ed93e68c1687d73789"})
    t = m.Templates.from_obj(templates, gis)

    def build(target=TEST, public=False, portal="agol"):
        mp = m.Map(
            target,
            transportation(t, public, portal),
            gis,
        )
        mp.build()
        logging.info("Target map updated.")
