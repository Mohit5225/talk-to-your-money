# api/prediction_service.py
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
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

    def _prepare_inference_data(self, symbol: str, target_ts: pd.Timestamp, debug: bool = False) -> dict:
        """
        Robust data preparation for inference:
        - Fetches a sufficiently large window
        - Removes any rows for the target day or after (ensures we only use historical data)
        - Selects the final `time_steps` rows to feed the model
        """
        normalized_target = target_ts.normalize()

        # Fetch a generous window (120 days back is fine)
        fetch_end_date = (normalized_target + pd.DateOffset(days=1)).strftime('%Y-%m-%d')
        start_date = (normalized_target - pd.DateOffset(days=120)).strftime('%Y-%m-%d')

        df = self.fetcher.fetch_data(symbol, start_date, fetch_end_date)
        df = df.dropna()

        # Ensure DateTimeIndex and normalize index to date-only for reliable comparison
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None).normalize()

        # IMPORTANT: exclude any rows >= target date so input is strictly historical
        df_hist = df[df.index < normalized_target]

        if debug:
            print(f"DEBUG: fetched df index min/max: {df.index.min()} / {df.index.max()}")
            print(f"DEBUG: filtered df_hist index min/max: {df_hist.index.min()} / {df_hist.index.max()}")
            print(f"DEBUG: rows fetched: {len(df)}  rows after filter: {len(df_hist)}")

        if len(df_hist) < self.config.data.time_steps:
            raise ValueError(
                f"Not enough historical rows strictly before {normalized_target.date()} for {symbol} "
                f"(need {self.config.data.time_steps}, got {len(df_hist)})"
            )

        # Select the most recent time_steps rows
        feature_names = self.config.data.get_active_features
        features_df = df_hist[feature_names].tail(self.config.data.time_steps)

        # Sanity checks: column order and shape should match scaler expectation
        # If your scaler was fit with a specific column order, ensure it's the same here.
        if hasattr(self.feature_scaler, "feature_names_in_"):
            expected_cols = list(self.feature_scaler.feature_names_in_)
            if list(features_df.columns) != expected_cols:
                # reorder if possible, otherwise raise to catch silent misalignment
                try:
                    features_df = features_df[expected_cols]
                except Exception:
                    raise RuntimeError("Feature columns do not match scaler feature_names_in_ and cannot be reordered.")

        # Scale and reshape for model input
        scaled_features = self.feature_scaler.transform(features_df.values)
        price_input = np.expand_dims(scaled_features, axis=0)  # shape (1, time_steps, n_features)

        # Stock id input remains the same
        stock_id = self.config.data.stock_identifier_mapping[symbol]
        stock_input = np.array([[stock_id]])

        if debug:
            print("DEBUG: features_df.index ->", features_df.index)
            print("DEBUG: features_df.head(1)->\n", features_df.head(1))
            print("DEBUG: scaled_features.shape ->", scaled_features.shape)
            print("DEBUG: price_input.shape ->", price_input.shape)
            print("DEBUG: stock_input ->", stock_input)

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