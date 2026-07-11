import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/AlgorithmInfo.css';

function AlgorithmInfo() {
  const [algorithms, setAlgorithms] = useState({});
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('Naive Bayes');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAlgorithmInfo();
  }, []);

  const fetchAlgorithmInfo = async () => {
    try {
      setLoading(true);
      const res = await axios.get('http://localhost:5001/algorithm-info');
      console.log('Algorithm info fetched successfully:', res.data);
      setAlgorithms(res.data);
      // Set selected algorithm to first available if Naive Bayes doesn't exist
      if (res.data && !res.data['Naive Bayes'] && Object.keys(res.data).length > 0) {
        setSelectedAlgorithm(Object.keys(res.data)[0]);
      }
      setError(null);
    } catch (err) {
      console.error('Error fetching algorithm info:', err);
      console.error('Error details:', err.response?.data || err.message);
      setError('Failed to load algorithm information: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="algo-loading">Loading algorithm information...</div>;
  }

  if (error) {
    return <div className="algo-error">{error}</div>;
  }

  if (!algorithms || Object.keys(algorithms).length === 0) {
    return <div className="algo-error">No algorithms available. Please check the API connection.</div>;
  }

  const currentAlgo = algorithms[selectedAlgorithm];

  return (
    <div className="algorithm-info-container">
      <h2>🤖 ML Algorithm Explanations</h2>
      
      {/* Algorithm Selection Buttons */}
      <div className="algorithm-buttons">
        {Object.keys(algorithms).map((algoName) => (
          <button
            key={algoName}
            className={`algo-btn ${selectedAlgorithm === algoName ? 'active' : ''}`}
            onClick={() => setSelectedAlgorithm(algoName)}
          >
            {algoName}
          </button>
        ))}
      </div>

      {/* Algorithm Details */}
      {currentAlgo ? (
        <div className="algorithm-details">
          <div className="algo-header">
            <h3>{currentAlgo.name}</h3>
            <div className="algo-accuracy">
              <span className="accuracy-label">Accuracy:</span>
              <span className="accuracy-value">{currentAlgo.accuracy}</span>
            </div>
          </div>

          {/* Description */}
          <div className="algo-section">
            <h4>📖 Description</h4>
            <p>{currentAlgo.description}</p>
          </div>

          {/* How It Works */}
          <div className="algo-section">
            <h4>⚙️ How It Works</h4>
            <ol className="algo-list">
              {currentAlgo.how_it_works && currentAlgo.how_it_works.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </div>

          {/* Prediction Process */}
          <div className="algo-section">
            <h4>🔮 How Output is Predicted</h4>
            <ol className="algo-list">
              {currentAlgo.prediction_process && currentAlgo.prediction_process.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </div>

          {/* Advantages */}
          <div className="algo-section">
            <h4>✅ Advantages</h4>
            <ul className="algo-list">
              {currentAlgo.advantages && currentAlgo.advantages.map((advantage, index) => (
                <li key={index}>{advantage}</li>
              ))}
            </ul>
          </div>

          {/* Output */}
          <div className="algo-section">
            <h4>📊 Output</h4>
            <p className="output-box">{currentAlgo.output}</p>
          </div>
        </div>
      ) : (
        <div className="algo-error">Selected algorithm not found. Please select a different algorithm.</div>
      )}
    </div>
  );
}

export default AlgorithmInfo;
