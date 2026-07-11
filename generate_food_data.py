import os
import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

genders = ['Male', 'Female', 'Other']
age_groups = ['0-18', '19-25', '26-40', '41-60', '60+']
food_prefs = ['Vegetarian', 'Non-Vegetarian', 'Vegan']
spice_levels = ['Mild', 'Medium', 'Spicy']
allergies_list = ['None', 'Nuts', 'Dairy', 'Gluten', 'Seafood']
cuisines = ['Indian', 'Chinese', 'Italian', 'Mexican', 'Continental']
meal_types = ['Breakfast', 'Lunch', 'Dinner', 'Snacks']

rows = []

for _ in range(1000):
    gender = random.choice(genders)
    age_group = random.choice(age_groups)
    food_pref = random.choice(food_prefs)
    spice = random.choice(spice_levels)
    allergy = random.choice(allergies_list)
    cuisine = random.choice(cuisines)
    meal = random.choice(meal_types)

    risk_score = 0.0

    # Base randomness
    risk_score += random.random() * 0.3

    # Allergy + cuisine mismatches increase risk
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

    # Age + spicy food risk
    if age_group == '60+' and spice == 'Spicy':
        risk_score += 0.15
    if age_group == '0-18' and spice == 'Spicy':
        risk_score += 0.10

    # Vegan + non-veg friendly cuisines (slight risk if no veg options assumed)
    if food_pref == 'Vegan' and cuisine in ['Italian', 'Mexican', 'Continental']:
        risk_score += 0.10

    # Heavy dinner spice risk
    if meal == 'Dinner' and spice == 'Spicy':
        risk_score += 0.08

    # Cap and decide target
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

df = pd.DataFrame(rows)
output_path = os.path.join(os.path.dirname(__file__), 'food_data.csv')
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} rows")
print(f"Saved file to: {output_path}")
print(df['target'].value_counts())

