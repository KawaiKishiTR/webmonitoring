from main_variables import *

### FOLDER PATHS
yemekhane_folder = folder / "yemekhane"
cache_folder = yemekhane_folder / "cache"
yemekler_folder = cache_folder / "yemekler"

### Creating paths
cache_folder.mkdir(exist_ok=True)
yemekler_folder.mkdir(exist_ok=True)

### .ENV VARİABLES
CU_YEMEKHANE = os.environ["CU-YEMEKHANE"]
CU_YEMEKHANE_URL = os.environ["CU-YEMEKHANE-URL"]
