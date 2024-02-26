import mapmakers as m
from examples.grants_pass.refs import *
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


gis = GIS_CONN

# run login.py prior to obtain the gis connection

# t = m.Templates.from_obj(templates, gis).workbook(
#     gis, "examples/grants_pass/workbooks", True
# )
t = m.Templates.from_workbook("examples/grants_pass/workbooks/workbook.csv")


def boundaries():
    plss = t.template["plss"].into_items().group("PLSS")
    boundaries = t.template["boundaries_group"].into_items()
    boundaries.items = boundaries.items[0:4]
    ugb = t.template["boundaries_group"].items["boundaries_group_4"].into_item()
    ugb.visible = True
    city_limits = t.template["boundaries_group"].items["boundaries_group_5"].into_item()
    city_limits.visible = True
    boundaries.items.extend([ugb, city_limits])
    boundaries = boundaries.layers()
    logging.info("Appending PLSS")
    boundaries = boundaries.append(plss).group("Boundaries")
    return boundaries


def property():
    prop = t.template["property"].items["property_0"].into_item()
    prop.title = "Taxlots (County)"
    props = t.template["property"].into_items()
    props.items = props.items[1:4]
    prop = m.Items([prop])
    prop.items.extend(props)
    prop = prop.group("Property")
    return prop


def planning(public=False):
    historic = (
        t.template["historic_cultural"].into_items().group("Historic/Cultural Areas")
    )
    agreements = t.template["agreements"].into_items().group("Agreements & Financial")
    permitting = (
        t.template["marijuana_permitting"].into_items().group("Marijuana Permitting")
    )
    adult = (
        t.template["marijuana_adult_use"].into_items().group("Marijuana & Adult Use")
    )
    zoning = m.Template("zoning", "a1efdf5297f74182a0b70d21d9945431")
    zoning.load(gis)
    zoning = zoning.into_items().group("Zoning Group")

    planning = t.template["planning"].into_items()
    planning.items = planning.items[0:5]
    planning.items[4].title = "Lawnridge-Washington Conservation District"
    planning = planning.layers()
    planning_public = copy.deepcopy(planning)
    planning.extend([zoning, adult, permitting, agreements, historic])
    planning = planning.group("Planning")

    planning_public.extend([zoning, adult, agreements, historic])
    planning_public = planning_public.group("Planning")
    if public:
        return planning_public
    else:
        return planning


def business():
    return t.template["business"].into_items().group("Economic Development")


def transportation():
    fixtures = t.template["transportation_wv"].into_items()
    fixtures.items = fixtures.items[13:18]
    fixtures = fixtures.group("Fixtures")
    bike = t.template["transportation_wv"].into_items()
    bike.items = bike.items[8:13]
    bike = bike.group("Bike | Walk | Ride")
    streets = t.template["transportation_wv"].into_items()
    streets.items = streets.items[1:8]
    streets = streets.group("Streets Group")
    traffic = t.template["traffic"].into_items().group("Traffic")

    transportation = t.template["transportation_wv"].into_items()
    transportation.items = [transportation.items[0]]
    transportation = transportation.layers()
    transportation.extend([traffic, streets, bike, fixtures])
    transportation = transportation.group("Transportation")
    return transportation


def utilities(public=False):
    power = (
        t.template["power_gas"].into_items().group("Power & Gas (Internal Use Only)")
    )
    water = t.template["water_wv"].into_items().group("Water Distribution")
    storm = t.template["stormwater"].into_items().group("Stormwater")
    sewer = t.template["sewer"].into_items().group("Wastewater")
    impervious = t.template["impervious"].into_items().group("Impervious Surface")
    utilities = t.template["as_builts"].into_items().group("As-Builts").into_layer()
    utilities_public = copy.deepcopy(utilities)
    utilities.extend([impervious, sewer, storm, water, power])
    utilities = utilities.group("Utilities")
    utilities_public.extend([impervious, sewer, storm, water])
    utilities_public = utilities_public.group("Utilities")
    if public:
        return utilities_public
    else:
        return utilities


def parks():
    return t.template["parks"].into_items().group("Parks")


def environment():
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


def public_safety(public=False):
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
    ecso_public = ecso_public.group("Public Safety")
    ecso.append(fire)
    ecso = ecso.group("Public Safety")
    if public:
        return ecso_public
    else:
        return ecso


def sketch():
    return t.template["sketch"].into_items().group("Sketch Editing")


def street_imagery():
    street = t.template["street_imagery"].items["street_imagery_0"].into_item().layer()
    logging.debug(pprint.pprint(street))
    return street


def aerials():
    imagery = t.template["aerials"].into_items().rasters()
    imagery = imagery.group("Aerials")
    return imagery


def build(target=Target.TEST.value, public=False):
    mp = m.Map(
        target,
        # [wetlands],
        [
            aerials(),
            street_imagery(),
            sketch(),
            public_safety(public),
            environment(),
            parks(),
            utilities(public),
            transportation(),
            business(),
            planning(),
            property(),
            boundaries(),
        ],
        gis,
    )
    # logging.debug(pprint.pprint(mp))
    mp.build()
    logging.info("Target map updated.")
