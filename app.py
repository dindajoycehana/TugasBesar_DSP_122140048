import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import find_peaks
import mediapipe as mp
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Simple rPPG Monitor",
    page_icon="💓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .settings-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .control-box {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 0.5rem 0;
    }
    .filter-adjustment {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .video-container {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        border: 2px dashed #ccc;
        text-align: center;
        min-height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_pose = mp.solutions.pose

# Initialize session state
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'rppg_data' not in st.session_state:
    st.session_state.rppg_data = []
if 'resp_data' not in st.session_state:
    st.session_state.resp_data = []
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = []
if 'capture_complete' not in st.session_state:
    st.session_state.capture_complete = False

# Header
st.markdown("""
<div class="main-header">
    <h1>💓 Simple rPPG & Respiration Monitor</h1>
    <p>Capture → Process → Visualize with Peak Detection</p>
</div>
""", unsafe_allow_html=True)

# Main layout: Left column for settings, Right column for camera control and video
left_col, right_col = st.columns([1, 1])

with left_col:
    # Camera Settings
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.subheader("📹 Camera Settings")
    resolution = st.selectbox("Resolution", ["640x480", "1280x720", "1920x1080"], index=1)
    fps = st.selectbox("FPS", [15, 30, 60], index=1)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Capture Settings
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.subheader("⏱️ Capture Settings")
    capture_time = st.slider("Capture Duration (seconds)", 10, 120, 30)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    # Camera Control
    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    st.subheader("📹 Camera Control")
    
    col_control1, col_control2, col_control3 = st.columns(3)
    
    with col_control1:
        start_capture = st.button("🎬 Start Capture", type="primary", use_container_width=True)
    
    with col_control2:
        stop_capture = st.button("⏹️ Stop Capture", use_container_width=True)
    
    with col_control3:
        clear_data = st.button("🗑️ Clear Data", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Status display
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    # Video display container - always visible in right column
    st.subheader("📺 Camera Feed")
    video_placeholder = st.empty()
    
    # Default video container when not recording
    if not st.session_state.recording:
        st.markdown("""
        <div class="video-container">
            <div>
                <h3>📷 Camera Ready</h3>
                <p>Click "Start Capture" to begin recording</p>
                <p>Camera feed will appear here</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def extract_rppg_signal(face_roi):
    """Simple green channel extraction for rPPG"""
    if face_roi.size == 0:
        return 0
    return np.mean(face_roi[:, :, 1])  # Green channel

def extract_respiration_signal(pose_landmarks):
    """Extract respiration from shoulder movement"""
    if pose_landmarks is None:
        return 0
    
    try:
        left_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        # Use vertical movement of chest area
        chest_y = (left_shoulder.y + right_shoulder.y) / 2
        return chest_y
    except:
        return 0

def apply_bandpass_filter(data, lowcut, highcut, fs):
    """Apply bandpass filter to signal"""
    if len(data) < 4:
        return data
    
    nyquist = fs / 2
    low = lowcut / nyquist
    high = highcut / nyquist
    
    # Ensure filter parameters are valid
    low = max(0.01, min(low, 0.99))
    high = max(low + 0.01, min(high, 0.99))
    
    try:
        b, a = signal.butter(4, [low, high], btype='band')
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data
    except:
        return data

def detect_peaks_and_calculate_rate(filtered_signal, fs):
    """Detect peaks and calculate rate (BPM)"""
    if len(filtered_signal) < fs:
        return [], 0
    
    # Find peaks
    peaks, _ = find_peaks(filtered_signal, height=np.std(filtered_signal)*0.3, distance=fs//4)
    
    if len(peaks) < 2:
        return peaks, 0
    
    # Calculate rate from peak intervals
    peak_intervals = np.diff(peaks) / fs  # Convert to seconds
    avg_interval = np.mean(peak_intervals)
    rate_bpm = 60 / avg_interval if avg_interval > 0 else 0
    
    return peaks, rate_bpm

def create_signal_plot(timestamps, raw_rppg, raw_resp, filtered_rppg, filtered_resp, rppg_peaks, resp_peaks, rppg_rate, resp_rate):
    """Create visualization with both raw and filtered signals plus peaks"""
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=(
            'Raw rPPG Signal (Captured)',
            f'Filtered rPPG Signal - Heart Rate: {rppg_rate:.1f} BPM',
            'Raw Respiration Signal (Captured)',
            f'Filtered Respiration Signal - Breathing Rate: {resp_rate:.1f} BPM'
        ),
        vertical_spacing=0.08,
        row_heights=[0.2, 0.3, 0.2, 0.3]
    )
    
    # Raw rPPG plot
    fig.add_trace(
        go.Scatter(x=timestamps, y=raw_rppg, mode='lines', name='Raw rPPG', 
                  line=dict(color='lightcoral', width=1.5)),
        row=1, col=1
    )
    
    # Filtered rPPG plot
    fig.add_trace(
        go.Scatter(x=timestamps, y=filtered_rppg, mode='lines', name='Filtered rPPG', 
                  line=dict(color='red', width=2)),
        row=2, col=1
    )
    
    # rPPG peaks
    if len(rppg_peaks) > 0:
        peak_times = [timestamps[i] for i in rppg_peaks if i < len(timestamps)]
        peak_values = [filtered_rppg[i] for i in rppg_peaks if i < len(filtered_rppg)]
        fig.add_trace(
            go.Scatter(x=peak_times, y=peak_values, mode='markers', name='Heart Peaks',
                      marker=dict(color='darkred', size=8, symbol='triangle-up')),
            row=2, col=1
        )
    
    # Raw Respiration plot
    fig.add_trace(
        go.Scatter(x=timestamps, y=raw_resp, mode='lines', name='Raw Respiration',
                  line=dict(color='lightblue', width=1.5)),
        row=3, col=1
    )
    
    # Filtered Respiration plot
    fig.add_trace(
        go.Scatter(x=timestamps, y=filtered_resp, mode='lines', name='Filtered Respiration',
                  line=dict(color='blue', width=2)),
        row=4, col=1
    )
    
    # Respiration peaks
    if len(resp_peaks) > 0:
        peak_times = [timestamps[i] for i in resp_peaks if i < len(timestamps)]
        peak_values = [filtered_resp[i] for i in resp_peaks if i < len(filtered_resp)]
        fig.add_trace(
            go.Scatter(x=peak_times, y=peak_values, mode='markers', name='Breath Peaks',
                      marker=dict(color='darkblue', size=8, symbol='triangle-up')),
            row=4, col=1
        )
    
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Raw vs Filtered Physiological Signals with Peak Detection"
    )
    
    fig.update_xaxes(title_text="Time (seconds)", row=4, col=1)
    fig.update_yaxes(title_text="Amplitude", row=1, col=1)
    fig.update_yaxes(title_text="Amplitude", row=2, col=1)
    fig.update_yaxes(title_text="Amplitude", row=3, col=1)
    fig.update_yaxes(title_text="Amplitude", row=4, col=1)
    
    return fig

# Results section (only shown after capture) - Full width below the main layout
if st.session_state.capture_complete and len(st.session_state.rppg_data) > 0:
    st.markdown("---")
    st.subheader("📊 Signal Analysis Results")
    
    # POST-CAPTURE FILTER ADJUSTMENT SECTION
    st.markdown('<div class="filter-adjustment">', unsafe_allow_html=True)
    st.subheader("🎛️ Adjust Filter Parameters (Real-time)")
    st.markdown("**Modify these values to see immediate changes in the filtered signal and peak detection:**")
    
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        st.markdown("**💓 rPPG Filter Settings:**")
        rppg_lowpass = st.slider("rPPG Lowpass (Hz)", 0.5, 4.0, 2.5, 0.1, key="post_rppg_low")
        rppg_highpass = st.slider("rPPG Highpass (Hz)", 0.1, 2.0, 0.8, 0.1, key="post_rppg_high")
        
    with filter_col2:
        st.markdown("**🫁 Respiration Filter Settings:**")
        resp_lowpass = st.slider("Resp Lowpass (Hz)", 0.1, 1.0, 0.5, 0.05, key="post_resp_low")
        resp_highpass = st.slider("Resp Highpass (Hz)", 0.05, 0.5, 0.1, 0.05, key="post_resp_high")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process signals with current filter settings
    rppg_array = np.array(st.session_state.rppg_data)
    resp_array = np.array(st.session_state.resp_data)
    time_array = np.array(st.session_state.timestamps)
    
    # Apply filters with current settings
    rppg_filtered = apply_bandpass_filter(rppg_array, rppg_highpass, rppg_lowpass, fps)
    resp_filtered = apply_bandpass_filter(resp_array, resp_highpass, resp_lowpass, fps)
    
    # Detect peaks and calculate rates
    rppg_peaks, heart_rate = detect_peaks_and_calculate_rate(rppg_filtered, fps)
    resp_peaks, breathing_rate = detect_peaks_and_calculate_rate(resp_filtered, fps)
    
    # Display results with current filter settings
    result_col1, result_col2, result_col3, result_col4 = st.columns(4)
    
    with result_col1:
        st.metric("💓 Heart Rate", f"{heart_rate:.1f} BPM", delta=None)
        st.metric("📊 Heart Peaks", len(rppg_peaks))
    
    with result_col2:
        st.metric("🫁 Breathing Rate", f"{breathing_rate:.1f} BPM", delta=None)
        st.metric("📊 Breath Peaks", len(resp_peaks))
    
    with result_col3:
        st.metric("⏱️ Capture Duration", f"{len(st.session_state.timestamps)/fps:.1f}s")
        st.metric("📈 Data Points", len(st.session_state.rppg_data))
    
    with result_col4:
        st.metric("🔧 rPPG Filter", f"{rppg_highpass:.1f}-{rppg_lowpass:.1f} Hz")
        st.metric("🔧 Resp Filter", f"{resp_highpass:.2f}-{resp_lowpass:.2f} Hz")
    
    # Create and display plot with both raw and filtered signals
    signal_plot = create_signal_plot(
        time_array, rppg_array, resp_array, rppg_filtered, resp_filtered,
        rppg_peaks, resp_peaks, heart_rate, breathing_rate
    )
    st.plotly_chart(signal_plot, use_container_width=True)
    
    # Show filter effect info
    st.info("🎛️ **Interactive Filtering**: Adjust the filter sliders above to see real-time changes in the processed signals and detected peaks. The raw signals remain unchanged, showing you the original captured data.")
    
    # Raw data option
    with st.expander("📋 View Raw Data Details"):
        col_raw1, col_raw2 = st.columns(2)
        with col_raw1:
            st.subheader("Raw rPPG Data")
            st.line_chart(rppg_array)
            st.write(f"Raw rPPG Stats:")
            st.write(f"- Mean: {np.mean(rppg_array):.3f}")
            st.write(f"- Std: {np.std(rppg_array):.3f}")
            st.write(f"- Range: {np.max(rppg_array) - np.min(rppg_array):.3f}")
            
        with col_raw2:
            st.subheader("Raw Respiration Data")
            st.line_chart(resp_array)
            st.write(f"Raw Respiration Stats:")
            st.write(f"- Mean: {np.mean(resp_array):.3f}")
            st.write(f"- Std: {np.std(resp_array):.3f}")
            st.write(f"- Range: {np.max(resp_array) - np.min(resp_array):.3f}")

# Handle button actions
if clear_data:
    st.session_state.rppg_data = []
    st.session_state.resp_data = []
    st.session_state.timestamps = []
    st.session_state.capture_complete = False
    st.session_state.recording = False
    status_placeholder.success("✅ Data cleared successfully!")

if start_capture:
    st.session_state.recording = True
    st.session_state.capture_complete = False
    st.session_state.rppg_data = []
    st.session_state.resp_data = []
    st.session_state.timestamps = []

if stop_capture:
    st.session_state.recording = False
    if len(st.session_state.rppg_data) > 0:
        st.session_state.capture_complete = True

# Main capture loop
if st.session_state.recording:
    # Parse resolution
    width, height = map(int, resolution.split('x'))
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    
    # Initialize MediaPipe
    with mp_face_detection.FaceDetection(min_detection_confidence=0.7) as face_detection, \
         mp_pose.Pose(min_detection_confidence=0.5) as pose:
        
        start_time = time.time()
        frame_count = 0
        
        status_placeholder.info(f"🎬 Recording for {capture_time} seconds...")
        progress_bar = progress_placeholder.progress(0)
        
        while st.session_state.recording:
            ret, frame = cap.read()
            if not ret:
                status_placeholder.error("❌ Failed to access webcam")
                break
            
            current_time = time.time() - start_time
            
            # Check if capture time reached
            if current_time >= capture_time:
                st.session_state.recording = False
                st.session_state.capture_complete = True
                break
            
            # Update progress
            progress = min(current_time / capture_time, 1.0)
            progress_bar.progress(progress)
            
            # Convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Face detection
            face_results = face_detection.process(frame_rgb)
            pose_results = pose.process(frame_rgb)
            
            # Draw annotations
            annotated_frame = frame_rgb.copy()
            
            rppg_signal = 0
            resp_signal = 0
            
            # Process face for rPPG
            if face_results.detections:
                for detection in face_results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = frame_rgb.shape
                    
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    width_box = int(bbox.width * w)
                    height_box = int(bbox.height * h)
                    
                    # Draw face bounding box
                    cv2.rectangle(annotated_frame, (x, y), (x + width_box, y + height_box), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, "rPPG ROI", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Extract signal
                    face_roi = frame_rgb[y:y+height_box, x:x+width_box]
                    rppg_signal = extract_rppg_signal(face_roi)
            
            # Process pose for respiration
            if pose_results.pose_landmarks:
                # Draw pose landmarks (simplified)
                landmarks = pose_results.pose_landmarks.landmark
                h, w, _ = frame_rgb.shape
                
                # Draw shoulder points
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                
                cv2.circle(annotated_frame, (int(left_shoulder.x * w), int(left_shoulder.y * h)), 8, (255, 0, 0), -1)
                cv2.circle(annotated_frame, (int(right_shoulder.x * w), int(right_shoulder.y * h)), 8, (255, 0, 0), -1)
                cv2.putText(annotated_frame, "Resp ROI", (int(left_shoulder.x * w), int(left_shoulder.y * h)-20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                resp_signal = extract_respiration_signal(pose_results.pose_landmarks)
            
            # Store data
            st.session_state.rppg_data.append(rppg_signal)
            st.session_state.resp_data.append(resp_signal)
            st.session_state.timestamps.append(current_time)
            
            # Display frame in the right column
            video_placeholder.image(annotated_frame, channels="RGB", use_column_width=True)
            
            frame_count += 1
            time.sleep(1/fps)
    
    cap.release()
    progress_placeholder.empty()
    
    if st.session_state.capture_complete:
        status_placeholder.success("✅ Capture completed! Now you can adjust filter parameters below to see real-time changes.")
        st.rerun()

# Instructions
with st.expander("📖 How to Use"):
    st.markdown("""
    ### Enhanced Layout & 3-Step Process:
    
    **📋 New Layout:**
    - **Left Side**: Camera & Capture settings (no scrolling needed)
    - **Right Side**: Camera controls & live video feed (always visible)
    - **Bottom**: Analysis results after capture (full width)
    
    1. **⚙️ Configure Settings (Left Panel)**
       - Set camera resolution and FPS
       - Choose capture duration (10-120 seconds)
    
    2. **🎬 Capture Data (Right Panel)**
       - Click "Start Capture" to begin recording
       - Camera feed appears immediately in right panel
       - Stay still and face the camera
       - Green box = face ROI for heart rate
       - Red dots = shoulder landmarks for breathing
    
    3. **📊 Interactive Analysis (Bottom Section)** ⭐
       - After capture ends, raw signals are permanently stored
       - **Adjust filter sliders in real-time** to see immediate changes
       - Compare raw vs filtered signals side-by-side
       - Peak detection updates automatically with filter changes
       - Experiment with different filter ranges to optimize results
    
    ### 🎛️ Benefits of New Layout:
    - **No scrolling required** during capture
    - **Camera feed always visible** in right panel
    - **Settings organized** on the left for easy access
    - **Results appear below** without interfering with capture area
    
    ### 🔧 Filter Settings Guide:
    - **rPPG**: 0.8-2.5 Hz (48-150 BPM heart rate range)
    - **Respiration**: 0.1-0.5 Hz (6-30 BPM breathing range)
    - Try different ranges to see which works best for your signal
    
    ### 💡 Tips:
    - Capture once, then experiment with multiple filter settings
    - Use steady lighting and sit still during capture
    - 30+ seconds recommended for reliable measurements
    - Compare raw vs filtered to understand signal processing effects
    """)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>💓 Simple rPPG Monitor with Improved Layout | For research and educational purposes only</p>
</div>
""", unsafe_allow_html=True)