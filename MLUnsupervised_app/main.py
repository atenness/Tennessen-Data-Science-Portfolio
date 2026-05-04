# Import libraries: 
import streamlit as st
import pandas as pd
import numpy as np
# For preprocessing
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
# The unsupervised learning models:
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
# Metrics:
from sklearn.metrics import silhouette_score
# For visualization
import matplotlib.pyplot as plt
# For sample data path: 
from pathlib import Path

# Initiate Streamlit Page:

st.set_page_config(page_title = "ML Streamlit App", layout = "wide")

st.title("Unsupervised Machine Learning App")
st.write(
    "Upload a dataset, select numeric features, choose an unsupervised model."
    "Tune hyperparameters and explore clustering or dimensionality reduction results."
)

#File Upload: 

#Allow for user to upload their own dataset:
chosen_file = st.file_uploader("Upload a CSV file", type = ["csv"])
# This is so streamlit will save the result, not reload dataset every time:
from pathlib import Path

@st.cache_data
def load_sample_data():
    file_path = Path(__file__).parent / "sample_data" / "Iris.csv"
    return pd.read_csv(file_path)

use_sample = st.checkbox("Use sample Iris dataset instead")
df = None
# Defining when streamlit should use sample data vs imported data:
if use_sample: 
    df = load_sample_data()
elif chosen_file is not None: 
    df = pd.read_csv(chosen_file)
#Preview data before modeling:
if df is not None:
    st.subheader("Dataset Preview")
    st.dataframe(df.head())
    st.write(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")    
   
# Feature Selection

    st.subheader("Choose Features for Unsupervised Learning")

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    selected_cols = st.multiselect(
        "Select numeric features for analysis",
        numeric_cols,
        default=numeric_cols
    )

    if len(selected_cols) < 2:
        st.error("Please select at least two numeric features.")
        st.stop()

    X = df[selected_cols].copy()

# Cleaning Pipeline

    # Drop duplicates
    X = X.drop_duplicates()

    # Impute missing values
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler())
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, selected_cols)
        ]
    )

    X_processed = preprocessor.fit_transform(X)

# Sidebar Model Selection

    st.sidebar.header("Model Settings")

    model_name = st.sidebar.selectbox(
        "Choose a model",
        ["K-Means", "Hierarchical Clustering", "PCA"]
        )

    if model_name  == "K-Means":
        k = st.sidebar.slider("Number of Clusters", 2, 10, 3)
    # K-means requires you to choose how many clusters before it runs, so the user chooses upfront, then "k" groups are formed immediately. 

    elif model_name == "Hierarchical Clustering": 
        max_k = st.sidebar.slider("Maximum Number of Clusters", 3, 10, 6)
    # For Hierarchical Clustering, we're only limiting the max number of clusters, and the model will pick the best value of "k"  
        
        linkage = st.sidebar.selectbox(
            "Linkage Method",
            ["ward", "complete", "average", "single"]
        )
        # Ensure the user knows which linkage method to pick:
        explanation = st.sidebar.checkbox("Click here for linkage descriptions")
        if explanation: 
            st.sidebar.markdown("""
        - Ward linkage merges clusters in order to minimize variance, for clean, spherical clusters. It only works with Euclidean distances. 
        - Complete linkage looks at the maximum distance between clusters, for tight and compact clusters.
        - Average linkage simply uses the average distance between all pairs of points. It can be less sensitive to extremes, and good for a balanced approach. 
        - Single linkeage looks at the minimum distance between any pair of points. This can create long, chain-like clusters. 
        - Choose accordingly! """)

        if linkage == "ward":
            metric = "euclidean"
            st.sidebar.info("Ward linkage requires Euclidean distance")

        else: 
            metric = st.sidebar.selectbox(
                "Distance Metric", 
                ["euclidean", "manhattan", "cosine"]
            )

            # Ensure the user knows which diastance metric to use:
            explanation1 = st.sidebar.checkbox("Click here for metric descriptions")
            if explanation1: 
                st.sidebar.markdown("""
            - Euclidian: straight line distance, best for scaled numeric data
            - Manhattan: distance along axes
            - Cosine: measures angle and similarity in direction, not magnitude of distance
            - Choose Acordingly! """)
        
    elif model_name == "PCA":
        num_features = len(selected_cols)
        
        n_components = st.sidebar.slider(
            "Number of Components",
            2,
            min(10, num_features),
            2
        )
        st.sidebar.markdown("""
        - Smaller number of components: strong compression, easy to visualize
        - Medium number of components: keeps more structure, more balanced. Good for downstream modeling
        - Large number of components: keeps almost all information""")

# Train Model Button

    if st.button("Run Model"):

        if model_name == "K-Means":
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            clusters = model.fit_predict(X_processed)

        elif model_name == "Hierarchical Clustering":
            silhouette_scores = {}
            # try multiple values of k:
            for test_k in range (2, max_k + 1):
                test_model = AgglomerativeClustering(
                    n_clusters = test_k,
                    linkage = linkage,
                    metric = metric
                )

                test_clusters = test_model.fit_predict(X_processed)
            # compare them using the silhouette score:    
                score = silhouette_score(X_processed, test_clusters)
                silhouette_scores[test_k] = score
            # Automatically choose the best one:
            best_k = max(silhouette_scores, key=silhouette_scores.get)

            model = AgglomerativeClustering(
                n_clusters=best_k,
                linkage=linkage,
                metric=metric
            )

            clusters = model.fit_predict(X_processed)

            st.write(f"Automatically selected **{best_k} clusters** (highest silhouette score)")

        else: # PCA by default
            model = PCA(n_components = n_components)
            X_pca = model.fit_transform(X_processed)

# Results

        st.subheader("Model Results")

        if model_name != "PCA":

            # Silhouette Score
            score = silhouette_score(X_processed, clusters)

            st.metric("Silhouette Score", f"{score:.3f}")

            # Interpretation
            if score > 0.5:
                st.success("Strong cluster separation")
            elif score > 0.25:
                st.warning("Moderate cluster structure")
            else:
                st.error("Weak clustering")

            # PCA Visualization (different here than the PCA model)
            st.caption("Clusters are visualized using PCA to reduce the data to 2D.")
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_processed)

            fig, ax = plt.subplots()
            ax.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters)
            ax.set_title("Cluster Visualization (PCA)")
            st.pyplot(fig)

            # Cluster Summary
            result_df = pd.DataFrame(X)
            result_df["Cluster"] = clusters

            st.subheader("Cluster Summary")
            st.dataframe(result_df.groupby("Cluster").mean())

            # Cluster Size Plot
            st.subheader("Cluster Sizes")

            counts = result_df["Cluster"].value_counts().sort_index()

            fig2, ax2 = plt.subplots()
            ax2.bar(counts.index, counts.values)
            ax2.set_title("Cluster Distribution")
            st.pyplot(fig2)

            # Elbow Plot
            # Elbow plots are specific to K-Means because they rely on inertia, which hierarchical clustering does not optimize)
            if model_name == "K-Means":
                st.subheader("Elbow Plot")

                inertias = []
                k_vals = range(1, 11)
                # inertia measures how tightly grouped clusters are
                for i in k_vals:
                    km = KMeans(n_clusters=i, random_state = 42, n_init=10)
                    km.fit(X_processed)
                    inertias.append(km.inertia_)

                fig3, ax3 = plt.subplots()
                ax3.plot(k_vals, inertias, marker="o")
                ax3.set_xlabel("Number of Clusters")
                ax3.set_ylabel("Inertia")
                ax3.set_title("Elbow Plot")
                st.pyplot(fig3)

                st.write(
                    "The elbow plot helps evaluate different values of K. "
                    "A good K is often where the line starts to flatten."
                )

            #Silhouette Plot (Hierarchical Clustering)
            elif model_name == "Hierarchical Clustering":
                st.subheader("Silhouette Scores by Number of Clusters")
                # visual representation of cluster quality based on silhouette score per number of clusters
                fig3, ax3 = plt.subplots()
                ax3.plot(
                    list(silhouette_scores.keys()),
                    list(silhouette_scores.values()),
                    marker="o"
                )
                
                ax3.set_xlabel("Number of Clusters")
                ax3.set_ylabel("Silhouette Score")
                ax3.set_title("Choosing the Best Number of Clusters")
                st.pyplot(fig3)
                
                st.write(
                    "For hierarchical clustering, the app tests several possible cluster counts "
                    "and chooses the one with the highest silhouette score."
                )

        else:
            # PCA Only Mode

            explained = model.explained_variance_ratio_

            st.metric("Total Variance Explained", f"{explained.sum():.3f}")
            # this metric tells us how much of the original datas information is captured 
            fig, ax = plt.subplots()
            
            ax.scatter(X_pca[:, 0], X_pca[:, 1])
            ax.set_xlabel("Principal Component 1")
            ax.set_ylabel("Principal Component 2")
            ax.set_title("PCA Projection")
            st.pyplot(fig)

            st.subheader("Explained Variance by Component")

            explained_df = pd.DataFrame({
                "Component": [f"PC{i+1}" for i in range(len(explained))],
                "Explained Variance Ratio": explained
            })

            st.dataframe(explained_df)
            # this hsows the breakdown interactively.
            fig2, ax2 = plt.subplots()
            ax2.bar(explained_df["Component"], explained_df["Explained Variance Ratio"])
            ax2.set_xlabel("Principal Component")
            ax2.set_ylabel("Explained Variance Ratio")
            ax2.set_title("Variance Explained by Each Principal Component")
            st.pyplot(fig2)

            st.write(
                "PCA reduces the dataset into fewer dimensions while preserving as much variation "
                "as possible. A higher total variance explained means the selected components capture "
                "more of the original dataset's information."
            )