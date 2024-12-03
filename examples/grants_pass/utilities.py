import mapmakers as m
import logging

gis = GIS_CONN

TEST = "2bc59679ad4040f4b7eb9ebec358152b"

templates = {}
templates.update({"water_agol": "d1267a14effc43af92d709fb00f034c2"})
templates.update({"water_gp": "1bf8453662d64d0280f03598a29ce81e"})
templates.update({"water_edit": "9e6b1dc1a8494505a3ab09393aead778"})
templates.update({"storm_agol": "3d22f13ef79f4563af9e80cfe63eb7c9"})
templates.update({"storm_gp": "7fa06f18d946453981c54578268cb5c8"})
templates.update({"storm_edit": "fecb4ce2f0834b2d8051a8d101f5307e"})
templates.update({"sewer_agol": "8988dbbb153c44f991f4edc8df9df305"})
templates.update({"sewer_gp": "652bdbe5576b4e109eed7b8214da6629"})
templates.update({"sewer_edit": "c373c6b928b1477b9d2b549a41d3593b"})
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
            return t.template["storm_gp"].into_items().group("Stormwater")
        case "edit":
            return t.template["storm_edit"].into_items().group("Stormwater")


def sewer(t, portal="agol"):
    match portal:
        case "agol":
            return t.template["sewer_agol"].into_items().group("Wastewater")
        case "gp":
            return t.template["storm_gp"].into_items().group("Wastewater")
        case "edit":
            return t.template["storm_edit"].into_items().group("Wastewater")


def build(portal="agol"):
    mp = m.Map(
        TEST,
        [
            sewer(t, portal),
            storm(t, portal),
            water(t, portal),
        ],
        gis,
    )
    mp.build()
    logging.info("Target map updated.")
