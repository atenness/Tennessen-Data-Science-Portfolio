import streamlit as st

st.title("Hello, Streamlit")
st.write("This is my first streamlit app.")

if st.button("Click me!"):
    st.write("🎉 You clicked the button! Nice Work! 🚀")
else: 
    st.write("Click the button to see what happens...")

color = st.color_picker("Pick a color", "#00f900")
st.write(f"You picked: {color}")

import pandas as pd
st.subheader("Exploring Our Dataset")
#Load the CSV file
df = pd.read_csv("data/sample_data-1.csv")
st.write("Here's our data: ")
st.dataframe(df)

#Fliter by city
city = st.selectbox("Select a city", df["City"].unique())
filtered_df = df[df["City"]==city]

st.write(f"People in a {city}: ")
st.dataframe(filtered_df)

#Filter by occupation
occupation = st.selectbox("Select an occupation", df["Occupation"].unique())
filtered_df = df[(df["City"] == city) & (df["Occupation"] == occupation)]

st.write(f"{occupation}s in {city}:")
st.dataframe(filtered_df)

#Extend Your App
st.write(df.describe())
st.bar_chart(df["Salary"])

# Add bar chart
st.bar_chart(df["Salary"])

import seaborn as sns

box_plot = sns.boxplot(x=df["City"], y=df["Salary"])

st.pyplot(box_plot.get_figure())