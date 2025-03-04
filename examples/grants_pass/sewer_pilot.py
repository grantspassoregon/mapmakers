import mapmakers as m
import logging
import pprint

gis = GIS_CONN

TEST = "2bc59679ad4040f4b7eb9ebec358152b"

templates = {}
templates.update({"sewer_pilot": "6dfb4bd8a7e0450695d4d3a91cb0ff50"})
t = m.Templates.from_obj(templates, gis)

logging.info("%s", pprint.pprint(t))


def sewer_pilot(t):
    return t.template["sewer_pilot"].into_items().reverse().group("Sewer Pilot")


def build():
    mp = m.Map(
        TEST,
        [
            sewer_pilot(t),
        ],
        gis,
    )
    mp.build()
    logging.info("Target map updated.")
