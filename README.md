# TugasBesar DSP
Name     : Dinda Joycehana
NIM      : 122140048

## Description Project
This project implements a comprehensive system that combines respiration signal measurement and remote photoplethysmography (rPPG) processing. The system performs real-time analysis of physiological signals captured through webcam video input, providing visualization and analysis of both respiratory patterns and cardiovascular signals.

This project provides two complementary applications for contactless physiological monitoring:

- Standalone rPPG Monitor and Repiration Measurement (signal_processing.ipynb) complete analysis with POS algorithm
- Streamlit Web App (app.py) - Interactive web interface with real-time filtering

---

## Key Features

- Real-time Video Processing: Captures and processes webcam input in real-time
- Dual Signal Analysis:
    - espiration signal measurement and analysis
    - Remote photoplethysmography (rPPG) signal extraction
- Signal Visualization: Real-time plotting and visualization using matplotlib
- Digital Signal Processing: Advanced DSP techniques for signal filtering and analysis
- User-friendly Interface: Intuitive display of both signal types simultaneously

---

# System Requirements

- Python 3.10 or higher
- Webcam or video capture device
- Minimum 4GB RAM recommended
- Operating System: Windows, macOS, or Linux

---

# Installation

1. Clone the repository:
bash

git clone https://github.com/dindajoycehana/TugasBesar_DSP_122140048.git
cd TugasBesar_DSP_122140048

2. Create a virtual environment (recommended):

- Install UV

bash

pip install uv

- Buat virtual environment

bash

uv venv --python=python3.10

- Aktifkan Virtual Environment 

On Windows :

bash
venv\Scripts\activate

On macOS/Linux :

source venv/bin/activate


Install required dependencies:

bash
uv pip install -r requirements.txt

---

# Usage

1. Standalone Application

bash 

python rppg_standalone.py

Features:

- 60-second automatic capture in 15 fps
- Advanced POS algorithm for rPPG
- Comprehensive signal analysis
- Matplotlib visualizations
- Press 'q' to quit early

2. Interactive Web Application

bash

streamlite run app.py

Features:

- Real-time camera preview
- Adjustable capture duration (10-120 seconds)
- Interactive filter parameter adjustment
- Live signal processing
- Comparative raw vs filtered signal display

---

# Dependencies
The project relies on several key Python libraries:

- MediaPipe for face detection and pose estimation
- OpenCV: Computer vision and video processing
- NumPy: Numerical computations and array operations
- SciPy: Advanced signal processing functions
- Matplotlib: Signal visualization and plotting
- Streamlit : Interactive Web Interface

---

🔧 Configuration Options
Camera Settings

Resolution: 640x480, 1280x720, 1920x1080
Frame Rate: 15, 30, 60 FPS
Capture Duration: 10-120 seconds (Streamlit only)

Signal Processing Parameters
rPPG (Heart Rate)

Frequency Range: 0.7-4.0 Hz (42-240 BPM)
Default Filter: 0.8-2.5 Hz (48-150 BPM)
Algorithm: POS (Standalone) / Green Channel (Streamlit)

Respiration

Frequency Range: 0.1-0.4 Hz (6-24 breaths/min)
Default Filter: 0.1-0.5 Hz
Method: Shoulder landmark Y-position tracking

📈 Signal Processing Pipeline
1. Data Acquisition

Face Detection: MediaPipe BlazeFace for ROI extraction
Pose Detection: MediaPipe Pose for shoulder landmarks
Signal Extraction: RGB channel analysis (face) + Y-position (shoulders)

2. Signal Processing

Preprocessing: Mean normalization and temporal windowing
Filtering: Butterworth bandpass filters
Peak Detection: Scipy find_peaks with adaptive thresholds

3. Analysis & Visualization

Rate Calculation: Peak interval analysis
Quality Assessment: Signal-to-noise evaluation
Real-time Display: Interactive plots with peak markers

🎛️ Interactive Features (Streamlit App)
Real-time Filter Adjustment

Post-capture filtering: Modify parameters after data collection
Immediate feedback: See changes instantly without re-capturing
Parameter ranges:

rPPG: 0.1-4.0 Hz
Respiration: 0.05-1.0 Hz



Visual Analysis

Raw vs Filtered: Side-by-side signal comparison
Peak Detection: Automatic heart/breath peak identification
Statistics Display: Real-time rate calculations and data quality metrics

💡 Best Practices
For Optimal Results:

Lighting: Ensure good, consistent lighting on face
Positioning: Sit 50-80cm from camera, face directly forward
Stability: Minimize movement during capture
Duration: Capture for at least 30 seconds for reliable measurements
Environment: Avoid flickering lights or strong shadows

Troubleshooting:

No face detected: Improve lighting, adjust camera angle
Poor signal quality: Increase capture duration, reduce movement
Incorrect readings: Adjust filter parameters in Streamlit app

🔬 Technical Details
Algorithms Used
POS (Plane-Orthogonal-to-Skin) Method

Advanced rPPG algorithm for robust heart rate detection
Handles motion artifacts and lighting variations
Operates on RGB color space projections

Green Channel Method

Simplified approach using green light absorption
Real-time processing capability
Good for controlled environments

Signal Processing

Butterworth Filters: 4th-order bandpass filtering
Peak Detection: Adaptive threshold with minimum distance constraints
Rate Calculation: Inter-beat interval analysis