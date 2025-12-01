import cv2
import os
import tempfile
from pathlib import Path

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        
    def save_uploaded_file(self, uploaded_file):
        """Save uploaded file to uploads directory"""
        try:
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            file_path = upload_dir / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            return str(file_path)
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    
    def get_video_properties(self, video_path):
        """Get video properties"""
        cap = cv2.VideoCapture(video_path)
        
        properties = {
            'fps': int(cap.get(cv2.CAP_PROP_FPS)),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return properties
    
    def process_video_tfhub(self, video_path, tfhub_recognizer, exercise_analyzer, progress_callback=None):
        """Process video with TFHub recognizer - Enhanced accuracy and professional overlay"""
        cap = cv2.VideoCapture(video_path)
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"analyzed_{Path(video_path).stem}.mp4"
        output_path = output_dir / output_filename
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        analysis_data = {
            'frames_analyzed': 0,
            'frames_with_pose': 0,
            'feedback_history': [],
            'angle_history': []
        }
        
        frame_count = 0
        
        # Exercise names for display
        exercise_names = {
            'squat': 'Squat  ',
            'pushup': 'Pushup ',
            'plank': 'Plank',
            'lunges': 'Lunges ',
            'jumping_jacks': 'Jumping Jacks ',
            'situp': 'Situp ',
            'high_knees': 'High Knees ',
            'running': 'Running ',
            'walking': 'Walking ',
            'burpees': 'Burpees ',
            'mountain_climbers': 'Mountain Climbers ',
            'side_plank': 'Side Plank ',
            'crunches': 'Crunches ',
            'leg_raises': 'Leg Raises ',
            'bicycle_crunches': 'Bicycle Crunches ',
            'standing_knee_raises': 'Knee Raises ',
            'wall_sit': 'Wall Sit ',
            'glute_bridge': 'Glute Bridge ',
            'jumping': 'Jumping ',
            'star_jumps': 'Star Jumps ',
            'squat_jumps': 'Squat Jumps '
        }
        
        selected_exercise = exercise_names.get(exercise_analyzer.exercise_type, exercise_analyzer.exercise_type)
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Detect with TFHub
            exercise, confidence, keypoints, angles = tfhub_recognizer.detect_exercise(frame)
            
            if keypoints is not None and angles:
                analysis_data['frames_with_pose'] += 1
                
                # Analyze using selected exercise only
                feedback, _ = exercise_analyzer.analyze_frame(angles)
                
                analysis_data['feedback_history'].append(feedback)
                analysis_data['angle_history'].append(angles)
                
                # Draw keypoints
                frame = tfhub_recognizer.draw_keypoints(frame, keypoints)
                
                # Professional overlay
                h, w = frame.shape[:2]
                
                # Semi-transparent background
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, 200), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                y_offset = 40
                
                # Exercise name with shadow effect
                cv2.putText(frame, selected_exercise, (22, y_offset + 2),
                           cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 3, cv2.LINE_AA)
                cv2.putText(frame, selected_exercise, (20, y_offset),
                           cv2.FONT_HERSHEY_DUPLEX, 0.9, (102, 126, 234), 2, cv2.LINE_AA)
                cv2.putText(frame, selected_exercise, (20, y_offset),
                           cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 1, cv2.LINE_AA)
                y_offset += 50
                
                # Feedback with icons and colors
                for key, message in feedback.items():
                    if key in ['reps']:
                        continue
                    
                    if "Perfect" in message or "Good" in message or "Excellent" in message:
                        color = (16, 185, 129)  # Green
                        icon = "✓"
                    elif "Watch" in message or "Adjust" in message or "Keep" in message:
                        color = (245, 158, 11)  # Orange
                        icon = "!"
                    else:
                        color = (239, 68, 68)  # Red
                        icon = "×"
                    
                    # Draw icon
                    cv2.putText(frame, icon, (25, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 3, cv2.LINE_AA)
                    
                    # Draw message with shadow
                    cv2.putText(frame, message, (62, y_offset + 2),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 3, cv2.LINE_AA)
                    cv2.putText(frame, message, (60, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
                    y_offset += 35
                
                # Rep counter with background box
                if 'reps' in feedback:
                    rep_text = feedback['reps']
                    
                    # Get text size
                    text_size = cv2.getTextSize(rep_text, cv2.FONT_HERSHEY_DUPLEX, 1.0, 2)[0]
                    box_width = text_size[0] + 30
                    
                    # Draw box with gradient effect
                    cv2.rectangle(frame, (15, y_offset - 30), (15 + box_width, y_offset + 10),
                                 (102, 126, 234), -1)
                    cv2.rectangle(frame, (15, y_offset - 30), (15 + box_width, y_offset + 10),
                                 (255, 255, 255), 2)
                    
                    # Draw rep text
                    cv2.putText(frame, rep_text, (27, y_offset - 5),
                               cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                # No pose detected overlay
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, 70), (239, 68, 68), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                cv2.putText(frame, "× No Pose Detected", (27, 47),
                           cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 3, cv2.LINE_AA)
                cv2.putText(frame, "× No Pose Detected", (25, 45),
                           cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
            
            out.write(frame)
            analysis_data['frames_analyzed'] += 1
            frame_count += 1
            
            if progress_callback:
                progress = int((frame_count / total_frames) * 100)
                progress_callback(progress)
        
        cap.release()
        out.release()
        
        analysis_data['summary'] = exercise_analyzer.get_summary()
        analysis_data['total_frames'] = total_frames
        analysis_data['detection_rate'] = (analysis_data['frames_with_pose'] / max(analysis_data['frames_analyzed'], 1)) * 100
        
        return str(output_path), analysis_data
    
    def cleanup_temp_files(self, file_path):
        """Remove temporary files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up file: {e}")