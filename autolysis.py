#Coded in colab

!pip install pandas seaborn matplotlib numpy

# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas",
#   "seaborn",
#   "matplotlib",
#   "numpy",
#   "scipy",
#   "openai",
#   "scikit-learn",
#   "requests",
#   "ipykernel",  
# ]
# ///

import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import requests
import json
import openai  

# Function to analyze the data (basic summary stats, missing values, correlation matrix)
def analyze_data(df):
    print("Analyzing the data...")  
    # Summary statistics for numerical columns
    summary_stats = df.describe()

    # Check for missing values
    missing_values = df.isnull().sum()

    # Select only numeric columns for correlation matrix
    numeric_df = df.select_dtypes(include=[np.number])

    # Correlation matrix for numerical columns
    corr_matrix = numeric_df.corr() if not numeric_df.empty else pd.DataFrame()

    print("Data analysis complete.")  
    return summary_stats, missing_values, corr_matrix


# Function to detect outliers using the IQR method
def detect_outliers(df):
    print("Detecting outliers...")  
    # Select only numeric columns
    df_numeric = df.select_dtypes(include=[np.number])

    # Apply the IQR method to find outliers in the numeric columns
    Q1 = df_numeric.quantile(0.25)
    Q3 = df_numeric.quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df_numeric < (Q1 - 1.5 * IQR)) | (df_numeric > (Q3 + 1.5 * IQR))).sum()

    print("Outliers detection complete.")  
    return outliers


# Function to generate visualizations (pairplot, boxplot, violin plot)
def visualize_data(df, output_dir):
    print("Generating visualizations...")  

    # Pairplot for relationships between all numerical features
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        sns.pairplot(numeric_df)
        pairplot_file = os.path.join(output_dir, 'pairplot.png')
        plt.savefig(pairplot_file)
        plt.close()
    else:
        pairplot_file = None

    # Boxplot for outliers detection in numerical columns
    plt.figure(figsize=(12, 8))
    numeric_df.boxplot(rot=90, grid=False)
    plt.title('Boxplot for Numerical Features')
    boxplot_file = os.path.join(output_dir, 'boxplot.png')
    plt.savefig(boxplot_file)
    plt.close()

    # Violin plot for the first numerical column (if exists)
    if not numeric_df.empty:
        first_numeric_column = numeric_df.columns[0]
        plt.figure(figsize=(10, 6))
        sns.violinplot(x=first_numeric_column, data=df, inner="quartile", color='skyblue')
        plt.title(f'Violin Plot for {first_numeric_column}')
        violinplot_file = os.path.join(output_dir, 'violin_plot.png')
        plt.savefig(violinplot_file)
        plt.close()
    else:
        violinplot_file = None

    print("Visualizations generated.")  
    return pairplot_file, boxplot_file, violinplot_file


# Function to create the README.md with a narrative and visualizations
def create_readme(summary_stats, missing_values, corr_matrix, outliers, output_dir):
    print("Creating README file...")  
    # Write the analysis report to a markdown file
    readme_file = os.path.join(output_dir, 'README.md')
    try:
        with open(readme_file, 'w') as f:
            f.write("# Automated Data Analysis Report\n\n")

            # Introduction Section
            f.write("## Introduction\n")
            f.write("This is an automated analysis of the dataset, providing summary statistics, visualizations, and insights from the data.\n\n")

            # Summary Statistics Section
            f.write("## Summary Statistics\n")
            f.write("The summary statistics of the dataset are as follows:\n")
            f.write("\n| Statistic    | Value |\n")
            f.write("|--------------|-------|\n")

            # Write summary statistics for each column (mean, std, min, etc.)
            for column in summary_stats.columns:
                f.write(f"| {column} - Mean | {summary_stats.loc['mean', column]:.2f} |\n")
                f.write(f"| {column} - Std Dev | {summary_stats.loc['std', column]:.2f} |\n")
                f.write(f"| {column} - Min | {summary_stats.loc['min', column]:.2f} |\n")
                f.write(f"| {column} - 25th Percentile | {summary_stats.loc['25%', column]:.2f} |\n")
                f.write(f"| {column} - 50th Percentile (Median) | {summary_stats.loc['50%', column]:.2f} |\n")
                f.write(f"| {column} - 75th Percentile | {summary_stats.loc['75%', column]:.2f} |\n")
                f.write(f"| {column} - Max | {summary_stats.loc['max', column]:.2f} |\n")
                f.write("|--------------|-------|\n")

            f.write("\n")

            # Missing Values Section (Formatted as Table)
            f.write("## Missing Values\n")
            f.write("The following columns contain missing values, with their respective counts:\n")
            f.write("\n| Column       | Missing Values Count |\n")
            f.write("|--------------|----------------------|\n")
            for column, count in missing_values.items():
                f.write(f"| {column} | {count} |\n")
            f.write("\n")

            # Outliers Detection Section (Formatted as Table)
            f.write("## Outliers Detection\n")
            f.write("The following columns contain outliers detected using the IQR method (values beyond the typical range):\n")
            f.write("\n| Column       | Outlier Count |\n")
            f.write("|--------------|---------------|\n")
            for column, count in outliers.items():
                f.write(f"| {column} | {count} |\n")
            f.write("\n")

            # Correlation Matrix Section
            f.write("## Correlation Matrix\n")
            f.write("Below is the correlation matrix of numerical features, indicating relationships between different variables:\n\n")
            f.write("![Correlation Matrix](pairplot.png)\n\n")

            # Outliers Visualization Section
            f.write("## Outliers Visualization\n")
            f.write("This chart visualizes the number of outliers detected in each column:\n\n")
            f.write("![Outliers](boxplot.png)\n\n")

            # Distribution Plot Section
            f.write("## Distribution of Data\n")
            f.write("Below is the distribution plot of the first numerical column in the dataset:\n\n")
            f.write("![Distribution](violin_plot.png)\n\n")

            # Conclusion Section
            f.write("## Conclusion\n")
            f.write("The analysis has provided insights into the dataset, including summary statistics, outlier detection, and correlations between key variables.\n")
            f.write("The generated visualizations and statistical insights can help in understanding the patterns and relationships in the data.\n\n")

            # Adding Story Section
            f.write("## Data Story\n")
            f.write("Based on the data analysis, here is a creative narrative that interprets the findings in an engaging and detailed manner:\n\n")

        print(f"README file created: {readme_file}")  
        return readme_file
    except Exception as e:
        print(f"Error writing to README.md: {e}")
        return None




# Function to generate a detailed story using the new OpenAI API through the proxy
def question_llm(prompt, context):
    print("Generating story using LLM...")  # Debugging line
    try:
        # Get the AIPROXY_TOKEN from the environment variable
        token = "Enter your  AI PROXY TOKEN"

        # Set the custom API base URL for the proxy
        api_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

        # Construct the full prompt
        full_prompt = f"""
        Based on the following data analysis, please generate a creative and engaging story. The story should include multiple paragraphs, a clear structure with an introduction, body, and conclusion, and should feel like a well-rounded narrative.

        Context:
        {context}

        Data Analysis Prompt:
        {prompt}

        The story should be elaborate and cover the following:
        - An introduction to set the context.
        - A detailed body that expands on the data points and explores their significance.
        - A conclusion that wraps up the analysis and presents any potential outcomes or lessons.
        - Use transitions to connect ideas and keep the narrative flowing smoothly.
        - Format the story with clear paragraphs and structure.
        """

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        # Prepare the body with the model and prompt
        data = {
            "model": "gpt-4o-mini",  # Specific model for proxy
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        # Send the POST request to the proxy
        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        # Check for successful response
        if response.status_code == 200:
            # Extract the story from the response
            story = response.json()['choices'][0]['message']['content'].strip()
            print("Story generated.")  
            return story
        else:
            print(f"Error with request: {response.status_code} - {response.text}")
            return "Failed to generate story."

    except Exception as e:
        print(f"Error: {e}")
        return "Failed to generate story."



# Main function that integrates all the steps
def main(csv_file):
    print("Starting the analysis...")  

    # Set the API token as an environment variable

    # Try reading the CSV file with 'ISO-8859-1' encoding to handle special characters
    try:
        df = pd.read_csv(csv_file, encoding='ISO-8859-1')
        print("Dataset loaded successfully!")  
    except UnicodeDecodeError as e:
        print(f"Error reading file: {e}")
        return

    summary_stats, missing_values, corr_matrix = analyze_data(df)

    # Debugging print
    print("Summary Stats:")
    print(summary_stats)

    outliers = detect_outliers(df)

    # Debugging print
    print("Outliers detected:")
    print(outliers)

    output_dir = os.path.splitext(csv_file)[0]
    os.makedirs(output_dir, exist_ok=True)

    # Visualize the data and check output paths
    pairplot_file, boxplot_file, violinplot_file = visualize_data(df, output_dir)

    print("Visualizations saved.")

    # Generate the story using the LLM
    story = question_llm("Generate a nice and creative story from the analysis",
                         context=f"Dataset Analysis:\nSummary Statistics:\n{summary_stats}\n\nMissing Values:\n{missing_values}\n\nCorrelation Matrix:\n{corr_matrix}\n\nOutliers:\n{outliers}")

    # Create the README file with the analysis and the story
    readme_file = create_readme(summary_stats, missing_values, corr_matrix, outliers, output_dir)
    if readme_file:
        try:
            # Append the story to the README.md file
            with open(readme_file, 'a') as f:
                f.write("## Story\n")
                f.write(f"{story}\n")

            print(f"Analysis complete! Results saved in '{output_dir}' directory.")
            print(f"README file: {readme_file}")
            print(f"Visualizations: {pairplot_file}, {boxplot_file}, {violinplot_file}")
        except Exception as e:
            print(f"Error appending story to README.md: {e}")
    else:
        print("Error generating the README.md file.")

csv_file = "Enter your dataset link"
main(csv_file)

