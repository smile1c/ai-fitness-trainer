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
    page_title="Fitness Trainer",
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
    st.markdown('<h1 class="main-header">🏋️ AI FITNESS TRAINER</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time Pose Estimation & Exercise Analysis</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        mode = st.selectbox(
            "📹 Mode",
            ["Upload Video", "Webcam (Real-time)"],
            help="Choose input method"
        )
        
        st.markdown("---")
        
        exercise_type = st.selectbox(
            "🎯 Exercise Type",
            list(SUPPORTED_EXERCISES),
            format_func=lambda x: EXERCISE_STANDARDS[x]['name'],
            help="Select the exercise you want to analyze"
        )
        
        st.markdown("---")
        
        st.markdown("### 📊 Supported Exercises")
        categories = {}
        for ex_id, ex_data in EXERCISE_STANDARDS.items():
            cat = ex_data.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(ex_data['name'])
        
        for cat, exercises in categories.items():
            with st.expander(f"📁 {cat.replace('_', ' ').title()} ({len(exercises)})"):
                for ex in exercises:
                    st.markdown(f"• {ex}")
    
    if mode == "Upload Video":
        st.markdown("## 📤 Upload Video")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a video file",
                type=['mp4', 'avi', 'mov', 'mkv'],
                help="Upload a video of you performing the exercise"
            )
        
        with col2:
            st.markdown("""
                <div class="info-card" style="padding: 1rem;">
                    <h4>📝 Tips</h4>
                    <ul style="font-size: 0.85rem;">
                        <li>Full body visible</li>
                        <li>Good lighting</li>
                        <li>Side view recommended</li>
                        <li>Clear background</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        if uploaded_file is not None:
            temp_file = Path("/tmp") / uploaded_file.name
            with open(temp_file, 'wb') as f:
                f.write(uploaded_file.read())
            
            st.markdown("### 🎬 Preview")
            st.video(str(temp_file))
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 ANALYZE VIDEO", use_container_width=True):
                    process_video(str(temp_file), exercise_type)
    
    else:  # Webcam mode
        st.markdown("## 🎥 Real-time Webcam Analysis")
        
        st.markdown("""
            <div class="info-card">
                <h3>📋 Instructions</h3>
                <ul>
                    <li>Position yourself 2-3 meters from the camera</li>
                    <li>Ensure your full body is visible in the frame</li>
                    <li>Stand in front of a clear background</li>
                    <li>Maintain good lighting</li>
                    <li>Start the webcam and begin exercising!</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎬 START WEBCAM", use_container_width=True):
                process_webcam_realtime(exercise_type)

def process_webcam_realtime(exercise_type):
    """Real-time webcam processing with improved UI"""
    st.markdown("---")
    st.markdown("## 🎥 Real-time Analysis")
    
    with st.spinner("🤖 Initializing AI Model..."):
        if st.session_state.tfhub_recognizer is None:
            st.session_state.tfhub_recognizer = TFHubExerciseRecognizer()
        recognizer = st.session_state.tfhub_recognizer
        exercise_analyzer = ExerciseAnalyzer(exercise_type=exercise_type)
        time.sleep(0.5)
    
    st.success("✅ Ready! Starting webcam...")
    
    video_placeholder = st.empty()
    metrics_placeholder = st.empty()
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("❌ Cannot access webcam. Please check permissions.")
        return
    
    frame_count = 0
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Extract keypoints
            keypoints = recognizer.extract_keypoints(frame)
            
            if keypoints is not None:
                # Calculate angles
                angles = recognizer.calculate_angles(keypoints)
                
                # Analyze frame
                feedback, _ = exercise_analyzer.analyze_frame(
                    angles, 
                    detected_exercise=exercise_type,
                    confidence=1.0
                )
                
                # Draw skeleton
                frame = recognizer.draw_keypoints(frame, keypoints)
                
                # ✅ IMPROVED UI - Larger fonts, better layout, English only
                h, w = frame.shape[:2]
                
                # Draw semi-transparent background (taller)
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, 300), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                y_offset = 55
                
                # 1. Exercise Name (Largest, English only, uppercase)
                exercise_names = {
                    'squat': 'SQUAT',
                    'pushup': 'PUSH-UP',
                    'plank': 'PLANK',
                    'lunges': 'LUNGES',
                    'jumping_jacks': 'JUMPING JACKS',
                    'situp': 'SIT-UP',
                    'high_knees': 'HIGH KNEES',
                    'burpees': 'BURPEES',
                    'mountain_climbers': 'MOUNTAIN CLIMBERS',
                    'side_plank': 'SIDE PLANK',
                    'running': 'RUNNING',
                    'crunches': 'CRUNCHES',
                    'leg_raises': 'LEG RAISES',
                    'bicycle_crunches': 'BICYCLE CRUNCHES',
                    'standing_knee_raises': 'KNEE RAISES',
                    'wall_sit': 'WALL SIT',
                    'glute_bridge': 'GLUTE BRIDGE',
                    'jumping': 'JUMPING',
                    'star_jumps': 'STAR JUMPS',
                    'squat_jumps': 'SQUAT JUMPS'
                }
                
                name = exercise_names.get(exercise_type, exercise_type.upper())
                cv2.putText(frame, name, (30, y_offset),
                           cv2.FONT_HERSHEY_DUPLEX, 1.6, (255, 255, 0), 4, cv2.LINE_AA)
                y_offset += 70
                
                # 2. Feedback Messages (Larger with icons and colors)
                for key, message in feedback.items():
                    if key in ['detected', 'reps']:
                        continue
                    
                    # Choose color based on feedback
                    if "Perfect" in message or "Good" in message or "Excellent" in message:
                        color = (0, 255, 0)  # Green
                        icon = "✓"
                    elif "Watch" in message or "Adjust" in message or "Keep" in message:
                        color = (0, 165, 255)  # Orange
                        icon = "!"
                    else:
                        color = (0, 0, 255)  # Red
                        icon = "✗"
                    
                    # Draw message with icon (larger)
                    display_text = f"{icon} {message}"
                    cv2.putText(frame, display_text, (30, y_offset),
                               cv2.FONT_HERSHEY_DUPLEX, 1.15, color, 3, cv2.LINE_AA)
                    y_offset += 52
                
                # 3. Rep Counter (Largest with green box)
                if 'reps' in feedback:
                    # Draw green box background
                    cv2.rectangle(frame, (20, y_offset - 38), (300, y_offset + 12), 
                                 (0, 255, 0), 3)
                    cv2.rectangle(frame, (22, y_offset - 36), (298, y_offset + 10), 
                                 (0, 120, 0), -1)
                    
                    # Draw REPS text (white, very large)
                    cv2.putText(frame, feedback['reps'], (35, y_offset - 5),
                               cv2.FONT_HERSHEY_DUPLEX, 1.6, (255, 255, 255), 4, cv2.LINE_AA)
            
            else:
                # No pose detected
                cv2.putText(frame, "NO POSE DETECTED", (30, 70),
                           cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 0, 255), 4, cv2.LINE_AA)
                cv2.putText(frame, "Please step into frame", (30, 120),
                           cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 3, cv2.LINE_AA)
            
            # Convert BGR to RGB for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Display frame
            video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            
            # Update metrics
            with metrics_placeholder.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Reps", exercise_analyzer.rep_count)
                with col2:
                    st.metric("Frames Processed", frame_count)
            
            frame_count += 1
            
            # Control frame rate (~30 FPS)
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