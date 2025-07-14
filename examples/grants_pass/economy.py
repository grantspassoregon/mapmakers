import mapmakers as m
import logging


def business(t):
    lyrs = t.template["business"].into_items()
    lyrs.items[1].visible = True  # set business points to visible
    return lyrs.group("Economic Development", False)  # set group to invisible


if __name__ == "__main__":
    gis = GIS_CONN

    TEST = "2bc59679ad4040f4b7eb9ebec358152b"

    templates = {}
    templates.update({"business": "a2d7706cec064905acf1e7faa1102ac4"})
    t = m.Templates.from_obj(templates, gis)

    def build():
        mp = m.Map(
            TEST,
            [
                business(t),
            ],
            gis,
        )
        mp.build()
        logging.info("Target map updated.")
