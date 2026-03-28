# 🚆 Railway Planner

A comprehensive train routing and ticket availability prediction system. This project features a FastAPI backend that calculates optimal train routes and a Streamlit frontend that provides an interactive user interface for checking seat availability, RAC, Waiting List (WL), and confirmation probabilities.

## 🌟 Features

* **Smart Routing Algorithm:** Utilizes Dijkstra's algorithm on the backend to find the shortest possible routes between a source and destination.
* **Layover Management:** Supports direct routes as well as routes with at most 1 layover, ensuring a minimum time gap of 30 minutes between connecting trains.
* **Interactive UI:** A user-friendly Streamlit frontend that takes Source, Destination, and Date as inputs.
* **Availability Status:** Displays real-time-like status of possible ways, showing the Waiting list, RAC list, and a calculated Confirmation Probability.
* **Custom Generated Dataset:** * **Train Data:** Dataset of 100 trains generated using Google's Gemini, tested and validated in Python via Google Colab.
    * **Seat Data:** Seat availability data generated for a 10-day window (1st April to 10th April) using Python's `random` function to simulate real-world ticketing scenarios.

## 📂 Project Structure

* `backend.py`: The FastAPI server handling route calculations (Dijkstra's) and data serving.
* `frontend.py`: The Streamlit application for the user interface.
* `Railway_dataset_generator.ipynb`: The Jupyter Notebook used for generating and validating the synthetic train data.
* `train_dataset.json`: The generated dataset of 100 trains.
* `seat_dataset.json`: The randomized seat availability data for April 1st to April 10th.

## 🚀 How to Run the Project

### Prerequisites
Ensure you have Python installed on your system. You will need to install the required libraries to run both the backend and frontend.

Open your terminal and install the dependencies:
```bash
pip install fastapi uvicorn streamlit python-dateutil
uvicorn backend:app --reload
streamlit run frontend.py
