import pandas as pd
from autogluon.tabular import TabularPredictor

# Load the processed data
df = pd.read_csv("data.csv")

# List of model folder names
model_names = [
    "NeuralNetTorch_r79_BAG_L1",
    "NeuralNetTorch_BAG_L1", 
    "XGBoost_r33_BAG_L1",
    "CatBoost_BAG_L1",
    "WeightedEnsemble_L2"
]

# Dictionary to store predictions
predictions = {}

# Predict using each model
for model_name in model_names:
    try:
        predictor = TabularPredictor.load(model_name)
        raw_preds = predictor.predict(df)
        binary_preds = (raw_preds == 1).astype(int)
        predictions[model_name] = binary_preds
    except Exception as e:
        print(f"Error loading model {model_name}: {e}")
        # Fill with zeros if model fails
        predictions[model_name] = [0] * len(df)

# Combine all model predictions
preds_df = pd.DataFrame(predictions)

# Compute probability
preds_df["Probability"] = preds_df.sum(axis=1) / len(model_names)

# Final majority vote prediction
preds_df["Prediction"] = (preds_df.sum(axis=1) >= 3).astype(int)

# Add ID column
preds_df["ID"] = range(1, len(df) + 1)

# Reorder columns
final_df = preds_df[["ID"] + model_names + ["Probability", "Prediction"]]

# Save to CSV
final_df.to_csv("predictions.csv", index=False)
print(final_df.to_string())
print("Predictions saved to predictions.csv")


