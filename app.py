#Untuk Menjalankan GUI webcam melalui Streamlit
import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("HI!, Welcome to Cap")
st.write("just click this camera to open your webcam and start to record your video")

if st.button("📷 Open Camera and Start"):
    st.info("Webcam starting... Please allow camera access.")
    cap = cv2.VideoCapture(0)
    frame_window = st.image([])
    count = 0
    while count < 900:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to access webcam.")
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_window.image(frame)
        count += 1
    cap.release()
    st.success("Capture finished. (You can add your signal processing here!)")