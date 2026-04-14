# Supervised Machine Learning Streamlit App

## Project Overview
This project is an interactive machine learning web application built using Streamlit. The app allows users to upload a dataset, select a target variable, train different supervised learning models, tune hyperparameters, and evaluate model performance in real time.

The goal of this project is to create an interactive tool for exploring how machine learning models behave and how changes in parameters affect performance.

## How to Run the App

### 1. Clone the Repository
git clone https://github.com/atenness/Tennessen-Data-Science-Portfolio/blob/main/MLStreamlitApp/app.py   

### 2. Install Required Libraries
Make sure you have Python 3.9+ installed, then run:  
pip install -r requirements.txt  

### 3. Run the App
streamlit run app.py  

### 4. Open in Browser
The app will automatically open at:  
http://localhost:8501  

## Deployed App  
https://tennessen-data-science-portfolio-ml.streamlit.app/  

## Required Libraries
- streamlit  
- pandas  
- numpy  
- scikit-learn  
- matplotlib  

## App Features

### Data Upload
- Upload any CSV dataset  
- Option to use a built-in sample dataset (Iris dataset)  

### Target Selection
- Choose any column as the prediction target  
- Validates that the target has at least two classes  

### Machine Learning Models

#### Logistic Regression
- Hyperparameters:
  - Regularization strength (C)
  - Max iterations
- Outputs:
  - Model coefficients
  - Feature importance insights  

#### Decision Tree Classifier
- Hyperparameters:
  - Max depth
  - Minimum samples per split
- Outputs:
  - Visualized decision tree  

#### K-Nearest Neighbors (KNN)
- Hyperparameters:
  - Number of neighbors (k)
- Outputs:
  - Explanation of classification logic  

## Data Preprocessing

The app uses a scikit-learn pipeline to automatically handle:

- Missing values:
  - Numerical → mean imputation  
  - Categorical → most frequent value  

- Feature scaling:
  - Standardization for numeric features  

- Encoding:
  - One-hot encoding for categorical variables  
  - Label encoding for the target variable  

---

## Model Evaluation

After training, the app displays:

- Accuracy  
- Precision  
- Recall  
- F1 Score  

Additional outputs:
- Classification report  
- Confusion matrix visualization  

## Model Interpretation

- Logistic Regression → Displays feature coefficients  
- Decision Tree → Visual tree diagram  
- KNN → Displays chosen value of k and explanation  

## References

- Streamlit Documentation: https://docs.streamlit.io  
- Scikit-learn Documentation: https://scikit-learn.org  

## Key Takeaways

- Demonstrates machine learning workflow  
- Allows interactive hyperparameter tuning  
- Provides model evaluation and visualization    

## Code Reference
See the main app file for implementation details.