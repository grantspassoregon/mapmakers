import mapmakers as m
from examples.grants_pass.services import Service
from mapmakers import expand_urls
import logging


def historic_service():
    historic_cultural = "https://services2.arcgis.com/pc4beVTMEhYHqerq/ArcGIS/rest/services/historic_cultural_areas/FeatureServer/"
    url_range = range(3, -1, -1)
    agol = expand_urls(historic_cultural, url_range)
    historic_cultural = "https://gisserver.grantspassoregon.gov/server/rest/services/CommunityDevlp/historic_cultural_areas/MapServer/"
    gp = expand_urls(historic_cultural, url_range)
    return Service("historic_cultural", agol, gp)


def historic(t, portal="agol"):
    lyrs = t.template["historic"].into_items()
    # items set to visible
    for lyr in lyrs.items:
        lyr.visible = True
    # parent group set to invisible
    lyrs = historic_service().urls(portal, lyrs)
    lyrs = lyrs.layers().insert(2, oprd(t))
    return lyrs.group("Historic & Cultural Areas", False)


def oprd(t):
    lyrs = t.template["oprd"].into_items()
    # items set to visible
    for lyr in lyrs.items:
        lyr.visible = True

    return lyrs.group("Historic Sites (OPRD)", False)


def agreements_service():
    agreements = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/agreements/FeatureServer/"
    url_range = range(4, -1, -1)
    agol = expand_urls(agreements, url_range)
    agreements = "https://gisserver.grantspassoregon.gov/server/rest/services/agreements/MapServer/"
    gp = expand_urls(agreements, url_range)
    return Service("agreements", agol, gp)


def agreements(t, portal="agol"):
    lyrs = t.template["agreements"].into_items()
    lyrs = agreements_service().urls(portal, lyrs)
    return lyrs.group("Agreements & Financial")


def marijuana(t):
    return t.template["marijuana"].into_items().group("Marijuana Permitting")


def adult_use_service():
    adult_use = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/marijuana_adult_use/FeatureServer/"
    url_range = range(13, -1, -1)
    agol = expand_urls(adult_use, url_range)
    adult_use = "https://gisserver.grantspassoregon.gov/server/rest/services/CommunityDevlp/marijuana_adult_use/MapServer/"
    gp = expand_urls(adult_use, url_range)
    return Service("adult_use", agol, gp)


def adult_use(t, portal="agol"):
    adult = t.template["adult_use"].into_items()
    adult = adult_use_service().urls(portal, adult)
    return adult.group("Adult Use")


def zoning_service():
    zoning = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/zoning/FeatureServer/"
    url_range = range(4, -1, -1)
    agol = expand_urls(zoning, url_range)
    zoning = "https://gisserver.grantspassoregon.gov/server/rest/services/CommunityDevlp/zoning/MapServer/"
    gp = expand_urls(zoning, url_range)
    return Service("zoning", agol, gp)


def zoning(t, portal="agol"):
    lyrs = t.template["zoning"].into_items()
    lyrs.items[1].visible = True
    lyrs = zoning_service().urls(portal, lyrs)
    return lyrs.group("Zoning Group", False)


def planning(t, portal="agol"):
    hist = historic(t, portal)
    agr = agreements(t, portal)
    permit = marijuana(t)
    adult = adult_use(t, portal)
    zon = zoning(t, portal)

    planning = t.template["planning"].into_items()
    planning.items = planning.items[0:5]
    planning.items[4].title = "Lawnridge-Washington Conservation District"
    planning = planning.layers()
    planning.extend([zon, adult, permit, agr, hist])
    return planning.group("Planning")


if __name__ == "__main__":
    gis = GIS_CONN

    TEST = "2bc59679ad4040f4b7eb9ebec358152b"

    templates = {}
    templates.update({"agreements": "55830091a35542998a55ac747e6563ee"})
    templates.update({"historic": "4466a682c4c04affbfe2c03130826570"})
    templates.update({"oprd": "0bc78b02a49549f38cf42b767891d3df"})
    templates.update({"marijuana": "1baefaebb8454d61af41c8bc9de26d6f"})
    templates.update({"adult_use": "a7ce3cca0f504d26b35d96a1097edbe6"})
    templates.update({"zoning": "a1efdf5297f74182a0b70d21d9945431"})
    templates.update({"planning": "6b93918357b943d180c877570829c92a"})
    t = m.Templates.from_obj(templates, gis)

    def build(portal="agol"):
        mp = m.Map(
            TEST,
            [
                planning(t, portal),
            ],
            gis,
        )
        mp.build()
        logging.info("Target map updated.")
