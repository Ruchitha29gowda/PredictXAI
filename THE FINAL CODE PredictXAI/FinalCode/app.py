from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  
import joblib
import os
import pandas as pd
import shap
import lime
import lime.lime_tabular
import numpy as np
import matplotlib.pyplot as plt
from flask import send_from_directory
import tempfile
import atexit
import shutil
import base64
from io import BytesIO
import warnings
import dice_ml
from dice_ml.utils import helpers
from sklearn.preprocessing import StandardScaler
    
app = Flask(__name__)
CORS(app)  

temp_dir = tempfile.mkdtemp()
atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))

scaler_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scaler.pkl')
boosting_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best_voting_model.pkl')
X_train_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'X_train.npy')

if not os.path.exists(scaler_path):
    raise FileNotFoundError(f"Scaler file not found: {scaler_path}")

if not os.path.exists(boosting_model_path):
    raise FileNotFoundError(f"Boosting model file not found: {boosting_model_path}")

scaler = joblib.load(scaler_path)
boosting_model = joblib.load(boosting_model_path)
X_train = np.load(X_train_path)

feature_names = ['age', 'sex', 'cp', 'trestbps', 'chol', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']

def generate_shap_plot(model, features, feature_names, temp_dir):
    
    try:
        explainer_model = model.named_estimators_['CatBoost']
    except (AttributeError, KeyError):
        explainer_model = model  # fallback
    
    explainer = shap.TreeExplainer(explainer_model)

    shap_values = explainer.shap_values(features)
    
    # For binary classification, take the positive class
    if isinstance(shap_values, list):
        shap_values = shap_values[1]
    
    # Take the first instance's SHAP values
    instance = features.iloc[0]
    instance_shap_values = shap_values[0]

    plt.switch_backend('Agg')  

    plot_file = os.path.join(temp_dir, f"shap_plot_{os.urandom(4).hex()}.png")
    
    #Plot 1: bar plot
    # plt.figure()
    # shap.summary_plot(shap_values, features, feature_names=feature_names, plot_type="bar", show=False)
    # plt.tight_layout()
    # plt.savefig(plot_file, bbox_inches='tight', dpi=100)
    # plt.close()

    # Plot 1: Waterfall plot
    plt.figure()
    shap.waterfall_plot(
        shap.Explanation(
            values=instance_shap_values,
            base_values=explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value,
            data=instance,
            feature_names=feature_names
        ),
        show=False
    )
    plt.tight_layout()
    plt.savefig(plot_file, bbox_inches='tight', dpi=100)
    plt.close()

    force_file = os.path.join(temp_dir, f"shap_force_{os.urandom(4).hex()}.png")
    
    plt.figure()
    shap.force_plot(
        explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value,
        instance_shap_values,
        instance,
        feature_names=feature_names,
        matplotlib=True,
        show=False
    )
    plt.tight_layout()
    plt.savefig(force_file, bbox_inches='tight', dpi=100)
    plt.close()
    
    return plot_file, force_file

def generate_lime_plot(model, sample, feature ):

    explainer_lime = lime.lime_tabular.LimeTabularExplainer(
        X_train,
        mode='classification',
        class_names=["Class 0 - No Stroke", "Class 1 - Stroke"],
        feature_names=feature_names
    )

    exp = explainer_lime.explain_instance(sample.flatten(), model.predict_proba)

    lime_explanation = exp.as_list()

    print("\nLIME Explanation Values:")
    for feature, value in lime_explanation:
        print(f"{feature}: {value:.4f}")

    features = [x[0] for x in lime_explanation] 
    values = [x[1] for x in lime_explanation]
    colors = ['#d62828' if x > 0 else '#4895ef' for x in values]  # Blue for positive, red for negative

    plt.figure(figsize=(7, 4))
    # bars = plt.barh(features, values, color=colors)
    bars = plt.barh(features[::-1], values[::-1], color=colors[::-1])
    plt.title('LIME Feature Importance', fontsize=14)
    plt.xlabel('Contribution to Prediction', fontsize=12)
    plt.ylabel('Features', fontsize=12)
    plt.axvline(x=0, color='black', linestyle='--', linewidth=0.8)
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        label_x = width + (0.01 if width > 0 else -0.01)
        plt.text(label_x, bar.get_y() + bar.get_height()/2,
                 f'{width:.3f}',
                 va='center', ha='left' if width > 0 else 'right',
                 fontsize=10)

    plt.tight_layout()
    
    # Save figure to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()
    
    # Convert to base64
    lime_image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return lime_image_base64

def generate_counterfactuals(model, features, target_class, original_prediction, n_cf=2):
    X_df = pd.DataFrame(X_train, columns=feature_names)
    X_df['target'] = boosting_model.predict(X_train)

    # Prepare Dice Data and Model objects
    data_dice = dice_ml.Data(dataframe=X_df, continuous_features=feature_names,
                            #   categorical_features=categorical,
                              outcome_name='target',
                            #   feature_ranges={
                            #     'age': [0,100],
                            #     'sex': [0,1],
                            #     'cp': [0,3],
                            #     'trestbps': [90, 200],
                            #     'chol': [100,600],
                            #     'thalach': [60,202],
                            #     'exang': [0,1],
                            #     'oldpeak': [0.0,6.5],
                            #     'slope': [ 0,2],
                            #     'ca': [0,3],
                            #     'thal': [0, 3],  
                            #     }
    )

    model_dice = dice_ml.Model(model=model, backend="sklearn", model_type='classifier')

    explainer = dice_ml.Dice(data_dice, model_dice, method='random')
    # explainer = dice_ml.Dice(data_dice, model_dice, method='genetic')
    # explainer = dice_ml.Dice(data_dice, model_dice, method='kdtree')

    input_df = pd.DataFrame([features], columns=feature_names)
    
    try:
        dice_exp = explainer.generate_counterfactuals(input_df, total_CFs=n_cf, desired_class="opposite", 
                                                    features_to_vary=['cp','trestbps','chol','thalach','exang','oldpeak','slope','ca','thal'],
                                                    permitted_range={
                                                        # 'cp': [0,3],
                                                        'trestbps': [90, 200],
                                                        'chol': [100,600],
                                                        # 'thalach': [60,202],
                                                        # 'exang': [0,1],
                                                        'oldpeak': [0.0,6.5],
                                                        'slope': [ 0,2],
                                                        # 'ca': [0,3],
                                                        'thal': [0, 3],  
                                                        },
                                                    # algorithm="genetic", 
                                                    verbose=True
        )
    except Exception as e:
        print("DiCE failed to generate counterfactuals:", e)
        return []

    cf_df = dice_exp.cf_examples_list[0].final_cfs_df

    print("Original input:\n", input_df)
    print("Original prediction:", original_prediction)
    print("Model prediction:", model.predict(input_df))
    print("Prediction probas:", model.predict_proba(input_df))

    counterfactuals = []

    for idx, row in cf_df.iterrows():
        print(row[feature_names]) 

        changes = {}
        for col in feature_names:
            orig = float(features[feature_names.index(col)])
            new = float(row[col])
            if not np.isclose(orig, new, atol=0.1):
                changes[col] = {
                    'original': round(orig, 2),
                    'new': round(new, 2)
                }

        cf_pred = int(row.get('prediction', target_class[0]))
        row_values = row[feature_names].values.astype(float).reshape(1, -1)
        probability_change = float(np.max(model.predict_proba(row_values)))
        explanation = ({
            'changes': changes,
            'new_prediction': cf_pred,
            'probability_change': probability_change
        })

        print(f"\nCounterfactual #{idx + 1}")
        print("Suggested changes:")
        for feat, val in changes.items():
            print(f"  - {feat}: {val['original']} → {val['new']}.abs()")
        print(f"New prediction: {cf_pred}")
        print(f"Confidence of new prediction: {probability_change:.4f}")

        if cf_pred != original_prediction:
            counterfactuals.append(explanation)


    return counterfactuals

@app.route('/predict', methods=['POST'])
def predict():
    try:
        print(boosting_model.named_estimators_)

        data = request.json
        print("DATA RECEIVED:\n", data)

        if 'features' not in data:
            return jsonify({'error': "'features' key is missing"}), 400
        
        features = data['features']
        input_data = np.array([features]).reshape(1, -1)  
        
        expected_feature_length = 11                                
        if len(features) < expected_feature_length:
            return jsonify({'error': f"Expected {expected_feature_length} features, got {len(features)}"}), 400


        print("\nFEATURES for Prediction:", input_data)
        print("Number of expected features:", boosting_model.n_features_in_)

        required_features = pd.DataFrame(input_data, columns=feature_names)
        features_scaled = scaler.transform(required_features)
        print("\nScaled Features: ", features_scaled) 
        print(features_scaled.shape)

        prediction = boosting_model.predict(features_scaled)
        print("\nPrediction: ", prediction)  # Debugging
        prediction_proba = boosting_model.predict_proba(features_scaled)
        print("\nPrediction Probabilities: ", prediction_proba)  # Debugging

         # Generate SHAP plots
        shap_bar_file, shap_force_file = generate_shap_plot(
            boosting_model, 
            required_features, 
            feature_names,
            temp_dir
        )

        # Generate LIME explanation
        lime_plot_base64 = generate_lime_plot(
            boosting_model,
            input_data,
            feature_names
        )
        # Suppress FutureWarnings
        warnings.filterwarnings("ignore")
        # Generate counterfactuals - target the opposite class
        target_class = 1 - prediction
        counterfactuals = generate_counterfactuals(boosting_model, features, target_class, prediction[0])

        # Get just the filenames for the endpoints
        shap_bar_filename = os.path.basename(shap_bar_file)
        shap_force_filename = os.path.basename(shap_force_file)


         # Use SHAP TreeExplainer
        try:
            model_for_explanation = boosting_model.named_estimators_['CatBoost']
        except AttributeError:
            model_for_explanation = boosting_model  # fallback
        
        # SHAP explanation
        explainer = shap.TreeExplainer(model_for_explanation)
        shap_values = explainer.shap_values(required_features)

        print("SHAP shape:", np.array(shap_values).shape)
        
       # Assuming class 1 is the positive class
        if isinstance(shap_values, list):
            shap_values_instance = shap_values[1][0]  # Get SHAP values for the first instance and class 1
        else:
            shap_values_instance = shap_values[0]  # For binary but non-list return

        # Make sure shap_values_instance is 1D with 11 values
        shap_values_instance = shap_values_instance.flatten()[:len(feature_names)]  # Ensure correct size

        if len(shap_values_instance) != len(feature_names):
            raise ValueError("SHAP values and feature names must have the same length.")

        print("Length of feature_names:", len(feature_names))
        print("Length of shap_values_instance:", len(shap_values_instance))
        print("Length of required_features.iloc[0]:", len(required_features.iloc[0].values))

        shap_df = pd.DataFrame({
            'feature': feature_names,
            'shap_value': shap_values_instance,
            'value': required_features.iloc[0].values
        })

        print("SHAP values (raw):", shap_values)
        print("SHAP DataFrame:", shap_df)
        print("Feature Names:", feature_names)

        print(boosting_model.named_estimators_['CatBoost'].feature_importances_)


        shap_df['abs_shap'] = shap_df['shap_value'] #here we should use .abs() 
        top_features = shap_df.sort_values('abs_shap', ascending=False).head(3)

        contributing_factors = ', '.join(f"{row['feature']} (value: {row['value']})" for _, row in top_features.iterrows())
        explanation = f"The model predicts a {'high' if prediction[0] == 1 else 'low'} risk of heart stroke. Top contributing factors: {contributing_factors}."

        # Return JSON response
        return jsonify({
            'prediction': int(prediction[0]),  
            'probabilities': prediction_proba.tolist(),
            "explanation": explanation,
             "shap_plot_bar": f"/shap_plot/{shap_bar_filename}",
            "shap_plot_force": f"/shap_plot/{shap_force_filename}",
            "lime_plot": lime_plot_base64,
            'counterfactuals': counterfactuals,
        })

    except Exception as e:
        print("\n ERROR IS: ", e)
        return jsonify({'error': str(e)}), 500  

@app.route('/shap_plot/<filename>')
def serve_shap_plot(filename):
    return send_from_directory(temp_dir, filename)

@app.route("/lime_plot")
def lime_plot():
    return send_file("lime_plot.png", mimetype="image/png")

if __name__ == '__main__':
    app.run(debug=True)