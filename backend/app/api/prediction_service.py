# api/prediction_service.py
import pickle
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd
import tensorflow as tf

from app.data.dataFetcher import DataFetcher
from app.data.stock_config import Config

class PredictionService:
    def __init__(self, model_path: Path, feature_scaler_path: Path, target_scaler_path: Path):
        """
        Loads the trained model and scalers into memory ONCE.
        """
        self.model = tf.keras.models.load_model(model_path)
        with open(feature_scaler_path, "rb") as f:
            self.feature_scaler = pickle.load(f)
        with open(target_scaler_path, "rb") as f:
            self.target_scaler = pickle.load(f)
        
        self.config = Config()
        self.fetcher = DataFetcher(self.config.data)
        print("✅ PredictionService initialized. Model and scalers are loaded.")

    def _prepare_inference_data(self, symbol: str, target_ts: pd.Timestamp) -> dict:
        """
        Fetches the LATEST data needed for a single prediction.
        """
        normalized_target = target_ts.normalize()

        # Fetch the last ~120 days to ensure enough data for a 30-day sequence after cleaning
        fetch_end_date = (normalized_target + pd.DateOffset(days=1)).strftime('%Y-%m-%d')
        start_date = (normalized_target - pd.DateOffset(days=120)).strftime('%Y-%m-%d')
        
        df = self.fetcher.fetch_data(symbol, start_date, fetch_end_date)
        df = df.dropna()
        
        # We only need the last `time_steps` worth of data
        if len(df) < self.config.data.time_steps:
            raise ValueError(f"Not enough recent data for {symbol} to make a prediction.")
        
        # Get feature names and slice the dataframe
        feature_names = self.config.data.get_active_features
        features_df = df[feature_names].tail(self.config.data.time_steps)
        
        # IMPORTANT: Use the LOADED scaler to TRANSFORM the new data
        scaled_features = self.feature_scaler.transform(features_df)
        
        # The model expects a batch dimension, so add one
        price_input = np.expand_dims(scaled_features, axis=0)
        
        # Get the stock ID for the embedding layer
        stock_id = self.config.data.stock_identifier_mapping[symbol]
        stock_input = np.array([[stock_id]])
        
        return {
            'price_input': price_input,
            'stock_input': stock_input
        }

    def predict(
        self,
        symbol: str,
        target_date: Union[str, pd.Timestamp, None] = None,
    ) -> Tuple[np.ndarray, str]:
        """
        The main prediction function.
        
        Args:
            symbol: Stock symbol to predict
            target_date: Optional date for prediction. If None or empty, uses current date.
            
        Returns:
            Tuple of (prediction_array, used_date_string)
        """
        if target_date is None or target_date == "":
            target_ts = pd.Timestamp.now()
        else:
            target_ts = pd.Timestamp(target_date)

        # Always work with timezone-naive date for downstream consumers
        target_ts = target_ts.tz_localize(None).normalize()
        target_date_iso = target_ts.strftime('%Y-%m-%d')

        # 1. Get and prepare the latest data
        inference_data = self._prepare_inference_data(symbol, target_ts)
        
        # 2. Make a prediction using the loaded model
        scaled_prediction = self.model.predict(inference_data)
        
        # 3. Inverse transform the prediction to get real values
        # The scaler expects the same number of features as during training,
        # so we create a dummy array and place our prediction in it.
        dummy_array = np.zeros((scaled_prediction.shape[0], self.target_scaler.n_features_in_))
        dummy_array[:, :self.config.model.output_dim] = scaled_prediction

        real_prediction = self.target_scaler.inverse_transform(dummy_array)

        # Return only the relevant columns (High, Low, Close)
        return real_prediction[:, :self.config.model.output_dim], target_date_iso