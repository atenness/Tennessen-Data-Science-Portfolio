#Start with importing all necessary libraries:
import streamlit as st
import pandas as pd
import numpy as np
#Import tools from Sci-Kit learn:
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.neighbors import KNeighborsClassifier
#Import the metrics we will use:
from sklearn.metrics import (
    accuracy_score, 
    precision_score,
    recall_score,
    f1_score, 
    confusion_matrix,
    classification_report
)
#For visualizations:
import matplotlib.pyplot as plt

# ----------------------------
# Initiate Streamlit Page:
# ----------------------------
st.set_page_config(page_title = "ML Streamlit App", layout = "wide")

st.title("Supervised Machine Learning App")
st.write(
    "Upload a dataset, choose a target variable, select a mdodel, tune hyperparameters, and evaluate performance"
)

# ----------------------------
#File Upload: 
# ----------------------------
#Allow for user to upload their own dataset:
chosen_file = st.file_uploader("Upload a CSV file", type = ["csv"])
#Tell streamlit to save the result, so as not to reload dataset every time:
from pathlib import Path

@st.cache_data
def load_sample_data():
    file_path = Path(__file__).parent / "sample_data" / "Iris.csv"
    return pd.read_csv(file_path)

use_sample = st.checkbox("Use sample Iris dataset instead")
df = None
# Defining when streamlit shouls use sample data vs imported data:
if use_sample: 
    df = load_sample_data()
elif chosen_file is not None: 
    df = pd.read_csv(chosen_file)
#Preview data before modeling:
if df is not None:
    st.subheader("Dataset Preview")
    st.dataframe(df.head())
    st.write(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")

    # ----------------------------
    # Target selection
    # ----------------------------
    # Creating a dropdown menu bar so user can choose which column they want to predict:
    target_col = st.selectbox("Select the target column", df.columns)
    # splitting dataset:
    X = df.drop(columns = [target_col])
    y = df[target_col]
    # ensuring the selected target has at least 2 unique categories:
    if y.nunique() < 2: 
        st.error("Target column must have at least 2 classes.")
        st.stop()
    
    #encode target labels into numbers if needed: 
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y.astype(str))

    # ----------------------------
    # Feature Types
    # ----------------------------
    # Separate predictor columns into numeric and categorical:
    numeric_features = X.select_dtypes(include = ["int64", "float64"]).columns.tolist()
    categorical_features = X.select_dtypes(exclude = ["int64", "float64"]).columns.tolist()
    # Fill missing values with mean, and standardize values (for numeric):
    numeric_transformer = Pipeline(
        steps = [
            ("imputer", SimpleImputer(strategy = "mean")),
            ("scaler", StandardScaler())
        ]
    )
    # Fill in missing values with most common category (for categorical):
    categorical_transformer = Pipeline(
        steps = [
            ("imputer", SimpleImputer(strategy = "most_frequent")), 
            ("onehot", OneHotEncoder(handle_unknown = "ignore"))
        ]
    )
    #^ One-hot encodes catrgories into binary columns
    # Combining both preprocessing pipelines:
    Preprocessor = ColumnTransformer(
        transformers = [
            ("num", numeric_transformer, numeric_features), 
            ("cat", categorical_transformer, categorical_features)
        ]
    )

    # ----------------------------
    # Sidebar model controls
    # ----------------------------
    # Create a sidebar:
    st.sidebar.header("Model Settings")
    # Model types: Logistic regression, decision tree, k-nearest neighbors
    model_name = st.sidebar.selectbox(
        "Choose a model", 
        ["Logistic Regression", "Decision Tree", "K-Nearest Neighbors"]
    )
    # set parameter options for test_size and random state:
    test_size = st.sidebar.slider("Test set size", 0.1, 0.4, 0.2, 0.05)
    random_state = st.sidebar.slider("Random state", 0, 100, 42, 1)
    
    # Set up each model:
    if model_name == "Logistic Regression": 
        c_value = st.sidebar.slider("Regularization strength inverse (C)", 0.01, 10.0, 1.0)
        max_iter = st.sidebar.slider("Max iterations", 100, 1000, 200, 50)
        model = LogisticRegression(C=c_value, max_iter = max_iter)
    
    elif model_name == "Decision Tree": 
        max_depth = st.sidebar.slider("Max depth", 1, 20, 5) 
        min_samples_split = st.sidebar.slider("Min samples split", 2, 20, 2)
        model = DecisionTreeClassifier(
            max_depth = max_depth, 
            min_samples_split = min_samples_split, 
            random_state = random_state
        )
    else: 
        n_neighbors = st.sidebar.slider("Numbers of neighbors (k)", 1, 15, 5)
        model = KNeighborsClassifier(n_neighbors = n_neighbors)
    
    # ----------------------------
    # Train/test split
    # ----------------------------
    class_counts = y.value_counts()
    #In order to ensure that the app user picks the right column for analysis:
    if class_counts.min() < 2: 
        st.error("Each class must have at least 2 samples. Please choose a different target column")
        st.stop()
    # Train  and test data for fitting the model:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
    )
    # make it into one unified pipeline:
    clf = Pipeline(
        steps = [
            ("preprocessor", Preprocessor),
            ("model", model)
        ]
    )
    # train pipeline when user pushes button
    if st.button("Train Model"): 
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        # Establish performance metrics:
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average = "weighted", zero_division = 0)
        recall = recall_score(y_test, y_pred, average = "weighted", zero_division = 0)
        f1 = f1_score(y_test, y_pred, average = "weighted", zero_division= 0)

        st.subheader("Model Performance")
        # Display classification metrics:
        col1, col2, col3, col4, = st.columns(4)
        col1.metric("Accuracy", f"{accuracy:.3f}")
        col2.metric("precision", f"{precision:.3f}")
        col3.metric("Recall", f"{recall:.3f}")
        col4.metric("F1 Score", f"{f1:.3f}")

        st.subheader("Classification Report")
        # show more detailed classification report with performance of each class:
        report = classification_report(
            y_test, y_pred, target_names = label_encoder.classes_, zero_division = 0
        )
        st.text(report)
        
        st.subheader("Confusion Matrix")
        cm = confusion_matrix(y_test, y_pred)
        # Creating confusion matrix
        fig, ax = plt.subplots()
        im = ax.imshow(cm)
        # Label the chart:
        ax.set_title("Confusion Matrix")
        ax.set_xlabel("Predicted Label")
        ax.set_ylabel("True Label")
        # Defining the lines for easy interpretation
        ax.set_xticks(np.arange(len(label_encoder.classes_)))
        ax.set_yticks(np.arange(len(label_encoder.classes_)))
        ax.set_xticklabels(label_encoder.classes_, rotation = 45)
        ax.set_yticklabels(label_encoder.classes_)
        # show each count inside each confusion matrix cell:
        for i in range(cm.shape[0]): 
            for j in range(cm.shape[1]): 
                ax.text(j, i, cm[i, j], ha = "center", va = "center")
        # use matplotlib figure:
        st.pyplot(fig)

        # ----------------------------
        # Model Interpretations
        # ----------------------------
        # Display actual models:
        st.subheader("Model Interpretation")
        if model_name == "Logistic Regression": 
            st.write("Learned coefficients for logistic regression model:")
            # Display coefficients for Regression
            model_step = clf.named_steps["model"]
            preprocessor_step = clf.named_steps["preprocessor"]
            feature_names = preprocessor_step.get_feature_names_out()

            if len(model_step.coef_) == 1: 
                coef_df = pd.DataFrame({
                    "Feature": feature_names,
                    "Coefficient": model_step.coef_[0]
                }).sort_values(by = "Coefficient", key = abs, ascending = False)

                st.dataframe(coef_df)
                st.write("Intercept:", model_step.intercept_[0])
            else:
                st.write("Each class has its own set of coefficients.")
                
                for i, class_name in enumerate(label_encoder.classes_):
                    st.markdown(f"**Class: {class_name}**")
                    coef_df = pd.DataFrame({
                        "Feature": feature_names,
                        "Coefficient": model_step.coef_[i]
                    }).sort_values(by="Coefficient", key = abs, ascending = False)  

                    st.dataframe(coef_df)
                    st.write("Intercept:", model_step.intercept_[i])
        elif model_name == "Decision Tree":
            st.write("Learned Decision Tree:")
            # display decision tree:
            model_step = clf.named_steps["model"]
            preprocessor_step = clf.named_steps["preprocessor"]
            feature_names = preprocessor_step.get_feature_names_out()

            fig_tree, ax_tree = plt.subplots(figsize = (20,10))
            plot_tree(
                model_step,
                feature_names = feature_names,
                class_names = label_encoder.classes_,
                filled = True,
                rounded = True,
                ax = ax_tree
            )
            st.pyplot(fig_tree)
        elif model_name == "K-Nearest Neighbors":
            model_step = clf.named_steps["model"]
            # Display the chosen k:
            st.write(f"This K-Nearest Neighbors model uses **k = {model_step.n_neighbors}** neighbors.")
            st.write(
                "KNN classifies new observations based on the labels of the nearest training points."
            )
# if no data has been uploaded yet, ask user to do so:
else: 
    st.info("Upload a CSV file or check the sample dataset box to get started.")