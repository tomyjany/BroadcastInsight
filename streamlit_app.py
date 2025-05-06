import streamlit as st
import requests
import json
from PIL import Image
import cv2
import tempfile
import os
from sceneDetector.agents.interface import libraries as scene_libraries
from ocr.agents.interface import libraries as ocr_libraries
import logging
from tools.config_mapper import cfg

logging.basicConfig(level=logging.INFO)

# API Endpoint
# API_URL = "http://localhost:8000/api/v1/NewsVideoMiner/inference"
API_URL = cfg.API_URL

logo = Image.open("logo.png")
st.set_page_config(layout="wide", page_title="News Video Miner", page_icon=logo)

st.title("News Video Miner")

# Sidebar for user inputs
st.sidebar.header("Configuration")
ocr_method = st.sidebar.selectbox("Select OCR Method", ocr_libraries)
scene_detect_method = st.sidebar.selectbox(
    "Select Scene Detection Method", scene_libraries
)
people_database_path = st.sidebar.text_input(
    "People Database Path", cfg.PEOPLE_DB_PATH
)
yolo_model_path = st.sidebar.text_input("YOLO Model Path", cfg.YOLO_MODEL_PATH)

# File uploader
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

if uploaded_file:
    st.info(f"Uploaded file: {uploaded_file.name}")

    # Submit button
    if st.button("Run Inference"):
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_video_path = temp_file.name

        # Prepare the request payload
        files = {"file": open(temp_video_path, "rb")}
        data = {
            "ocr_method": ocr_method,
            "scene_detect_method": scene_detect_method,
            "people_database_path": people_database_path,
            "yolo_model_path": yolo_model_path,
        }

        # Call the API
        with st.spinner("Processing..."):
            try:
                response = requests.post(API_URL, files=files, data=data)
                response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
                results = response.json()

                # Save results to session state
                scenes = results.get("message", [])
                if not isinstance(scenes, list):
                    st.error("Unexpected response format from the API.")
                    st.stop()

                # Store data in session state
                st.session_state.scenes = scenes
                st.session_state.video_path = temp_video_path
                st.session_state.selected_scene = 0 if scenes else None

                st.success("Inference completed successfully!")
                st.rerun()  # Use st.rerun() instead of experimental_rerun()

            except requests.exceptions.RequestException as e:
                st.error(f"Error during API call: {e}")

# Display results if available in session state
if "scenes" in st.session_state and "video_path" in st.session_state:
    scenes = st.session_state.scenes
    video_path = st.session_state.video_path

    # Create scene selector
    scene_options = [f"Scene {scene['scene_info']['id']}" for scene in scenes]

    # Create a row with scene selector and navigation buttons
    col_select, col_prev, col_next = st.columns([3, 1, 1])

    with col_select:
        selected_scene_idx = st.selectbox(
            "Select a scene to view:",
            range(len(scene_options)),
            format_func=lambda i: scene_options[i],
            key="scene_selector",
            index=st.session_state.selected_scene,
        )
        st.session_state.selected_scene = selected_scene_idx

    # Navigation buttons
    with col_prev:
        if st.button("← Previous Scene"):
            st.session_state.selected_scene = max(
                0, st.session_state.selected_scene - 1
            )
            st.rerun()

    with col_next:
        if st.button("Next Scene →"):
            st.session_state.selected_scene = min(
                len(scenes) - 1, st.session_state.selected_scene + 1
            )
            st.rerun()

    # Display the selected scene
    if st.session_state.selected_scene is not None:
        scene = scenes[st.session_state.selected_scene]

        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            st.error("Failed to open video file.")
            st.stop()

        # Extract frame
        frame_number = scene["scene_info"]["frame_number"]
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if ret:
            # Convert frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            # Create two columns
            col1, col2 = st.columns([3, 2])

            # Display frame in the first column
            with col1:
                st.image(
                    pil_image, caption=f"Frame {frame_number}", use_container_width=True
                )

            # Display metadata in the second column
            with col2:
                st.subheader("Scene Information")
                st.markdown(
                    f"""
                **Scene ID:** {scene['scene_info']['id']}  
                **Frame Number:** {scene['scene_info']['frame_number']}  
                **Begin Time:** {scene['scene_info']['begin_time']} ms  
                **End Time:** {scene['scene_info']['end_time']} ms  
                **TV Logo:** {scene['tv_logo']}
                """
                )

                st.subheader("Detected People")
                if scene["detected_people"]:
                    for person in scene["detected_people"]:
                        st.markdown(
                            f"- {person['person']}) (predicted_age: {person['age']}, predicted_gender: {person['gender']})"
                        )
                else:
                    st.markdown("None")

                st.subheader("OCR Text")
                st.text_area("", scene["ocr_text"], height=150, disabled=True)
        else:
            st.warning(f"Failed to load frame {frame_number}.")

        cap.release()
