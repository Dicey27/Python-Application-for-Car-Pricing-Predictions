import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv('C://Users//edcs9//Desktop//pythonProject1interfata//detalii_masini_complet.csv')

# Data cleaning and preparation
data['Anul'] = data['Anul'].astype(int)
data['Kilometrajul'] = data['Kilometrajul'].str.replace(' km', '').str.replace(' ', '').astype(int)
data['Capacitatea motorului'] = data['Capacitatea motorului'].str.replace(' cm3', '').str.replace(' ', '').astype(int)
data['Preț'] = data['Preț'].str.replace(' ', '').astype(int)

# Features and target variable
X = data.drop('Preț', axis=1)
y = data['Preț']

# Splitting the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Encoding categorical variables and building the pipeline
categorical_features = ['Marca', 'Model', 'Tipul de combustibil']
numeric_features = ['Anul', 'Kilometrajul', 'Capacitatea motorului']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Replace LinearRegression with DecisionTreeRegressor
regressor = Pipeline(steps=[('preprocessor', preprocessor),
                            ('regressor', DecisionTreeRegressor(random_state=42))])
regressor.fit(X_train, y_train)

# Visualize the decision tree
plt.figure(figsize=(40, 20))  # Adjust size as needed for your display
plot_tree(regressor.named_steps['regressor'], max_depth=4, fontsize=10, feature_names=preprocessor.get_feature_names_out(), filled=True, proportion=True, rounded=True, impurity=False)
#plt.show()

# Function to estimate price based on input features
def estimate_price(marca, model, anul, kilometrajul, capacitatea_motorului, tipul_de_combustibil):
    input_data = {
        'Marca': [marca],
        'Model': [model],
        'Anul': [anul],
        'Kilometrajul': [kilometrajul],
        'Capacitatea motorului': [capacitatea_motorului],
        'Tipul de combustibil': [tipul_de_combustibil]
    }
    input_df = pd.DataFrame.from_dict(input_data)
    input_df['Anul'] = input_df['Anul'].astype(int)
    input_df['Kilometrajul'] = input_df['Kilometrajul'].astype(int)
    input_df['Capacitatea motorului'] = input_df['Capacitatea motorului'].astype(int)
    price_prediction = regressor.predict(input_df)
    return price_prediction[0]

# Example usage
#estimated_price = estimate_price(marca='Dacia', model='Duster', anul=2024, kilometrajul=1790,
#                                 capacitatea_motorului=1450, tipul_de_combustibil='Diesel')
#print(f'Estimare pret masina: {estimated_price: .2f} EUR')
