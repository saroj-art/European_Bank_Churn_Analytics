import pandas as pd
import numpy as np


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load the European banking customer dataset.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Dataset not found at: {file_path}"
        )

    return df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw dataset and recreate the same
    segmentation logic used in the analysis notebook.
    """

    df = df.copy()

    # -------------------------------------------------
    # 1. Remove non-analytical columns
    # -------------------------------------------------
    # CustomerId is retained because it can be useful
    # in the dashboard drill-down table.
    #
    # Surname is removed as required by the analysis.
    # Year is removed because it contains only 2025.
    # -------------------------------------------------

    df = df.drop(
        columns=["Surname", "Year"],
        errors="ignore"
    )

    # -------------------------------------------------
    # 2. Geography Segment
    # -------------------------------------------------

    df["Geography_Segment"] = df["Geography"]

    # -------------------------------------------------
    # 3. Age Segment
    # -------------------------------------------------

    df["Age_Segment"] = pd.cut(
        df["Age"],
        bins=[0, 29, 45, 60, np.inf],
        labels=["<30", "30–45", "46–60", "60+"],
        right=True
    )

    # -------------------------------------------------
    # 4. Credit Score Segment
    # -------------------------------------------------

    df["CreditScore_Segment"] = pd.cut(
        df["CreditScore"],
        bins=[-np.inf, 599, 699, np.inf],
        labels=["Low", "Medium", "High"]
    )

    # -------------------------------------------------
    # 5. Tenure Segment
    # -------------------------------------------------

    df["Tenure_Segment"] = pd.cut(
        df["Tenure"],
        bins=[-1, 3, 6, 10],
        labels=["New", "Mid-term", "Long-term"]
    )

    # -------------------------------------------------
    # 6. Balance Segment
    # -------------------------------------------------

    positive_balance_median = df.loc[
        df["Balance"] > 0,
        "Balance"
    ].median()

    df["Balance_Segment"] = np.select(
        [
            df["Balance"] == 0,

            (
                (df["Balance"] > 0) &
                (df["Balance"] <= positive_balance_median)
            ),

            df["Balance"] > positive_balance_median
        ],
        [
            "Zero-balance",
            "Low-balance",
            "High-balance"
        ],
        default="Unassigned"
    )

    # -------------------------------------------------
    # 7. High-Value Customer Proxy
    # -------------------------------------------------

    df["High_Value_Flag"] = np.where(
        df["Balance_Segment"] == "High-balance",
        "High-Value",
        "Non-High-Value"
    )

    # -------------------------------------------------
    # 8. Customer Activity
    # -------------------------------------------------

    df["Activity_Group"] = df["IsActiveMember"].map({
        0: "Inactive",
        1: "Active"
    })

    # -------------------------------------------------
    # 9. Product Group
    # -------------------------------------------------

    df["Product_Group"] = df["NumOfProducts"].astype(str)

    # -------------------------------------------------
    # 10. Churn Status
    # -------------------------------------------------

    df["Churn_Status"] = df["Exited"].map({
        0: "Retained",
        1: "Churned"
    })

    return df