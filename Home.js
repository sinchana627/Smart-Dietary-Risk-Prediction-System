import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="home-container">
      <h1>🍽️ Smart Dietary Risk Prediction System</h1>
      <p>Predict dietary health risks based on your preferences, allergies, and meal choices using advanced machine learning algorithms</p>
      <div className="nav-links">
        <Link to="/login">Login</Link>
        <Link to="/signup">Signup</Link>
      </div>
    </div>
  );
}

export default Home;