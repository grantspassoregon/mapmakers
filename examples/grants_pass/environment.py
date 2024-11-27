import mapmakers as m

# import copy
import logging
from examples.grants_pass.refs import templates

gis = GIS_CONN

TEST = "2bc59679ad4040f4b7eb9ebec358152b"
t = m.Templates.from_obj(templates, gis)


def nfhl(t):
    return t.template["nfhl"].into_items().group("NFHL (local copy)")


def esh(t):
    return t.template["dsl_esh"].into_items().group("Essential Salmon Habitat (DSL)")


def environment(t):
    fema = t.template["fema_flood_wv"].into_items().group("NFHL (FEMA)")
    nfhl = t.template["nfhl"].into_items().group("NFHL (local copy)")
    deq = (
        t.template["deq_dw_source"]
        .into_items()
        .group("Drinking Water Source Areas (DEQ)")
    )
    esh = t.template["dsl_esh"].into_items().group("Essential Salmon Habitat (DSL)")
    env = t.template["contours_1ft"].into_items().vector_tiles()
    wetlands = t.template["wetlands"].into_items().layers()
    streams = t.template["features"].items["features_1"].into_item().layer()
    hazards = t.template["hazards"].into_items().layers()
    env.extend([wetlands, esh, deq, streams, nfhl, fema, hazards])
    env = env.group("Environment")
    return env


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
