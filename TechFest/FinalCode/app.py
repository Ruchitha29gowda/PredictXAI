from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the scaler and the best boosting model
scaler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scaler.pkl')
voting_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), './best_voting_model.pkl')

# Check if the scaler and model files exist before loading
if not os.path.exists(scaler_path):
    raise FileNotFoundError(f"Scaler file not found: {scaler_path}")

if not os.path.exists(voting_model_path):
    raise FileNotFoundError(f"Boosting model file not found: {voting_model_path}")

scaler = joblib.load(scaler_path)
voting_model = joblib.load(voting_model_path)

# @app.route('/predict', methods=['POST'])
@app.route('/predict', methods=['POST'])


def predict():
    print("Scaler Path:", os.path.abspath("scaler.pkl"))
    try:
        # Get the input data from the request
        data = request.json
        print("DATA RECEIVED IS :\n", data)
        features = data['features'] 
        
        # Check if the length of features matches the expected number
        if len(features) < 6:  # Expecting at least 6 features for the model
            raise ValueError(f"Expected at least 6 features, got {len(features)}")

        # Extract the required features for prediction (assuming you know the order)
        # required_features = [
        #     features[0],  # age
        #     features[1],  # sex
        #     features[2],  # cp
        #     features[3],  # trestbps
        #     features[4],  # chol
        #     features[5],  # thalach
        #     features[6],  # exang
        #     features[7],  # oldpeak
        #     features[8],  # slope
        #     features[9], # ca
        #     features[10], # thal
        # ]


        required_features = [
            features[8],  # slope
            features[3],  # trestbps
            features[6],  # exang
            features[7],  # oldpeak
            features[1],  # sex
            features[2],  # cp
            features[4],  # chol
            features[5],  # thalach
            features[10], # thal
            features[0],  # age
            features[9], # ca
            
        ]

        print("\n\nFEATURES for Prediction", required_features)

        # Convert features to a numpy array and scale
        features_array = np.array(features).reshape(1, -1)
        features_scaled = scaler.transform(features_array)
        print("Scaled value: ")
        print(features_scaled)
        
        # 'chol', 'thal', 'exang', 'oldpeak', 'trestbps', 'ca', 'age', 'sex', 'slope', 'cp', 'thalach
        
        # required_features = [
        #     features_scaled[0][0],  # age
        #     features_scaled[0][1],  # sex
        #     features_scaled[0][2],  # cp
        #     features_scaled[0][3],  # trestbps
        #     features_scaled[0][4],  # chol
        #     features_scaled[0][5],  # thalach
        #     features_scaled[0][6],  # exang
        #     features_scaled[0][7],  # oldpeak
        #     features_scaled[0][8],  # slope
        #     features_scaled[0][9], # ca
        #     features_scaled[0][10], # thal
        # ]

        required_features = [
            features_scaled[0][0],  # age
            features_scaled[0][1],  # sex
            features_scaled[0][2],  # cp
            features_scaled[0][3],  # trestbps
            features_scaled[0][4],  # chol
            features_scaled[0][5],  # thalach
            features_scaled[0][6],  # exang
            features_scaled[0][7],  # oldpeak
            features_scaled[0][8],  # slope
            features_scaled[0][9], # ca
            features_scaled[0][10], # thal
        ]
        
        required_features = np.array(required_features).reshape(1, -1)

        # Make predictions
        prediction = voting_model.predict(required_features)
        prediction_proba = voting_model.predict_proba(required_features)

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