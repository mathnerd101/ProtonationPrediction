import pandas as pd
from autogluon.tabular import TabularPredictor

# Your input DataFrame (uncomment and adjust if needed)
# df = pd.read_csv("your_data.csv")

# List of model folder names (relative to current working directory)
model_names = [
    "NeuralNetTorch_r79_BAG_L1",
    "NeuralNetTorch_BAG_L1",
    "XGBoost_r33_BAG_L1",
    "CatBoost_BAG_L1",
    "WeightedEnsemble_L2"
]

# Dictionary to store predictions from each model
predictions = {}

# Predict using each individual model folder
for model_name in model_names:
    predictor = TabularPredictor.load(model_name)
    raw_preds = predictor.predict(df)
    binary_preds = (raw_preds == 1).astype(int)  # Adjust if positive class is not 1
    predictions[model_name] = binary_preds

# Combine all model predictions into a DataFrame
preds_df = pd.DataFrame(predictions)

# Compute the Probability = number of positive votes / total models
preds_df["Probability"] = preds_df.sum(axis=1) / len(model_names)

# Final majority vote prediction (1 if ≥ 3 of 5 predict positive)
preds_df["Prediction"] = (preds_df.sum(axis=1) >= 3).astype(int)

# Add ID column starting from 1
preds_df["ID"] = range(1, len(df) + 1)

# Reorder columns
final_df = preds_df[["ID"] + model_names + ["Probability", "Prediction"]]

# Save to CSV
print(final_df)
counts_per_row = preds_df[model_names].sum(axis=1)

plt.figure(figsize=(10, 6))
plt.bar(range(1, len(df) + 1), counts_per_row)
plt.xlabel("Row Number (1 to n)")
plt.ylabel("Number of Models Predicting TRUE")
plt.title("Number of Models Predicting TRUE per Row")
plt.tight_layout()
plt.savefig("histogram.png")  # Save plot if needed
plt.show()
