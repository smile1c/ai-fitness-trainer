import streamlit as st
import cv2
import numpy as np
from pathlib import Path
import time

from models.tfhub_recognizer import TFHubExerciseRecognizer
from models.exercise_analyzer import ExerciseAnalyzer
from utils.video_processor import VideoProcessor
from exercise_standards import SUPPORTED_EXERCISES, EXERCISE_STANDARDS

st.set_page_config(
    page_title="AI Fitness Trainer Pro",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .block-container {
        padding-top: 2rem;
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }
    
    .sub-header {
        text-align: center;
        color: #9ca3af;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 0.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
    }
    
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.3rem;
    }
    
    .metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0.3rem 0;
        line-height: 1.1;
        word-wrap: break-word;
    }
    
    .metric-label {
        font-size: 0.65rem;
        opacity: 0.9;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .info-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    
    .success-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
    }
    
    .exercise-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.95rem;
        margin: 0.5rem;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(102, 126, 234, 0.5);
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 10px;
        border-radius: 10px;
    }
    
    .feedback-positive {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        margin: 0.4rem 0;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.2);
    }
    
    .feedback-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        margin: 0.4rem 0;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 4px 10px rgba(245, 158, 11, 0.2);
    }
    
    .feedback-negative {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        margin: 0.4rem 0;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.2);
    }
    
    .stats-container {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .stats-container p {
        color: #d1d5db;
        margin: 0.5rem 0;
    }
    
    .stats-container strong {
        color: #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    h1, h2, h3 {
        color: #e5e7eb;
    }
    
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid rgba(102, 126, 234, 0.5);
        font-weight: 500;
        background-color: #1e1e2e;
        color: #e5e7eb;
    }
    
    .uploadedFile {
        border-radius: 12px;
        border: 2px dashed #667eea;
        background: #1e1e2e;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #d1d5db;
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #e5e7eb;
    }
    </style>
""", unsafe_allow_html=True)

if 'video_processor' not in st.session_state:
    st.session_state.video_processor = VideoProcessor()
if 'processed_videos' not in st.session_state:
    st.session_state.processed_videos = []
if 'tfhub_recognizer' not in st.session_state:
    st.session_state.tfhub_recognizer = None
if 'webcam_running' not in st.session_state:
    st.session_state.webcam_running = False

def main():
    st.markdown('<h1 class="main-header">💪 AI FITNESS TRAINER PRO</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Research-Backed Analysis • 16 Validated Exercises • ACE + NSCA Standards</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        st.markdown("---")
        
        st.markdown("### 🎯 Select Exercise")
        
        # Build exercise options from standards
        exercise_options = {}
        for ex_key in SUPPORTED_EXERCISES:
            ex_data = EXERCISE_STANDARDS[ex_key]
            icon_map = {
                'lower_body': '🏋️',
                'upper_body': '💪',
                'core': '🔥',
                'cardio': '🏃'
            }
            icon = icon_map.get(ex_data['category'], '🎯')
            exercise_options[ex_key] = f"{icon} {ex_data['name']} / {ex_data['name_thai']}"
        
        exercise_type = st.selectbox(
            "Choose your exercise",
            options=SUPPORTED_EXERCISES,
            format_func=lambda x: exercise_options[x],
            help="16 exercises with validated biomechanical standards (ACE + NSCA)"
        )
        
        st.markdown("---")
        
        st.markdown("### 📖 Exercise Info")
        
        # Get exercise data from standards
        ex_data = EXERCISE_STANDARDS.get(exercise_type, {})
        
        with st.expander("📝 View Details", expanded=False):
            st.markdown(f"**{ex_data.get('name', exercise_type)}** / {ex_data.get('name_thai', '')}")
            st.markdown(f"*{ex_data.get('description', '')}*")
            st.markdown(f"**Category:** {ex_data.get('category', '').replace('_', ' ').title()}")
            st.markdown(f"**Difficulty:** {ex_data.get('difficulty', '').title()}")
            st.markdown(f"**Standards:** {', '.join(ex_data.get('references', []))}")
        
        st.markdown("---")
        
        if st.session_state.processed_videos:
            st.markdown("### 📊 Session Stats")
            total_videos = len(st.session_state.processed_videos)
            total_reps = sum([v.get('reps', 0) for v in st.session_state.processed_videos])
            
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 1rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 1rem;'>
                    <div style='font-size: 2rem; font-weight: bold;'>{total_videos}</div>
                    <div style='font-size: 0.85rem; opacity: 0.9;'>Videos Analyzed</div>
                </div>
                <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                            padding: 1rem; border-radius: 15px; color: white; text-align: center;'>
                    <div style='font-size: 2rem; font-weight: bold;'>{total_reps}</div>
                    <div style='font-size: 0.85rem; opacity: 0.9;'>Total Reps</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; padding: 1rem; color: #6b7280; font-size: 0.85rem;'>
                <p><strong>Powered by</strong></p>
                <p>TensorFlow Hub MoveNet</p>
                <p style='margin-top: 0.5rem;'>🎓 Senior Project</p>
                <p>Rangsit University</p>
            </div>
        """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📹 Video Analysis", "📷 Live Camera"])
    
    with tab1:
        video_upload_mode(exercise_type)
    
    with tab2:
        webcam_mode(exercise_type)
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 2rem; color: #9ca3af;'>
            <p style='font-size: 0.9rem; font-weight: 500;'>
                🚀 AI-Powered Fitness Analysis | 
                💻 Real-time Motion Tracking | 
                📊 Advanced Performance Metrics
            </p>
            <p style='font-size: 0.75rem; margin-top: 0.5rem; color: #6b7280;'>
                © 2025 AI Fitness Trainer Pro. All rights reserved.
            </p>
        </div>
    """, unsafe_allow_html=True)

def video_upload_mode(exercise_type):
    st.markdown("## 📹 Video Analysis")
    
    exercise_names = {
        'squat': 'Squat',
        'pushup': 'Pushup',
        'plank': 'Plank',
        'lunges': 'Lunges',
        'jumping_jacks': 'Jumping Jacks',
        'situp': 'Situp',
        'high_knees': 'High Knees',
        'running': 'Running',
        'walking': 'Walking',
        'burpees': 'Burpees',
        'mountain_climbers': 'Mountain Climbers',
        'side_plank': 'Side Plank',
        'crunches': 'Crunches',
        'leg_raises': 'Leg Raises',
        'bicycle_crunches': 'Bicycle Crunches',
        'standing_knee_raises': 'Knee Raises',
        'wall_sit': 'Wall Sit',
        'glute_bridge': 'Glute Bridge',
        'jumping': 'Jumping',
        'star_jumps': 'Star Jumps',
        'squat_jumps': 'Squat Jumps'
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
            <div class="info-card">
                <h3>🎯 Current Exercise</h3>
                <div class="exercise-badge">{exercise_names.get(exercise_type, exercise_type)}</div>
                <p style='margin-top: 1rem; color: #9ca3af; font-size: 0.9rem;'>
                    <strong style='color: #e5e7eb;'>What to expect:</strong><br/>
                    • Real-time pose detection<br/>
                    • Accurate rep counting<br/>
                    • Form feedback and corrections<br/>
                    • Downloadable analyzed video
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "📤 Upload Your Workout Video",
            type=['mp4', 'mov', 'avi', 'webm'],
            help="Maximum file size: 200MB"
        )
        
        if uploaded_file is not None:
            with st.spinner("💾 Processing upload..."):
                video_path = st.session_state.video_processor.save_uploaded_file(uploaded_file)
            
            st.markdown(f"""
                <div class="success-card">
                    <h4 style='margin: 0; color: white;'>✅ Upload Successful!</h4>
                    <p style='margin: 0.5rem 0 0 0; opacity: 0.95;'>📁 {uploaded_file.name}</p>
                </div>
            """, unsafe_allow_html=True)
            
            props = st.session_state.video_processor.get_video_properties(video_path)
            
            with col2:
                st.markdown("### 📊 Video Info")
                st.markdown(f"""
                    <div class="stats-container">
                        <p style='margin: 0.5rem 0;'><strong>⏱️ Duration:</strong> {props['duration']:.1f}s</p>
                        <p style='margin: 0.5rem 0;'><strong>🎬 FPS:</strong> {props['fps']}</p>
                        <p style='margin: 0.5rem 0;'><strong>📐 Size:</strong> {props['width']}×{props['height']}</p>
                        <p style='margin: 0.5rem 0;'><strong>🎞️ Frames:</strong> {props['frame_count']:,}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 🎥 Preview")
            st.video(video_path)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.button("🚀 START ANALYSIS", type="primary", use_container_width=True):
                    process_video(video_path, exercise_type)

def webcam_mode(exercise_type):
    st.markdown("## 📷 Live Camera Analysis")
    
    st.markdown("""
        <div class="info-card">
            <h3>🎥 Real-time Workout Analysis</h3>
            <p style='color: #9ca3af;'>
                Click <strong style='color: #e5e7eb;'>START CAMERA</strong> to begin live analysis of your workout form.
                Make sure your entire body is visible in the frame for best results.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📷 START CAMERA", type="primary", use_container_width=True):
            st.session_state.webcam_running = True
            st.rerun()
        
        if st.button("⏹️ STOP CAMERA", type="secondary", use_container_width=True):
            st.session_state.webcam_running = False
            st.rerun()
    
    if st.session_state.webcam_running:
        run_webcam_analysis(exercise_type)

def run_webcam_analysis(exercise_type):
    with st.spinner("🤖 Initializing AI Model..."):
        if st.session_state.tfhub_recognizer is None:
            st.session_state.tfhub_recognizer = TFHubExerciseRecognizer()
        recognizer = st.session_state.tfhub_recognizer
        exercise_analyzer = ExerciseAnalyzer(exercise_type=exercise_type)
    
    st.success("✅ Camera Ready!")
    
    video_placeholder = st.empty()
    metrics_placeholder = st.empty()
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("❌ Cannot access camera. Please check your camera permissions.")
        return
    
    exercise_names = {
        'squat': 'Squat / สควอท',
        'pushup': 'Pushup / วิดพื้น',
        'plank': 'Plank / แพลงค์',
        'lunges': 'Lunges / ลันจ์',
        'jumping_jacks': 'Jumping Jacks / กระโดดแจ็ค',
        'situp': 'Situp / ซิทอัพ',
        'high_knees': 'High Knees / ยกเข่าสูง',
        'running': 'Running / วิ่งหน้าที่',
        'walking': 'Walking / เดิน',
        'burpees': 'Burpees / เบอร์ปี้',
        'mountain_climbers': 'Mountain Climbers / ปีนเขา',
        'side_plank': 'Side Plank / แพลงค์ข้าง',
        'crunches': 'Crunches / ครันช์',
        'leg_raises': 'Leg Raises / ยกขา',
        'bicycle_crunches': 'Bicycle Crunches / ปั่นจักรยาน',
        'standing_knee_raises': 'Knee Raises / ยกเข่ายืน',
        'wall_sit': 'Wall Sit / นั่งพิงกำแพง',
        'glute_bridge': 'Glute Bridge / ยกสะโพก',
        'jumping': 'Jumping / กระโดด',
        'star_jumps': 'Star Jumps / กระโดดดาว',
        'squat_jumps': 'Squat Jumps / สควอทกระโดด'
    }
    
    frame_count = 0
    
    try:
        while st.session_state.webcam_running:
            ret, frame = cap.read()
            
            if not ret:
                st.warning("⚠️ Cannot read from camera")
                break
            
            exercise, confidence, keypoints, angles = recognizer.detect_exercise(frame)
            
            if keypoints is not None and angles:
                feedback, _ = exercise_analyzer.analyze_frame(angles)
                
                frame = recognizer.draw_keypoints(frame, keypoints)
                
                h, w = frame.shape[:2]
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, 180), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
                
                y_offset = 35
                
                cv2.putText(frame, exercise_names.get(exercise_type, exercise_type), (20, y_offset),
                           cv2.FONT_HERSHEY_DUPLEX, 0.8, (102, 126, 234), 2, cv2.LINE_AA)
                cv2.putText(frame, exercise_names.get(exercise_type, exercise_type), (20, y_offset),
                           cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
                y_offset += 40
                
                for key, message in feedback.items():
                    if key == 'reps':
                        continue
                    
                    if "Perfect" in message or "Good" in message or "Excellent" in message:
                        color = (16, 185, 129)
                    elif "Watch" in message or "Adjust" in message or "Keep" in message:
                        color = (245, 158, 11)
                    else:
                        color = (239, 68, 68)
                    
                    cv2.putText(frame, message, (20, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
                    y_offset += 30
                
                if 'reps' in feedback:
                    cv2.rectangle(frame, (20, y_offset - 25), (150, y_offset + 5),
                                 (102, 126, 234), -1)
                    cv2.putText(frame, feedback['reps'], (30, y_offset - 5),
                               cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame, "No pose detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            
            with metrics_placeholder.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Reps", exercise_analyzer.rep_count)
                with col2:
                    st.metric("Frames Processed", frame_count)
            
            frame_count += 1
            
            time.sleep(0.03)
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def process_video(video_path, exercise_type):
    st.markdown("---")
    st.markdown("## 🔄 Analysis in Progress")
    
    with st.spinner("🤖 Initializing TensorFlow Hub MoveNet..."):
        if st.session_state.tfhub_recognizer is None:
            st.session_state.tfhub_recognizer = TFHubExerciseRecognizer()
        recognizer = st.session_state.tfhub_recognizer
        exercise_analyzer = ExerciseAnalyzer(exercise_type=exercise_type)
        time.sleep(0.5)
    
    st.success("✅ AI Model Ready!")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    time_text = st.empty()
    
    start_time = time.time()
    
    def update_progress(progress):
        progress_bar.progress(progress)
        elapsed = time.time() - start_time
        eta = (elapsed / progress * 100) - elapsed if progress > 0 else 0
        status_text.markdown(f"**Processing:** {progress}%")
        time_text.markdown(f"⏱️ **Elapsed:** {elapsed:.1f}s | **ETA:** {eta:.1f}s")
    
    try:
        output_path, analysis_data = st.session_state.video_processor.process_video_tfhub(
            video_path,
            recognizer,
            exercise_analyzer,
            progress_callback=update_progress
        )
        
        progress_bar.progress(100)
        status_text.markdown("**Status:** ✅ Complete!")
        time_text.markdown(f"⏱️ **Total Time:** {time.time() - start_time:.1f}s")
        
        st.session_state.processed_videos.append({
            'path': output_path,
            'reps': analysis_data['summary']['total_reps'],
            'exercise': exercise_type,
            'timestamp': time.time()
        })
        
        st.balloons()
        display_results(output_path, analysis_data, exercise_type)
        
    except Exception as e:
        st.error(f"❌ **Error:** {str(e)}")
        st.exception(e)

def display_results(output_path, analysis_data, exercise_type):
    st.markdown("---")
    st.markdown("## 🎯 Analysis Results")
    
    exercise_names = {
        'squat': 'Squat',
        'pushup': 'Pushup',
        'plank': 'Plank',
        'lunges': 'Lunges',
        'jumping_jacks': 'J. Jacks',
        'situp': 'Situp',
        'high_knees': 'H. Knees',
        'running': 'Running',
        'walking': 'Walking',
        'burpees': 'Burpees',
        'mountain_climbers': 'Mt. Climb',
        'side_plank': 'S. Plank',
        'crunches': 'Crunches',
        'leg_raises': 'L. Raises',
        'bicycle_crunches': 'Bicycle',
        'standing_knee_raises': 'K. Raise',
        'wall_sit': 'Wall Sit',
        'glute_bridge': 'G. Bridge',
        'jumping': 'Jumping',
        'star_jumps': 'S. Jumps',
        'squat_jumps': 'S. Jumps'
    }
    
    # Format frame count for display
    frames = analysis_data['frames_analyzed']
    if frames >= 10000:
        frame_display = f"{frames/1000:.1f}K"
    elif frames >= 1000:
        frame_display = f"{frames/1000:.1f}K"
    else:
        frame_display = str(frames)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🎯</div>
                <div class="metric-value">{exercise_names.get(exercise_type, exercise_type)}</div>
                <div class="metric-label">Exercise</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🔢</div>
                <div class="metric-value">{analysis_data['summary']['total_reps']}</div>
                <div class="metric-label">Reps</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🎬</div>
                <div class="metric-value">{frame_display}</div>
                <div class="metric-label">Frames</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">✨</div>
                <div class="metric-value">{analysis_data['detection_rate']:.0f}%</div>
                <div class="metric-label">Detect</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    st.markdown("### 🎥 Analyzed Video")
    st.video(output_path)
    
    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
    with col_dl2:
        with open(output_path, 'rb') as f:
            st.download_button(
                label="📥 DOWNLOAD VIDEO",
                data=f,
                file_name=Path(output_path).name,
                mime="video/mp4",
                use_container_width=True
            )
    
    st.markdown("### 💡 Performance Feedback")
    
    if len(analysis_data['feedback_history']) > 0:
        feedback_summary = {}
        for feedback in analysis_data['feedback_history']:
            for key, value in feedback.items():
                if key not in ['reps']:
                    if value not in feedback_summary:
                        feedback_summary[value] = 0
                    feedback_summary[value] += 1
        
        sorted_feedback = sorted(feedback_summary.items(), key=lambda x: x[1], reverse=True)
        
        for feedback, count in sorted_feedback[:5]:
            percentage = (count / len(analysis_data['feedback_history'])) * 100
            
            if "Perfect" in feedback or "Good" in feedback or "Excellent" in feedback:
                css_class = "feedback-positive"
                icon = "✅"
            elif "Watch" in feedback or "Adjust" in feedback or "Keep" in feedback:
                css_class = "feedback-warning"
                icon = "⚠️"
            else:
                css_class = "feedback-negative"
                icon = "❌"
            
            st.markdown(f"""
                <div class="{css_class}">
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span>{icon} <strong>{feedback}</strong></span>
                        <span style='opacity: 0.95;'>{percentage:.1f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    if len(analysis_data['angle_history']) > 0:
        st.markdown("### 📈 Joint Angle Analysis")
        
        import plotly.graph_objects as go
        
        knee_angles = []
        elbow_angles = []
        
        for angles in analysis_data['angle_history']:
            knee_angles.append((angles.get('left_knee', 0) + angles.get('right_knee', 0)) / 2)
            elbow_angles.append((angles.get('left_elbow', 0) + angles.get('right_elbow', 0)) / 2)
        
        frames = list(range(len(knee_angles)))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=frames, y=knee_angles,
            mode='lines',
            name='Knee Angle',
            line=dict(color='#667eea', width=2),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        
        fig.add_trace(go.Scatter(
            x=frames, y=elbow_angles,
            mode='lines',
            name='Elbow Angle',
            line=dict(color='#764ba2', width=2),
            fill='tozeroy',
            fillcolor='rgba(118, 75, 162, 0.1)'
        ))
        
        fig.update_layout(
            title="Joint Angles Over Time",
            xaxis_title="Frame Number",
            yaxis_title="Angle (degrees)",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()