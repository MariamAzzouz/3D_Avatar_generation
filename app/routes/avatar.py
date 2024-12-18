from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required
import pandas as pd
from scipy.spatial import distance
import open3d as o3d
import numpy as np
import os
from app2.config import CSV_FILE_PATH, OBJ_FOLDER_PATH

avatar = Blueprint('avatar', __name__)

# Charger le fichier CSV
df = pd.read_csv(CSV_FILE_PATH)

@avatar.route('/avatar.index')
@login_required
def index():
    return render_template('index.html')

@avatar.route('/generate', methods=['POST'])
@login_required
def generate():
    try:
        # Collect input measurements from the form
        input_measurements = {
            'Gender': request.form['Gender'],
            'Neck girth': float(request.form['NeckGirth']),
            'Back neck point to waist': float(request.form['BackNeckToWaist']),
            'Upper arm girth R': float(request.form['UpperArmGirthR']),
            'Upper arm girth L': float(request.form['UpperArmGirthL']),
            'Back neck point to wrist R': float(request.form['BackNeckToWristR']),
            'Back neck point to wrist L': float(request.form['BackNeckToWristL']),
            'Across back shoulder width': float(request.form['AcrossShoulderWidth']),
            'Bust girth': float(request.form['BustGirth']),
            'Waist girth': float(request.form['WaistGirth']),
            'Hip girth': float(request.form['HipGirth']),
            'Thigh girth R': float(request.form['ThighGirthR']),
            'Thigh girth L': float(request.form['ThighGirthL']),
            'Total crotch length': float(request.form['TotalCrotchLength']),
            'Inside leg height': float(request.form['InsideLegHeight'])
        }
    except ValueError:
        return jsonify({'error': 'Invalid input: Please ensure all measurements are valid numbers'}), 400

    # Filter DataFrame based on gender
    filtered_df = df[df['Gendre'] == input_measurements['Gender']]

    measurement_columns = ['Neck girth', 'Back neck point to waist', 'Upper arm girth R', 'Upper arm girth L',
                           'Back neck point to wrist R', 'Back neck point to wrist L', 'Across back shoulder width',
                           'Bust girth', 'Waist girth', 'Hip girth', 'Thigh girth R', 'Thigh girth L',
                           'Total crotch length', 'Inside leg height']
    
    input_df = pd.DataFrame([input_measurements], columns=['Gender'] + measurement_columns).iloc[:, 1:]

    # Calculate Euclidean distances to find the closest match
    distances = filtered_df[measurement_columns].apply(
        lambda row: distance.euclidean(row.values, input_df.iloc[0].values), axis=1)

    closest_index = distances.idxmin()
    closest_match = filtered_df.loc[closest_index]
    processor = closest_match['Processor']
    subject = closest_match['Subject']
    measuring_station = closest_match['Measuring station']

    # Construct the avatar file name based on the match
    file_prefix = (
        f"{subject}_R1S1_{measuring_station}_{processor}"
        if "SizeStream" in processor and "SS20" in measuring_station 
        else f"{subject}_R1_{measuring_station}_{processor}"
    )

    avatar_file_name = next(
        (file for file in os.listdir(OBJ_FOLDER_PATH) if file.startswith(file_prefix) and file.endswith(".obj")),
        None
    )

    if avatar_file_name:
        avatar_file_path = os.path.join(OBJ_FOLDER_PATH, avatar_file_name)
        mesh = o3d.io.read_triangle_mesh(avatar_file_path)
        vertices = np.asarray(mesh.vertices).tolist()
        triangles = np.asarray(mesh.triangles).tolist()

        # Load default clothing
        cloth_file_path = "static/3D_CLOTHING/dress_M.obj"
        cloth_mesh = o3d.io.read_triangle_mesh(cloth_file_path)
        cloth_vertices = np.asarray(cloth_mesh.vertices).tolist()
        cloth_triangles = np.asarray(cloth_mesh.triangles).tolist()

        # Store only the file paths in session instead of the full data
        session['avatar_file'] = avatar_file_path
        session['cloth_file'] = cloth_file_path

        return redirect(url_for('avatar.customize'))
    else:
        return jsonify({'error': 'No matching 3D avatar found'}), 404

@avatar.route('/customize')
@login_required
def customize():
    avatar_file = session.get('avatar_file')
    if not avatar_file:
        flash('Please generate an avatar first')
        return redirect(url_for('avatar.index'))
    
    try:
        avatar_mesh = o3d.io.read_triangle_mesh(avatar_file)
        vertices = np.asarray(avatar_mesh.vertices).tolist()
        triangles = np.asarray(avatar_mesh.triangles).tolist()
        
        avatar_data = {
            'vertices': vertices,
            'triangles': triangles
        }
        return render_template('customize.html', avatar_data=avatar_data)
    except Exception as e:
        flash('Error loading avatar data')
        return redirect(url_for('avatar.index')) 