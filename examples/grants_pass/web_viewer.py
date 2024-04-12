import mapmakers as m
from examples.grants_pass.refs import *
from examples.grants_pass.services import services
from enum import Enum
import copy
import pprint


class Target(Enum):
    TEST = "2bc59679ad4040f4b7eb9ebec358152b"
    STAFF = "2c76b256e6954677802813291d22a2b9"
    STAFF1 = "199ca9a74d824a2287895cd736394138"
    PUBLIC = "8b104a6cfc774ba29cd873edf2bbef73"
    PUBLIC1 = "df37a2bec8554462a4e33d02bea239dc"
    EDITOR = "54738cddf51648ad99ba0ec5dfff2625"
    INTERNAL = "1d90a7718910422faceaaf91a2a95f52"


gis = GIS_CONN

# run login.py prior to obtain the gis connection


def read_template():
    return m.Templates.from_workbook("examples/grants_pass/workbooks/workbook.csv")


def workbook():
    m.Templates.from_obj(templates, gis).workbook(
        gis, "examples/grants_pass/workbooks", True
    )


def boundaries(t, portal="agol", url=services):
    plss = t.template["plss"].into_items().group("PLSS")
    boundaries = t.template["boundaries_group"].into_items()
    boundaries.items = boundaries.items[0:4]
    ugb = t.template["boundaries_group"].items["boundaries_group_4"].into_item()
    ugb.visible = True
    city_limits = t.template["boundaries_group"].items["boundaries_group_5"].into_item()
    city_limits.visible = True
    boundaries.items.extend([ugb, city_limits])
    boundaries = url["boundaries"].urls(portal, boundaries)
    boundaries = boundaries.layers()
    logging.info("Appending PLSS")
    boundaries = boundaries.append(plss).group("Boundaries")
    return boundaries


def property(t, portal="agol", url=services):
    prop = t.template["property"].items["property_0"].into_item()
    prop.title = "Taxlots (County)"
    props = t.template["property"].into_items()
    props.items = props.items[1:4]
    prop = m.Items([prop])
    prop.items.extend(props)
    prop = url["property"].urls(portal, prop)
    prop = prop.group("Property")
    return prop


def historic_cultural(t, portal="agol", url=services):
    historic = t.template["historic_cultural"].into_items()
    historic = url["historic_cultural"].urls(portal, historic)
    return historic.group("Historic/Cultural Areas")


def agreements(t, portal="agol", url=services):
    agreements = t.template["agreements"].into_items()
    agreements = url["agreements"].urls(portal, agreements)
    return agreements.group("Agreements & Financial")


def adult_use(t, portal="agol", url=services):
    adult = t.template["marijuana_adult_use"].into_items()
    adult = url["adult_use"].urls(portal, adult)
    return adult.group("Adult Use")


def zoning(t, portal="agol", url=services):
    zoning = t.template["zoning"].into_items()
    zoning = url["zoning"].urls(portal, zoning)
    return zoning.group("Zoning Group")


def planning(t, portal="agol", url=services):
    historic = historic_cultural(t, portal, url)
    agr = agreements(t, portal, url)
    permitting = (
        t.template["marijuana_permitting"].into_items().group("Marijuana Permitting")
    )
    adult = adult_use(t, portal, url)
    zon = zoning(t, portal, url)

    planning = t.template["planning"].into_items()
    planning.items = planning.items[0:5]
    planning.items[4].title = "Lawnridge-Washington Conservation District"
    planning = planning.layers()
    planning.extend([zon, adult, permitting, agr, historic])
    planning = planning.group("Planning")

    return planning


def business(t):
    return t.template["business"].into_items().group("Economic Development")


def parking(t):
    logging.info("Calling parking.")
    return t.template["parking"].into_items().group("Parking")


def fixtures(t, public=False, portal="agol", url=services):
    logging.info("Calling fixtures.")
    fixtures_public = t.template["transport"].into_items()
    fixtures_public.items = fixtures_public.items[16:21]
    urls = url["transportation"]
    urls.agol = urls.agol[13:18]
    urls.gp = urls.gp[13:18]
    logging.info("Calling urls for fixtures.")
    fixtures_public = urls.urls(portal, fixtures_public)
    fixtures_public = url["transportation"].urls(portal, fixtures_public)
    if public:
        return fixtures_public.group("Fixtures")
    else:
        fixtures = t.template["transportation_editing"].into_items()
        fixtures.items = fixtures.items[1:4]
        fixtures.items.insert(2, fixtures_public.items[2])
        fixtures.items.insert(4, fixtures_public.items[4])
        return fixtures.group("Fixtures")


def bike(t, portal="agol", url=services):
    logging.info("Calling bike.")
    bike = t.template["transport"].into_items()
    bike.items = bike.items[11:16]
    urls = url["transportation"]
    urls.agol = urls.agol[8:13]
    urls.gp = urls.gp[8:13]
    logging.info("Calling urls for bike.")
    bike = urls.urls(portal, bike)
    return bike.group("Bike | Walk | Ride")


def streets(t, public=False, portal="agol", url=services):
    logging.info("Calling streets.")
    streets = t.template["transport"].into_items()
    streets.items = streets.items[3:11]
    urls = url["transportation"]
    url_range = [1, 2, 3, 4, 5, 5, 6, 7]
    agol = []
    gp = []
    for i in url_range:
        agol.append(urls.agol[i])
        gp.append(urls.gp[i])
    urls.agol = agol
    urls.gp = gp
    logging.info("Calling urls for streets.")
    streets = urls.urls(portal, streets)
    streets_public = copy.deepcopy(streets)
    if public:
        streets_public = streets_public.group("Streets Group")
        return streets_public
    else:
        streets.items = streets.items[0:7]
        streets.items[6] = (
            t.template["transportation_editing"]
            .items["transportation_editing_0"]
            .into_item()
        )
        streets = streets.group("Streets Group")
        return streets


def traffic(t):
    logging.info("Calling traffic.")
    return t.template["traffic"].into_items().group("Traffic")


def transportation(t, public=False, portal="agol", url=services):
    logging.info("Calling transportation.")
    transportation = t.template["transport"].into_items()
    logging.info("Calling url for transportation.")
    transportation = url["transportation"].urls(portal, transportation)
    transportation.items = [transportation.items[0]]
    transportation = transportation.layers()
    transportation.extend(
        [
            parking(t),
            traffic(t),
            streets(t, public, portal, url),
            bike(t, portal, url),
            fixtures(t, public, portal, url),
        ]
    )

    transportation = transportation.group("Transportation")
    return transportation


def water_utilities(t, public=False, portal="agol", url=services):
    water = t.template["water_wv"].into_items()
    urls = url["water_utilities"]
    index = [0, 2, 4, 5, 6, 7, 10, 9, 8, 11]
    edit = [5, 6, 8, 9, 10, 11]
    agol = []
    gp = []
    for i in index:
        if not public and i in edit:
            agol.append(urls.edit[i])
            gp.append(urls.edit[i])
        else:
            agol.append(urls.agol[i])
            gp.append(urls.gp[i])

    urls.agol = agol
    urls.gp = gp
    water = urls.urls(portal, water)
    return water.group("Water Distribution")


def stormwater(t, public=False, portal="agol", url=services):
    storm = t.template["stormwater"].into_items()
    urls = url["stormwater"]
    edit = [3, 4, 5, 6, 7, 8, 9, 10, 11]
    agol = []
    gp = []
    for i in range(0, len(storm.items)):
        if not public and i in edit:
            agol.append(urls.edit[i])
            gp.append(urls.edit[i])
        else:
            agol.append(urls.agol[i])
            gp.append(urls.gp[i])

    urls.agol = agol
    urls.gp = gp
    storm = urls.urls(portal, storm)
    return storm.group("Stormwater")


def wastewater(t, public=False, portal="agol", url=services):
    waste = t.template["sewer"].into_items()
    urls = url["wastewater"]
    edit = [4, 5, 6, 7, 8, 9, 10, 11]
    agol = []
    gp = []
    for i in range(0, len(waste.items)):
        if not public and i in edit:
            logging.info("Adding wastewater editing.")
            agol.append(urls.edit[i])
            gp.append(urls.edit[i])
        else:
            agol.append(urls.agol[i])
            gp.append(urls.gp[i])

    urls.agol = agol
    urls.gp = gp
    waste = urls.urls(portal, waste)
    return waste.group("Wastewater")


def utilities(t, public=False, portal="agol", url=services):
    power = (
        t.template["power_gas"].into_items().group("Power & Gas (Internal Use Only)")
    )
    water = water_utilities(t, public, portal, url)
    storm = stormwater(t, public, portal, url)
    sewer = wastewater(t, public, portal, url)
    impervious = t.template["impervious"].into_items().group("Impervious Surface")
    utilities = t.template["as_builts"].into_items().group("As-Builts").into_layer()
    utilities_public = copy.deepcopy(utilities)
    if public:
        utilities_public.extend([impervious, sewer, storm, water])
        utilities_public = utilities_public.group("Utilities")
        return utilities_public
    else:
        utilities.extend([impervious, sewer, storm, water, power])
        utilities = utilities.group("Utilities")
        return utilities


def parks(t):
    return t.template["parks"].into_items().group("Parks")


def environment(t):
    fema = t.template["fema_flood_wv"].into_items().group("FEMA Flood Hazard")
    deq = (
        t.template["deq_dw_source"]
        .into_items()
        .group("Drinking Water Source Areas (DEQ)")
    )
    esh = m.Template("esh", "08ebe57f03d949ef8afb183200566687")
    esh.load(gis)
    esh = esh.into_items().group("Essential Salmon Habitat (DSL)")

    contours_2012 = t.template["contours"].into_items()
    contours_2012.items = contours_2012.items[5:10]
    contours_2012 = contours_2012.group("2012 Contours (DEM)")
    contours = t.template["contours"].into_items()
    contours.items = contours.items[0:5]
    contours = contours.group("2004 Contours").into_layer()
    contours.append(contours_2012)
    contours = contours.group("Topographic Contours")

    wetlands = t.template["wetlands"].into_items()
    wetlands = wetlands.layers()

    # wetlands.extend([contours, esh, deq, fema])
    streams = t.template["features"].items["features_1"].into_item().layer()
    hazards = t.template["hazards"].into_items().layers()

    env = contours.into_layer()
    env.extend([wetlands, esh, deq, streams, fema, hazards])
    env = env.group("Environment")
    return env


def public_safety(t, public=False):
    zonehaven = t.template["zonehaven"].items["zonehaven_0"].into_item()
    zonehaven.title = "Zonehaven"
    fire = t.template["fire"].into_items()
    fire.items.append(zonehaven)
    fire = fire.group("Fire").into_layer()
    ems = m.Item(
        "https://gis.ecso911.com/server/rest/services/Hosted/EMS_Polygon_View/FeatureServer/0",
        title="EMS Response Zones (ECSO 911)",
    )
    fire_zone = m.Item(
        "https://gis.ecso911.com/server/rest/services/Hosted/Fire_Polygon_View/FeatureServer/0",
        title="Fire Response Zones (ECSO 911)",
    )
    law = m.Item(
        "https://gis.ecso911.com/server/rest/services/Hosted/Law_Polygon_View/FeatureServer/0",
        title="Law Enforcement Zone (ECSO 911)",
    )
    ecso = m.Items([law, fire_zone, ems]).layers()
    ecso_public = copy.deepcopy(ecso)
    if public:
        ecso_public = ecso_public.group("Public Safety")
        return ecso_public
    else:
        ecso.append(fire)
        ecso = ecso.group("Public Safety")
        return ecso


def sketch(t):
    return t.template["sketch"].into_items().group("Sketch Editing")


def street_imagery(t):
    street = t.template["street_imagery"].items["street_imagery_0"].into_item().layer()
    logging.debug(pprint.pprint(street))
    return street


def aerials(t):
    imagery = t.template["aerials"].into_items().rasters()
    imagery = imagery.group("Aerials")
    return imagery


def build(target=Target.TEST.value, public=False, portal="agol", url=services):
    t = read_template()
    layers = [
        aerials(t),
        street_imagery(t),
        public_safety(t, public),
        environment(t),
        parks(t),
        utilities(t, public, portal, url),
        transportation(t, public, portal, url),
        business(t),
        planning(t, portal, url),
        property(t, portal, url),
        boundaries(t, portal, url),
    ]
    if not public:
        layers.insert(2, sketch(t))
    mp = m.Map(
        target,
        layers,
        gis,
    )
    # logging.debug(pprint.pprint(mp))
    mp.build()
    logging.info("Target map updated.")


def internal_build(target=Target.TEST.value, public=False, portal="agol", url=services):
    t = read_template()
    layers = [
        aerials(t),
        street_imagery(t),
        public_safety(t, public),
        environment(t),
        parks(t),
        utilities(t, public, portal, url),
        transportation(t, public, portal, url),
        business(t),
        planning(t, portal, url),
        property(t, portal, url),
        boundaries(t, portal, url),
    ]
    if not public:
        layers.insert(2, sketch(t))
    mp = m.Map(
        target,
        layers,
        INT_CONN,
    )
    # logging.debug(pprint.pprint(mp))
    mp.build()
    logging.info("Target map updated.")
