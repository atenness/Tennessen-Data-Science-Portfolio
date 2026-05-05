# Tidy Data Project

## Overview
This project demonstrates the process of cleaning, transforming, and analyzing a real-world dataset using tidy data principles. The dataset contains information on **Olympic medalists from the 2008 Beijing Olympics**, organized in a wide and non-tidy format.

The goal of this project is to:
- Reshape the dataset into a tidy structure
- Perform exploratory data analysis
- Generate visual insights from the cleaned data

## Dataset
The dataset includes Olympic medalists categorized by sport and gender, with variables initially embedded within column names (e.g., "male_swimming", "female_archery"). This structure violates tidy data principles and requires transformation.

## Data Cleaning Process
The dataset was transformed by:

1. **Reshaping (Wide to Long Format)**  
   - Used `pandas.melt()` to convert the dataset into a long format.

2. **Splitting Variables**  
   - Applied "str.split()" to separate combined column names into two variables:
     - "gender"
     - "sport"

3. **Handling Missing Values**  
   - Removed null values to ensure each row represents a valid observation.

## Exploratory Data Analysis

### Key Analyses Performed:
- Medal counts by sport
- Gender distribution of medalists
- Identification of sports with the largest gender disparities

### Pivot Table
A pivot table was created to summarize medal counts by sport and gender, enabling comparison across categories and supporting further analysis.

## Visualizations
The project includes several visualizations, such as:
- Bar charts of top sports by medal count
- Gender comparisons across sports
- Visualizations highlighting disparities between male and female medalists

These visualizations were created using:
- matplotlib
- seaborn

## Key Insights
- Certain sports have significantly higher medal counts than others
- Gender representation varies across sports
- Some sports have significant disparities between male and female medalists

## Tools & Libraries
- Python
- Pandas
- Matplotlib
- Seaborn
- Jupyter Notebook

## Links to References: 
- Pandas Cheat Sheet: https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf
- Tidy Data Principles: https://vita.had.co.nz/papers/tidy-data.pdf 
