from dataclasses import dataclass
from mapmakers import expand_urls, Items
import logging
import copy


@dataclass
class Service:
    _name: str
    _agol: list[str]
    _gp: list[str]
    _edit: list[str]

    __slots__ = (
        "_name",
        "_agol",
        "_gp",
        "_edit",
    )

    def __init__(self, name: str, agol: list[str], gp: list[str], edit: list[str] = []):
        self._name = name
        self._agol = agol
        self._gp = gp
        self._edit = edit

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def agol(self):
        return self._agol

    @agol.setter
    def agol(self, agol: list[str]):
        self._agol = agol

    @property
    def gp(self):
        return self._gp

    @gp.setter
    def gp(self, gp: list[str]):
        self._gp = gp

    @property
    def edit(self):
        return self._edit

    @edit.setter
    def edit(self, edit: list[str]):
        self._edit = edit

    def portal(self, portal: str) -> list[str]:
        match portal:
            case "agol":
                return self._agol
            case "gp":
                return self._gp
            case "edit":
                return self._edit
            case _:
                logging.warn("Bad portal name.")
                return [""]

    def urls(self, portal: str, items: Items) -> Items:
        urls = self.portal(portal)
        for i in range(0, len(urls)):
            item = items.items[i]
            logging.info("Item: %s", item.title)
            item.url = urls[i]
            logging.info("Url: %s", item.url)
            items.items[i] = item
        return items


services = {}

# Grants Pass city services
# regulatory boundaries
boundaries = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/regulatory_boundaries/FeatureServer/"
url_range = [7, 6, 3, 2, 1, 0]
agol = expand_urls(boundaries, url_range)
boundaries = "https://gisserver.grantspassoregon.gov/server/rest/services/city_boundaries/MapServer/"
gp = expand_urls(boundaries, url_range)
boundaries = Service("boundaries", agol, gp)
services.update({boundaries.name: boundaries})

# land use
county_parcels = "https://gis.co.josephine.or.us/arcgis/rest/services/Assessor/Assessor_Taxlots/MapServer/0"
property = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/land_use/FeatureServer/"
url_range = [2, 1, 0]
agol = expand_urls(property, url_range)
agol.insert(0, county_parcels)
ecso = "https://gis.ecso911.com/server/rest/services/Hosted/JoCo_SiteStructureAddressPoints_View/FeatureServer/0"
strategic_plan = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/strategic_plan/FeatureServer/1"
verification = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/address_verification/FeatureServer/0"
gp = [strategic_plan, verification, ecso]
gp.extend(copy.deepcopy(agol))
property = Service("property", agol, gp, gp)
services.update({property.name: property})

# environmental features
# features = "https://gisserver.grantspassoregon.gov/server/rest/services/environmental_features/MapServer/"
# url_range = [1, 0]
# features = expand_urls(features, url_range)

# historic and cultural areas
historic_cultural = "https://services2.arcgis.com/pc4beVTMEhYHqerq/ArcGIS/rest/services/historic_cultural_areas/FeatureServer/"
url_range = range(3, -1, -1)
agol = expand_urls(historic_cultural, url_range)
historic_cultural = "https://gisserver.grantspassoregon.gov/server/rest/services/CommunityDevlp/historic_cultural_areas/MapServer/"
gp = expand_urls(historic_cultural, url_range)
historic_cultural = Service("historic_cultural", agol, gp)
services.update({historic_cultural.name: historic_cultural})

# agreements and financial
agreements = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/agreements/FeatureServer/"
url_range = range(4, -1, -1)
agol = expand_urls(agreements, url_range)
agreements = (
    "https://gisserver.grantspassoregon.gov/server/rest/services/agreements/MapServer/"
)
gp = expand_urls(agreements, url_range)
agreements = Service("agreements", agol, gp)
services.update({agreements.name: agreements})

# adult use
adult_use = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/marijuana_adult_use/FeatureServer/"
url_range = range(13, -1, -1)
agol = expand_urls(adult_use, url_range)
adult_use = "https://gisserver.grantspassoregon.gov/server/rest/services/CommunityDevlp/marijuana_adult_use/MapServer/"
gp = expand_urls(adult_use, url_range)
adult_use = Service("adult_use", agol, gp)
services.update({adult_use.name: adult_use})

# zoning
zoning = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/zoning/FeatureServer/"
url_range = range(4, -1, -1)
agol = expand_urls(zoning, url_range)
zoning = "https://gisserver.grantspassoregon.gov/server/rest/services/CommunityDevlp/zoning/MapServer/"
gp = expand_urls(zoning, url_range)
zoning = Service("zoning", agol, gp)
services.update({zoning.name: zoning})

# transportation
county_roads = "https://gis.ecso911.com/server/rest/services/Hosted/RoadCenterlines_View/FeatureServer/0"
odot_railroad = "https://gis.odot.state.or.us/arcgis1006/rest/services/transgis/catalog/MapServer/143"
transportation = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/transportation/FeatureServer/"
url_range = [16, 15, 14, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
agol = expand_urls(transportation, url_range)
agol.insert(4, county_roads)
agol.insert(0, odot_railroad)
transportation = "https://gisserver.grantspassoregon.gov/server/rest/services/transportation/MapServer/"
gp = expand_urls(transportation, url_range)
gp.insert(4, county_roads)
gp.insert(0, odot_railroad)
transportation = Service("transportation", agol, gp)
services.update({transportation.name: transportation})

# street_adoption_editing = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/street_adoption/FeatureServer/0"
# transportation_editing = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/transportation_editing/FeatureServer/"
# url_range = [1, 4, 3]
# agol = expand_urls(transportation_editing, url_range)
# agol.append(street_adoption_editing)

# water utilities
water = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/water_utilities/FeatureServer/"
url_range = [11, 9, 7, 6, 5, 4, 3, 2, 1, 0]
agol = expand_urls(water, url_range)
water = "https://gisserver.grantspassoregon.gov/server/rest/services/PublicWorks/water_utilities/MapServer/"
gp = expand_urls(water, url_range)
water_editing = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/water_editing/FeatureServer/"
edit = expand_urls(water_editing, url_range)
water = Service("water_utilities", agol, gp, edit)
services.update({water.name: water})

# stormwater
stormwater = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/stormwater/FeatureServer/"
url_range = range(11, -1, -1)
agol = expand_urls(stormwater, url_range)
stormwater = "https://gisserver.grantspassoregon.gov/server/rest/services/PublicWorks/stormwater/MapServer/"
gp = expand_urls(stormwater, url_range)
stormwater_editing = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/stormwater_editing/FeatureServer/"
edit = expand_urls(stormwater_editing, url_range)
stormwater = Service("stormwater", agol, gp, edit)
services.update({stormwater.name: stormwater})

# wastewater utilities
wastewater = "https://services2.arcgis.com/pc4beVTMEhYHqerq/arcgis/rest/services/sewer_utilities/FeatureServer/"
url_range = range(11, -1, -1)
agol = expand_urls(wastewater, url_range)
wastewater = "https://gisserver.grantspassoregon.gov/server/rest/services/PublicWorks/sewer_utilities/MapServer/"
gp = expand_urls(wastewater, url_range)
wastewater_editing = "https://gisserver.grantspassoregon.gov/server/rest/services/Editing/sewer_editing/FeatureServer/"
edit = expand_urls(wastewater_editing, url_range)
wastewater = Service("wastewater", agol, gp, edit)
services.update({wastewater.name: wastewater})
