from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Load food dataset
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
data_path = os.path.join(base_dir, 'data', 'food_data.csv')

feature_cols = ['gender', 'ageGroup', 'foodPreference', 'spicinessLevel',
                'allergies', 'cuisinePreference', 'mealType']
target_col = 'target'


def generate_synthetic_food_data(num_rows=1000):
    np.random.seed(42)
    random = np.random.RandomState(42)

    categories = {
        'gender': ['Male', 'Female', 'Other'],
        'ageGroup': ['0-18', '19-25', '26-40', '41-60', '60+'],
        'foodPreference': ['Vegetarian', 'Non-Vegetarian', 'Vegan'],
        'spicinessLevel': ['Mild', 'Medium', 'Spicy'],
        'allergies': ['None', 'Nuts', 'Dairy', 'Gluten', 'Seafood'],
        'cuisinePreference': ['Indian', 'Chinese', 'Italian', 'Mexican', 'Continental'],
        'mealType': ['Breakfast', 'Lunch', 'Dinner', 'Snacks']
    }

    rows = []
    for _ in range(num_rows):
        gender = random.choice(categories['gender'])
        age_group = random.choice(categories['ageGroup'])
        food_pref = random.choice(categories['foodPreference'])
        spice = random.choice(categories['spicinessLevel'])
        allergy = random.choice(categories['allergies'])
        cuisine = random.choice(categories['cuisinePreference'])
        meal = random.choice(categories['mealType'])

        risk_score = random.random() * 0.3
        if allergy != 'None':
            risk_score += 0.15
            if allergy == 'Nuts' and cuisine in ['Chinese', 'Continental']:
                risk_score += 0.25
            if allergy == 'Dairy' and cuisine in ['Italian', 'Continental', 'Mexican']:
                risk_score += 0.25
            if allergy == 'Gluten' and cuisine in ['Italian', 'Continental', 'Mexican']:
                risk_score += 0.25
            if allergy == 'Seafood' and cuisine in ['Chinese', 'Continental', 'Mexican']:
                risk_score += 0.25

        if age_group == '60+' and spice == 'Spicy':
            risk_score += 0.15
        if age_group == '0-18' and spice == 'Spicy':
            risk_score += 0.10
        if food_pref == 'Vegan' and cuisine in ['Italian', 'Mexican', 'Continental']:
            risk_score += 0.10
        if meal == 'Dinner' and spice == 'Spicy':
            risk_score += 0.08

        risk_score = min(risk_score, 1.0)
        target = 1 if risk_score > 0.5 else 0

        rows.append({
            'gender': gender,
            'ageGroup': age_group,
            'foodPreference': food_pref,
            'spicinessLevel': spice,
            'allergies': allergy,
            'cuisinePreference': cuisine,
            'mealType': meal,
            'target': target
        })

    return pd.DataFrame(rows)


def load_dataset(path, min_rows=1000):
    if os.path.exists(path):
        df = pd.read_csv(path)
        required_columns = set(feature_cols + [target_col])
        if required_columns - set(df.columns):
            raise ValueError(f"Dataset at {path} must contain columns: {', '.join(sorted(required_columns))}")
        if len(df) < min_rows:
            if os.path.basename(path) == 'food_data.csv':
                df = generate_synthetic_food_data(min_rows)
                df.to_csv(path, index=False)
            else:
                raise ValueError(f"Dataset at {path} must contain at least {min_rows} rows.")
    else:
        if os.path.basename(path) == 'food_data.csv':
            df = generate_synthetic_food_data(min_rows)
            df.to_csv(path, index=False)
        else:
            raise FileNotFoundError(f"Dataset {path} not found.")

    df = df[feature_cols + [target_col]].fillna('None')
    return df

current_dataset = 'food_data.csv'
current_test_size = 0.2


def get_available_datasets():
    # Only allow food_data.csv
    return ['food_data.csv']


def train_models(X_train_scaled, y_train):
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train_scaled, y_train)

    cart_dt = DecisionTreeClassifier(criterion='gini', splitter='best', random_state=42, max_depth=5)
    cart_dt.fit(X_train_scaled, y_train)

    nb = GaussianNB()
    nb.fit(X_train_scaled, y_train)

    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X_train_scaled, y_train)

    return knn, cart_dt, nb, lr


def update_metrics():
    global model_metrics, accuracies
    model_metrics = {
        'KNN': calculate_metrics(knn, X_test_scaled, y_test),
        'CART Decision Tree': calculate_metrics(cart_dt, X_test_scaled, y_test),
        'Naive Bayes': calculate_metrics(nb, X_test_scaled, y_test),
        'Logistic Regression': calculate_metrics(lr, X_test_scaled, y_test)
    }
    accuracies = {model: metrics['accuracy'] for model, metrics in model_metrics.items()}


def prepare_data(dataset_name='food_data.csv', test_size=0.2):
    global df, encoders, encoded_df, X, y, X_train, X_test, y_train, y_test
    global train_df, test_df, scaler, X_train_scaled, X_test_scaled
    global knn, cart_dt, nb, lr, kmeans, pca, pca_data
    global current_dataset, current_test_size

    current_dataset = dataset_name
    current_test_size = test_size
    dataset_path = os.path.join(base_dir, 'data', current_dataset)
    df = load_dataset(dataset_path)

    encoders = {}
    encoded_df = df.copy()
    for col in feature_cols:
        le = LabelEncoder()
        encoded_df[col] = le.fit_transform(encoded_df[col].astype(str))
        encoders[col] = le

    X = encoded_df[feature_cols]
    y = encoded_df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=current_test_size, random_state=42)
    train_df = df.loc[X_train.index, feature_cols + [target_col]].reset_index(drop=True)
    test_df = df.loc[X_test.index, feature_cols + [target_col]].reset_index(drop=True)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    knn, cart_dt, nb, lr = train_models(X_train_scaled, y_train)

    kmeans = KMeans(n_clusters=2, random_state=42)
    kmeans.fit(X_train_scaled)

    pca = PCA(n_components=2)
    pca_data = pca.fit_transform(X_train_scaled)

    update_metrics()


# Evaluation metrics

def calculate_metrics(model, X, y):
    preds = model.predict(X)
    return {
        'accuracy': float(accuracy_score(y, preds)),
        'precision': float(precision_score(y, preds, zero_division=0)),
        'recall': float(recall_score(y, preds, zero_division=0)),
        'f1_score': float(f1_score(y, preds, zero_division=0))
    }

# Initialize data and models with default dataset and split
prepare_data(current_dataset, current_test_size)

@app.route('/train-config', methods=['GET', 'POST'])
def train_config():
    """Get or update the dataset and train/test split configuration."""
    try:
        if request.method == 'GET':
            return jsonify({
                'available_datasets': get_available_datasets(),
                'current_dataset': current_dataset,
                'current_test_size': current_test_size,
                'train_count': len(train_df),
                'test_count': len(test_df)
            })

        data = request.json or {}
        dataset = data.get('dataset', current_dataset)
        test_size = float(data.get('test_size', current_test_size))

        if not 0.0 < test_size < 1.0:
            return jsonify({'error': 'test_size must be a float between 0 and 1'}), 400

        if dataset not in get_available_datasets():
            return jsonify({'error': f'Dataset {dataset} not found'}), 404

        prepare_data(dataset_name=dataset, test_size=test_size)

        return jsonify({
            'available_datasets': get_available_datasets(),
            'current_dataset': current_dataset,
            'current_test_size': current_test_size,
            'train_count': len(train_df),
            'test_count': len(test_df),
            'accuracy': accuracies,
            'metrics': model_metrics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ML API is running', 'models_trained': True})

@app.route('/predict', methods=['POST'])
def predict():
    """Predict dietary risk using multiple models"""
    try:
        data = request.json

        # Encode incoming categorical values
        input_values = []
        for col in feature_cols:
            val = data.get(col, '')
            le = encoders[col]
            if val in le.classes_:
                input_values.append(le.transform([val])[0])
            else:
                # Fallback for unseen values
                input_values.append(0)

        input_array = np.array([input_values])
        input_scaled = scaler.transform(input_array)

        # Get predictions from all models
        knn_pred = int(knn.predict(input_scaled)[0])
        cart_dt_pred = int(cart_dt.predict(input_scaled)[0])
        nb_pred = int(nb.predict(input_scaled)[0])
        lr_pred = int(lr.predict(input_scaled)[0])

        # Get probabilities from the models that support predict_proba
        knn_prob = float(knn.predict_proba(input_scaled)[0][1])
        cart_dt_prob = float(cart_dt.predict_proba(input_scaled)[0][1])
        lr_prob = float(lr.predict_proba(input_scaled)[0][1])
        nb_prob = float(nb.predict_proba(input_scaled)[0][1])
        avg_risk = (knn_prob + cart_dt_prob + lr_prob + nb_prob) / 4

        # Determine risk level
        if avg_risk < 0.3:
            risk_level = "Low"
        elif avg_risk < 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"

        results = {
            'predictions': {
                'KNN': knn_pred,
                'CART Decision Tree': cart_dt_pred,
                'Naive Bayes': nb_pred,
                'Logistic Regression': lr_pred
            },
            'probabilities': {
                'KNN': knn_prob,
                'CART Decision Tree': cart_dt_prob,
                'Logistic Regression': lr_prob,
                'Naive Bayes': nb_prob
            },
            'risk': risk_level,
            'risk_score': avg_risk,
            'recommendation': get_recommendation(avg_risk)
        }

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/eda', methods=['GET'])
def eda():
    """Get EDA statistics"""
    try:
        stats = {
            'shape': df.shape,
            'describe': df.describe(include='all').to_dict(),
            'target_distribution': df['target'].value_counts().to_dict(),
            'missing': df.isnull().sum().to_dict(),
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/pca', methods=['GET'])
def get_pca():
    """Get PCA visualization data"""
    try:
        pca_dict = {
            'pca_data': pca_data.tolist(),
            'explained_variance': pca.explained_variance_ratio_.tolist(),
            'targets': y_train.tolist()
        }
        return jsonify(pca_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/cluster', methods=['GET'])
def get_cluster():
    """Get clustering visualization data"""
    try:
        cluster_labels = kmeans.labels_.tolist()
        cluster_dict = {
            'cluster_labels': cluster_labels,
            'n_clusters': kmeans.n_clusters
        }
        return jsonify(cluster_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/model-accuracy', methods=['GET'])
def model_accuracy():
    """Get model accuracies and evaluation metrics"""
    try:
        return jsonify({'accuracies': accuracies, 'metrics': model_metrics})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get dataset statistics"""
    try:
        stats = {
            'total_samples': len(df),
            'features': len(feature_cols),
            'at_risk': int((y == 1).sum()),
            'safe': int((y == 0).sum()),
            'healthy': int((y == 0).sum()),
            'risk_percentage': float((y == 1).sum() / len(y) * 100),
            'feature_names': feature_cols,
            'train_count': len(train_df),
            'test_count': len(test_df),
            'dataset': current_dataset,
            'test_size': current_test_size,
            'available_datasets': get_available_datasets(),
            'train_sample': train_df.head(3).to_dict(orient='records'),
            'test_sample': test_df.head(3).to_dict(orient='records')
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_recommendation(risk_score):
    """Get dietary recommendation based on risk score"""
    if risk_score < 0.3:
        return "Your dietary choice appears safe. Enjoy your meal!"
    elif risk_score < 0.7:
        return "Your dietary choice has moderate risk. Review ingredients and consider alternatives."
    else:
        return "Your dietary choice has high risk due to allergies or preferences. Please reconsider your selection."

# Algorithm explanations and information
def get_algorithm_info_dict():
    """Generate algorithm info dictionary with current metrics"""
    return {
        'Naive Bayes': {
            'name': 'Naive Bayes',
            'description': 'Naive Bayes is a probabilistic classifier based on Bayes\' theorem that assumes feature independence.',
            'how_it_works': [
                'Calculates probability of each class given the input features',
                'Assumes all features are independent (naive assumption)',
                'Uses Bayes theorem: P(Class|Features) = P(Features|Class) × P(Class) / P(Features)',
                'For each feature, calculates probability distribution during training',
                'Multiplies probabilities of all features to get final class probability'
            ],
            'prediction_process': [
                'Your dietary input features are analyzed individually',
                'Algorithm calculates: "Given these features, what\'s the probability of High Risk?"',
                'Uses learned probability distributions from training data',
                'Example: If 80% of High Risk cases had allergy "Nuts", this feature contributes to prediction',
                'Combines all feature probabilities to get final prediction',
                'If probability > 0.5, classified as High Risk; otherwise Low Risk'
            ],
            'advantages': ['Fast training and prediction', 'Works well with smaller datasets', 'Handles high-dimensional data', 'Probabilistic predictions'],
            'output': 'Risk classification (0=Low Risk, 1=High Risk) + Probability score',
            'accuracy': f"{model_metrics.get('Naive Bayes', {}).get('accuracy', 0):.2%}"
        },
        'CART Decision Tree': {
            'name': 'CART Decision Tree',
            'description': 'A CART (Classification and Regression Tree) Decision Tree makes predictions by learning a series of binary splits using the Gini criterion.',
            'how_it_works': [
                'Recursively splits data based on feature values that maximize category purity',
                'Creates a tree-like structure of decision nodes and leaf nodes',
                'At each node, asks: "If feature X <= value Y, go left; otherwise go right"',
                'Continues splitting until reaching pure or terminal nodes (leaves)',
                'Each leaf node contains the predicted class'
            ],
            'prediction_process': [
                'Your dietary preferences start at the tree\'s root node',
                'Algorithm asks a series of "yes/no" questions (e.g., "Is your age > 40?")',
                'Based on your answers, it navigates down the tree branches',
                'Eventually reaches a leaf node which contains the risk prediction',
                'The path taken shows which factors were most important for your prediction'
            ],
            'advantages': ['Easy to interpret', 'No data scaling needed', 'Handles non-linear patterns', 'Fast predictions'],
            'output': 'Risk classification (0=Low Risk, 1=High Risk)',
            'accuracy': f"{model_metrics.get('CART Decision Tree', {}).get('accuracy', 0):.2%}"
        },
        'KNN (K-Nearest Neighbors)': {
            'name': 'K-Nearest Neighbors (KNN)',
            'description': 'KNN classifies a new point based on the classes of its k nearest neighbors in the training data.',
            'how_it_works': [
                'Stores all training data in memory (lazy learner)',
                'For a new sample, calculates distance to all training samples',
                'Finds the k nearest neighbors (k=5 in this model)',
                'Counts how many neighbors belong to each class',
                'Assigns the class with the most neighbors'
            ],
            'prediction_process': [
                'Your dietary profile is compared to all 800+ training samples',
                'Calculates how similar your profile is to each training sample',
                'Finds the 5 most similar profiles (nearest neighbors)',
                'Checks: how many of these 5 had High Risk vs Low Risk?',
                'If 3 out of 5 are High Risk, your prediction is High Risk (probability = 60%)',
                'This is like asking: "People with similar diets - what was their risk?"'
            ],
            'advantages': ['Simple and intuitive', 'No training phase', 'Works well with local patterns', 'Flexible for multi-class'],
            'output': 'Risk classification (0=Low Risk, 1=High Risk) + Probability score',
            'accuracy': f"{model_metrics.get('KNN', {}).get('accuracy', 0):.2%}"
        },
        'Logistic Regression': {
            'name': 'Logistic Regression',
            'description': 'Logistic Regression models the probability of a binary outcome using a logistic function.',
            'how_it_works': [
                'Learns coefficients (weights) for each feature during training',
                'Combines weighted features with a bias term: sum(weight × feature) + bias',
                'Applies a sigmoid function (S-curve) to convert the result to probability',
                'Sigmoid function squashes values between 0 and 1',
                'Probability > 0.5 predicts Class 1 (High Risk); < 0.5 predicts Class 0 (Low Risk)'
            ],
            'prediction_process': [
                'Each feature (age, allergy, cuisine, etc.) gets a learned weight',
                'Features are multiplied by their weights and summed',
                'Example: (0.8 × age_score) + (-1.2 × allergy_score) + ... = raw score',
                'Raw score is converted to probability using sigmoid: P = 1 / (1 + e^(-score))',
                'If P > 0.5, prediction is High Risk; otherwise Low Risk',
                'The probability tells you the confidence in the prediction'
            ],
            'advantages': ['Fast training and prediction', 'Probabilistic output', 'Interpretable coefficients', 'Works well for linear relationships'],
            'output': 'Risk classification (0=Low Risk, 1=High Risk) + Probability score',
            'accuracy': f"{model_metrics.get('Logistic Regression', {}).get('accuracy', 0):.2%}"
        }
    }

ALGORITHM_INFO = get_algorithm_info_dict()

@app.route('/algorithm-info', methods=['GET'])
def get_algorithm_info():
    """Get detailed information about all algorithms"""
    try:
        algo_info = get_algorithm_info_dict()
        return jsonify(algo_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/algorithm-info/<algorithm>', methods=['GET'])
def get_specific_algorithm_info(algorithm):
    """Get detailed information about a specific algorithm"""
    try:
        algo_info = get_algorithm_info_dict()
        if algorithm in algo_info:
            return jsonify(algo_info[algorithm])
        else:
            return jsonify({'error': f'Algorithm {algorithm} not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint that returns dietary plan suggestions."""
    try:
        data = request.json or {}
        message = data.get('message', '')
        context = data.get('context', {})
        reply = generate_chatbot_reply(message, context)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


def generate_chatbot_reply(message, context=None):
    message = (message or '').strip().lower()
    if not message:
        return "Hi! I can help you build a healthy diet plan. Ask me about meal suggestions, allergies, or balanced food options."

    context = context or {}
    food_pref = context.get('foodPreference', '')
    allergies = context.get('allergies', '')
    spiciness = context.get('spicinessLevel', '')
    meal_type = context.get('mealType', '')
    age_group = context.get('ageGroup', '')

    def sanitize(value):
        return value.strip().title() if isinstance(value, str) and value.strip() else None

    food_pref = sanitize(food_pref)
    allergies = sanitize(allergies)
    spiciness = sanitize(spiciness)
    meal_type = sanitize(meal_type)
    age_group = sanitize(age_group)

    if any(term in message for term in ['diet plan', 'meal plan', 'healthy plan', 'plan', 'food plan']):
        parts = [
            "A healthy diet plan focuses on balanced meals with vegetables, lean proteins, whole grains, and healthy fats."
        ]
        if food_pref:
            if food_pref == 'Vegan':
                parts.append("Since you prefer vegan food, favor legumes, tofu, whole grains, nuts, and plenty of vegetables.")
            elif food_pref == 'Vegetarian':
                parts.append("As a vegetarian, include eggs, dairy, beans, lentils, and colorful vegetables for protein.")
            elif food_pref == 'Non-Vegetarian':
                parts.append("For non-vegetarian meals, choose grilled fish, chicken, or lean meats and keep portions moderate.")
        if allergies and allergies != 'None':
            parts.append(f"Avoid {allergies.lower()} and choose safe alternatives like fresh fruits, vegetables, and whole grains.")
        if spiciness:
            parts.append(f"If you like {spiciness.lower()} flavor, balance it with cooling sides like salads or yogurt.")
        if meal_type:
            parts.append(f"For {meal_type.lower()}, aim for a mix of protein, fiber, and vegetables.")
        if age_group:
            parts.append(f"For {age_group.lower()}, keep portions balanced and stay hydrated.")
        parts.append("Try a sample menu with a vegetable-rich breakfast, a lean-protein lunch, and a lighter dinner with fresh greens.")
        return ' '.join(parts)

    if any(term in message for term in ['allergy', 'allergies', 'avoid', 'safe', 'unsafe']):
        if allergies and allergies != 'None':
            return f"Since you're allergic to {allergies.lower()}, avoid dishes that contain that ingredient and choose clean, simple meals with fresh produce and whole grains."
        return "If you have allergies, let me know which ones so I can suggest safe, allergy-friendly meal ideas."

    if any(term in message for term in ['breakfast', 'lunch', 'dinner', 'snack']):
        if meal_type:
            return f"For {meal_type.lower()}, choose a balanced plate with protein, vegetables, and a healthy carbohydrate source."
        return "For each meal, include protein, fiber, and vegetables to stay energized and satisfied."

    if any(term in message for term in ['spicy', 'spice']):
        return "Spicy food can be part of a healthy diet when balanced with vegetables, lean protein, and cooling sides like salad or yogurt."

    if any(term in message for term in ['healthy', 'nutrition', 'nutritious']):
        return "Healthy eating means choosing whole foods, moderate portions, and a balance of protein, fiber, and healthy fats. Avoid processed foods and drink plenty of water."

    return "I can help you with healthy meal ideas, diet plans, and allergy-safe food choices. Ask me something like 'Suggest a healthy meal plan' or 'What can I eat if I am allergic to dairy?'"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

