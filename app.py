import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px




from src.data_processing import load_data, prepare_data


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="European Banking Churn Analytics",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def get_data():
    df = load_data("data/European_Bank.csv")
    return prepare_data(df)


df = get_data()


# =========================================================
# TITLE
# =========================================================

st.title("Customer Segmentation & Churn Pattern Analytics")
st.markdown(
    "### European Banking Customer Churn Dashboard"
)

st.markdown(
    "Use the filters in the sidebar to explore customer churn "
    "across geography, demographics, financial profile, and engagement."
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("Customer Filters")

# Geography
geography_options = sorted(
    df["Geography_Segment"].dropna().unique().tolist()
)

selected_geography = st.sidebar.multiselect(
    "Geography",
    options=geography_options,
    default=geography_options
)


# Age
age_options = [
    "<30",
    "30–45",
    "46–60",
    "60+"
]

selected_age = st.sidebar.multiselect(
    "Age Group",
    options=age_options,
    default=age_options
)


# Gender
gender_options = sorted(
    df["Gender"].dropna().unique().tolist()
)

selected_gender = st.sidebar.multiselect(
    "Gender",
    options=gender_options,
    default=gender_options
)


# Credit Score
credit_options = [
    "Low",
    "Medium",
    "High"
]

selected_credit = st.sidebar.multiselect(
    "Credit Score",
    options=credit_options,
    default=credit_options
)


# Tenure
tenure_options = [
    "New",
    "Mid-term",
    "Long-term"
]

selected_tenure = st.sidebar.multiselect(
    "Tenure",
    options=tenure_options,
    default=tenure_options
)


# Balance
balance_options = [
    "Zero-balance",
    "Low-balance",
    "High-balance"
]

selected_balance = st.sidebar.multiselect(
    "Balance Segment",
    options=balance_options,
    default=balance_options
)


# Activity
activity_options = [
    "Active",
    "Inactive"
]

selected_activity = st.sidebar.multiselect(
    "Activity",
    options=activity_options,
    default=activity_options
)


# Number of products
product_options = sorted(
    df["Product_Group"].unique().tolist(),
    key=lambda x: int(x)
)

selected_products = st.sidebar.multiselect(
    "Number of Products",
    options=product_options,
    default=product_options
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df[
    df["Geography_Segment"].isin(selected_geography)
    & df["Age_Segment"].astype(str).isin(selected_age)
    & df["Gender"].isin(selected_gender)
    & df["CreditScore_Segment"].astype(str).isin(selected_credit)
    & df["Tenure_Segment"].astype(str).isin(selected_tenure)
    & df["Balance_Segment"].isin(selected_balance)
    & df["Activity_Group"].isin(selected_activity)
    & df["Product_Group"].isin(selected_products)
].copy()


# =========================================================
# HANDLE EMPTY FILTER RESULT
# =========================================================

if filtered_df.empty:

    st.warning(
        "No customers match the selected filters. "
        "Please adjust the filters in the sidebar."
    )

    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_customers = len(filtered_df)

churned_customers = int(
    filtered_df["Exited"].sum()
)

retained_customers = (
    total_customers - churned_customers
)

churn_rate = (
    churned_customers
    / total_customers
) * 100


high_value_df = filtered_df[
    filtered_df["High_Value_Flag"] == "High-Value"
]

high_value_customers = len(high_value_df)

high_value_churners = int(
    high_value_df["Exited"].sum()
)

if high_value_customers > 0:

    high_value_churn_rate = (
        high_value_churners
        / high_value_customers
    ) * 100

else:

    high_value_churn_rate = 0


inactive_df = filtered_df[
    filtered_df["Activity_Group"] == "Inactive"
]

active_df = filtered_df[
    filtered_df["Activity_Group"] == "Active"
]


if len(active_df) > 0:

    active_churn_rate = (
        active_df["Exited"].sum()
        / len(active_df)
    ) * 100

else:

    active_churn_rate = 0


if len(inactive_df) > 0:

    inactive_churn_rate = (
        inactive_df["Exited"].sum()
        / len(inactive_df)
    ) * 100

else:

    inactive_churn_rate = 0


engagement_gap = (
    inactive_churn_rate
    - active_churn_rate
)


# =========================================================
# KPI SECTION
# =========================================================

st.subheader("Dashboard KPIs")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Customers",
        f"{total_customers:,}"
    )

with col2:
    st.metric(
        "Churned",
        f"{churned_customers:,}"
    )

with col3:
    st.metric(
        "Churn Rate",
        f"{churn_rate:.2f}%"
    )

with col4:
    st.metric(
        "High-Value Churn",
        f"{high_value_churn_rate:.2f}%"
    )

with col5:
    st.metric(
        "Engagement Gap",
        f"{engagement_gap:.2f} pp"
    )


# =========================================================
# FILTER SUMMARY
# =========================================================

st.markdown("---")

st.subheader("Current Filter Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:

    st.write(
        f"**Customers displayed:** {total_customers:,}"
    )

with summary_col2:

    st.write(
        f"**Retained customers:** {retained_customers:,}"
    )

with summary_col3:

    st.write(
        f"**High-value customers:** {high_value_customers:,}"
    )


# =========================================================
# OVERALL CHURN SUMMARY
# =========================================================

st.markdown("---")

st.subheader("Overall Churn Summary")


summary_df = pd.DataFrame({
    "Customer Status": [
        "Retained",
        "Churned"
    ],
    "Customers": [
        retained_customers,
        churned_customers
    ]
})

summary_df["Percentage"] = (
    summary_df["Customers"]
    / total_customers
) * 100


fig_summary = px.bar(
    summary_df,
    x="Customer Status",
    y="Percentage",
    text="Percentage",
    title="Customer Retention vs Churn"
)

fig_summary.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_summary.update_layout(
    yaxis_title="Percentage (%)",
    xaxis_title="",
    height=450
)

st.plotly_chart(
    fig_summary,
    width="stretch"
)


# =========================================================
# DATA PREVIEW
# =========================================================

st.markdown("---")

st.subheader("Filtered Customer Data")

display_columns = [
    "CustomerId",
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "IsActiveMember",
    "EstimatedSalary",
    "Churn_Status",
    "High_Value_Flag"
]

display_columns = [
    col for col in display_columns
    if col in filtered_df.columns
]

st.dataframe(
    filtered_df[display_columns],
    width="stretch",
    hide_index=True
)


# =========================================================
# GEOGRAPHY-WISE CHURN ANALYSIS
# =========================================================

st.markdown("---")

st.subheader("Geography-wise Churn Analysis")

geo_analysis = (
    filtered_df
    .groupby("Geography_Segment", observed=True)
    .agg(
        Customers=("Exited", "size"),
        Churned_Customers=("Exited", "sum")
    )
    .reset_index()
)

geo_analysis["Retained_Customers"] = (
    geo_analysis["Customers"]
    - geo_analysis["Churned_Customers"]
)

geo_analysis["Churn_Rate_%"] = (
    geo_analysis["Churned_Customers"]
    / geo_analysis["Customers"]
) * 100

geo_analysis["Churn_Rate_%"] = (
    geo_analysis["Churn_Rate_%"].round(2)
)


# ---------------------------------------------------------
# Geography charts
# ---------------------------------------------------------

geo_col1, geo_col2 = st.columns(2)


# Churn Rate
with geo_col1:

    fig_geo_rate = px.bar(
        geo_analysis,
        x="Geography_Segment",
        y="Churn_Rate_%",
        text="Churn_Rate_%",
        title="Churn Rate by Geography"
    )

    fig_geo_rate.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_geo_rate.update_layout(
        xaxis_title="Geography",
        yaxis_title="Churn Rate (%)",
        height=450
    )

    st.plotly_chart(
        fig_geo_rate,
        width="stretch"
    )


# Churned Customers
with geo_col2:

    fig_geo_count = px.bar(
        geo_analysis,
        x="Geography_Segment",
        y="Churned_Customers",
        text="Churned_Customers",
        title="Churned Customers by Geography"
    )

    fig_geo_count.update_traces(
        textposition="outside"
    )

    fig_geo_count.update_layout(
        xaxis_title="Geography",
        yaxis_title="Number of Churned Customers",
        height=450
    )

    st.plotly_chart(
        fig_geo_count,
        width="stretch"
    )


# ---------------------------------------------------------
# Geography summary table
# ---------------------------------------------------------

st.write("### Geography Summary")

st.dataframe(
    geo_analysis,
    width="stretch",
    hide_index=True
)


# =========================================================
# GEOGRAPHIC RISK INDEX
# =========================================================

geo_analysis["Geographic_Risk_Index"] = (
    geo_analysis["Churn_Rate_%"]
    / churn_rate
)

geo_analysis["Geographic_Risk_Index"] = (
    geo_analysis["Geographic_Risk_Index"].round(2)
)

st.write("### Geographic Risk Index")

st.dataframe(
    geo_analysis[
        [
            "Geography_Segment",
            "Customers",
            "Churned_Customers",
            "Churn_Rate_%",
            "Geographic_Risk_Index"
        ]
    ],
    width="stretch",
    hide_index=True
)
# =========================================================
# DATA PREVIEW
# =========================================================
# =========================================================
# AGE-WISE CHURN ANALYSIS
# =========================================================

st.markdown("---")

st.subheader("Age-wise Churn Analysis")

age_analysis = (
    filtered_df
    .groupby("Age_Segment", observed=True)
    .agg(
        Customers=("Exited", "size"),
        Churned_Customers=("Exited", "sum")
    )
    .reset_index()
)

age_analysis["Retained_Customers"] = (
    age_analysis["Customers"]
    - age_analysis["Churned_Customers"]
)

age_analysis["Churn_Rate_%"] = (
    age_analysis["Churned_Customers"]
    / age_analysis["Customers"]
) * 100

age_analysis["Churn_Rate_%"] = (
    age_analysis["Churn_Rate_%"].round(2)
)


# ---------------------------------------------------------
# Age Charts
# ---------------------------------------------------------

age_col1, age_col2 = st.columns(2)


# Age Churn Rate
with age_col1:

    fig_age_rate = px.bar(
        age_analysis,
        x="Age_Segment",
        y="Churn_Rate_%",
        text="Churn_Rate_%",
        title="Churn Rate by Age Group"
    )

    fig_age_rate.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_age_rate.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Churn Rate (%)",
        height=450
    )

    st.plotly_chart(
        fig_age_rate,
        width="stretch"
    )


# Age Churned Customers
with age_col2:

    fig_age_count = px.bar(
        age_analysis,
        x="Age_Segment",
        y="Churned_Customers",
        text="Churned_Customers",
        title="Churned Customers by Age Group"
    )

    fig_age_count.update_traces(
        textposition="outside"
    )

    fig_age_count.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Churned Customers",
        height=450
    )

    st.plotly_chart(
        fig_age_count,
        width="stretch"
    )


# ---------------------------------------------------------
# Age Summary
# ---------------------------------------------------------

st.write("### Age Summary")

st.dataframe(
    age_analysis,
    width="stretch",
    hide_index=True
)

# =========================================================
# TENURE-WISE CHURN ANALYSIS
# =========================================================

st.markdown("---")

st.subheader("Tenure-wise Churn Analysis")

tenure_analysis = (
    filtered_df
    .groupby("Tenure_Segment", observed=True)
    .agg(
        Customers=("Exited", "size"),
        Churned_Customers=("Exited", "sum")
    )
    .reset_index()
)

tenure_analysis["Retained_Customers"] = (
    tenure_analysis["Customers"]
    - tenure_analysis["Churned_Customers"]
)

tenure_analysis["Churn_Rate_%"] = (
    tenure_analysis["Churned_Customers"]
    / tenure_analysis["Customers"]
) * 100

tenure_analysis["Churn_Rate_%"] = (
    tenure_analysis["Churn_Rate_%"].round(2)
)


# ---------------------------------------------------------
# Tenure Charts
# ---------------------------------------------------------

tenure_col1, tenure_col2 = st.columns(2)


# Tenure Churn Rate
with tenure_col1:

    fig_tenure_rate = px.bar(
        tenure_analysis,
        x="Tenure_Segment",
        y="Churn_Rate_%",
        text="Churn_Rate_%",
        title="Churn Rate by Tenure Group"
    )

    fig_tenure_rate.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_tenure_rate.update_layout(
        xaxis_title="Tenure Group",
        yaxis_title="Churn Rate (%)",
        height=450
    )

    st.plotly_chart(
        fig_tenure_rate,
        width="stretch"
    )


# Tenure Churned Customers
with tenure_col2:

    fig_tenure_count = px.bar(
        tenure_analysis,
        x="Tenure_Segment",
        y="Churned_Customers",
        text="Churned_Customers",
        title="Churned Customers by Tenure Group"
    )

    fig_tenure_count.update_traces(
        textposition="outside"
    )

    fig_tenure_count.update_layout(
        xaxis_title="Tenure Group",
        yaxis_title="Churned Customers",
        height=450
    )

    st.plotly_chart(
        fig_tenure_count,
        width="stretch"
    )


# ---------------------------------------------------------
# Tenure Summary
# ---------------------------------------------------------

st.write("### Tenure Summary")

st.dataframe(
    tenure_analysis,
    width="stretch",
    hide_index=True
)

# =========================================================
# AGE × TENURE CHURN ANALYSIS
# =========================================================

st.markdown("---")

st.subheader("Age × Tenure Churn Analysis")

age_tenure_analysis = (
    filtered_df
    .groupby(
        ["Age_Segment", "Tenure_Segment"],
        observed=True
    )
    .agg(
        Customers=("Exited", "size"),
        Churned_Customers=("Exited", "sum")
    )
    .reset_index()
)

age_tenure_analysis["Churn_Rate_%"] = (
    age_tenure_analysis["Churned_Customers"]
    / age_tenure_analysis["Customers"]
) * 100

age_tenure_analysis["Churn_Rate_%"] = (
    age_tenure_analysis["Churn_Rate_%"].round(2)
)


# ---------------------------------------------------------
# Age × Tenure Matrix
# ---------------------------------------------------------

age_tenure_matrix = (
    age_tenure_analysis
    .pivot(
        index="Age_Segment",
        columns="Tenure_Segment",
        values="Churn_Rate_%"
    )
)

st.write("### Age × Tenure Churn Rate")

st.dataframe(
    age_tenure_matrix,
    width="stretch"
)
# ---------------------------------------------------------
# Age × Tenure Heatmap
# ---------------------------------------------------------

fig_age_tenure = px.imshow(
    age_tenure_matrix,
    text_auto=".2f",
    aspect="auto",
    title="Churn Rate by Age and Tenure"
)

fig_age_tenure.update_layout(
    xaxis_title="Tenure Group",
    yaxis_title="Age Group",
    height=500
)

st.plotly_chart(
    fig_age_tenure,
    width="stretch"
)
# =========================================================
# AGE vs TENURE COMPARISON
# =========================================================

st.markdown("---")

st.subheader("Age vs Tenure Churn Comparison")

comparison_col1, comparison_col2 = st.columns(2)


with comparison_col1:

    fig_age_compare = px.line(
        age_analysis,
        x="Age_Segment",
        y="Churn_Rate_%",
        markers=True,
        title="Age Group Churn Trend"
    )

    fig_age_compare.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Churn Rate (%)",
        height=400
    )

    st.plotly_chart(
        fig_age_compare,
        width="stretch"
    )


with comparison_col2:

    fig_tenure_compare = px.line(
        tenure_analysis,
        x="Tenure_Segment",
        y="Churn_Rate_%",
        markers=True,
        title="Tenure Group Churn Trend"
    )

    fig_tenure_compare.update_layout(
        xaxis_title="Tenure Group",
        yaxis_title="Churn Rate (%)",
        height=400
    )

    st.plotly_chart(
        fig_tenure_compare,
        width="stretch"
    )
    # =========================================================
# DATA PREVIEW
# =========================================================

# =========================================================
# PHASE 5: HIGH-VALUE CUSTOMER CHURN EXPLORER
# =========================================================

st.markdown("---")

st.header("High-Value Customer Churn Explorer")

st.info(
    "High-Value customers are defined as customers in the "
    "High-balance segment. This is used as a financial-value "
    "proxy because the dataset does not contain direct revenue "
    "or profitability measures."
)


# =========================================================
# HIGH-VALUE CUSTOMER DATA
# =========================================================

high_value_df = filtered_df[
    filtered_df["High_Value_Flag"] == "High-Value"
].copy()

non_high_value_df = filtered_df[
    filtered_df["High_Value_Flag"] == "Non-High-Value"
].copy()


# =========================================================
# HIGH-VALUE KPI CALCULATIONS
# =========================================================

hv_customers = len(high_value_df)

hv_churners = int(
    high_value_df["Exited"].sum()
)

hv_retained = (
    hv_customers - hv_churners
)

if hv_customers > 0:

    hv_churn_rate = (
        hv_churners / hv_customers
    ) * 100

    hv_total_balance = (
        high_value_df["Balance"].sum()
    )

    hv_churned_balance = (
        high_value_df.loc[
            high_value_df["Exited"] == 1,
            "Balance"
        ].sum()
    )

    if hv_total_balance > 0:

        hv_balance_exposure = (
            hv_churned_balance
            / hv_total_balance
        ) * 100

    else:

        hv_balance_exposure = 0

else:

    hv_churn_rate = 0
    hv_total_balance = 0
    hv_churned_balance = 0
    hv_balance_exposure = 0


# =========================================================
# HIGH-VALUE KPI CARDS
# =========================================================

st.subheader("High-Value Customer KPIs")

hv_col1, hv_col2, hv_col3, hv_col4, hv_col5 = st.columns(5)


with hv_col1:

    st.metric(
        "High-Value Customers",
        f"{hv_customers:,}"
    )


with hv_col2:

    st.metric(
        "High-Value Churners",
        f"{hv_churners:,}"
    )


with hv_col3:

    st.metric(
        "High-Value Churn Rate",
        f"{hv_churn_rate:.2f}%"
    )


with hv_col4:

    st.metric(
        "High-Value Balance",
        f"{hv_total_balance:,.0f}"
    )


with hv_col5:

    st.metric(
        "Balance Exposure",
        f"{hv_balance_exposure:.2f}%"
    )


# =========================================================
# HIGH-VALUE VS NON-HIGH-VALUE COMPARISON
# =========================================================

st.markdown("---")

st.subheader("High-Value vs Non-High-Value Churn")

comparison_data = pd.DataFrame({
    "Customer Group": [
        "High-Value",
        "Non-High-Value"
    ],
    "Customers": [
        hv_customers,
        len(non_high_value_df)
    ],
    "Churned Customers": [
        hv_churners,
        int(non_high_value_df["Exited"].sum())
    ]
})

comparison_data["Churn Rate (%)"] = (
    comparison_data["Churned Customers"]
    / comparison_data["Customers"].replace(0, np.nan)
) * 100

comparison_data["Churn Rate (%)"] = (
    comparison_data["Churn Rate (%)"].fillna(0).round(2)
)


fig_hv_compare = px.bar(
    comparison_data,
    x="Customer Group",
    y="Churn Rate (%)",
    text="Churn Rate (%)",
    title="High-Value vs Non-High-Value Churn Rate"
)

fig_hv_compare.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig_hv_compare.update_layout(
    xaxis_title="",
    yaxis_title="Churn Rate (%)",
    height=450
)

st.plotly_chart(
    fig_hv_compare,
    width="stretch"
)


# =========================================================
# HIGH-VALUE CHURN BY GEOGRAPHY
# =========================================================

st.markdown("---")

st.subheader("High-Value Churn by Geography")

if not high_value_df.empty:

    hv_geo = (
        high_value_df
        .groupby("Geography_Segment", observed=True)
        .agg(
            Customers=("Exited", "size"),
            Churned_Customers=("Exited", "sum"),
            Total_Balance=("Balance", "sum")
        )
        .reset_index()
    )

    hv_geo["Retained_Customers"] = (
        hv_geo["Customers"]
        - hv_geo["Churned_Customers"]
    )

    hv_geo["Churn_Rate_%"] = (
        hv_geo["Churned_Customers"]
        / hv_geo["Customers"]
    ) * 100

    hv_geo["Churn_Rate_%"] = (
        hv_geo["Churn_Rate_%"].round(2)
    )

    geo_col1, geo_col2 = st.columns(2)


    # -------------------------------
    # Geography churn rate
    # -------------------------------

    with geo_col1:

        fig_hv_geo = px.bar(
            hv_geo,
            x="Geography_Segment",
            y="Churn_Rate_%",
            text="Churn_Rate_%",
            title="High-Value Churn Rate by Geography"
        )

        fig_hv_geo.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig_hv_geo.update_layout(
            xaxis_title="Geography",
            yaxis_title="Churn Rate (%)",
            height=450
        )

        st.plotly_chart(
            fig_hv_geo,
            width="stretch"
        )


    # -------------------------------
    # Geography churned customers
    # -------------------------------

    with geo_col2:

        fig_hv_geo_count = px.bar(
            hv_geo,
            x="Geography_Segment",
            y="Churned_Customers",
            text="Churned_Customers",
            title="High-Value Churned Customers by Geography"
        )

        fig_hv_geo_count.update_traces(
            textposition="outside"
        )

        fig_hv_geo_count.update_layout(
            xaxis_title="Geography",
            yaxis_title="Churned Customers",
            height=450
        )

        st.plotly_chart(
            fig_hv_geo_count,
            width="stretch"
        )


    st.dataframe(
        hv_geo,
        width="stretch",
        hide_index=True
    )

else:

    st.warning(
        "No high-value customers match the current filters."
    )


# =========================================================
# HIGH-VALUE CHURN BY AGE
# =========================================================

st.markdown("---")

st.subheader("High-Value Churn by Age")

if not high_value_df.empty:

    hv_age = (
        high_value_df
        .groupby("Age_Segment", observed=True)
        .agg(
            Customers=("Exited", "size"),
            Churned_Customers=("Exited", "sum")
        )
        .reset_index()
    )

    hv_age["Retained_Customers"] = (
        hv_age["Customers"]
        - hv_age["Churned_Customers"]
    )

    hv_age["Churn_Rate_%"] = (
        hv_age["Churned_Customers"]
        / hv_age["Customers"]
    ) * 100

    hv_age["Churn_Rate_%"] = (
        hv_age["Churn_Rate_%"].round(2)
    )


    fig_hv_age = px.bar(
        hv_age,
        x="Age_Segment",
        y="Churn_Rate_%",
        text="Churn_Rate_%",
        title="High-Value Customer Churn Rate by Age"
    )

    fig_hv_age.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_hv_age.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Churn Rate (%)",
        height=450
    )

    st.plotly_chart(
        fig_hv_age,
        width="stretch"
    )


    st.dataframe(
        hv_age,
        width="stretch",
        hide_index=True
    )


# =========================================================
# HIGH-VALUE CHURN BY ACTIVITY
# =========================================================

st.markdown("---")

st.subheader("High-Value Customer Churn by Activity")

if not high_value_df.empty:

    hv_activity = (
        high_value_df
        .groupby("Activity_Group")
        .agg(
            Customers=("Exited", "size"),
            Churned_Customers=("Exited", "sum")
        )
        .reset_index()
    )

    hv_activity["Churn_Rate_%"] = (
        hv_activity["Churned_Customers"]
        / hv_activity["Customers"]
    ) * 100

    hv_activity["Churn_Rate_%"] = (
        hv_activity["Churn_Rate_%"].round(2)
    )


    fig_hv_activity = px.bar(
        hv_activity,
        x="Activity_Group",
        y="Churn_Rate_%",
        text="Churn_Rate_%",
        title="High-Value Churn Rate by Activity Status"
    )

    fig_hv_activity.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_hv_activity.update_layout(
        xaxis_title="Activity Status",
        yaxis_title="Churn Rate (%)",
        height=450
    )

    st.plotly_chart(
        fig_hv_activity,
        width="stretch"
    )

    st.dataframe(
        hv_activity,
        width="stretch",
        hide_index=True
    )


# =========================================================
# HIGH-VALUE CHURN BY NUMBER OF PRODUCTS
# =========================================================

st.markdown("---")

st.subheader("High-Value Customer Churn by Products")

if not high_value_df.empty:

    hv_products = (
        high_value_df
        .groupby("NumOfProducts")
        .agg(
            Customers=("Exited", "size"),
            Churned_Customers=("Exited", "sum")
        )
        .reset_index()
    )

    hv_products["Churn_Rate_%"] = (
        hv_products["Churned_Customers"]
        / hv_products["Customers"]
    ) * 100

    hv_products["Churn_Rate_%"] = (
        hv_products["Churn_Rate_%"].round(2)
    )


    fig_hv_products = px.bar(
        hv_products,
        x="NumOfProducts",
        y="Churn_Rate_%",
        text="Churn_Rate_%",
        title="High-Value Churn Rate by Number of Products"
    )

    fig_hv_products.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_hv_products.update_layout(
        xaxis_title="Number of Products",
        yaxis_title="Churn Rate (%)",
        height=450
    )

    st.plotly_chart(
        fig_hv_products,
        width="stretch"
    )

    st.dataframe(
        hv_products,
        width="stretch",
        hide_index=True
    )


# =========================================================
# HIGH-VALUE FINANCIAL EXPOSURE
# =========================================================

st.markdown("---")

st.subheader("High-Value Financial Exposure")

exposure_col1, exposure_col2 = st.columns(2)


with exposure_col1:

    st.metric(
        "Total High-Value Balance",
        f"{hv_total_balance:,.2f}"
    )


with exposure_col2:

    st.metric(
        "Balance Associated with Churned Customers",
        f"{hv_churned_balance:,.2f}"
    )


st.write(
    f"**High-Value Balance Exposure:** "
    f"{hv_balance_exposure:.2f}%"
)


# ---------------------------------------------------------
# Balance exposure chart
# ---------------------------------------------------------

exposure_chart = pd.DataFrame({
    "Balance Status": [
        "Retained High-Value",
        "Churned High-Value"
    ],
    "Balance": [
        hv_total_balance - hv_churned_balance,
        hv_churned_balance
    ]
})

fig_exposure = px.bar(
    exposure_chart,
    x="Balance Status",
    y="Balance",
    text="Balance",
    title="High-Value Balance Exposure by Customer Status"
)

fig_exposure.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

fig_exposure.update_layout(
    xaxis_title="Customer Status",
    yaxis_title="Account Balance",
    height=450
)

st.plotly_chart(
    fig_exposure,
    width="stretch"
)


# =========================================================
# HIGH-VALUE GEOGRAPHY × AGE
# =========================================================

st.markdown("---")

st.subheader("High-Value Geography × Age Analysis")

if not high_value_df.empty:

    hv_geo_age = (
        high_value_df
        .groupby(
            ["Geography_Segment", "Age_Segment"],
            observed=True
        )
        .agg(
            Customers=("Exited", "size"),
            Churned_Customers=("Exited", "sum")
        )
        .reset_index()
    )

    hv_geo_age["Churn_Rate_%"] = (
        hv_geo_age["Churned_Customers"]
        / hv_geo_age["Customers"]
    ) * 100

    hv_geo_age["Churn_Rate_%"] = (
        hv_geo_age["Churn_Rate_%"].round(2)
    )


    hv_geo_age_matrix = (
        hv_geo_age
        .pivot(
            index="Geography_Segment",
            columns="Age_Segment",
            values="Churn_Rate_%"
        )
    )


    fig_hv_geo_age = px.imshow(
        hv_geo_age_matrix,
        text_auto=".2f",
        aspect="auto",
        title="High-Value Churn Rate by Geography × Age"
    )

    fig_hv_geo_age.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Geography",
        height=500
    )

    st.plotly_chart(
        fig_hv_geo_age,
        width="stretch"
    )


    st.dataframe(
        hv_geo_age,
        width="stretch",
        hide_index=True
    )


# =========================================================
# PRIORITY HIGH-VALUE SEGMENT
# =========================================================

st.markdown("---")

st.subheader("Priority High-Value Segment")

if not high_value_df.empty:

    priority_segment = (
        hv_geo_age
        .sort_values(
            "Churn_Rate_%",
            ascending=False
        )
        .head(1)
    )

    priority_row = priority_segment.iloc[0]

    st.metric(
        "Highest Observed High-Value Segment",
        f"{priority_row['Geography_Segment']} + "
        f"{priority_row['Age_Segment']}"
    )

    st.metric(
        "Segment Churn Rate",
        f"{priority_row['Churn_Rate_%']:.2f}%"
    )

    st.write(
        f"Customers in this filtered segment: "
        f"{int(priority_row['Customers']):,}"
    )

    st.write(
        f"Churned customers in this filtered segment: "
        f"{int(priority_row['Churned_Customers']):,}"
    )


# =========================================================
# HIGH-VALUE CUSTOMER DRILL-DOWN
# =========================================================

st.markdown("---")

st.subheader("High-Value Customer Drill-Down")

if not high_value_df.empty:

    drill_columns = [
        "CustomerId",
        "CreditScore",
        "Geography",
        "Gender",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
        "Churn_Status",
        "High_Value_Flag",
        "Activity_Group"
    ]

    drill_columns = [
        col for col in drill_columns
        if col in high_value_df.columns
    ]

    drill_df = high_value_df[
        drill_columns
    ].copy()

    st.write(
        f"Showing {len(drill_df):,} high-value customers "
        "matching the selected filters."
    )

    st.dataframe(
        drill_df,
        width="stretch",
        hide_index=True
    )


    # -----------------------------------------------------
    # Download button
    # -----------------------------------------------------

    csv_data = drill_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download High-Value Customer Data",
        data=csv_data,
        file_name="high_value_customer_analysis.csv",
        mime="text/csv"
    )

else:

    st.warning(
        "No high-value customers match the current filters."
    )