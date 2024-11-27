import mapmakers as m
import logging

gis = GIS_CONN

TEST = "2bc59679ad4040f4b7eb9ebec358152b"

templates = {}
templates.update({"water_agol": "d1267a14effc43af92d709fb00f034c2"})
templates.update({"water_gp": "1bf8453662d64d0280f03598a29ce81e"})
templates.update({"water_edit": "9e6b1dc1a8494505a3ab09393aead778"})
templates.update({"storm_agol": "3d22f13ef79f4563af9e80cfe63eb7c9"})
t = m.Templates.from_obj(templates, gis)


def water(t, portal="agol"):
    match portal:
        case "agol":
            return t.template["water_agol"].into_items().group("Water Distribution")
        case "gp":
            return t.template["water_gp"].into_items().group("Water Distribution")
        case "edit":
            return t.template["water_edit"].into_items().group("Water Distribution")


def storm(t, portal="agol"):
    match portal:
        case "agol":
            return t.template["storm_agol"].into_items().group("Stormwater")
        case "gp":
            return t.template["water_gp"].into_items().group("Stormwater")
        case "edit":
            return t.template["water_edit"].into_items().group("Stormwater")


def build(portal="agol"):
    mp = m.Map(
        TEST,
        [
            storm(t, portal),
            water(t, portal),
        ],
        gis,
    )
    mp.build()
    logging.info("Target map updated.")
