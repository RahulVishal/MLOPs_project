# app.py
from flask import Flask, render_template, request
import pickle
import numpy as np
from config import Config
import pandas as pd

app = Flask(__name__)
app.config.from_object(Config)

# Load the model
with open(app.config['MODEL_PATH'], 'rb') as model_file:
    model = pickle.load(model_file)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract only the 4 features used during training
        features = [
            int(request.form['number_of_riders']),
            int(request.form['number_of_drivers']),
            int(request.form['vehicle_type']),
            float(request.form['expected_ride_duration']),
        ]

        # Convert to numpy array for prediction
        input_array = np.array([features])
        prediction = model.predict(input_array)[0]

        return render_template('result.html', prediction=round(prediction, 2))
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
