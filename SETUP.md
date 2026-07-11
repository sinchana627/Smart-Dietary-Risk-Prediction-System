# HealthML - Smart Health Risk Prediction System

A full-stack application for predicting dietary risk using food preference data and machine learning.

## Quick Start

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- MongoDB (running locally or Atlas)
- npm or yarn

### Installation & Setup

#### 1. Backend Setup (Node.js + Express)
```bash
cd server
npm install
```

Create `.env` file in `server/` with MongoDB URI and JWT secret:
```
MONGO_URI=mongodb://localhost:27017/healthml
JWT_SECRET=your_secret_key
```

Run backend:
```bash
npm run dev    # Development mode with nodemon
npm start      # Production mode
```

Backend runs on **http://localhost:5000**

#### 2. ML API Setup (Python + Flask)
```bash
cd ml-api
pip install -r requirements.txt
```

Run ML API:
```bash
python app.py
```

ML API runs on **http://localhost:5001**

#### 3. Frontend Setup (React)
```bash
cd client
npm install
```

Run frontend:
```bash
npm start
```

Frontend runs on **http://localhost:3000**

### Dataset

The application uses a synthetic food preference dataset located in `data/food_data.csv`. If the file is missing or incomplete, the ML API generates it automatically when it starts.

### Usage

1. **Sign Up**: Create account on http://localhost:3000/signup
2. **Login**: Login with credentials
3. **Dashboard**: Enter dietary information and get predictions
4. **View Results**: See risk assessment and model predictions
5. **Check History**: View all previous predictions

## API Endpoints

### Authentication (Backend)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Predictions (Backend)
- `POST /api/predictions/predict` - Get prediction (requires token)
- `GET /api/predictions/history` - Get prediction history (requires token)

### ML Models (ML API)
- `POST /predict` - Predict dietary risk
- `GET /statistics` - Dataset statistics
- `GET /model-accuracy` - Model performance metrics
- `GET /eda` - Exploratory data analysis
- `GET /pca` - PCA visualization data
- `GET /cluster` - Clustering analysis

## Technologies Used

### Backend
- Express.js - REST API framework
- Mongoose - MongoDB ODM
- JWT - Authentication
- Bcrypt - Password hashing
- CORS - Cross-origin requests

### ML API
- Flask - Python web framework
- Scikit-learn - Machine learning algorithms
- Pandas - Data processing
- NumPy - Numerical computing
- Flask-CORS - Cross-origin requests

### Frontend
- React - UI library
- React Router - Navigation
- Axios - HTTP client
- Recharts - Data visualization
- CSS3 - Styling

## Machine Learning Models

1. **K-Nearest Neighbors (KNN)** - Classification
2. **Decision Tree** - Classification
3. **Logistic Regression** - Classification & Probability
4. **Random Forest** - Classification
5. **Naive Bayes** - Classification
6. **K-Means** - Clustering
7. **PCA** - Dimensionality reduction

## Project Structure

```
HealthML/
├── client/              # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Home.js
│   │   │   ├── Login.js
│   │   │   ├── Signup.js
│   │   │   └── Dashboard.js
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   └── package.json
│
├── server/              # Node.js backend
│   ├── models/
│   │   ├── User.js
│   │   └── Prediction.js
│   ├── routes/
│   │   ├── auth.js
│   │   └── predictions.js
│   ├── .env
│   ├── server.js
│   └── package.json
│
├── ml-api/              # Flask ML API
│   ├── app.py
│   └── requirements.txt
│
└── data/                # Dataset folder
    └── food_data.csv
```

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongod`
- Check MONGO_URI in `.env`

### CORS Errors
- Make sure all 3 services are running
- Check API URLs in frontend (Dashboard.js)

### Module Not Found
- Run `npm install` in client/ and server/
- Run `pip install -r requirements.txt` in ml-api/

### Port Already in Use
- Backend: Change PORT in .env
- Frontend: `PORT=3001 npm start`
- ML API: Modify port in app.py

## Features

✅ User authentication & authorization
✅ Multiple ML models for prediction
✅ Risk assessment with probabilities
✅ Prediction history tracking
✅ Dataset analysis & visualization
✅ Model performance metrics
✅ Responsive design
✅ Real-time predictions

## Future Enhancements

- [ ] Add more health datasets
- [ ] Deep learning models
- [ ] Advanced data visualization
- [ ] Mobile app
- [ ] Email notifications
- [ ] Export reports as PDF
- [ ] Dockerization
- [ ] Deployment to AWS/Azure/GCP

## License

MIT

## Support

For issues or questions, please create an issue in the repository.
