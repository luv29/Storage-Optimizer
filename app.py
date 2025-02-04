import re
import os
import json
import pickle
import uvicorn
import pandas as pd
import tensorflow as tf
from typing import List
from dotenv import load_dotenv
import google.generativeai as genai
from schemas.cargoData import CargoData
from schemas.CargoInfo import CargoInfo
from fastapi import FastAPI, HTTPException

load_dotenv()
app = FastAPI()

try:
    model = tf.keras.models.load_model('model/storage_optimizer.keras')
    with open('model/pipeline.pkl', 'rb') as file:
        loaded_pipeline = pickle.load(file)
except Exception as e:
    print(f"Error loading model or pipeline: {e}")
    raise e

slot_names = [f"{chr(65 + i // 10)}{i % 10 + 1}" for i in range(100)]

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
genai_model = genai.GenerativeModel('gemini-2.0-flash-exp')

@app.get('/')
def index():
    return {'message': 'Test'}

@app.post('/get-optimum-slots')
def get_optimum_slots(cargo_data_list: List[CargoData]):
    predictions = []
    try:
        for cargo_data in cargo_data_list:
            slot_matrix_flat = [item for sublist in cargo_data.Slot_Matrix for item in sublist]

            if len(slot_matrix_flat) != 100:
                raise ValueError("Slot_Matrix must be a 10x10 matrix.")

            features = [
                cargo_data.Cargo_ID,
                cargo_data.Size_Category,
                cargo_data.Weight,
                cargo_data.Hazardous,
                cargo_data.Stackable,
                cargo_data.Duration,
                cargo_data.Transport_Type,
                *slot_matrix_flat 
            ]

            features_df = pd.DataFrame([features], columns=[
                'Cargo_ID', 'Size_Category', 'Weight (kg)', 'Hazardous', 'Stackable', 'Duration (days)', 'Transport Type',
                *slot_names 
            ])

            processed_data = loaded_pipeline.transform(features_df)  
            prediction = model.predict(processed_data)

            predicted_slot_index = prediction.argmax(axis=1)[0]  
            predicted_slot = slot_names[predicted_slot_index]

            predictions.append({'Cargo_ID': cargo_data.Cargo_ID, 'optimum_slot': predicted_slot})

        return {'slots': predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-insights")
def get_insights(cargo_list: List[CargoInfo]):
    try:
        cargo_data = [item.dict() for item in cargo_list]

        df = pd.DataFrame(cargo_data)
        df['expected_arrival_time'] = pd.to_datetime(df['expected_arrival_time'], format='%H:%M')
        df = df.sort_values(by='expected_arrival_time')

        prompt = f"""
        You are an AI assistant helping the management of ICD Patparganj, India's first dry port.

        Here is today's cargo arrival schedule:
        {df.to_string(index=False)}

        Suggest **exactly 3 actionable steps** to efficiently unload the cargos without congestion.
        Make sure to:
        - Identify which cargos should be unloaded in parallel.
        - Consider workforce balance between manual labor and forklifts.
        - Prioritize cargo based on arrival time to avoid delays.

        Respond strictly in **JSON list format**, without markdown or any extra formatting:
        ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
        """

        response = genai_model.generate_content(prompt)
        output_text = response.text

        clean_text = re.sub(r"```json\n|\n```", "", output_text).strip()
        suggestions = json.loads(clean_text)

        return {"suggestions": suggestions}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing Gemini response. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)