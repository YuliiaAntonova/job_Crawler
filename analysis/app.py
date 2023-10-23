from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI()

# Load the trained model from the Pickle file
with open("classifier.pkl", "rb") as file:
    model = pickle.load(file)


class JobNote(BaseModel):
    title: int
    company: int
    source: int
    location: int


def predict_salary(title, company, source, location):
    num_features = 1321
    input_data = [0] * num_features  # Initialize with zeros

    input_data[0] = title
    input_data[1] = company
    input_data[2] = source
    input_data[3] = location

    prediction = model.predict([input_data])

    if prediction[0] == 1:
        return "Fake note"
    else:
        return "It's a Job note"


@app.post('/predict_salary')
def predict_job_salary(job_note: JobNote):
    result = predict_salary(job_note.title, job_note.company, job_note.source, job_note.location)
    return {"prediction": result}
