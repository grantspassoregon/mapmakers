import mapmakers as m
import copy
import logging


def public_safety(t, public=False):
    zonehaven = t.template["zonehaven"].items["zonehaven_0"].into_item()
    zonehaven.title = "Zonehaven"
    fire = t.template["fire"].into_items()
    fire.items.append(zonehaven)
    fire = fire.group("Fire").into_layer()
    ems = m.Item(
        "https://gis.ecso911.com/server/rest/services/Hosted/EMS_Polygon_View/FeatureServer/0",
        title="EMS Response Zones (ECSO 911)",
    )
    fire_zone = m.Item(
        "https://gis.ecso911.com/server/rest/services/Hosted/Fire_Polygon_View/FeatureServer/0",
        title="Fire Response Zones (ECSO 911)",
    )
    law = m.Item(
        "https://gis.ecso911.com/server/rest/services/Hosted/Law_Polygon_View/FeatureServer/0",
        title="Law Enforcement Zone (ECSO 911)",
    )
    ecso = m.Items([law, fire_zone, ems]).layers()
    ecso_public = copy.deepcopy(ecso)
    if public:
        ecso_public = ecso_public.group("Public Safety")
        return ecso_public
    else:
        ecso.append(fire)
        ecso = ecso.group("Public Safety")
        return ecso


if __name__ == "__main__":
    gis = GIS_CONN

    TEST = "2bc59679ad4040f4b7eb9ebec358152b"

    templates = {}
    templates.update({"fire": "c4addbc208a14dc4990f10389698d3eb"})
    templates.update({"zonehaven": "21df018dc0b44499bbf055bc6dbbc7cf"})
    t = m.Templates.from_obj(templates, gis)

    def build(public=True):
        mp = m.Map(
            TEST,
            [
                public_safety(t, public),
            ],
            gis,
        )
        mp.build()
        logging.info("Target map updated.")
