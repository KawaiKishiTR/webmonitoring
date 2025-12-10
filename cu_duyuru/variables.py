from main_variables import *
import json

### FOLDER PATHS
duyuru_folder = folder / "cu_duyuru"
cache_folder = duyuru_folder / "cache"

cache_folder.mkdir(exist_ok=True)

### .ENV VARİABLES
CU_DUYURU = os.environ["CU-DUYURU"]
CU_DUYURU_URLS = json.loads(os.environ["CU-DUYURU-URLS"])
