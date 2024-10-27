import React, { useState } from 'react';
import axios from 'axios';
import './app.css'

const Form = () => {
    // Define state for each feature
    const [age, setAge] = useState('');
    const [sex, setSex] = useState('');
    const [cp, setCp] = useState('');
    const [trestbps, setTrestbps] = useState('');
    const [chol, setChol] = useState('');
    const [fbs, setFbs] = useState('');
    const [restecg, setRestecg] = useState('');
    const [thalach, setThalach] = useState('');
    const [exang, setExang] = useState('');
    const [oldpeak, setOldpeak] = useState('');
    const [slope, setSlope] = useState('');
    const [ca, setCa] = useState('');
    const [thal, setThal] = useState('');
    const [prediction, setPrediction] = useState(null);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        const features = [
            Number(age),
            Number(sex),
            Number(cp),
            Number(trestbps),
            Number(chol),
            Number(fbs),
            Number(restecg),
            Number(thalach),
            Number(exang),
            Number(oldpeak),
            Number(slope),
            Number(ca),
            Number(thal),
        ];

        try {
            const response = await axios.post('http://127.0.0.1:5000/predict', { features });
            setPrediction(response.data.prediction); // Adjust according to your API response
        } catch (err) {
            setError('Error fetching prediction: ' + err.message);
        }
    };

    return (
        <div id='form-comp'>
            <h1>Heart Stroke Prediction</h1>
            <section id="form-section">
                <form onSubmit={handleSubmit} id='form'>
                    <div id="fields">
                        <input
                            type="number"
                            placeholder="Age"
                            value={age}
                            onChange={(e) => setAge(e.target.value)}
                            required
                        />
                        <input
                            type="number"
                            placeholder="Sex (0 or 1)"
                            value={sex}
                            onChange={(e) => setSex(e.target.value)}
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Chest Pain Type (cp)"
                            value={cp}
                            onChange={(e) => setCp(e.target.value)}
                            required
                        />
                        <input
                            type="number"
                            placeholder="Resting Blood Pressure (trestbps)"
                            value={trestbps}
                            onChange={(e) => setTrestbps(e.target.value)}
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Cholesterol (chol)"
                            value={chol}
                            onChange={(e) => setChol(e.target.value)}
                            required
                        />
                        <input
                            type="number"
                            placeholder="Fasting Blood Sugar (fbs)"
                            value={fbs}
                            onChange={(e) => setFbs(e.target.value)}
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Resting Electrocardiographic Results (restecg)"
                            value={restecg}
                            onChange={(e) => setRestecg(e.target.value)}
                            required
                        />
                        <input
                            type="number"
                            placeholder="Maximum Heart Rate Achieved (thalach)"
                            value={thalach}
                            onChange={(e) => setThalach(e.target.value)}
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Exercise Induced Angina (exang)"
                            value={exang}
                            onChange={(e) => setExang(e.target.value)}
                            required
                        />
                        <input
                            type="number"
                            placeholder="Old Peak"
                            value={oldpeak}
                            onChange={(e) => setOldpeak(e.target.value)}
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Slope of Peak Exercise ST Segment (slope)"
                            value={slope}
                            onChange={(e) => setSlope(e.target.value)}
                            required
                        />
                        <input
                            type="number"
                            placeholder="Number of Major Vessels (ca)"
                            value={ca}
                            onChange={(e) => setCa(e.target.value)}
                            required
                        />
                    </div>
                    <div id="fields">
                    <input
                            type="number"
                            placeholder="Thalassemia (thal)"
                            value={thal}
                            onChange={(e) => setThal(e.target.value)}
                            required
                        />
                        <button id='pred-button' type="submit">Predict</button>
                    </div>
                </form>
            </section>

            {prediction !== null && <h2 id='results'>{prediction==1? "Potential risk of heart stroke": "You're safe"}</h2>}
            {error && <p>{error}</p>}
        </div>
    );
};

export default Form;
