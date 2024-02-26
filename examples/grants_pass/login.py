from arcgis.gis import GIS
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

load_dotenv()
PORTAL = "https://grantspassoregon.maps.arcgis.com/"
CLIENT_ID = os.getenv("CLIENT_ID")
logging.info("Environmental variables loaded.")
GIS_CONN = GIS(PORTAL, client_id=CLIENT_ID)
