# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 22:05:06 2024

@author: limja
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define aggregation options
aggregation_options = ['Weekly', 'Monthly', 'Quarterly', 'Yearly']

# CSS styling (unchanged)
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
    </style>
""", unsafe_allow_html=True)

# Predefined fields and title (unchanged)
predefined_fields = {
    "Customer Name": None,
    "Date": None,
    "Quantity": None,
    "Sales": None
}

st.title("Understand Your Business Data")

# Notification message about required and optional fields (unchanged)
st.markdown("""
<div class="info-box">
**Before uploading your CSV file, please ensure it contains the following columns:**
- **Customer Name** (Required)
- **Date** (Required)
- **Sales** (Required)
- **Quantity** (Optional)
</div>
""", unsafe_allow_html=True)

# File handling logic (unchanged)
file_option = st.radio("Choose data source:", ('Upload CSV file', 'Use Sample CSV - Alteryx Data'))

if file_option == 'Upload CSV file':
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
else:
    sample_file_path = "Data/SampleInput.csv"
    df = pd.read_csv(sample_file_path)

# Continue processing if dataframe is loaded (unchanged)
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
        
        # Data Processing (unchanged)
        df_mapped = df.rename(columns={
            predefined_fields["Customer Name"]: "Customer Name",
            predefined_fields["Date"]: "Date",
            predefined_fields["Quantity"]: "Quantity" if predefined_fields["Quantity"] else "Ignore",
            predefined_fields["Sales"]: "Sales"
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

            # Visualization (unchanged)
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

            if "Quantity" in df_agg.columns:
                quantity = df_agg["Quantity"]
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

            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

            # Top Customers by Sales
            st.write("### Top Customers by Sales")
            top_options = [5, 10, 20, 30]
            top_n = st.selectbox("Select number of top customers to display", top_options, index=1, key="top_customers")
            top_customers = df_filtered.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(top_n).reset_index()
            st.write(f"Top {top_n} Customers:")
            st.table(top_customers)

    else:
        st.write("Please map 'Customer Name', 'Date', and 'Sales' fields to proceed.")




#%% 
