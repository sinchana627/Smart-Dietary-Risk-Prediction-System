import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import AlgorithmInfo from './AlgorithmInfo';

const dropdownOptions = {
  gender: ['Male', 'Female', 'Other'],
  ageGroup: ['0-18', '19-25', '26-40', '41-60', '60+'],
  foodPreference: ['Vegetarian', 'Non-Vegetarian', 'Vegan'],
  spicinessLevel: ['Mild', 'Medium', 'Spicy'],
  allergies: ['None', 'Nuts', 'Dairy', 'Gluten', 'Seafood'],
  cuisinePreference: ['Indian', 'Chinese', 'Italian', 'Mexican', 'Continental'],
  mealType: ['Breakfast', 'Lunch', 'Dinner', 'Snacks']
};

function Dashboard() {
  const [formData, setFormData] = useState({
    gender: '',
    ageGroup: '',
    foodPreference: '',
    spicinessLevel: '',
    allergies: '',
    cuisinePreference: '',
    mealType: ''
  });
  const [results, setResults] = useState(null);
  const [stats, setStats] = useState(null);
  const [accuracy, setAccuracy] = useState(null);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [history, setHistory] = useState([]);
  const [datasetOptions, setDatasetOptions] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('food_data.csv');
  const [testSize, setTestSize] = useState(0.2);
  const [retrainLoading, setRetrainLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [showTrainConfig, setShowTrainConfig] = useState(false);

  useEffect(() => {
    fetchConfig();
    fetchStats();
    fetchAccuracy();
    fetchHistory();
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await axios.get('http://localhost:5001/train-config');
      setDatasetOptions(res.data.available_datasets || []);
      setSelectedDataset(res.data.current_dataset || 'food_data.csv');
      setTestSize(res.data.current_test_size || 0.2);
    } catch (error) {
      console.error('Error fetching train config:', error);
    }
  };

  const handleConfigChange = (e) => {
    const { name, value } = e.target;
    if (name === 'dataset') {
      setSelectedDataset(value);
    } else if (name === 'testSize') {
      setTestSize(parseFloat(value));
    }
  };

  const handleRetrain = async (e) => {
    e.preventDefault();
    setRetrainLoading(true);
    try {
      const res = await axios.post('http://localhost:5001/train-config', {
        dataset: selectedDataset,
        test_size: testSize
      });
      setDatasetOptions(res.data.available_datasets || datasetOptions);
      setSelectedDataset(res.data.current_dataset || selectedDataset);
      setTestSize(res.data.current_test_size || testSize);
      fetchStats();
      fetchAccuracy();
      alert('Training data updated and models retrained successfully.');
    } catch (error) {
      const message = error.response?.data?.error || error.message;
      alert('Retrain failed: ' + message);
    } finally {
      setRetrainLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get('http://localhost:5001/statistics');
      setStats(res.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchAccuracy = async () => {
    try {
      const res = await axios.get('http://localhost:5001/model-accuracy');
      setAccuracy(res.data.accuracies);
      setModelMetrics(res.data.metrics);
    } catch (error) {
      console.error('Error fetching accuracy:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const res = await axios.get('http://localhost:5000/api/predictions/history', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setHistory(res.data);
      }
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const handleDeleteHistory = async (predictionId) => {
    if (window.confirm('Are you sure you want to delete this prediction?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`http://localhost:5000/api/predictions/history/${predictionId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchHistory();
        alert('Prediction deleted successfully');
      } catch (error) {
        const message = error.response?.data?.error || error.message;
        alert('Delete failed: ' + message);
      }
    }
  };

  const validate = () => {
    const newErrors = {};
    Object.keys(formData).forEach((key) => {
      if (!formData[key]) {
        newErrors[key] = 'Please select an option';
      }
    });
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.post('http://localhost:5000/api/predictions/predict', formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResults(res.data);
      fetchHistory();
      alert('Prediction successful!');
    } catch (error) {
      const message = error.response?.data?.error || error.message;
      alert('Prediction failed: ' + message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => {
        const updated = { ...prev };
        delete updated[name];
        return updated;
      });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'Low': return '#4caf50';
      case 'Medium': return '#ff9800';
      case 'High': return '#f44336';
      default: return '#666';
    }
  };

  const accuracyData = accuracy ? Object.entries(accuracy).map(([model, acc]) => ({
    name: model,
    accuracy: (acc * 100).toFixed(2)
  })) : [];

  const pieData = stats ? [
    { name: 'At Risk', value: stats.at_risk },
    { name: 'Safe', value: stats.safe }
  ] : [];

  const metricsData = modelMetrics ? Object.entries(modelMetrics).map(([model, metric]) => ({
    model,
    accuracy: (metric.accuracy * 100).toFixed(2),
    precision: (metric.precision * 100).toFixed(2),
    recall: (metric.recall * 100).toFixed(2),
    f1: (metric.f1_score * 100).toFixed(2)
  })) : [];

  const metricsChartData = modelMetrics ? Object.entries(modelMetrics).map(([model, metric]) => ({
    model,
    accuracy: Number((metric.accuracy * 100).toFixed(2)),
    precision: Number((metric.precision * 100).toFixed(2)),
    recall: Number((metric.recall * 100).toFixed(2)),
    f1: Number((metric.f1_score * 100).toFixed(2))
  })) : [];

  const bestAlgorithm = modelMetrics ? Object.entries(modelMetrics).reduce((best, [model, metric]) => {
    if (!best) return { model, metric };
    if (metric.accuracy > best.metric.accuracy) return { model, metric };
    if (metric.accuracy === best.metric.accuracy && metric.f1_score > best.metric.f1_score) return { model, metric };
    return best;
  }, null) : null;

  const renderSampleTable = (rows) => {
    if (!rows || rows.length === 0) return null;
    const headers = Object.keys(rows[0]);
    return (
      <table className="sample-table">
        <thead>
          <tr>{headers.map((key) => <th key={key}>{key}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx}>
              {headers.map((key) => <td key={key}>{row[key]}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  const renderHistoryDetails = (entry) => {
    const inputRows = Object.entries(entry.input || {}).map(([key, value]) => (
      <tr key={key}>
        <td>{key}</td>
        <td>{value}</td>
      </tr>
    ));

    const predictionRows = Object.entries(entry.results?.predictions || {}).map(([model, value]) => (
      <tr key={model}>
        <td>{model}</td>
        <td>{value === 1 ? 'Risky' : 'Safe'}</td>
      </tr>
    ));

    const probabilityRows = Object.entries(entry.results?.probabilities || {}).map(([model, value]) => (
      <tr key={model}>
        <td>{model}</td>
        <td>{typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : value}</td>
      </tr>
    ));

    return (
      <div className="history-detail">
        <div className="history-section-block">
          <h4>Input Values</h4>
          <table className="history-table">
            <tbody>{inputRows}</tbody>
          </table>
        </div>
        <div className="history-section-block">
          <h4>Model Predictions</h4>
          <table className="history-table">
            <tbody>{predictionRows}</tbody>
          </table>
        </div>
        {probabilityRows.length > 0 && (
          <div className="history-section-block">
            <h4>Prediction Probabilities</h4>
            <table className="history-table">
              <tbody>{probabilityRows}</tbody>
            </table>
          </div>
        )}
      </div>
    );
  };

  const COLORS = ['#ff7c7c', '#8bd34f'];

  const renderSelect = (name, label) => (
    <div className="form-field" key={name}>
      <label htmlFor={name}>{label}</label>
      <select
        id={name}
        name={name}
        value={formData[name]}
        onChange={handleChange}
        required
      >
        <option value="" disabled>Select an option</option>
        {dropdownOptions[name].map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
      {errors[name] && <span className="error-text">{errors[name]}</span>}
    </div>
  );

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>Dietary Risk Prediction Dashboard</h2>
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </div>

      <div className="dashboard-content">
        {/* Prediction Form */}
        <section className="prediction-section">
          <h3>Enter Dietary Preferences</h3>
          <form onSubmit={handleSubmit} className="prediction-form" noValidate>
            <div className="form-row">
              {renderSelect('gender', 'Gender')}
              {renderSelect('ageGroup', 'Age Group')}
              {renderSelect('foodPreference', 'Food Preference')}
            </div>
            <div className="form-row">
              {renderSelect('spicinessLevel', 'Spiciness Level')}
              {renderSelect('allergies', 'Allergies')}
              {renderSelect('cuisinePreference', 'Cuisine Preference')}
            </div>
            <div className="form-row">
              {renderSelect('mealType', 'Meal Type')}
            </div>
            <button type="submit" disabled={loading}>{loading ? 'Analyzing...' : 'Get Prediction'}</button>
          </form>
        </section>

        {/* Prediction Results */}
        {results && (
          <section className="results-section">
            <h3>Prediction Results</h3>
            <div className="results-card">
              <div className="risk-indicator" style={{ borderColor: getRiskColor(results.risk) }}>
                <h4>Risk Level</h4>
                <p style={{ color: getRiskColor(results.risk), fontSize: '24px', fontWeight: 'bold' }}>
                  {results.risk}
                </p>
                <p className="risk-score">Risk Score: {(results.risk_score * 100).toFixed(2)}%</p>
              </div>
              
              <div className="recommendations">
                <h4>Recommendation</h4>
                <p>{results.recommendation}</p>
              </div>

              <div className="model-predictions">
                <h4>Model Predictions</h4>
                <table>
                  <tbody>
                    {Object.entries(results.predictions).map(([model, pred]) => (
                      <tr key={model}>
                        <td>{model}</td>
                        <td>{pred === 1 ? '🔴 Risky' : '🟢 Safe'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="probabilities">
                <h4>Risk Probabilities</h4>
                <table>
                  <tbody>
                    {Object.entries(results.probabilities).map(([model, prob]) => (
                      <tr key={model}>
                        <td>{model}</td>
                        <td>{(prob * 100).toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        )}

        {/* Algorithm Explanations */}
        <AlgorithmInfo />

        {/* Statistics */}
        {stats && (
          <section className="stats-section">
            <h3>Dataset Statistics</h3>
            
            {/* Train/Test Configuration Button */}
            <button 
              className="config-toggle-btn" 
              onClick={() => setShowTrainConfig(!showTrainConfig)}
              style={{ marginBottom: '20px', padding: '10px 20px', backgroundColor: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              {showTrainConfig ? '▼ Hide Train/Test Configuration' : '▶ Configure Training & Testing Data'}
            </button>
            
            {/* Train/Test Configuration Form */}
            {showTrainConfig && (
              <form onSubmit={handleRetrain} className="training-config-form" style={{ marginBottom: '30px', padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '4px', border: '1px solid #ddd' }} noValidate>
                <div className="form-row">
                  <div className="form-field" style={{ marginRight: '20px' }}>
                    <label htmlFor="dataset">Dataset</label>
                    <select id="dataset" name="dataset" value={selectedDataset} onChange={handleConfigChange}>
                      {datasetOptions.map((dataset) => (
                        <option key={dataset} value={dataset}>{dataset}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-field">
                    <label htmlFor="testSize">Test Size (%)</label>
                    <select id="testSize" name="testSize" value={testSize} onChange={handleConfigChange}>
                      {[0.1, 0.2, 0.25, 0.3, 0.4].map((size) => (
                        <option key={size} value={size}>{(size * 100).toFixed(0)}%</option>
                      ))}
                    </select>
                  </div>
                </div>
                <button type="submit" disabled={retrainLoading} style={{ marginTop: '15px' }}>{retrainLoading ? 'Updating...' : 'Update Train/Test Split'}</button>
              </form>
            )}

            <div className="stats-cards">
              <div className="stat-card">
                <h4>Total Samples</h4>
                <p className="stat-value">{stats.total_samples}</p>
              </div>
              <div className="stat-card">
                <h4>Features</h4>
                <p className="stat-value">{stats.features}</p>
              </div>
              <div className="stat-card">
                <h4>At Risk Cases</h4>
                <p className="stat-value">{stats.at_risk}</p>
              </div>
              <div className="stat-card">
                <h4>Risk Rate</h4>
                <p className="stat-value">{stats.risk_percentage.toFixed(2)}%</p>
              </div>
              <div className="stat-card">
                <h4>Train Samples</h4>
                <p className="stat-value">{stats.train_count}</p>
              </div>
              <div className="stat-card">
                <h4>Test Samples</h4>
                <p className="stat-value">{stats.test_count}</p>
              </div>
            </div>

            {/* Charts */}
            <div className="charts-container">
              {accuracyData.length > 0 && (
                <div className="chart">
                  <h4>Model Accuracy</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={accuracyData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="accuracy" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {pieData.length > 0 && (
                <div className="chart">
                  <h4>Dataset Distribution</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} fill="#8884d8" dataKey="value">
                        {COLORS.map((color, index) => (
                          <Cell key={`cell-${index}`} fill={color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {metricsData.length > 0 && (
              <div className="evaluation-section">
                <h4>Model Evaluation Metrics</h4>

                <div className="chart">
                  <h5>Evaluation Metrics Comparison</h5>
                  <ResponsiveContainer width="100%" height={360}>
                    <BarChart data={metricsChartData} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="model" />
                      <YAxis />
                      <Tooltip formatter={(value) => `${value}%`} />
                      <Legend />
                      <Bar dataKey="accuracy" fill="#8884d8" />
                      <Bar dataKey="precision" fill="#82ca9d" />
                      <Bar dataKey="recall" fill="#ffc658" />
                      <Bar dataKey="f1" fill="#ff7f50" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <table className="metrics-table">
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Accuracy</th>
                      <th>Precision</th>
                      <th>Recall</th>
                      <th>F1 Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metricsData.map((row) => (
                      <tr key={row.model}>
                        <td>{row.model}</td>
                        <td>{row.accuracy}%</td>
                        <td>{row.precision}%</td>
                        <td>{row.recall}%</td>
                        <td>{row.f1}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {bestAlgorithm && (
                  <div className="best-algo-card">
                    <h4>Best Algorithm</h4>
                    <p>
                      <strong>{bestAlgorithm.model}</strong> is the top performer with <strong>{(bestAlgorithm.metric.accuracy * 100).toFixed(2)}%</strong> accuracy and <strong>{(bestAlgorithm.metric.f1_score * 100).toFixed(2)}%</strong> F1 score.
                    </p>
                  </div>
                )}
              </div>
            )}

          </section>
        )}

        {/* Prediction History */}
        <section className="history-section">
          <h3>Prediction History</h3>
          {history.length > 0 ? (
            <div className="history-list">
              {history.map((pred, i) => (
                <div key={i} className="history-item" style={{ borderLeftColor: getRiskColor(pred.risk) }}>
                  <div className="history-summary">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <p><strong>Risk:</strong> {pred.risk}</p>
                        <p><strong>Date:</strong> {new Date(pred.createdAt).toLocaleString()}</p>
                        <p><strong>Score:</strong> {(pred.results?.risk_score * 100).toFixed(2)}%</p>
                      </div>
                      <button
                        onClick={() => handleDeleteHistory(pred._id)}
                        style={{
                          padding: '8px 16px',
                          backgroundColor: '#f44336',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '14px'
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  {renderHistoryDetails(pred)}
                </div>
              ))}
            </div>
          ) : (
            <p>No predictions yet</p>
          )}
        </section>
      </div>
    </div>
  );
}

export default Dashboard;

