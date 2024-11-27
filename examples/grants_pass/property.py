import mapmakers as m
import logging

gis = GIS_CONN

TEST = "2bc59679ad4040f4b7eb9ebec358152b"

templates = {}
templates.update({"property_agol": "adc211e50f974291aeddad1dfdb5bf73"})
templates.update({"property_edit": "f78b6396c657442a856160da5ce78019"})
templates.update({"property_gp": "0962f657ebd54556ba5c3f8dcc187989"})
templates.update({"strategic_plan_edit": "540dd5e5025245f4ab3b57d2b23e1429"})
t = m.Templates.from_obj(templates, gis)


def strategic_plan(t):
    return (
        t.template["strategic_plan_edit"].into_items().group("Address Strategic Plan")
    )


def property_agol(t):
    return t.template["property_agol"].into_items().group("Property")


def property_edit(t):
    prop = t.template["property_edit"].into_items().layers()
    strat = strategic_plan(t)
    prop.insert(5, strat)
    prop = prop.group("Property")
    return prop


def property_gp(t):
    prop = t.template["property_gp"].into_items().layers()
    strat = strategic_plan(t)
    prop.insert(5, strat)
    prop = prop.group("Property")
    return prop


def property(t, portal="agol"):
    match portal:
        case "agol":
            return property_agol(t)
        case "gp":
            return property_gp(t)
        case "edit":
            return property_edit(t)


def build(portal="agol"):
    mp = m.Map(
        TEST,
        [
            property(t, portal),
        ],
        gis,
    )
    mp.build()
    logging.info("Target map updated.")
