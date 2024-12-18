from flask import Blueprint, request, jsonify, session, send_from_directory
import open3d as o3d
import numpy as np
import os
from app.config import CLOTHES_FOLDER_PATH

clothing = Blueprint('clothing', __name__)

@clothing.route('/update_cloth', methods=['POST'])
def update_cloth():
    print("Received update_cloth request")
    data = request.get_json()
    print(f"Request data: {data}")
    
    selected_cloth = data.get('cloth')
    cloth_size = data.get('size')
    
    if not all([selected_cloth, cloth_size]):
        print("Missing cloth type or size")
        return jsonify({'error': 'Invalid cloth type or size'}), 400

    cloth_file_name = f"{selected_cloth}_{cloth_size}.obj"
    cloth_file_path = os.path.join(CLOTHES_FOLDER_PATH, cloth_file_name)
    print(f"Looking for file: {cloth_file_path}")

    if not os.path.exists(cloth_file_path):
        print(f"File not found: {cloth_file_path}")
        return jsonify({'error': f'Clothing model not found: {cloth_file_name}'}), 404

    try:
        cloth_mesh = o3d.io.read_triangle_mesh(cloth_file_path)
        cloth_vertices = np.asarray(cloth_mesh.vertices).tolist()
        cloth_triangles = np.asarray(cloth_mesh.triangles).tolist()

        response_data = {
            'success': True,
            'cloth_vertices': cloth_vertices,
            'cloth_triangles': cloth_triangles
        }
        print("Successfully processed cloth model")
        return jsonify(response_data)
    except Exception as e:
        print(f"Error processing cloth model: {str(e)}")
        return jsonify({'error': f'Error processing cloth model: {str(e)}'}), 500

@clothing.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename) 
