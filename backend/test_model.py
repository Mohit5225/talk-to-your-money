# ...existing code...
import sys
import os
import pickle
import pandas as pd
import numpy as np
import tensorflow as tf
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to sys.path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.dataFetcher import DataFetcher
from app.data.stock_config import Config, DataConfig
# ...existing code...

def main():
    print("🔍 Stock Prediction CLI Tool")
    print("--------------------------")
    
    # Load configuration
    config = Config()
    data_config = config.data

    # Paths to model artifacts
    model_path = Path(r"C:\Users\mohit\Desktop\python\FinancialAgent\LJ_Hackathon\backend\models\saved\multi_stock_model.keras")
    feature_scaler_path = Path(r"C:\Users\mohit\Desktop\python\FinancialAgent\LJ_Hackathon\backend\models\saved\multi_stock_feature_scaler.pkl")
    target_scaler_path = Path(r"C:\Users\mohit\Desktop\python\FinancialAgent\LJ_Hackathon\backend\models\saved\multi_stock_target_scaler.pkl")
    
    # Check if files exist
    for file_path, file_desc in [
        (model_path, "Model file"),
        (feature_scaler_path, "Feature scaler"),
        (target_scaler_path, "Target scaler")
    ]:
        if not file_path.exists():
            print(f"❌ Error: {file_desc} not found at {file_path}")
            return
        else:
            print(f"✅ Found {file_desc} at {file_path}")
    
    try:
        # Load model
        print("⏳ Loading model...")
        model = tf.keras.models.load_model(model_path)
        
        # Load scalers
        print("⏳ Loading scalers...")
        with open(feature_scaler_path, "rb") as f:
            feature_scaler = pickle.load(f)
        with open(target_scaler_path, "rb") as f:
            target_scaler = pickle.load(f)
        
        print("✅ Model and scalers loaded successfully")
        
        # Initialize data fetcher
        fetcher = DataFetcher(data_config)
        
        # Get user inputs
        supported_symbols = list(data_config.stock_identifier_mapping.keys())
        print(f"\nSupported stocks: {', '.join(supported_symbols)}")
        
        while True:
            symbol = input("\nEnter stock symbol (e.g. AAPL) or 'q' to quit: ").strip().upper()
            if symbol.lower() == 'q':
                break
                
            if symbol not in data_config.stock_identifier_mapping:
                print(f"❌ Symbol '{symbol}' is not supported. Choose from: {', '.join(supported_symbols)}")
                continue
            
            # Ask for the prediction date (user-specified)
            prediction_date_str = input("Enter the date to predict for (YYYY-MM-DD): ").strip()
            try:
                prediction_date = datetime.strptime(prediction_date_str, "%Y-%m-%d").date()
            except ValueError:
                print("❌ Invalid date format. Use YYYY-MM-DD.")
                continue

            # Determine fetch end: we fetch historical data up to the day BEFORE requested prediction date.
            # (Model expects past sequence; if you want to predict the next trading day, provide that future date.)
            fetch_end_date = prediction_date - timedelta(days=1)
            # fetch start wide enough to cover time_steps plus buffer
            fetch_start_date = fetch_end_date - timedelta(days=120)

            # yfinance 'end' is exclusive, so add one day to include fetch_end_date
            yf_end_param = (fetch_end_date + timedelta(days=1)).strftime('%Y-%m-%d')
            yf_start_param = fetch_start_date.strftime('%Y-%m-%d')

            print(f"⏳ Fetching data for {symbol} from {yf_start_param} to {yf_end_param} (inclusive up to {fetch_end_date})...")
            
            try:
                df = fetcher.fetch_data(symbol, yf_start_param, yf_end_param)
                print(f"✅ Fetched {len(df)} data points")
                
                # Prepare input for model
                if len(df) < data_config.time_steps:
                    print(f"❌ Not enough data points. Need at least {data_config.time_steps}, got {len(df)}")
                    continue
                
                # Select feature columns and handle missing values
                feature_names = data_config.get_active_features
                features_df = df[feature_names].copy()
                features_df = features_df.ffill().bfill()  # Fill NA values
                
                # Scale features
                scaled_features = feature_scaler.transform(features_df.tail(data_config.time_steps))
                
                # Prepare input tensors for model
                price_input = np.expand_dims(scaled_features, axis=0)  # Add batch dimension
                stock_id = data_config.stock_identifier_mapping[symbol]
                stock_input = np.array([[stock_id]])
                
                # Make prediction
                print("🧠 Making prediction...")
                prediction = model.predict({'price_input': price_input, 'stock_input': stock_input}, verbose=0)
                
                # Inverse transform the prediction
                dummy_array = np.zeros((prediction.shape[0], target_scaler.n_features_in_))
                dummy_array[:, :prediction.shape[1]] = prediction
                
                real_prediction = target_scaler.inverse_transform(dummy_array)
                high, low, close = real_prediction[0, 0], real_prediction[0, 1], real_prediction[0, 2]
                
                # Display results
                print("\n📊 PREDICTION RESULTS")
                print("-----------------")
                print(f"Stock: {symbol}")
                print(f"Prediction Date: {prediction_date_str}")
                print(f"Used historical data up to: {fetch_end_date}")
                print(f"Predicted High: ${high:.2f}")
                print(f"Predicted Low: ${low:.2f}")
                print(f"Predicted Close: ${close:.2f}")
                print("-----------------")
                
            except Exception as e:
                print(f"❌ Error during prediction: {str(e)}")
    
    except Exception as e:
        print(f"❌ Error initializing model: {str(e)}")

if __name__ == "__main__":
    main()
# ...existing code...