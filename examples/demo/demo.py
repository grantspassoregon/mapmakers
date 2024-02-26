import mapmakers as m
import logging

logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

gis = GIS_CONN
demo_id = "6b81b63a99e74192ac00c3a53b88ca27"

templates = {}
templates.update({"aerials": "553b8d97bbeb415c81e41bbb0649d66a"})
templates.update({"boundaries": "c65bd751b50441cd9e07f9607f151b34"})
templates.update({"plss": "f1e719ca11d248178d2d886654b38f44"})
templates.update({"property": "c984c06eaf6f4869aab5ec3eaac999df"})


def workbook():
    tmp = m.Templates.from_obj(templates, gis)
    logging.info("Templates: %s", len(tmp.template))
    tmp.workbook(gis, "examples/demo", True)
    logging.info("Workbook printed.")


def aerials(template):
    imagery = template.template["aerials"].into_items().rasters()
    imagery = imagery.group("Aerials")
    return imagery


def property(template):
    return template.template["property"].into_items().group("Property")


def boundaries(template):
    plss = template.template["plss"].into_items().group("PLSS")
    boundaries = template.template["boundaries"].into_items().layers()
    logging.info("Appending PLSS")
    boundaries = boundaries.append(plss).group("Boundaries")
    return boundaries


def cherry_pick(t: m.Templates):
    # cherry pick an item using the item name
    city_limits = t.template["boundaries"].items["boundaries_5"].into_item()
    prop = t.template["property"].into_items()
    # index into *items* to cherry pick layers
    prop.items = prop.items[1:4]
    quarters = t.template["plss"].into_items()
    # the type of the *items* property is a list
    # to cherry pick a single item, pass it in a list
    quarters.items = [quarters.items[0]]
    lyrs = prop
    # use extend to add a list of items to the *items* field
    lyrs.items.extend(quarters.items)
    # use append to add a single item to the *items* field
    lyrs.items.append(city_limits)
    mp = m.Map(demo_id, lyrs, gis)
    mp.build()
    logging.info("Target map updated.")


def load():
    return m.Templates.from_workbook("examples/demo/workbook.csv")


def build():
    workbook()
    template = load()
    mp = m.Map(
        demo_id,
        [
            aerials(template),
            property(template),
            boundaries(template),
        ],
        gis,
    )
    mp.build()
    logging.info("Target map updated.")


logging.info("Run `login.py` to log in and create the GIS_CONN variable.")
