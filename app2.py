from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

# Load the model
with open(app.config['MODEL_PATH'], 'rb') as model_file:
    model = pickle.load(model_file)

data = pd.read_csv("dynamic_pricing.csv")

@app.route('/')
def home():
    return render_template('index2.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        features = [
            int(request.form['number_of_riders']),
            int(request.form['number_of_drivers']),
            int(request.form['vehicle_type']),
            float(request.form['expected_ride_duration']),
        ]
        
        input_array = np.array([features])
        prediction = model.predict(input_array)[0]

        return render_template('result.html', prediction=round(prediction, 2))
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/graph')
def show_graph():
    high_demand_percentile = 75
    low_demand_percentile = 25

    data['demand_multiplier'] = np.where(data['Number_of_Riders'] > np.percentile(data['Number_of_Riders'], high_demand_percentile),
                                        data['Number_of_Riders'] / np.percentile(data['Number_of_Riders'], high_demand_percentile),
                                        data['Number_of_Riders'] / np.percentile(data['Number_of_Riders'], low_demand_percentile))

    # Calculate supply_multiplier based on percentile for high and low supply
    high_supply_percentile = 75
    low_supply_percentile = 25

    data['supply_multiplier'] = np.where(data['Number_of_Drivers'] > np.percentile(data['Number_of_Drivers'], low_supply_percentile),
                                        np.percentile(data['Number_of_Drivers'], high_supply_percentile) / data['Number_of_Drivers'],
                                        np.percentile(data['Number_of_Drivers'], low_supply_percentile) / data['Number_of_Drivers'])

    # Define price adjustment factors for high and low demand/supply
    demand_threshold_high = 1.2  # Higher demand threshold
    demand_threshold_low = 0.8  # Lower demand threshold
    supply_threshold_high = 0.8  # Higher supply threshold
    supply_threshold_low = 1.2  # Lower supply threshold

    # Calculate adjusted_ride_cost for dynamic pricing
    data['adjusted_ride_cost'] = data['Historical_Cost_of_Ride'] * (
        np.maximum(data['demand_multiplier'], demand_threshold_low) *
        np.maximum(data['supply_multiplier'], supply_threshold_high)
    )


    # Calculate the profit percentage for each ride
    data['profit_percentage'] = ((data['adjusted_ride_cost'] - data['Historical_Cost_of_Ride']) / data['Historical_Cost_of_Ride']) * 100
    # Identify profitable rides where profit percentage is positive
    profitable_rides = data[data['profit_percentage'] > 0]

    # Identify loss rides where profit percentage is negative
    loss_rides = data[data['profit_percentage'] < 0]

    # Calculate the count of profitable and loss rides
    profitable_count = len(profitable_rides)
    loss_count = len(loss_rides)

    # Create a donut chart to show the distribution of profitable and loss rides
    labels = ['Profitable Rides', 'Loss Rides']
    values = [profitable_count, loss_count]
    data["Vehicle_Type"] = data["Vehicle_Type"].map({"Premium": 1,
                                                 "Economy": 0})

    x = np.array(data[["Number_of_Riders", "Number_of_Drivers", "Vehicle_Type", "Expected_Ride_Duration"]])
    y = np.array(data[["adjusted_ride_cost"]])
    
    y_pred = model.predict(x)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y.flatten(), y=y_pred, mode='markers', name='Actual vs Predicted'))
    fig.add_trace(go.Scatter(x=[min(y.flatten()), max(y.flatten())], y=[min(y.flatten()), max(y.flatten())],
                             mode='lines', name='Ideal', line=dict(color='red', dash='dash')))

    fig.update_layout(title='Actual vs Predicted Values', xaxis_title='Actual Values', yaxis_title='Predicted Values', showlegend=True)
    
    graph_html = fig.to_html(full_html=False)
    return render_template('graph.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)