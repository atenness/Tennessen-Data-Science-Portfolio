import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Palmer's Penguins Dataset Exploration")
st.write("This app is an exploration of the Penguin's dataset, exploring streamlit's data visualization and interactive tools.")

#loading the dataset
df = pd.read_csv("data/penguins.csv")

st.subheader("Exploring the Dataset")
#Displaying data: 
st.write("Here's our data:")
st.dataframe(df)

#Filter by species
st.write("Pick a species:")
species = st.selectbox("Select a species", df["species"].unique())
filtered_df = df[df["species"] == species]
st.write(f"{species} Penguins:")
st.dataframe(filtered_df)

#Filter by Island
st.write("Pick an island:")
island = st.selectbox("Select an island", df["island"].unique())
filtered_df = df[(df["island"] == island) & (df["species"] == species)]
st.dataframe(filtered_df)
st.write(f"{species} penguins on {island}")

#Understanding key statistics:
st.subheader("Key Statistics:")
st.dataframe(df.describe())

#Visualizing Body Mass: 
fig, ax = plt.subplots()
#do this so plots don't draw from previous charts
sns.boxplot(data = df,
            x = "island",
            y = "body_mass_g", 
            ax = ax
)
st.pyplot(fig)

#Using slider for body mass:
st.subheader("Distribution by body mass:")
#ensure each value is an integer
min_mass, max_mass = st.slider(
    "Select body mass range (grams)",
    min_value = int(df["body_mass_g"].min()),
    max_value = int(df["body_mass_g"].max()),
    value = (3000, 5000),
    step = 100
)

bodymass_slider = df[
    (df["body_mass_g"] >= min_mass) &
    (df["body_mass_g"] <= max_mass)
]
st.dataframe(bodymass_slider)

#visualizing this data:
st.write("Visualizing this data:")
fig, ax = plt.subplots()
sns.boxplot(data = bodymass_slider,
            x = "species", 
            y = "body_mass_g",
            ax = ax
)
st.pyplot(fig)


st.subheader("Comparing size trends")
#Experimenting with buttons and visualizations: 
comparison = st.radio(
    "Choose a comparison:",
    ["None", "Flipper length to body mass", "Bill length to body mass"]
)
if comparison == "Flipper length to body mass":
    fig, ax = plt.subplots()
    sns.scatterplot(data = df,
                            x = "body_mass_g",
                            y = "flipper_length_mm",
                            ax = ax
    )
    st.pyplot(fig)
elif comparison == "Bill length to body mass":
    fig, ax = plt.subplots()
    sns.scatterplot(data = df,
                    x = f"body_mass_g",
                    y = "bill_length_mm",
                    ax = ax
    )
    st.pyplot(fig)

#Male and female comparisons
st.subheader("Visualizing Males and Females:")
male = df[df["sex"] == "male"]
female = df[df["sex"] == "female"]
sex_plot = st.radio(
    "Choose a comparison:",
    ["None", "Male size vs Species", "Female size vs Species"]
)
if sex_plot == "Male size vs Species":
    fig, ax = plt.subplots()
    sns.boxplot(data = male,
                x = "species",
                y = "body_mass_g",
                ax = ax
)
    st.pyplot(fig)
elif sex_plot == "Female size vs Species":
    fig, ax = plt.subplots()
    sns.boxplot(data = female,
                x = "species",
                y = "body_mass_g",
                ax = ax
)
    st.pyplot(fig)

#Finish with a button:
if st.button("Click Here to Finish!"):
    st.write("Congrats! You have explored the Palmer's Penguins dataset!")
else: st.write("Click the button to conclude.")