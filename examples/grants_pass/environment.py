import mapmakers as m
import logging


def fema(t):
    lyrs = t.template["fema_flood_wv"].into_items()
    for lyr in lyrs:
        lyr.visible = True
    return lyrs.group("NFHL (FEMA)", False)


def nfhl(t):
    lyrs = t.template["nfhl"].into_items()
    # set default visible layers
    lyrs.items[2].visible = True  # flood hazard zones
    lyrs.items[6].visible = True  # base flood elevations
    lyrs.items[11].visible = True  # LOMRS
    lyrs.items[12].visible = True  # FIRM panels
    return lyrs.group("NFHL (local copy)", False)  # parent group not visible


def esh(t):
    lyrs = t.template["esh_2025"].into_items()
    lyrs.reverse()
    lyrs.items[8].visible = True  # show main ESH layer only by default
    return lyrs.group("Essential Salmon Habitat (DSL)", False)


def deq(t):
    lyrs = t.template["deq_dw_source"].into_items()
    lyrs.items[4].visible = True  # Groundwater 2-yr TOT (Zone 1 for Springs)
    return lyrs.group("Drinking Water Source Areas (DEQ)", False)


def environment(t):
    env = t.template["contours_1ft"].into_items().vector_tiles()
    wetlands = t.template["wetlands"].into_items().layers()
    streams = t.template["features"].items["features_1"].into_item().layer()
    hazards = t.template["hazards"].into_items().layers()
    env.extend([wetlands, esh(t), deq(t), streams, nfhl(t), fema(t), hazards])
    return env.group("Environment")


if __name__ == "__main__":
    gis = GIS_CONN

    TEST = "2bc59679ad4040f4b7eb9ebec358152b"
    templates = {}
    templates.update({"contours_1ft": "f84bca3cfa884c57800242cff68e1a35"})
    templates.update({"deq_dw_source": "2787dd5d59aa44caa4628209797374ac"})
    templates.update({"esh_2025": "e2c68a56743142f883cc4874e621492e"})
    templates.update({"features": "63d8e60aff49498c8977548f58e1331a"})
    templates.update({"fema_flood_wv": "e0e23c893acd49a286d449d6741610cd"})
    templates.update({"hazards": "3db4a937c3f74a989412d4aae3688352"})
    templates.update({"nfhl": "2ca3f59c5749424eac2c9c07334b27a9"})
    templates.update({"wetlands": "42092cbf017745348a0e9b50bc9bec23"})
    t = m.Templates.from_obj(templates, gis)

    def build():
        mp = m.Map(
            TEST,
            [
                environment(t),
            ],
            gis,
        )
        mp.build()
        logging.info("Target map updated.")
