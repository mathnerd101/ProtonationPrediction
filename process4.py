import pandas as pd
import os
import sys

try:
    from autogluon.tabular import TabularPredictor
except ImportError:
    print("Error: AutoGluon not installed. Please install with: pip install autogluon")
    sys.exit(1)

def make_prediction():
    """Run model prediction on processed features"""
    try:
        # Check if the processed features file exists
        if not os.path.exists('processed_features.csv'):
            print("Error: processed_features.csv not found. Please run process3.py first.")
            return None
        
        # Load the processed features
        df = pd.read_csv('processed_features.csv')
        print(f"Loaded {len(df)} rows for prediction")
        
        # Load the trained model
        if not os.path.exists('models'):
            print("Error: models directory not found")
            return None
            
        predictor = TabularPredictor.load('models')
        print("Model loaded successfully")
        
        # Define model names to use
        model_names = [
            "NeuralNetTorch_r79_BAG_L1",
            "NeuralNetTorch_BAG_L1", 
            "XGBoost_r33_BAG_L1",
            "CatBoost_BAG_L1",
            "WeightedEnsemble_L2"
        ]
        
        # Get available models from the predictor
        available_models = predictor.model_names()
        print(f"Available models: {available_models}")
        
        # Filter model names to only include available ones
        valid_models = [model for model in model_names if model in available_models]
        
        if not valid_models:
            # If no specific models found, use all available models
            valid_models = available_models
            print(f"Using all available models: {valid_models}")
        else:
            print(f"Using specified models: {valid_models}")
        
        # Make predictions with each model
        model_preds = {}
        for model in valid_models:
            try:
                preds = predictor.predict(df, model=model)
                # Convert predictions to binary (assuming boolean predictions)
                preds_binary = (preds == True).astype(int)
                model_preds[model] = preds_binary
                print(f"Predictions from {model}: {sum(preds_binary)} positive out of {len(preds_binary)}")
            except Exception as e:
                print(f"Warning: Could not get predictions from {model}: {e}")
                continue
        
        if not model_preds:
            print("Error: No valid predictions obtained from any model")
            return None
        
        # Create a DataFrame from the predictions
        preds_df = pd.DataFrame(model_preds)
        
        # Calculate ensemble predictions
        preds_df["Probability"] = preds_df.sum(axis=1) / len(preds_df.columns)
        
        # Use majority voting for final prediction (>=50% of models predict positive)
        threshold = len(preds_df.columns) / 2
        preds_df["Prediction"] = (preds_df.sum(axis=1) >= threshold).astype(int)
        
        # Add sequence position ID
        preds_df["ID"] = range(1, len(df) + 1)
        
        # Reorder columns
        column_order = ["ID"] + list(model_preds.keys()) + ["Probability", "Prediction"]
        preds_df = preds_df[column_order]
        
        # Save predictions to CSV
        preds_df.to_csv("predictions.csv", index=False)
        
        # Print summary
        total_positions = len(preds_df)
        positive_predictions = sum(preds_df["Prediction"])
        avg_probability = preds_df["Probability"].mean()
        
        summary = f"""Prediction Summary:
Total positions analyzed: {total_positions}
Positions predicted as protonated: {positive_predictions} ({positive_predictions/total_positions*100:.1f}%)
Average probability: {avg_probability:.3f}
Results saved to predictions.csv"""
        
        print(summary)
        return summary
        
    except Exception as e:
        error_msg = f"Error in prediction: {str(e)}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    result = make_prediction()
    if result:
        print("\nPrediction completed successfully!")
    else:
        print("\nPrediction failed!")
        sys.exit(1)
