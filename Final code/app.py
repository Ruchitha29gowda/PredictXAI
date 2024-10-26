from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the scaler and the best boosting model
scaler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scaler.pkl')
boosting_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), './best_ada_model.pkl')

# Check if the scaler and model files exist before loading
if not os.path.exists(scaler_path):
    raise FileNotFoundError(f"Scaler file not found: {scaler_path}")

if not os.path.exists(boosting_model_path):
    raise FileNotFoundError(f"Boosting model file not found: {boosting_model_path}")

scaler = joblib.load(scaler_path)
boosting_model = joblib.load(boosting_model_path)

# @app.route('/predict', methods=['POST'])
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data from the request
        data = request.json
        print("DATA RECEIVED IS :\n", data)
        features = data['features'] 
        
        # Check if the length of features matches the expected number
        if len(features) < 6:  # Expecting at least 6 features for the model
            raise ValueError(f"Expected at least 6 features, got {len(features)}")

        # Extract the required features for prediction (assuming you know the order)
        required_features = [
            features[1],  # sex
            features[2],  # cp
            features[3],  # trestbps
            features[7],  # thalach
            features[11], # ca
            features[12], # thal
        ]

        print("\n\nFEATURES for Prediction", required_features)

        # Convert features to a numpy array and scale
        features_array = np.array(features).reshape(1, -1)
        features_scaled = scaler.transform(features_array)
        print(features_scaled)
        
        
        required_features = [
            features_scaled[0][1],  # sex
            features_scaled[0][2],  # cp
            features_scaled[0][3],  # trestbps
            features_scaled[0][7],  # thalach
            features_scaled[0][11], # ca
            features_scaled[0][12], # thal
        ]
        
        required_features = np.array(required_features).reshape(1, -1)

        # Make predictions
        prediction = boosting_model.predict(required_features)
        prediction_proba = boosting_model.predict_proba(required_features)

        # Return the prediction and probabilities as JSON
        return jsonify({
            'prediction': int(prediction[0]),  # Convert to int for JSON serializable
            'probabilities': prediction_proba.tolist()  # Convert to list for JSON serialization
        })
    except Exception as e:
        print("\n\n ERROR IS: ", e)
        return jsonify({'error': str(e)}), 500  # Return error message

if __name__ == '__main__':
    app.run(debug=True)
