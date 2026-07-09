import os

UNIDADES = {
    "dens_susp": "g/cm³",
    "dens_solids": "g/cm³",
    "teor_solids": "fração",
    "dp_medio": "µm",
    "ROA": "-",
    "m": "-",
    "n": "-"
}

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8010"
)

BASE_URL = API_URL
