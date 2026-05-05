# Unsupervised Machine Learning Streamlit App

## Project Overview
This project is an interactive machine learning web application built using Streamlit. Users can upload a dataset, and select their target variables. Then they can train three different supervised learning models, and choose hyperparameters. The model's performance is then evaluated in real time. 

The goal is to understand how unsupervised ML models change with different parameters. 

## How to Run the App

### 1. Clone the Repository
git clone https://github.com/atenness/Tennessen-Data-Science-Portfolio/blob/main/MLUnsupervised_app/main.py 

### 2. Install the Required Libraries
Male sure Python 3.9+ is installed then run: `pip install -r requirements.txt`

### 3. Run the App
In the terminal, run: `streamlit run main.py`
- The app will automatically open at: http://localhost:8503
- For the **Deployed App:** https://mainpy-x8h3k2rdmwjz6kxrgmpsro.streamlit.app/ 

### Required Libraries: 
- streamlit
- pandas
- numpy
- scikit-learn
- matplotlib

## App Features

### Data Upload
- Upload any CSV dataset  
- Option to use a built-in sample dataset (Iris dataset)  

### Feature Selection
- Choose at least two numeric features for analysis

### Machine Learning Models

#### K-Means Clustering
- Users select number of clusters (k) using a slider
- Model groups data by minimizing within-cluster variance
- Evaluation tools:
    - **Silhouette Score**
    - **Elbow Plot** (This helps the user choose the optimal k)

#### Hierarchical Clustering
- Users Select: 
    - Maximum number of clusters
    - Linkage method (ward, complete, average, single)
    - Distance metric (when applicable)
- The app tests multiple cluster sizes and automatically selects the k with the highest silhouette score

#### Principle Component Analysis (PCA)
- Users select the number of compnents
- PCA reduces dimensionality while preserving variance
- Outputs: 
    - 2D visualizations of data
    - Total variance explained
    - Variance explained by each compontent (table + bar chart)

### Visualizations
- Clusrer visualization using **PCA projection**
- Elbow plots for K-means
- Silhouette score plots for hierarchical clustering
- PCA varaiance bar charts

## Data Preprocessing
- Missing values handled using mean imputation
- Features scaled using standardization
- Only numeric features are used for modelin

## References
- Streamlit Documentation: https://docs.streamlit.io  
- Scikit-learn Documentation: https://scikit-learn.org

## Key Takeaways
- Demonstrates core unsupervised learning techniques
- Highlights trade-offs between clustering methods
- Provides an interactive environment for exploring unknown datasets
- Emphasizes both **model performance and interpretability**

## Code Reference
See the main app file for implementation details.