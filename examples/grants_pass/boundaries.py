import mapmakers as m
from examples.grants_pass.services import Service
from mapmakers import expand_urls
import logging


def plss(t):
    plss = t.template["plss"].into_items()
    # items set to visible
    for itm in plss.items:
        itm.visible = True
    # parent group set to invisible
    return plss.group("PLSS", False)


def boundaries_service():
    boundaries = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/regulatory_boundaries/FeatureServer/"
    url_range = [7, 6, 3, 2, 1, 0]
    agol = expand_urls(boundaries, url_range)
    boundaries = "https://gisserver.grantspassoregon.gov/server/rest/services/city_boundaries/MapServer/"
    gp = expand_urls(boundaries, url_range)
    return Service("boundaries", agol, gp)


def boundaries(t, portal="agol"):
    pls = plss(t)
    boundaries = t.template["boundaries"].into_items()
    # remove CMAQ and section quadrant layers
    boundaries.items.pop(3)
    boundaries.items.pop(2)
    # rename UGB and CL, set to visible
    boundaries.items[4].title = "Urban Growth Boundary (UGB)"
    boundaries.items[4].visible = True
    boundaries.items[5].title = "City Limits"
    boundaries.items[5].visible = True
    # set target urls by portal
    boundaries = boundaries_service().urls(portal, boundaries)
    logging.info("Appending PLSS")
    boundaries = boundaries.layers().append(pls).group("Boundaries")
    return boundaries


if __name__ == "__main__":
    gis = GIS_CONN

    TEST = "2bc59679ad4040f4b7eb9ebec358152b"

    templates = {}
    templates.update({"boundaries": "92f6873e24c84bd6acfd55193665719f"})
    templates.update({"plss": "ebd9e0eb423e4a3c852a5677e89f7298"})
    t = m.Templates.from_obj(templates, gis)

    def build(portal="agol"):
        mp = m.Map(
            TEST,
            [
                boundaries(t, portal),
            ],
            gis,
        )
        mp.build()
        logging.info("Target map updated.")
