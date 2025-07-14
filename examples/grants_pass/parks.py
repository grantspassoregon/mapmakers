import mapmakers as m
from mapmakers import expand_urls
from examples.grants_pass.services import Service
import logging


# regulatory boundaries
def parks_service():
    parks = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/parks/FeatureServer/"
    url_range = [1, 0]
    county_parks = "https://gis.co.josephine.or.us/arcgis/rest/services/Parks/Park_Areas/MapServer/0"
    agol = expand_urls(parks, url_range)
    agol.insert(0, county_parks)
    parks = "https://gisserver.grantspassoregon.gov/server/rest/services/public_parks/MapServer/"
    gp = expand_urls(parks, url_range)
    gp.insert(0, county_parks)
    return Service("boundaries", agol, gp)


def parks(t, portal="agol"):
    lyrs = t.template["parks"].into_items()
    lyrs.items[0].visible = True  # set city parks to visible
    lyrs.items[2].visible = True  # set county parks to visible
    lyrs = parks_service().urls(portal, lyrs)
    return lyrs.group("Parks", False)  # set group to invisible


if __name__ == "__main__":
    gis = GIS_CONN

    TEST = "2bc59679ad4040f4b7eb9ebec358152b"

    templates = {}
    templates.update({"parks": "8297f5bc7c4c4c8ba641d0d19971aaff"})
    t = m.Templates.from_obj(templates, gis)

    def build(portal="agol"):
        mp = m.Map(
            TEST,
            [
                parks(t, portal),
            ],
            gis,
        )
        mp.build()
        logging.info("Target map updated.")
