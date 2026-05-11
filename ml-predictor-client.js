// ml-predictor-client.js
// Sample Express router for integrating with FastAPI ML Predictor

const express = require('express');
const axios = require('axios');

const router = express.Router();

// Configuration
const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';
const ML_API_TIMEOUT = parseInt(process.env.ML_API_TIMEOUT || '30000');

// Axios instance for ML API
const mlClient = axios.create({
  baseURL: ML_API_URL,
  timeout: ML_API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
});

/**
 * Get runway prediction from ML service
 * @param {Object} predictionData - { userId, currentBalance, transactions }
 * @returns {Promise<Object>} - Prediction result
 */
async function getPredictionFromML(predictionData) {
  try {
    const response = await mlClient.post('/predict', predictionData);
    return response.data;
  } catch (error) {
    console.error('ML API Error:', error.message);
    throw new Error(`Failed to get prediction: ${error.message}`);
  }
}

/**
 * POST /api/runway
 * Receive callback from ML service with prediction results
 * This endpoint is called by the FastAPI backend asynchronously
 */
router.post('/api/runway', async (req, res) => {
  try {
    const { prediction, userId, timestamp } = req.body;
    
    console.log(`Received prediction callback for user: ${userId}`);
    console.log('Prediction:', prediction);
    
    // TODO: Save prediction to database
    // await db.savePrediction({ userId, prediction, timestamp: new Date() });
    
    // TODO: Send notification to user (websocket, email, etc.)
    // await notifyUser(userId, prediction);
    
    res.json({
      success: true,
      message: 'Prediction received and processed',
      data: { userId, prediction }
    });
  } catch (error) {
    console.error('Error processing prediction:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * POST /api/predict
 * Get runway prediction for user
 * Request body: { userId, currentBalance, transactions }
 */
router.post('/api/predict', async (req, res) => {
  try {
    const { userId, currentBalance, transactions } = req.body;
    
    // Validate input
    if (!currentBalance || currentBalance < 0) {
      return res.status(422).json({
        success: false,
        error: 'currentBalance must be a positive number'
      });
    }
    
    if (!transactions || transactions.length === 0) {
      return res.status(422).json({
        success: false,
        error: 'transactions array is required and must not be empty'
      });
    }
    
    console.log(`Processing prediction request for user: ${userId}`);
    
    // Call ML service
    const predictionResult = await getPredictionFromML({
      userId,
      currentBalance,
      transactions
    });
    
    if (!predictionResult.success) {
      return res.status(400).json({
        success: false,
        error: predictionResult.error || 'Prediction failed'
      });
    }
    
    // TODO: Save to database
    // await db.savePredictionResult({ userId, result: predictionResult.data });
    
    res.json({
      success: true,
      prediction: predictionResult.data,
      userId
    });
  } catch (error) {
    console.error('Error in /api/predict:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * GET /api/ml-health
 * Check ML service health
 */
router.get('/api/ml-health', async (req, res) => {
  try {
    const response = await mlClient.get('/health');
    res.json({
      success: true,
      mlService: response.data
    });
  } catch (error) {
    res.status(503).json({
      success: false,
      error: 'ML service unavailable',
      details: error.message
    });
  }
});

/** 
 * GET /api/runway/:userId/latest
 * Get latest prediction for a user
 * TODO: Implement database query
 */
router.get('/api/runway/:userId/latest', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // TODO: Query database for latest prediction
    // const prediction = await db.getLatestPrediction(userId);
    
    res.json({
      success: true,
      userId,
      prediction: {} // Replace with actual data from DB
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router;
