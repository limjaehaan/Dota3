# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 22:05:06 2024

@author: limja
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Predefined fields
predefined_fields = {
    "Customer Name": None,
    "Date": None,
    "Quantity": None,
    "Sales": None
}

# Title of the app
st.title("CSV Data Mapper and Sales Visualizer")

# Step 1: Upload CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

# Options for aggregation basis dropdown
aggregation_options = ['Daily', 'Weekly', 'Monthly', 'Quarterly']

if uploaded_file:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:")
    st.write(df.head())

    # Step 2: Manual Mapping
    st.write("### Map Columns to Predefined Fields")
    for field in predefined_fields.keys():
        options = [None] + list(df.columns)
        predefined_fields[field] = st.selectbox(f"Select column for {field}", options)

    # Check if all fields are mapped
    if None not in predefined_fields.values():
        # Step 3: Data Processing and Visualization
        df_mapped = df.rename(columns={
            predefined_fields["Customer Name"]: "Customer Name",
            predefined_fields["Date"]: "Date",
            predefined_fields["Quantity"]: "Quantity",
            predefined_fields["Sales"]: "Sales"
        })

        # Ensure 'Date' column is of datetime type
        df_mapped["Date"] = pd.to_datetime(df_mapped["Date"], errors='coerce')
        df_mapped = df_mapped.dropna(subset=["Date"])

        # Group by date and sum sales
        df_mapped['Date'] = pd.to_datetime(df_mapped['Date'])
        
        # Define aggregation level based on user selection
        aggregation_basis = st.selectbox("Select aggregation basis", aggregation_options)

        if aggregation_basis == 'Daily':
            df_agg = df_mapped.groupby(df_mapped['Date'].dt.date)['Sales', 'Quantity'].sum().reset_index()
            date_label = "Daily"
        elif aggregation_basis == 'Weekly':
            df_agg = df_mapped.resample('W-Mon', on='Date').sum().reset_index()
            date_label = "Weekly"
        elif aggregation_basis == 'Monthly':
            df_agg = df_mapped.resample('M', on='Date').sum().reset_index()
            date_label = "Monthly"
        elif aggregation_basis == 'Quarterly':
            df_agg = df_mapped.resample('Q', on='Date').sum().reset_index()
            date_label = "Quarterly"

        # Convert to numpy arrays for plotting
        dates = df_agg["Date"]
        sales = df_agg["Sales"]
        quantity = df_agg["Quantity"]

        # Plotting Sales over time
        st.write(f"### {date_label} Sales Over Time")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, sales, marker='o', linestyle='-', color='#007acc', linewidth=2, markersize=8, label='Sales')
        ax.set_xlabel("Date", fontsize=14, fontweight='bold')
        ax.set_ylabel("Sales", fontsize=14, fontweight='bold')
        ax.set_title(f"{date_label} Sales Over Time", fontsize=16, fontweight='bold', pad=20)
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(loc='upper left', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # Plotting Quantity over time
        st.write(f"### {date_label} Quantity Sold Over Time")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.plot(dates, quantity, marker='o', linestyle='-', color='#ff7f0e', linewidth=2, markersize=8, label='Quantity')
        ax2.set_xlabel("Date", fontsize=14, fontweight='bold')
        ax2.set_ylabel("Quantity", fontsize=14, fontweight='bold')
        ax2.set_title(f"{date_label} Quantity Sold Over Time", fontsize=16, fontweight='bold', pad=20)
        ax2.tick_params(axis='both', which='major', labelsize=12)
        ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax2.legend(loc='upper left', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)

    else:
        st.write("Please map all fields to proceed.")


#%% 
