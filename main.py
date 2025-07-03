from fastapi import FastAPI, HTTPException
import requests
import xml.etree.ElementTree as ET
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Optional: allow calls from Excel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Currency API is running!"}

@app.get("/convert")
def convert(from_curr: str, to_curr: str, amount: float):
    try:
        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        response = requests.get(url, timeout=5)
        tree = ET.fromstring(response.content)

        rates = {"EUR": 1.0}
        for cube in tree.findall(".//{*}Cube[@currency]"):
            currency = cube.attrib["currency"]
            rate = float(cube.attrib["rate"])
            rates[currency] = rate

        if from_curr not in rates or to_curr not in rates:
            raise HTTPException(status_code=400, detail="Currency not found.")

        result = amount * (rates[to_curr] / rates[from_curr])
        return {"result": round(result, 4)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
