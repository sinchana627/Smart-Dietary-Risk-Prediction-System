const mongoose = require('mongoose');

const predictionSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  input: { type: Object, required: true },
  results: { type: Object, required: true },
  risk: { type: String, required: true },
}, { timestamps: true });

module.exports = mongoose.model('Prediction', predictionSchema);