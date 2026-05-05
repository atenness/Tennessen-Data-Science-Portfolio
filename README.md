# Data Science Portfolio – Gus Tennessen

## Overview
This repository contains a collection of data science projects demonstrating skills in data analysis, visualization, regression analysis, and application development.

## Projects

### 1. Streamlit App

[View the Project](https://github.com/atenness/Tennessen-Data-Science-Portfolio/tree/main/basic_streamlit_app)

**Description:** This project is an interactive Streamlit application that explores the Palmer Penguins dataset through dynamic visualizations. Users can analyze how physical characteristics like body mass, flipper length, and bill length vary across species, sex, and island.

**Tools:** Python, Streamlit, Pandas, etc.

**Key Features:**
- Interactive filtering by species, sex, island, etc. 
- Scatterplots showing relationships between:
    - Flipper length and body mass
    - Bill length and body mass

**Location:** `basic_streamlit_app/`

### 2. Tidy Data Project

[View the Project](https://github.com/atenness/Tennessen-Data-Science-Portfolio/tree/main/TidyData-Project)

**Description:** This project demonstrates the process of cleaning, transforming, and analyzing a real-world dataset using tidy data principles. The dataset contains information on Olympic medalists from the 2008 Beijing Olympics, organized in a wide, unstructured format.

This project strengthens my data wrangling and processing skills, which are essential for any data science workflow. It complements my portfolio by demonstrating my ability to take messy, real-world data and prepare it for analysis and visualization. 

**Tools:** Python, Pandas, Seaborn, Matplotlib.

**Key Features:**
- Bar charts for gender comparison and medal count
- Pivot table for analyzing medal counts by gender and sport

**Location:** `TidyData-Project/`

### 3. Supervised Machine Learning Web App

[View the Project](https://github.com/atenness/Tennessen-Data-Science-Portfolio/tree/main/MLStreamlitApp)

**Description:** This app is an interactive machine learning application using Streamlit that allows users to upload datasets, select target variables, train models, tune hyperparameters, and evaluate performance in real time.

The key development for this project was designing a full preprocessing and modeling pipeline using scikit-learn, and making it flexible enough to handle different datasets. It expands my portfolio from just running models, to building interfaces. I focused on model evaluation and interpretability, so users could understand why a model performed the way it did.

**Key Features:**
- Upload custom datasets or use a built-in sample dataset
- Select from multiple supervised learning models:
  - Logistic Regression
  - Decision Tree
  - K-Nearest Neighbors
- Interactive hyperparameter tuning via UI sliders
- Automated preprocessing pipeline
- Model evaluation with:
  - Accuracy, Precision, Recall, F1 Score
- Model interpretability

**Tools & Technologies:** Python, Streamlit, Scikit-learn, Pandas, NumPy, Matplotlib  

**Location:** `MLStreamlitApp`

### 4. Unsupervised Machine Learning Web App

[View the Project](https://github.com/atenness/Tennessen-Data-Science-Portfolio/tree/main/MLUnsupervised_app)

**Description:** This ia an interactive unsupervised machine learnign app using Streamlit. Users can upload a dataset and select whichever numeric features they want for analysis. After selecting from three different unsupervised ML models, they can tune hyperparameters and evaluate performance. 

This was a very important app for my coding development. After learning how to design a full preprocessing and modeling pipeline with machine learning, this was key for being able to interpret data structures for real world analysis. There was also more of a focus on interprtability, through understanding of silhouette scores, elbow plots, and PCA variance. I extended beyond just generating results, to actually explaining them with this app. 

**Key Features:**
- Upload custom datasets or use a built-in sample dataset
- Select from multiple supervised learning models:
  - K-Means
  - Hierarchical Clustering
  - Principal Component Analysis
- Interactive hyperparameter tuning via UI sliders
- Automated preprocessing pipeline
- Model evaluation with:
  - Silhouette scores, cluster visualization, elbow plots, total variances. 
- Model interpretability

**Tools & Technologies:** Python, Streamlit, Scikit-learn, Pandas, NumPy, Matplotlib  

**Location:** `MLStreamlitApp`

## Skills Demonstrated
- Data visualization
- Statistical analysis
- Interactive app development
- Machine Learning: Supervised and Unsupervised
- Model interpretation

## How to Use
Each project is contained in its own folder with instructions.