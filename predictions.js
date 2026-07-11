const express = require('express');
const jwt = require('jsonwebtoken');
const axios = require('axios');
const Prediction = require('../models/Prediction');

const router = express.Router();

// Middleware to verify token
const verifyToken = (req, res, next) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'Access denied' });
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secret');
    req.user = decoded;
    next();
  } catch (error) {
    res.status(400).json({ error: 'Invalid token' });
  }
};

const ML_API_URL = process.env.ML_API_URL || 'http://localhost:5001';

// Predict
router.post('/predict', verifyToken, async (req, res) => {
  try {
    const input = req.body;
    const response = await axios.post(`${ML_API_URL}/predict`, input);
    const results = response.data;
    const prediction = new Prediction({
      user: req.user.id,
      input,
      results,
      risk: results.risk
    });
    await prediction.save();
    res.json(results);
  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json({ error: error.response.data?.error || error.message });
    }
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json({ error: `ML API unavailable at ${ML_API_URL}. Start the ML API and retry.` });
    }
    res.status(500).json({ error: error.message });
  }
});

// Get history
router.get('/history', verifyToken, async (req, res) => {
  try {
    const predictions = await Prediction.find({ user: req.user.id }).sort({ createdAt: -1 });
    res.json(predictions);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete a specific prediction
router.delete('/history/:id', verifyToken, async (req, res) => {
  try {
    const prediction = await Prediction.findById(req.params.id);
    if (!prediction) {
      return res.status(404).json({ error: 'Prediction not found' });
    }
    if (prediction.user.toString() !== req.user.id) {
      return res.status(403).json({ error: 'Not authorized to delete this prediction' });
    }
    await Prediction.findByIdAndDelete(req.params.id);
    res.json({ message: 'Prediction deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;