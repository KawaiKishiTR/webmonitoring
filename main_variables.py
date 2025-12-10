from pathlib import Path
from dotenv import load_dotenv
import os

### FOLDER PATHS
folder = Path(__file__).parent

### FİLE PATHS
dotenv_file = folder / ".env"

### LOAD .ENV FİLE
load_dotenv(dotenv_file)
