import numpy as np
import math

def calculate_angle(point1, point2, point3):
    """
    Calculate angle between three points
    point2 is the vertex of the angle
    
    Args:
        point1, point2, point3: tuples of (x, y) coordinates
    
    Returns:
        angle in degrees
    """
    # Convert to numpy arrays
    a = np.array(point1)
    b = np.array(point2)
    c = np.array(point3)
    
    # Calculate vectors
    ba = a - b
    bc = c - b
    
    # Calculate angle using dot product
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    
    # Clamp to avoid numerical errors
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    angle = np.arccos(cosine_angle)
    
    return np.degrees(angle)

def get_joint_angles(landmarks):
    """
    Calculate relevant joint angles from pose landmarks
    
    Returns:
        dict: Dictionary of joint angles
    """
    angles = {}
    
    # Left elbow angle (shoulder-elbow-wrist)
    angles['left_elbow'] = calculate_angle(
        (landmarks[11].x, landmarks[11].y),  # Left shoulder
        (landmarks[13].x, landmarks[13].y),  # Left elbow
        (landmarks[15].x, landmarks[15].y)   # Left wrist
    )
    
    # Right elbow angle
    angles['right_elbow'] = calculate_angle(
        (landmarks[12].x, landmarks[12].y),  # Right shoulder
        (landmarks[14].x, landmarks[14].y),  # Right elbow
        (landmarks[16].x, landmarks[16].y)   # Right wrist
    )
    
    # Left knee angle (hip-knee-ankle)
    angles['left_knee'] = calculate_angle(
        (landmarks[23].x, landmarks[23].y),  # Left hip
        (landmarks[25].x, landmarks[25].y),  # Left knee
        (landmarks[27].x, landmarks[27].y)   # Left ankle
    )
    
    # Right knee angle
    angles['right_knee'] = calculate_angle(
        (landmarks[24].x, landmarks[24].y),  # Right hip
        (landmarks[26].x, landmarks[26].y),  # Right knee
        (landmarks[28].x, landmarks[28].y)   # Right ankle
    )
    
    # Left hip angle (shoulder-hip-knee)
    angles['left_hip'] = calculate_angle(
        (landmarks[11].x, landmarks[11].y),  # Left shoulder
        (landmarks[23].x, landmarks[23].y),  # Left hip
        (landmarks[25].x, landmarks[25].y)   # Left knee
    )
    
    # Right hip angle
    angles['right_hip'] = calculate_angle(
        (landmarks[12].x, landmarks[12].y),  # Right shoulder
        (landmarks[24].x, landmarks[24].y),  # Right hip
        (landmarks[26].x, landmarks[26].y)   # Right knee
    )
    
    # Back angle (shoulder-hip-vertical)
    # Using left side
    angles['back'] = calculate_angle(
        (landmarks[11].x, landmarks[11].y),  # Left shoulder
        (landmarks[23].x, landmarks[23].y),  # Left hip
        (landmarks[23].x, landmarks[23].y + 0.1)  # Point below hip (vertical reference)
    )
    
    return angles