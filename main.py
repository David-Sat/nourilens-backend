import json
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
from ai_utils.ai_adapter import process_image, filter_list, create_raw_json, add_nutritional_data, get_suggestions
from ai_utils.failure_handling import retry_function
from typing import List
from pydantic import BaseModel


class Item(BaseModel):
    itemName: str
    price: float
    nutritionalValue: int

class ReceiptItem(BaseModel):
    itemName: str
    price: float
    nutritionalValue: int

class SuggestionItem(BaseModel):
    prevItem: str
    prevItemPrice: float
    newItem: str
    newItemPrice: float
    description: str

class SuggestionsRequest(BaseModel):
    items_string: str


app = FastAPI()

origins = [
    "http://localhost:61012", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

mock_items = [
    {"itemName": "Frischmilch 3,5%", "price": 0.88, "nutritionalValue": 7},
    {"itemName": "Bio-Salami", "price": 0.55, "nutritionalValue": 4},
    {"itemName": "Schältomaten 425 ml Dose", "price": 0.55, "nutritionalValue": 6},
    {"itemName": "Dt. Markenbutter", "price": 2.09, "nutritionalValue": 3},
    {"itemName": "Bratwurst Gr. QS", "price": 3.49, "nutritionalValue": 5},
    {"itemName": "Premium Salami auf -", "price": 1.39, "nutritionalValue": 4},
    {"itemName": "Bio Hähn.-Brustfilet", "price": 8.62, "nutritionalValue": 10},
    {"itemName": "Bio Eier oKt, 10 St.", "price": 3.29, "nutritionalValue": 9}
]

@app.get("/mock-items", response_model=List[Item])
async def get_mock_items():
    return mock_items


@app.post("/upload", response_model=List[Item])
async def upload_image(file: UploadFile = File(...)):
    # Read and process the image
    image_bytes = await file.read()
    image_stream = BytesIO(image_bytes)
    pil_image = Image.open(image_stream)
    processed_image_output = process_image(pil_image)

    # Filter, convert to JSON, and enrich the data
    filtered_list = filter_list(processed_image_output)
    raw_json = retry_function(create_raw_json, filtered_list)
    enriched_json = retry_function(add_nutritional_data, raw_json)

    output_json = json.loads(enriched_json)

    return output_json['receiptItems']


@app.post("/suggestions", response_model=SuggestionItem)
async def healthy_alternatives(request_body: SuggestionsRequest):

    items_string = request_body.items_string
    suggestions = retry_function(get_suggestions, items_string)

    output_json = json.loads(suggestions)
    
    return output_json


@app.post("/test")
async def test_post(data: dict):
    return {"echo": data}