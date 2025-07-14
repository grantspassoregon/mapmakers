import mapmakers as m
from mapmakers import expand_urls
from examples.grants_pass.services import Service
import logging


def property_service():
    county_parcels = "https://gis.co.josephine.or.us/arcgis/rest/services/Assessor/Assessor_Taxlots/MapServer/0"
    property = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/land_use/FeatureServer/"
    url_range = [2, 1, 0]
    agol = expand_urls(property, url_range)
    agol.insert(0, county_parcels)
    address_edit = "https://gisserver.grantspassoregon.gov/server/rest/services/CommunityDevlp/addresses/FeatureServer/0"
    subdivisions = "https://gisserver.grantspassoregon.gov/server/rest/services/CommunityDevlp/subdivisions/FeatureServer/0"
    buildings = "https://gisserver.grantspassoregon.gov/server/rest/services/CommunityDevlp/building_footprints/FeatureServer/0"
    verification = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/address_verification/FeatureServer/0"
    ecso = "https://gis.ecso911.com/server/rest/services/Hosted/JoCo_SiteStructureAddressPoints_View/FeatureServer/0"
    edit = [county_parcels, buildings, subdivisions, verification, ecso, address_edit]
    return Service("property", agol, edit, edit)


def strategic_plan(t):
    plan = t.template["strategic_plan_edit"].into_items()
    # remove the copy of the UGB attached to this service
    plan.items.pop(0)
    for lyr in plan:
        lyr.visible = True
    return plan.group("Address Strategic Plan", False)


def property(t, portal="agol"):
    lyrs = t.template["property_gp"].into_items()
    lyrs = property_service().urls(portal, lyrs)
    show = [0, 5]
    for item in show:
        lyrs.items[item].visible = True

    match portal:
        case "agol":
            lyrs.items.pop(4)  # ecso
            lyrs.items.pop(3)  # verification
        case "gp" | "edit":
            strat = strategic_plan(t)
            lyrs = lyrs.layers()
            lyrs.insert(5, strat)

    return lyrs.group("Property", False)


if __name__ == "__main__":
    gis = GIS_CONN

    TEST = "2bc59679ad4040f4b7eb9ebec358152b"

    templates = {}
    templates.update({"property_gp": "0962f657ebd54556ba5c3f8dcc187989"})
    templates.update({"strategic_plan_edit": "540dd5e5025245f4ab3b57d2b23e1429"})
    t = m.Templates.from_obj(templates, gis)

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
