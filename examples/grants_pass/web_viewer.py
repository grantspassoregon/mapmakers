import mapmakers as m
import logging
from examples.grants_pass.refs import templates
from examples.grants_pass.boundaries import boundaries
from examples.grants_pass.economy import business
from examples.grants_pass.environment import environment
from examples.grants_pass.parks import parks
from examples.grants_pass.planning import planning
from examples.grants_pass.property import property
from examples.grants_pass.public_safety import public_safety
from examples.grants_pass.transportation import transportation
from examples.grants_pass.utilities import utilities
from enum import Enum
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


def sketch(t):
    return t.template["sketch"].into_items().group("Sketch Editing")


# def street_imagery(t):
#     street = t.template["street_imagery"].items["street_imagery_0"].into_item().layer()
#     logging.debug(pprint.pprint(street))
#     return street


def aerials(t):
    imagery = t.template["aerials"].into_items()
    imagery.items[
        len(imagery.items) - 1
    ].visible = True  # Top-most aerial is the most recent.
    imagery = imagery.rasters().group("Aerials", False)
    return imagery


def build(target=Target.TEST.value, public=True, portal="agol"):
    t = read_template()
    layers = [
        aerials(t),
        public_safety(t, public),
        environment(t),
        parks(t, portal),
        utilities(t, public, portal),
        transportation(t, public, portal),
        business(t),
        planning(t, portal),
        property(t, portal),
        boundaries(t, portal),
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


def internal_build(target=Target.TEST.value, public=False, portal="agol"):
    t = read_template()
    layers = [
        aerials(t),
        # removed (its getting old)
        # street_imagery(t),
        public_safety(t, public),
        environment(t),
        parks(t, portal),
        utilities(t, public, portal),
        transportation(t, public, portal),
        business(t),
        planning(t, portal),
        property(t, portal),
        boundaries(t, portal),
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
