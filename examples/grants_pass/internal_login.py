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
PORTAL = "https://gis.grantspassoregon.gov/arcgis/home"
CLIENT_ID = os.getenv("INTERNAL_ID")
logging.info("Environmental variables loaded.")
INT_CONN = GIS(PORTAL, client_id=CLIENT_ID)
