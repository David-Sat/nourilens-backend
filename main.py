from fastapi import FastAPI, File, UploadFile
from io import BytesIO
from PIL import Image
from ai_utils.ai_adapter import process_image, filter_list, create_raw_json, enrich_json
from ai_utils.failure_handling import retry_function


app = FastAPI()

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Read and process the image
    image_bytes = await file.read()
    image_stream = BytesIO(image_bytes)
    pil_image = Image.open(image_stream)
    processed_image_output = retry_function(process_image, pil_image)

    # Filter, convert to JSON, and enrich the data
    filtered_list = retry_function(filter_list, processed_image_output)
    raw_json = retry_function(create_raw_json, filtered_list)
    enriched_json = retry_function(enrich_json, raw_json)

    return {"message": "Image processed and data enriched", "enriched_output": enriched_json}

