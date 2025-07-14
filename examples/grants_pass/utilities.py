import mapmakers as m
from mapmakers import expand_urls
from examples.grants_pass.services import Service
import logging


def water_service():
    water = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/water_utilities/FeatureServer/"
    # leaving out 10 [pressure zone 20-yr plan] and 8 [water rights boundaries]
    url_range = [11, 9, 7, 6, 5, 4, 1, 2, 3, 0]
    agol = expand_urls(water, url_range)
    # water = "https://gisserver.grantspassoregon.gov/server/rest/services/PublicWorks/water_utilities/MapServer/"
    # gp = expand_urls(water, url_range)
    water_editing = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/water_editing/FeatureServer/"
    edit = expand_urls(water_editing, url_range)
    # set the default GP build to EDIT
    return Service("water_utilities", agol, edit, edit)


def water(t, portal="agol"):
    lyrs = t.template["water_agol"].into_items()
    lyrs = water_service().urls(portal, lyrs)
    seen = [3, 4, 6, 7, 8, 9]
    for item in seen:
        lyrs.items[item].visible = True
    return lyrs.group("Water Distribution", False)


def storm_service():
    stormwater = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/stormwater/FeatureServer/"
    url_range = range(11, -1, -1)
    agol = expand_urls(stormwater, url_range)
    # stormwater = "https://gisserver.grantspassoregon.gov/server/rest/services/PublicWorks/stormwater/MapServer/"
    # gp = expand_urls(stormwater, url_range)
    stormwater_editing = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/stormwater_editing/FeatureServer/"
    edit = expand_urls(stormwater_editing, url_range)
    # set the default GP build to EDIT
    return Service("stormwater", agol, edit, edit)


def storm(t, portal="agol"):
    lyrs = t.template["storm_agol"].into_items()
    lyrs = storm_service().urls(portal, lyrs)
    seen = [2, 3, 4, 5, 7, 8, 9, 10, 11]
    for item in seen:
        lyrs.items[item].visible = True
    return lyrs.group("Stormwater", False)


def waste_service():
    wastewater = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/sewer_utilities/FeatureServer/"
    url_range = range(11, -1, -1)
    agol = expand_urls(wastewater, url_range)
    # wastewater = "https://gisserver.grantspassoregon.gov/server/rest/services/PublicWorks/sewer_utilities/MapServer/"
    # gp = expand_urls(wastewater, url_range)
    wastewater_editing = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/sewer_editing/FeatureServer/"
    edit = expand_urls(wastewater_editing, url_range)
    return Service("wastewater", agol, edit, edit)


def sewer(t, portal="agol"):
    lyrs = t.template["sewer_agol"].into_items()
    lyrs = waste_service().urls(portal, lyrs)
    show = [4, 5, 6, 7, 8, 9, 11]
    for item in show:
        lyrs.items[item].visible = True
    return lyrs.group("Wastewater", False)


def power_gas(t):
    lyrs = t.template["power_gas"].into_items()
    show = [0, 2, 3]
    for item in show:
        lyrs.items[item].visible = True
    return lyrs.group("Power & Gas (Internal Use Only)", False)


def impervious(t):
    lyrs = t.template["impervious"].into_items()
    lyrs.items[1].visible = True
    return lyrs.group("Impervious Surface", False)


def as_builts(t):
    lyrs = t.template["as_builts"].into_items()
    lyrs.items[0].visible = True
    return lyrs.group("As-Builts", False)


def tracker_service():
    url = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/project_footprints/FeatureServer/"
    url_range = [1, 0]
    agol = expand_urls(url, url_range)
    url = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/project_footprints/MapServer/"
    edit = expand_urls(url, url_range)
    return Service("wastewater", agol, edit, edit)


def project_tracker(t, portal="agol"):
    lyrs = t.template["project_tracker"].into_items()
    lyrs = tracker_service().urls(portal, lyrs)
    for lyr in lyrs:
        lyr.visible = True
    return lyrs.group("Project Tracker", False)


def utilities(t, public=False, portal="agol"):
    utilities = project_tracker(t, portal).into_layer()
    utilities.extend(
        [
            as_builts(t),
            impervious(t),
            sewer(t, portal),
            storm(t, portal),
            water(t, portal),
        ]
    )
    if not public:
        utilities.append(power_gas(t))
    return utilities.group("Utilities")


if __name__ == "__main__":
    gis = GIS_CONN

    TEST = "2bc59679ad4040f4b7eb9ebec358152b"

    templates = {}
    templates.update({"as_builts": "3ceb4d228f5a435681ca2af4624b39ae"})
    templates.update({"impervious": "566db9999f9d45029abeb389803307a2"})
    templates.update({"power_gas": "2fd77e08c41c49a4a405754d677725c0"})
    templates.update({"project_tracker": "4f50157041b6488698c918e23be87391"})
    templates.update({"water_agol": "d1267a14effc43af92d709fb00f034c2"})
    templates.update({"sewer_agol": "8988dbbb153c44f991f4edc8df9df305"})
    templates.update({"storm_agol": "3d22f13ef79f4563af9e80cfe63eb7c9"})
    t = m.Templates.from_obj(templates, gis)

    def build(public=True, portal="agol"):
        mp = m.Map(
            TEST,
            [
                # sewer(t, portal),
                # storm(t, portal),
                # water(t, portal),
                utilities(t, public, portal)
            ],
            gis,
        )
        mp.build()
        logging.info("Target map updated.")
