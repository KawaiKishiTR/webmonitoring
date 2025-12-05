from pathlib import Path
from dotenv import load_dotenv
import os


### FOLDER PATHS
yemekhane_folder = Path(__file__).parent
folder = yemekhane_folder.parent
cache_folder = yemekhane_folder / "cache"

### FİLE PATHS
dotenv_file = folder / ".env"


### LOAD .ENV FİLE
load_dotenv(dotenv_file)

### .ENV VARİABLES
CU_YEMEKHANE = os.environ["CU-YEMEKHANE"]
CU_YEMEKHANE_URL = os.environ["CU-YEMEKHANE-URL"]
