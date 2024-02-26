import mapmakers as m
import arcgis
from examples.grants_pass.refs import *
import logging
from enum import Enum
import pprint

gis = GIS_CONN


class Target(Enum):
    TEST = "2bc59679ad4040f4b7eb9ebec358152b"
    STAFF = "2c76b256e6954677802813291d22a2b9"
    STAFF1 = "199ca9a74d824a2287895cd736394138"
    PUBLIC = "8b104a6cfc774ba29cd873edf2bbef73"
    PUBLIC1 = "df37a2bec8554462a4e33d02bea239dc"
    EDITOR = "54738cddf51648ad99ba0ec5dfff2625"


def test_named():
    """
    Create a template from an ID.
    Assert the ArcGIS Item is the correct type.
    Assign names to the layers.
    Export the Template to csv.

    The items in a Template are stored in a hash table wher the key is a string "nickname" and the value is a TemplateItem.  The with_names() method sets the key values associated with each template item.

    """
    parks = "8297f5bc7c4c4c8ba641d0d19971aaff"
    tmp = m.Template("parks", parks)
    logging.info("Check: %s", tmp.check_template(gis))
    assert tmp.check_template(gis)
    tmp.load(gis)
    tmp.with_names(["a", "b", "c"])
    logging.info("Layer: %s", pprint.pprint(tmp))
    tmp.workbook("examples/grants_pass/workbooks", named=True)
    logging.info("Test test_named successful.")


def workbook():
    """
    Create a template from an ID.
    Write template contents to a workbook.

    Each template has a unique ArcGIS Item ID, visible in the url of the item page.  Given an Item ID, we want to create a new Template object from our library using the nickname of our choice (e.g. "parks").
    """
    # ArcGIS Item ID
    parks = "8297f5bc7c4c4c8ba641d0d19971aaff"
    # Create new Template object from name and id
    # Load layer definition and popup info from object at Item ID
    tmp = m.Template("parks", parks).load(gis)

    # Used to visually inspect results
    logging.info("Template: %s", pprint.pprint(tmp))
    #
    tmp.workbook("examples/grants_pass/workbooks")
    logging.info("Single workbook created.")
    logging.info("Test workbook successful.")


def workbooks():
    """
    Create templates from file.
    Write templates to workbooks.
    Write master workbook.

    In examples/grants_pass/refs.py, we record reference templates as a variable named `templates` set to a dictionary of template names and ArcGIS Item IDs.  We want to loop through the name/id pairs in `templates`, read the layer definition and popup info from the ArcGISFeatureLayer, and store the information in a `Templates` object from our library.
    We write the results to csv, both as one per template, and as a single csv with rows from each template. The `auto` field on the workbook functions is set to `True`, to check that the names auto-populate correctly.
    """
    tmp = m.Templates.from_obj(templates, gis)
    logging.info("Templates: %s", len(tmp.template))
    logging.info(pprint.pprint(tmp.template.keys()))
    for item in tmp.template.values():
        logging.info(pprint.pprint(item.items.keys()))
    tmp.workbooks("examples/grants_pass/workbooks", True)
    tmp.workbook(gis, "examples/grants_pass/workbooks", True)
    logging.info("Workbooks printed.")
    logging.info("Test workbooks successful.")


def from_workbook():
    """
    Create a template from a workbook.
    """
    tmp = m.Template.from_workbook("examples/grants_pass/workbooks/parks.csv")
    logging.info("Results: %s", pprint.pprint(tmp))
    logging.info("Test from_workbook successful.")


def into_item():
    parks = "8297f5bc7c4c4c8ba641d0d19971aaff"
    tmp = m.Template("parks", parks).load(gis)
    logging.info("%s", pprint.pprint(tmp))
    for itm in tmp.items.values():
        item = itm.into_item()
        logging.info("%s", pprint.pprint(item))
    logging.info("Test into_item successful.")


def into_items():
    parks = "8297f5bc7c4c4c8ba641d0d19971aaff"
    tmp = m.Template("parks", parks).load(gis)
    items = tmp.into_items()
    logging.info("%s", pprint.pprint(items))

    logging.info("Test into_items successful.")


def into_all_items():
    tmp = m.Templates.from_workbook("examples/grants_pass/workbooks/workbook.csv")
    items = tmp.into_items()
    # logging.info("%s", pprint.pprint(items))
    ln = len(items.items)
    logging.info("Items: %s", ln)
    logging.info("Test into_all_items successful.")


def item():
    stub = "https://services2.arcgis.com/pc4beVTMEhYHqerq/ArcGIS/rest/services/land_use/FeatureServer"
    targets = range(0, 4)
    urls = m.expand_urls(stub, targets)
    land_use = "40134429392a42ceb2d4b977b076d042"
    tmp = m.Template("land_use", land_use).load(gis)
    i = 0
    for url in urls:
        lyr = "land_use_" + str(i)
        itm = m.Item(url, tmp._items[lyr])
        i += 1
        logging.info(pprint.pprint(itm))

    logging.info(urls)
    logging.info("Test item successful.")


def items():
    stub = "https://services2.arcgis.com/pc4beVTMEhYHqerq/ArcGIS/rest/services/land_use/FeatureServer"
    targets = range(0, 4)
    urls = m.expand_urls(stub, targets)
    land_use = "40134429392a42ceb2d4b977b076d042"
    tmp = m.Template("land_use", land_use).load(gis)
    names = ["land_use_0", "land_use_1", "land_use_2", "land_use_3"]
    items = m.Items.from_names(urls, names, tmp)
    logging.info("Items from named succeeded.")
    items = m.Items.from_template(urls, tmp)
    logging.debug("%s", pprint.pprint(items))
    logging.info("Items from template succeeded.")
    logging.info("Test items successful.")


def layer():
    urls = m.expand_urls(
        "https://services2.arcgis.com/pc4beVTMEhYHqerq/ArcGIS/rest/services/land_use/FeatureServer",
        range(0, 4),
    )
    tmp = m.Template("land_use", "adc211e50f974291aeddad1dfdb5bf73").load(gis)
    print(tmp)
    items = m.Items.from_template(urls, tmp)
    if items is not None:
        if items.items is not None:
            for item in items.items:
                lyr = m.Layer(item)
                logging.info("%s", pprint.pprint(lyr))
    logging.info("Layer from Item successful.")
    if items is not None:
        if items.items is not None:
            for item in items.items:
                lyr = item.layer()
                logging.info("%s", pprint.pprint(lyr))
    logging.info("Item into Layer successful.")

    logging.info("Test layer successful.")

    aerials = "8a8f324bcb3840ec8eee62f90fa60228"
    tmp = m.Template("aerials", aerials).load(gis)
    items = tmp.into_items()
    # items = items.layers()
    items = items.group("Aerials")
    # items = items.layers().group("Aerials")
    logging.info("%s", pprint.pprint(items))


def group():
    urls = m.expand_urls(
        "https://services2.arcgis.com/pc4beVTMEhYHqerq/ArcGIS/rest/services/land_use/FeatureServer",
        range(0, 4),
    )
    tmp = m.Template("land_use", "adc211e50f974291aeddad1dfdb5bf73").load(gis)
    items = m.Items.from_template(urls, tmp)
    logging.info(pprint.pprint(items))
    if items is not None:
        group = m.Group.from_items("Land Use", items)
        logging.debug(pprint.pprint(group))
        logging.info("Group from items successful.")
        group = items.group("Land Use")
        logging.debug(pprint.pprint(group))
        logging.info("Items into group successful.")
        for item in items:
            grp = m.Group.from_item("Singleton", item)
            logging.info(pprint.pprint(grp))
        logging.info("Group from single item successful.")
        for item in items:
            grp = item.group("Singleton")
            logging.info(pprint.pprint(grp))
        logging.info("Single item into group successful.")
        logging.info("Test group successful.")


def layers():
    urls = m.expand_urls(
        "https://services2.arcgis.com/pc4beVTMEhYHqerq/ArcGIS/rest/services/land_use/FeatureServer",
        range(0, 4),
    )
    tmp = m.Template("land_use", "adc211e50f974291aeddad1dfdb5bf73").load(gis)
    items = m.Items.from_template(urls, tmp)
    layers = []
    if items is not None:
        group = m.Group.from_items("Land Use", items)
        layers.append(group)
        search = group.search
        for item in items.items:
            layer = m.Layer(item)
            layers.append(layer.layer)
            if layer.search is not None:
                search.extend(layer.search)

    mp = m.Map(Target.TEST.value, layers, gis)
    logging.info(pprint.pprint(mp))
    logging.info("Map from mixed layer and group successful.")
    logging.info("Layers made from loop of Layer calls.")
    if items is not None:
        lyrs = m.Layers.from_items(items)
        logging.info(pprint.pprint(lyrs))
        logging.info(type(lyrs))
        logging.info(type(lyrs).__name__)
        if lyrs is not None:
            mp = m.Map(Target.TEST.value, lyrs, gis)
            logging.info(pprint.pprint(mp))
            logging.info("Layers from items for map successful.")
        lyrs = items.layers()
        if lyrs is not None:
            mp = m.Map(Target.TEST.value, lyrs, gis)
            logging.info(pprint.pprint(mp))
            logging.info("Items into Layers for map successful.")
    logging.info("Test layers successful.")


def test_map():
    # parks = "8297f5bc7c4c4c8ba641d0d19971aaff"
    # tmp = m.Template("parks", parks).load(gis)
    # items = tmp.into_items()
    # items = items.group("Parks")
    # logging.info(pprint.pprint(items))
    urls = m.expand_urls(
        "https://services2.arcgis.com/pc4beVTMEhYHqerq/ArcGIS/rest/services/land_use/FeatureServer",
        range(0, 4),
    )
    tmp = m.Template("property", "4c070f42ece24ea0b493611c21d6862d").load(gis)
    items = m.Items.from_template(urls, tmp)
    if items is not None:
        mp = m.Map(Target.TEST.value, items, gis)
        # logging.info(pprint.pprint(mp))
        mp.build()
        logging.info("Map from items successful.")
        items = items.group("Property")
        mp = m.Map(Target.TEST.value, items, gis)
        mp.build()


def test_def():
    urls = m.expand_urls(
        "https://services2.arcgis.com/pc4beVTMEhYHqerq/ArcGIS/rest/services/land_use/FeatureServer",
        range(0, 4),
    )
    tmp = m.Template("land_use", "40134429392a42ceb2d4b977b076d042").load(gis)
    items = m.Items.from_template(urls, tmp)
    test_map = "40134429392a42ceb2d4b977b076d042"
    mp = m.Map(test_map, items.layers(), gis)
    definition = mp.handle.get_data()
    logging.info(pprint.pprint(definition))


def test_def2(id):
    tmp = gis.content.get(id)
    logging.info(pprint.pprint(tmp.get_data()))
    logging.info(tmp.get_data())


def read_plss():
    tmp = m.Templates.from_workbook("examples/grants_pass/workbooks/plss.csv")
    items = tmp.into_items()
    items = items.layers()
    logging.debug(pprint.pprint(items))
    test_map = "40134429392a42ceb2d4b977b076d042"
    mp = m.Map(test_map, items, gis)
    logging.info(pprint.pprint(mp))


def no_template():
    url = "https://gis.co.josephine.or.us/arcgis/rest/services/Assessor/Assessor_Taxlots/FeatureServer/0"
    item = m.Item(url, title="Taxlots").layer()
    mp = m.Map(Target.TEST.value, [item], gis)
    logging.info(pprint.pprint(mp))
    mp.build()


def test_rasters():
    # tmp = m.Templates.from_workbook("examples/grants_pass/workbooks/workbook.csv")
    tmp = m.Templates.from_workbook("examples/grants_pass/workbooks/aerials.csv")
    imagery = tmp.template["aerials"].into_items().rasters()
    imagery = imagery.group("Aerials")
    # logging.info(pprint.pprint(layers))
    # layers = []
    # for item in items:
    #     layer = m.Layer.from_raster(item)
    #     layers.append(layer)
    # lyrs = m.Layers(layers)
    # lyrs = lyrs.group("Aerials")
    mp = m.Map(Target.TEST.value, imagery, gis)
    mp.build()


def search():
    item = gis.content.get("8297f5bc7c4c4c8ba641d0d19971aaff")
    # item = gis.content.get(Target.STAFF.value)
    d = m.Template.get_search(item)
    logging.info("items: %s", len(d))
    logging.info(pprint.pprint(d))


def address():
    tmp = m.Templates.from_workbook("examples/grants_pass/workbooks/property.csv")
    tmp = tmp.template["property"].items["property_3"]
    item = tmp.into_item()
    mp = m.Map(Target.TEST.value, item, gis)
    mp.build()


def boundary():
    tmp = m.Templates.from_workbook(
        "examples/grants_pass/workbooks/boundaries_group.csv"
    )
    tmp = tmp.template["boundaries_group"].items["boundaries_group_5"]
    # logging.info(tmp)
    item = tmp.into_item()
    # logging.info(pprint.pprint(item))
    mp = m.Map(Target.TEST.value, item, gis)
    # logging.info(pprint.pprint(mp))
    mp.build()


def boundaries():
    tmp = m.Templates.from_workbook("examples/grants_pass/workbooks/workbook.csv")
    logging.info("workbook read")
    # logging.info(pprint.pprint(tmp))
    # items = tmp.items["boundaries_group"].items["boundaries_group_0"]
    items = tmp.template["boundaries_group"].into_items().group("Boundaries")
    # logging.info(pprint.pprint(items))
    mp = m.Map(Target.TEST.value, items, gis)
    # logging.info(pprint.pprint(mp))
    mp.build()


def environment():
    tmp = m.Templates.from_workbook("examples/grants_pass/workbooks/workbook.csv")
    fema = tmp.template["fema_flood_wv"].into_items().group("FEMA Flood Hazard")
    deq = (
        tmp.template["deq_dw_source"]
        .into_items()
        .group("Drinking Water Source Areas (DEQ)")
    )
    logging.info("workbook read")
    mp = m.Map(Target.TEST.value, deq, gis)
    mp.build()


def utilities():
    tmp = m.Templates.from_workbook("examples/grants_pass/workbooks/workbook.csv")
    power = (
        tmp.template["power_gas"].into_items().group("Power & Gas (Internal Use Only)")
    )
    water = tmp.template["water_wv"].into_items().group("Water Distribution")
    storm = tmp.template["stormwater"].into_items().group("Stormwater")
    storm = tmp.template["stormwater"].items["stormwater_0"].into_item()
    mp = m.Map(Target.TEST.value, storm, gis)
    mp.build()


def planning():
    tmp = m.Templates.from_workbook("examples/grants_pass/workbooks/workbook.csv")
    historic = (
        tmp.template["historic_cultural"].into_items().group("Historic/Cultural Areas")
    )
    agreements = tmp.template["agreements"].into_items().group("Agreements & Financial")
    # items = tmp.into_items().group("Planning")
    mp = m.Map(Target.TEST.value, agreements, gis)
    mp.build()


def test_all():
    test_named()
    workbook()
    workbooks()
    from_workbook()
    into_item()
    into_items()
    into_all_items()
    item()
    items()
    layer()
    group()
    layers()
    logging.info("All tests succeeded.")
