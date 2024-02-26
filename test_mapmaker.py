from arcgis.gis import GIS
import mapmakers as m
import logging
from examples.grants_pass.refs import *
import pprint

# format log messages to include time before message
logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

gis = GIS()


def test_temp_item():
    item = m.TemplateItem(
        "title",
        "group_name",
        "item_name",
        "layer_definition",
        "popup_info",
        "url",
        ["search"],
    )
    print(pprint.pprint(item))


def test_initial_read():
    id = "207f8377cf9c403b996c7f02de0ac477"
    # assert m.Item.check_template_in(id, gis)
    tmp = m.Template("missing_sidewalks", id).load(gis)
    assert tmp.check_template(gis)
    tmp = tmp.with_names(
        [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
        ],
    )
    tmp.workbook("examples/data/workbook_named.csv", named=True)
    print(pprint.pprint(tmp))


def test_item_init():
    tmp = m.Template.from_workbook("examples/data/workbook_named.csv")
    logging.info(pprint.pprint(tmp))
    lib = m.Templates()
    lib.add(tmp)
    itm = m.Item("https://www.google.com", lib.template["workbook_named"].items["a"])
    itm.visible = True
    assert itm.check_url()
    itm1 = m.Item("second", lib.template["workbook_named"].items["b"])
    itm2 = m.Item("third", lib.template["workbook_named"].items["c"])
    itms = m.Items([itm, itm1, itm2])
    logging.info(len(list(itms)))


def test_make_template():
    id = "207f8377cf9c403b996c7f02de0ac477"
    tmp = m.Template("missing_sidewalks", id)
    assert tmp.check_template(gis)
    tmp.workbook("examples/data/workbook.csv")


def test_read_template():
    id = "207f8377cf9c403b996c7f02de0ac477"
    tmp = m.Template("missing_sidewalks", id)
    assert tmp.check_template(gis)
    tmp.from_workbook("examples/data/workbook_named.csv")
    lib = m.Templates()
    lib.add(tmp)
    logging.info(lib.template.keys())
