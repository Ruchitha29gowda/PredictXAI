import React, { useState } from 'react';
import axios from 'axios';
import './app.css';

const Form = () => {
    // Define state for each feature
    const [age, setAge] = useState('');
    const [sex, setSex] = useState('');
    const [cp, setCp] = useState('');
    const [trestbps, setTrestbps] = useState('');
    const [chol, setChol] = useState('');
    const [thalach, setThalach] = useState('');
    const [exang, setExang] = useState('');
    const [oldpeak, setOldpeak] = useState('');
    const [slope, setSlope] = useState('');
    const [ca, setCa] = useState('');
    const [thal, setThal] = useState('');

    // State for API response
    const [prediction, setPrediction] = useState(null);
    const [probabilities, setProbabilities] = useState([]);
    const [explanation, setExplanation] = useState("");
    const [shapBarPlot, setShapBarPlot] = useState("");
    const [shapForcePlot, setShapForcePlot] = useState("");
    const [limePlot, setLimePlot] = useState("");
    const [counterfactuals, setCounterfactuals] = useState([]);
    const [error, setError] = useState('');
    const [showForm, setShowForm] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [showInfo, setShowInfo] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        
        const features = [
            Number(age),
            Number(sex),
            Number(cp),
            Number(trestbps),
            Number(chol),
            Number(thalach),
            Number(exang),
            Number(oldpeak),
            Number(slope),
            Number(ca),
            Number(thal),
        ];

        try {
            const response = await axios.post('http://127.0.0.1:5000/predict', { features });
            const data = response.data;
            
            setPrediction(data.prediction);
            setProbabilities(data.probabilities);
            setExplanation(data.explanation);
            setShapBarPlot(data.shap_plot_bar);
            setShapForcePlot(data.shap_plot_force);
            setLimePlot(data.lime_plot);
            setCounterfactuals(data.counterfactuals || []);
            setShowForm(false);
        } catch (err) {
            setError('Error fetching prediction: ' + (err.response?.data?.error || err.message));
            console.error('Prediction error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleBackToHome = () => {
        setShowForm(true);
        setPrediction(null);
        setShapBarPlot("");
        setShapForcePlot("");
        setLimePlot("");
        setCounterfactuals([]);
    };
    
     // Function to render counterfactual explanations
     const renderCounterfactuals = () => {
        if (!counterfactuals || counterfactuals.length === 0) {
            return <p>No counterfactual explanations available for this prediction.</p>;
        }

        return (
            <div className="counterfactuals-container">
                <h3>Counterfactual Explanations</h3>
                <p className="explanation-note">
                    These show the minimal changes needed to get a different prediction:
                </p>
                
                {counterfactuals.map((cf, index) => (
                    <div key={1} className="counterfactual-box">
                        <h4>Scenario {index + 1}:</h4>
                        <div className="changes-list">
                            {Object.entries(cf.changes).map(([feature, change]) => (
                                <div key={feature} className="change-item">
                                    <span className="feature-name">{feature}:</span>
                                    <span className="original-value">{change.original}</span>
                                    <span className="arrow">→</span>
                                    {/* <span className="new-value">{change.new}</span> */}
                                    <span className="new-value">{feature === 'cp' ? Math.abs(change.new) : change.new}</span>
                                </div>
                            ))}
                        </div>
                        <div className="cf-result">
                            This change would result in: <strong>{cf.new_prediction === 1 ? 
                                "High risk of heart disease" : "Low risk of heart disease"}</strong>
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div className='form-vis'>
            <div id='form-comp'>
            <h1>Heart Stroke Prediction</h1>
            
            {showForm ? (
                <section id="form-section">
                <form onSubmit={handleSubmit} id='form'>
                    <div id="fields">
                        <input
                            type="number"
                            placeholder="Age"
                            value={age}
                            onChange={(e) => setAge(e.target.value)}
                            min="0"
                            max="100"
                            required
                        />
                        <input
                            type="number"
                            placeholder="Sex (0 or 1)"
                            value={sex}
                            onChange={(e) => setSex(e.target.value)}
                            min="0"
                            max="1"
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Chest Pain Type (cp)"
                            value={cp}
                            onChange={(e) => setCp(e.target.value)}
                            min="0"
                            max="3"
                            required
                        />
                        <input
                            type="number"
                            placeholder="Resting Blood Pressure (trestbps)"
                            value={trestbps}
                            onChange={(e) => setTrestbps(e.target.value)}
                            min="90"
                            max="200"
                            required
                        />
                    </div>
                    <div id="fields">
                        <input
                            type="number"
                            placeholder="Cholesterol (chol)"
                            value={chol}
                            onChange={(e) => setChol(e.target.value)}
                            min="100"
                            max="600"
                            required
                        />
                        <input
                            type="number"
                            placeholder="Maximum Heart Rate Achieved (thalach)"
                            value={thalach}
                            onChange={(e) => setThalach(e.target.value)}
                            min="60"
                            max="202"
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Exercise Induced Angina (exang)"
                            value={exang}
                            onChange={(e) => setExang(e.target.value)}
                            min="0"
                            max="1"
                            required
                        />
                        <input
                            type="number"
                            placeholder="Old Peak"
                            value={oldpeak}
                            onChange={(e) => setOldpeak(e.target.value)}
                            min="0.0"
                            max="6.5"
                            step="0.1"
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Slope of Peak Exercise ST Segment (slope)"
                            value={slope}
                            onChange={(e) => setSlope(e.target.value)}
                            min="0"
                            max="2"
                            required
                        />
                        <input
                            type="number"
                            placeholder="Number of Major Vessels (ca)"
                            value={ca}
                            onChange={(e) => setCa(e.target.value)}
                            min="0"
                            max="3"
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Thalassemia (thal)"
                            value={thal}
                            onChange={(e) => setThal(e.target.value)}
                            min="0"
                            max="3"
                            required
                        />
                        <button id='pred-button' type="submit" disabled={isLoading}>
                            {isLoading ? 'Predicting...' : 'Predict'}
                        </button>
                    </div>
                </form>

                <button onClick={() => setShowInfo(!showInfo)} className="info-toggle">
                        {showInfo ? "Hide Info" : "Show Info"}
                    </button>

                    {showInfo && (
                        <div className="input-info-box">
                            <h4>Field Descriptions</h4>
                            <ul>
                                <li><strong>Age</strong>: Age of the person</li>
                                <li><strong>Sex</strong>: 1 = Male, 0 = Female</li>
                                <li><strong>cp</strong>: Chest pain type <br></br> (0-Typical Angina, 1-Atypical Angina, 2- Non-anginal pain, 3-Asymptomatic)</li>
                                <li><strong>trestbps</strong>: Resting blood pressure (mm/HG)</li>
                                <li><strong>chol</strong>: Serum cholesterol (mg/dl)</li>
                                <li><strong>thalach</strong>: Max heart rate achieved</li>
                                <li><strong>exang</strong>: Exercise-induced angina <br></br>(1 = Yes, 0 = No)</li>
                                <li><strong>oldpeak</strong>: ST depression induced by exercise</li>
                                <li><strong>slope</strong>: Slope of the ST segment<br></br> (0- Up sloping; 1- Flat; 2- Down sloping)</li>
                                <li><strong>ca</strong>: Number of major vessels (0–3)</li>
                                <li><strong>thal</strong>: Thalassemia blood disorder <br></br>(0-Null, 1 = Normal blood flow,<br></br> 2 = Fixed defect(no blood flow in some part of the heart),<br></br> 3 = Reversible defect(a blood flow is observed but it is not normal))</li>
                            </ul>
                        </div>
                    )}

            </section>
            ) : (
                <div id="results">
                    <h2 style={{ color: prediction === 1 ? '#d32f2f' : '#388e3c' }}>
                        {prediction === 1 ? "Potential risk of heart stroke" : "Low risk of heart stroke"}
                    </h2>
                    
                    <div className="probability-meter">
                        <div className="meter-label">Risk Probability</div>
                        <div className="meter-bar">
                            <div 
                                className="meter-fill"
                                style={{ 
                                    width: `${probabilities[0][1] * 100}%`,
                                    backgroundColor: prediction === 1 ? '#d32f2f' : '#388e3c'
                                }}
                            ></div>
                        </div>
                        <div className="meter-value">
                            {(probabilities[0][1] * 100).toFixed(1)}%
                        </div>
                    </div>
                    
                    <div className="explanation-box">
                        <h3>Explanation</h3>
                        <p>{explanation}</p>
                    </div>
                    
                    
                    <div className="shap-plots">
                        <div className="plot-container">
                            <h3>Feature Importance using SHAP</h3>
                            <div className="plot-wrapper">
                                {shapBarPlot && (
                                    <img 
                                        src={`http://127.0.0.1:5000${shapBarPlot}`} 
                                        alt="SHAP Bar Plot" 
                                        className="shap-image shapBarPlot"
                                        onError={(e) => {
                                            e.target.onerror = null;
                                            console.error('Error loading SHAP bar plot:', e);
                                            e.target.style.display = 'none';
                                            e.target.src = 'placeholder.jpg';
                                        }}
                                    />
                                )}
                            </div>
                            <p className="explanation-note">
                                {/* The above SHAP chart shows the overall importance of each feature across all predictions.
                                Higher bars indicate features that generally have larger impacts on the model's decisions. */}
                                The above SHAP chart shows the contribution of each feature toward the final prediction for a specific instance. 
                                Features increasing the prediction are highlighted in red, while those decreasing it are shown in blue.

                            </p>
                        </div>
                        
                        <div className="plot-container">
                            <h3>SHAP Prediction Breakdown</h3>
                            <div className="plot-wrapper">
                                {shapForcePlot && (
                                    <img 
                                        src={`http://127.0.0.1:5000${shapForcePlot}`} 
                                        alt="SHAP Force Plot" 
                                        className="shap-image force-plot"
                                        onError={(e) => {
                                            e.target.onerror = null;
                                            e.target.src = 'placeholder.jpg';
                                            console.error('Error loading SHAP bar plot:', e);
                                            e.target.style.display = 'none';
                                        }}
                                    />
                                )}
                            </div>
                            <p className="explanation-note">
                                This visual shows how each feature value contributed to pushing the prediction
                                from the base value (average prediction) to the final output.
                            </p>
                        </div>
                    </div>

                    <div className="explanations-container">
                        <div className="plot-container">
                            <h3>Local Explanation (LIME)</h3>
                            <div className="plot-wrapper">
                                {limePlot && (
                                    <img 
                                        src={`data:image/png;base64,${limePlot}`} 
                                        alt="LIME Explanation" 
                                        className="lime-image"
                                    />
                                )}
                            </div>
                            <p className="explanation-note">
                                LIME shows how each feature contributed to this specific prediction.
                                Features in green pushed the prediction toward "No Heart Disease",
                                while features in red pushed toward "Heart Disease".
                            </p>
                        </div>
                    </div>
                    
                    <div className="counterfactual-explanation">
                        <div className="plot-container">
                            {/* Render counterfactual explanations */}
                            {renderCounterfactuals()}
                        </div>
                    </div>

                    
                    <button 
                        id='back-button' 
                        onClick={handleBackToHome}
                        style={{
                            marginTop: '20px',
                            padding: '10px 20px',
                            backgroundColor: '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: 'pointer',
                            width: 'auto', 
                            minWidth: '200px', 
                            whiteSpace: 'nowrap'
                        }}
                    >
                        Back to Prediction Page
                    </button>
                </div>
            )}
            
            {error && <div className="error-message">{error}</div>}
            </div>
        </div>
    );
    
};

export default Form;