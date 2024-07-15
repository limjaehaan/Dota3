# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 22:05:06 2024

@author: limja
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set the path to your config.toml file using a relative path
# Assuming config.toml is located in the same directory as your Python script
config_filename = "config.toml"
config_path = os.path.join(".", ".streamlit", config_filename)

# Set page configuration
st.set_page_config(layout="wide")

# Define aggregation options
aggregation_options = ['Weekly', 'Monthly', 'Quarterly', 'Yearly']

# CSS styling (including column margin)
st.markdown("""
    <style>
    .info-box {
        background-color: #e8f4fa;
        padding: 1rem;
        border: 1px solid #c1e1ec;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #007acc;
        margin-bottom: 1rem;
    }
    .mapping-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .mapping-item {
        flex: 1 1 45%;
        min-width: 250px;
    }
    .section-divider {
        border-top: 1px solid #ccc;
        margin: 2rem 0;
    }
    .stColumn {
        margin-right: 2rem; /* Adjust the margin as needed */
    }
    
    </style>
""", unsafe_allow_html=True)

# Predefined fields and title (unchanged)
predefined_fields = {
    "Transaction ID": None,
    "Date": None,
    "Customer ID": None,
    "Customer Name": None,
    "Product ID": None,
    "Product Name": None,
    "Product Category": None,
    "Quantity": None,
    "Sales": None
}

# Dashboard Title
st.title("Understand Your Business Data")
#  Get rid of top default padding
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

# File handling logic (unchanged)
left, middle, right = st.columns([2, 0.2, 2])  # Adding a middle empty column for spacing

# Add the provided section to st.sidebar:
with st.sidebar:
    file_option = st.radio("Choose Data Source:", ('Upload CSV file', 'Use Sample Transaction Data'))

    if file_option == 'Upload CSV file':
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
    else:
        sample_file_path = "Data/SampleInput.csv"  # Adjust the path as per your file location
        df = pd.read_csv(sample_file_path)

    if 'df' in locals():
        st.write("Data Preview:")
        st.write(df.head())

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # Manual Mapping (unchanged)
        st.markdown('<div class="section-header">Map Columns to Predefined Fields</div>', unsafe_allow_html=True)
        st.markdown('<div class="mapping-container">', unsafe_allow_html=True)
        for field in predefined_fields.keys():
            options = [None] + list(df.columns)
            predefined_fields[field] = st.selectbox(f"Select column for {field}", options, key=field)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # Ensure necessary fields are mapped (unchanged)
        if predefined_fields["Customer Name"] and predefined_fields["Date"] and predefined_fields["Sales"]:

            # Data Processing (updated)
            df_mapped = df.rename(columns={
                predefined_fields["Transaction ID"]: "Transaction ID" if predefined_fields["Transaction ID"] else None,
                predefined_fields["Date"]: "Date" if predefined_fields["Date"] else None,
                predefined_fields["Customer ID"]: "Customer ID" if predefined_fields["Customer ID"] else None,
                predefined_fields["Customer Name"]: "Customer Name" if predefined_fields["Customer Name"] else "Ignore",
                predefined_fields["Product ID"]: "Product ID" if predefined_fields["Product ID"] else None,
                predefined_fields["Product Name"]: "Product Name" if predefined_fields["Product Name"] else None,
                predefined_fields["Product Category"]: "Product Category" if predefined_fields["Product Category"] else None,
                predefined_fields["Quantity"]: "Quantity" if predefined_fields["Quantity"] else "Ignore",
                predefined_fields["Sales"]: "Sales" if predefined_fields["Sales"] else None
            })

            if "Ignore" in df_mapped.columns:
                df_mapped = df_mapped.drop(columns=["Ignore"])

            df_mapped["Date"] = pd.to_datetime(df_mapped["Date"], errors='coerce')
            df_mapped = df_mapped.dropna(subset=["Date"])

            min_date = df_mapped["Date"].min()
            max_date = df_mapped["Date"].max()
            st.markdown('<div class="section-header">Select Date Range</div>', unsafe_allow_html=True)

            start_date = st.date_input(
                "Start date",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )

            end_date = st.date_input(
                "End date",
                value=max_date,
                min_value=min_date,
                max_value=max_date
            )

            if start_date > end_date:
                st.error("Error: End date must fall after start date.")
            else:
                # Filter based on date range
                df_filtered = df_mapped[(df_mapped["Date"] >= pd.to_datetime(start_date)) & (df_mapped["Date"] <= pd.to_datetime(end_date))]

                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

with left:
    if 'df_filtered' in locals():
        # Aggregation Level Selection
        st.markdown('<div class="section-header">Select Aggregation Basis</div>', unsafe_allow_html=True)
        aggregation_basis = st.selectbox("Select aggregation basis", aggregation_options)

        if aggregation_basis == 'Weekly':
            df_agg = df_filtered.resample('W-Mon', on='Date').sum().reset_index()
            date_label = "Weekly"
        elif aggregation_basis == 'Monthly':
            df_agg = df_filtered.resample('M', on='Date').sum().reset_index()
            date_label = "Monthly"
        elif aggregation_basis == 'Quarterly':
            df_agg = df_filtered.resample('Q', on='Date').sum().reset_index()
            date_label = "Quarterly"
        elif aggregation_basis == 'Yearly':
            df_agg = df_filtered.resample('Y', on='Date').sum().reset_index()
            date_label = "Yearly"

        dates = df_agg["Date"]
        sales = df_agg["Sales"]

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # Visualization (updated for professional style)
        st.markdown(f'<div class="section-header">{date_label} Sales Over Time</div>', unsafe_allow_html=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, sales, marker='o', linestyle='-', color='#4C78A8', linewidth=2, markersize=8, label='Sales')
        ax.set_xlabel("Date", fontsize=14, fontweight='bold')
        ax.set_ylabel("Sales", fontsize=14, fontweight='bold')
        ax.set_title("", fontsize=16, fontweight='bold', pad=20)  # Empty string for title
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)  # Set alpha value here
        ax.legend(loc='upper left', fontsize=12)
        # Define a nice color palette:
        colors = ["#2B2F42", "#8D99AE", "#EF233C"]
        # Hide the all but the bottom spines (axis lines)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        

        if "Quantity" in df_agg.columns:
            quantity = df_agg["Quantity"]
            st.markdown(f'<div class="section-header">{date_label} Quantity Over Time</div>', unsafe_allow_html=True)
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            ax2.plot(dates, quantity, marker='o', linestyle='-', color='#ff7f0e', linewidth=2, markersize=8, label='Quantity')
            ax2.set_xlabel("Date", fontsize=14, fontweight='bold')
            ax2.set_ylabel("Quantity", fontsize=14, fontweight='bold')
            ax2.set_title("", fontsize=16, fontweight='bold', pad=20)  # Empty string for title
            ax2.tick_params(axis='both', which='major', labelsize=12)
            ax2.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)
            ax2.legend(loc='upper left', fontsize=12)
            # Hide the all but the bottom spines (axis lines)
            ax2.spines["right"].set_visible(False)
            ax2.spines["left"].set_visible(False)
            ax2.spines["top"].set_visible(False)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig2)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


with right:
    if 'df_filtered' in locals():
        # Top Customers by Sales
        st.markdown(f'<div class="section-header">Top Customers by Sales', unsafe_allow_html=True)
        top_options = [5, 10, 20, 30]
        top_n = st.selectbox("Select number of top customers to display", top_options, index=1, key="top_customers")
        top_customers = df_filtered.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(top_n).reset_index()
        st.write(f"Top {top_n} Customers:")
        st.table(top_customers)
    else:
        pass
        # st.write("Please map 'Customer Name', 'Date', and 'Sales' fields to proceed.")
        
        
    if 'df_filtered' in locals():
        # Top Product by Sales
        st.markdown(f'<div class="section-header">Top Products by Sales', unsafe_allow_html=True)
        top_options = [5, 10, 20, 30]
        top_n = st.selectbox("Select number of top prodcuts to display", top_options, index=1, key="top_products")
        top_customers = df_filtered.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(top_n).reset_index()
        st.write(f"Top {top_n} Products:")
        st.table(top_customers)
    else:
        pass
        # st.write("Please map 'Product Name', 'Date', and 'Sales' fields to proceed.")



#%%  