import pandas as pd
from autogluon.tabular import TabularPredictor


model_names = [
    "NeuralNetTorch_r79_BAG_L1",
    "NeuralNetTorch_BAG_L1",
    "XGBoost_r33_BAG_L1",
    "CatBoost_BAG_L1",
    "WeightedEnsemble_L2"
]


model_preds = {}


for model in model_names:
    predictor = TabularPredictor.load(model)
    preds = predictor.predict(df, model=model)
    preds_binary = (preds == True).astype(int)
    model_preds[model] = preds_binary

# Create a DataFrame from the predictions
preds_df = pd.DataFrame(model_preds)

preds_df["Probability"] = preds_df.sum(axis=1) / len(model_names)

preds_df["Prediction"] = (preds_df.sum(axis=1) >= 3).astype(int)

preds_df["ID"] = range(1, len(df) + 1)

preds_df = preds_df[["ID"] + model_names + ["Probability", "Prediction"]]

preds_df.to_csv("predictions.csv", index=False)


