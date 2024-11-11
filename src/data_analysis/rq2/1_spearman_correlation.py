import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr


def calculate_spearman_correlation(data, target_column="severity"):
    """
    Calculate Spearman correlation between the target column and all other numerical columns.

    Parameters:
    - data (pd.DataFrame): The input data containing numerical metrics.
    - target_column (str): The name of the target column to correlate with. Default is 'severity'.

    Returns:
    - pd.DataFrame: A DataFrame containing columns 'Metric', 'Spearman Correlation', and 'p-value',
                    sorted by the absolute value of the correlation in descending order.
    """
    if target_column not in data.columns:
        raise ValueError(f"Target column '{target_column}' not found in the data.")

    # Select numerical columns excluding the target column
    numerical_cols = data.select_dtypes(include=["number"]).columns.tolist()
    numerical_cols = [col for col in numerical_cols if col != target_column]

    if not numerical_cols:
        raise ValueError(
            "No numerical columns found to correlate with the target column."
        )

    correlations = []

    for col in numerical_cols:
        # Drop rows with NaN values in either the target or the current column
        valid_data = data[[target_column, col]].dropna()

        if valid_data.empty:
            corr, p_value = (None, None)
        else:
            corr, p_value = spearmanr(valid_data[target_column], valid_data[col])

        correlations.append(
            {"Metric": col, "Spearman Correlation": corr, "p-value": p_value}
        )

    # Create a DataFrame from the correlations list
    corr_df = pd.DataFrame(correlations)

    # Drop rows where correlation could not be computed
    corr_df = corr_df.dropna(subset=["Spearman Correlation"])

    # Sort by absolute correlation value in descending order
    corr_df["abs_correlation"] = corr_df["Spearman Correlation"].abs()
    corr_df = corr_df.sort_values(by="abs_correlation", ascending=False).drop(
        columns=["abs_correlation"]
    )

    return corr_df.reset_index(drop=True)


# Load the enriched data
df = pd.read_csv("data/rq2_8_enriched.csv")

# Calculate Spearman correlations
spearman_corr = calculate_spearman_correlation(df, target_column="severity")

print(spearman_corr)

# Calculate correlation matrix for all numerical columns
numerical_df = df.select_dtypes(include=["number"])
correlation_matrix = numerical_df.corr(method="spearman")

# Create a heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", center=0, fmt=".2f")
plt.title("Spearman Correlation Matrix")
plt.tight_layout()
plt.savefig("data/rq2_correlation_matrix.png")
plt.close()
