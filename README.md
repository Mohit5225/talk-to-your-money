# Talk To Your Money

AI-powered financial insights and stock predictions platform.

## 🚀 Features

- **Stock Price Prediction:** Get AI-driven forecasts for various stock symbols (e.g., AAPL).
- **Financial Insights:** Talk to your financial data and get intelligent analysis.
- **User Authentication:** Secure access to your personal financial insights.
- **Interactive Dashboard:** Modern and responsive UI for visualizing stock data and predictions.

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** MongoDB
- **Machine Learning:** TensorFlow, Keras (Multi-stock prediction model)
- **API Server:** Uvicorn
- **Data Fetching:** Custom DataFetcher for historical stock data

### Frontend
- **Framework:** Next.js (React)
- **Language:** TypeScript
- **Styling:** Tailwind CSS

## 📁 Project Structure

```
.
├── backend/            # FastAPI backend
│   ├── app/           # Main application logic (API, Data, Models)
│   ├── auth/          # Authentication routes and logic
│   ├── mongo_db/      # Database connection and setup
│   ├── main.py        # Entry point for the backend API
│   └── ...
├── frontend/           # Next.js frontend
│   ├── src/           # Components, pages, and hooks
│   ├── public/        # Static assets
│   └── ...
└── README.md           # Project documentation
```

## ⚙️ Getting Started

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Install dependencies (it's recommended to use a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your MongoDB connection and any necessary environment variables.
4. Run the API:
   ```bash
   python run_prediction_api.py
   # OR
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```
3. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📄 License

This project is licensed under the MIT License.