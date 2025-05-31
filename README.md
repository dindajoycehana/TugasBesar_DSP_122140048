# 🧠 Real-Time Respiration and rPPG Signal Measurement - Final Project
Name     : Dinda Joycehana

NIM      : 122140048

course   : Digital Signal Processing (DSP)   

---

## 📌 Project Overview

This project implements a real-time physiological signal measurement system that combines two key measurements:

- ❤️ **Remote Photoplethysmography (rPPG):** Estimated from facial color changes within a bounding box obtained via face detection.
- 🫁 **Respiration Signal:** Estimated from shoulder motion tracked using pose landmarks.

Video is captured through a webcam and processed in real-time. The extracted signals are visualized using `Matplotlib`, and a lightweight web interface is built using `Streamlit`.

📌 Disclaimer & Credits
- The **pose estimation model** and **face detection implementation** used in this project are adapted from the materials and examples provided in the **Digital Signal Processing hands-on session** by the **Informatics Engineering Department**.
- These models and base codes are credited to the original GitHub repository maintained by the **Informatics Engineering** instructors or assistants.

---

## 🚀 Key Features

- 📹 **Real-Time Webcam Input**
- 🫀 **rPPG Signal Extraction:** Based on facial bounding box region (face detection).
- 🫁 **Respiration Signal Extraction:** Based on shoulder landmark movement.
- 🧽 **Signal Filtering:** Includes Butterworth and moving average filters for denoising.
- 📊 **Live Signal Visualization:** Using `Matplotlib` embedded in a `Streamlit` interface.

---

## 🛠️ Technologies Used

- Python 3.10 or higher
- `OpenCV` – Video capture & face detection  
- `Mediapipe` – Pose estimation (for shoulder landmarks)  
- `NumPy` – Numerical computing  
- `SciPy` – Signal filtering  
- `Matplotlib` – Signal visualization  
- `Streamlit` – Simple web-based UI

---

## 📁 Project Structure

```bash
TugasBesar_DSP_122140048/
├── app.py                      # Main Streamlit app/Web UI signal
├── signal_processing.ipynb     # Jupyter notebook for testing & analysis
├── models/                     # Model or auxiliary data folder (if needed)
├── requirement.txt             # Required Python libraries
└── README.md                   # Project documentation
```

---
## 🧠 Signal Processing Pipeline

This project extracts physiological signals using computer vision and signal processing techniques. The steps are divided as follows:

---

### 1. rPPG Signal (❤️)

- **Source:** Face skin region inside bounding box (detected using Haar Cascade or similar).
- **Tool:** OpenCV + POS Algorithm
- **Process:**
  - Extract ROI (Region of Interest) from facial bounding box.
  - Calculate average green channel intensity over time (rPPG sensitive to green).
  - Use **Plane-Orthogonal-to-Skin (POS)** algorithm to enhance the pulse signal:
    - Normalize color channels.
    - Apply projection matrix to isolate pulse-related variations.
  - Filter signal using a **bandpass filter (0.7–2.5 Hz)** for heart rate range.
- **Output:** Real-time rPPG waveform with possible BPM estimation.

### 2. Respiration Signal (🫁)

- **Source:** Shoulder motion from pose landmarks (left and right shoulders).
- **Tool:** Mediapipe Pose
- **Process:**
  - Track vertical movement (Y-axis) of both shoulders over time.
  - Calculate displacement as a surrogate for breathing motion.
  - Apply filtering (e.g., **bandpass filter 0.1–0.5 Hz**) to isolate the breathing frequency.
- **Output:** Real-time respiration waveform plotted over time.

### 3. Signal Filtering

- **Type:** Butterworth Bandpass Filter (implemented using `scipy.signal`)
- **Purpose:**
  - Remove motion artifacts.
  - Isolate physiological signal frequencies.
- **Parameters:**
  - Respiration: 0.1 – 0.5 Hz
  - rPPG: 0.7 – 4 Hz

### 4. Visualization

- **Matplotlib:** Static and live plotting (in both notebook and Streamlit).
- **Plotly:** Interactive signal plots in Jupyter Notebook.
- **Streamlit:** Integrated plots + webcam feed.

### 5. Models / Tools Used

| Component              | Tool / Library       | Description                          |
|------------------------|----------------------|--------------------------------------|
| Pose Estimation        | Mediapipe Pose       | Landmark tracking for respiration    |
| Face Detection         | OpenCV Haar Cascade  | Bounding box for rPPG extraction     |
| Signal Filtering       | SciPy                | Butterworth bandpass filter          |
| rPPG Algorithm         | POS (Plane Orthogonal to Skin) | Color projection technique     |
| Visualization          | Matplotlib, Plotly   | Real-time and interactive plotting   |

--- 

## ▶️ How to Run the Program
Follow these steps to run the project on your local machine:

1. Clone the repository:
```bash
git clone https://github.com/dindajoycehana/TugasBesar_DSP_122140048.git
cd TugasBesar_DSP_122140048
```

2. Create a virtual environment (recommended):
Write this command via terminal VSCode. MKake sure you are in the right folder. 
use uv environment and python 3.10 version.
- Install UV
```bash
pip install uv
```

- Create Virtual Environment
```bash
uv venv --python=python3.10
```

- Virtual Environment Activate

On Windows :
```bash
venv\Scripts\activate
```

On macOS/Linux :
```bash
source venv/bin/activate
```

3. Install required dependencies:
```bash
uv pip install -r requirements.txt
```

4. Run Program
You can run this project using **two different methods** depending on your needs:

1. Using Jupyter Notebook (`signal_processing.ipynb`)
- Make sure you have Jupyter installed:
    ```bash
    uv pip install notebook
    ```
- Launch the notebook
    ```bash
    jupyter notebook
    ```
- Open `signal_processing.ipynb` and run the cells in order.


2. Using Streamlit App (app.py)
- Make sure you have install streamlit from requirement.txt or you can run this command in terminal
  ```bash
  uv pip instal streamlit plotly
  ```
- Run the app
  ```bash
  streamlit run app.py
  ```
- Your browser will open automatically at: http://localhost:8501
  
---

