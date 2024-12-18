from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
import pandas as pd
from scipy.spatial import distance
import os
import numpy as np
import open3d as o3d
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import torch
import torch.nn as nn
import numpy as np
from flask import Flask, request, render_template
import open3d as o3d
from flask_compress import Compress

app = Flask(__name__)
Compress(app)

# Add compression configuration
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/javascript', 'application/json']
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Configuration de la clé secrète et de la base de données
app.config['SECRET_KEY'] = 'b9e7c45dacc7041a402b95ed81f2895d'  # Remplacez par votre clé générée
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Gestion de la connexion
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirige vers login si non authentifié

# Définition des chemins de fichiers
CSV_FILE_PATH = "Body_Measurements_output_modified2.csv"
OBJ_FOLDER_PATH = "static/3D_AVATARS"
CLOTHES_FOLDER_PATH = "static/3D_CLOTHING"

# Charger le fichier CSV
df = pd.read_csv(CSV_FILE_PATH)

class Generator(nn.Module):
    def __init__(self, num_points, measurement_dim):
        super(Generator, self).__init__()
        self.num_points = num_points
        
        self.fc1 = nn.Sequential(
            nn.Linear(measurement_dim, 512),
            nn.GroupNorm(32, 512),  # 32 groups
            nn.SiLU(),
            nn.Linear(512, 1024),
            nn.GroupNorm(32, 1024),
            nn.SiLU(),
            nn.Linear(1024, 2048),
            nn.GroupNorm(32, 2048),
            nn.SiLU(),
            nn.Linear(2048, 4096),
            nn.GroupNorm(32, 4096),
            nn.SiLU()
        )

        self.fc2 = nn.Sequential(
            nn.Linear(4096, num_points * 3),
            nn.Tanh()  # Output between -1 and 1
        )

    def forward(self, measurements):
        x = self.fc1(measurements)
        pointcloud = self.fc2(x).view(-1, self.num_points, 3)
        return pointcloud

# Define the Discriminator for cGAN
class Discriminator(nn.Module):
    def __init__(self, num_points, measurement_dim):
        super(Discriminator, self).__init__()
        self.fc1_pointcloud = nn.Sequential(
            nn.Linear(num_points * 3, 4096),
            nn.BatchNorm1d(4096),
            nn.LeakyReLU(0.2),
            nn.Linear(4096, 2048),
            nn.BatchNorm1d(2048),
            nn.LeakyReLU(0.2),
            nn.Linear(2048, 1024),
            nn.BatchNorm1d(1024),
            nn.LeakyReLU(0.2)
        )
        
        self.fc1_measurements = nn.Sequential(
            nn.Linear(measurement_dim, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.2)
        )
        
        self.fc2 = nn.Sequential(
            nn.Linear(1024 + 512, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 1),
            nn.Sigmoid()  # Output a probability
        )
    def forward(self, pointcloud, measurements):
        pointcloud_flat = pointcloud.view(pointcloud.size(0), -1)
        pc_features = self.fc1_pointcloud(pointcloud_flat)
        meas_features = self.fc1_measurements(measurements)
        combined_features = torch.cat((pc_features, meas_features), dim=1)
        return self.fc2(combined_features)

# Load the pretrained Generator
def load_pretrained_generator(model, checkpoint_path, device):
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))

# Generate a point cloud using the cGAN Generator
def generate_point_cloud_from_cgan(generator, device, example_measurements):
    generator.eval()
    with torch.no_grad():
        measurements = torch.tensor(example_measurements, dtype=torch.float32).to(device).unsqueeze(0)
        generated_point_cloud = generator(measurements)
        return generated_point_cloud[0].cpu().numpy()

# Point cloud processing functions (unchanged)
def filter_noise(point_cloud, nb_neighbors=20, std_ratio=20.0):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)
    cl, ind = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    filtered_point_cloud = pcd.select_by_index(ind)
    return np.asarray(filtered_point_cloud.points)

def densify_point_cloud(point_cloud, voxel_size=0.001):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)
    pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    return np.asarray(pcd.points)

def create_mesh_from_point_cloud(point_cloud, target_triangles=9200, target_vertices=27000):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)
    pcd.estimate_normals()
    pcd.orient_normals_consistent_tangent_plane(1000)
    mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=14)
    mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=target_triangles)
    while len(mesh.vertices) < target_vertices:
        mesh = mesh.subdivide_midpoint(number_of_iterations=1)
    mesh = mesh.filter_smooth_simple(number_of_iterations=5)
    return mesh
# Modèles pour la base de données

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect')
            return render_template('login.html')
    return render_template('login.html')
@app.route('/view_users')
def view_users():
    users = User.query.all()
    user_data = [{'ID': user.id, 'Name': user.name, 'Surname': user.surname, 'Email': user.email, 'password': user.password} for user in users]
    return jsonify(user_data)

# Route d'inscription
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà enregistré')
            return redirect(url_for('signup'))
        
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Inscription réussie ! Vous pouvez maintenant vous connecter')
        return redirect(url_for('login'))
    return render_template('signup.html')

# Route de déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Page principale
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# Autres routes existantes, incluant la génération de modèle et la sélection de vêtements...

# Load the CSV file

@app.route('/generate', methods=['POST'])
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

        return redirect(url_for('customize'))
    else:
        return jsonify({'error': 'No matching 3D avatar found'}), 404

@app.route('/select_cloth', methods=['POST'])
def select_cloth():
    selected_cloth = request.form.get('cloth_type')
    cloth_size = request.form.get('cloth_size')
    cloth_vertices = []
    cloth_triangles = []

    if selected_cloth and cloth_size:
        cloth_file_name = "dress_M.obj"
        cloth_file_name = f"{selected_cloth}_{cloth_size}.obj"  # e.g., 'dress_L.obj'
        cloth_file_path = os.path.join(CLOTHES_FOLDER_PATH, cloth_file_name)

        if os.path.exists(cloth_file_path):
            cloth_mesh = o3d.io.read_triangle_mesh(cloth_file_path)
            cloth_vertices = np.asarray(cloth_mesh.vertices).tolist()
            cloth_triangles = np.asarray(cloth_mesh.triangles).tolist()
    cloth_file_path = "static\3D_CLOTHING\dress_M.obj"
    cloth_mesh = o3d.io.read_triangle_mesh(cloth_file_path)
    cloth_vertices = np.asarray(cloth_mesh.vertices).tolist()
    cloth_triangles = np.asarray(cloth_mesh.triangles).tolist()    
    return render_template(
        'view_3model.html',
        cloth_vertices=cloth_vertices if cloth_vertices else [],
        cloth_triangles=cloth_triangles if cloth_triangles else []
    )

# New /update_cloth route to handle clothing updates
@app.route('/update_cloth', methods=['POST'])
def update_cloth():
    data = request.get_json()
    selected_cloth = data.get('cloth')
    cloth_size = data.get('size')

    if selected_cloth and cloth_size:
        cloth_file_name = f"{selected_cloth}_{cloth_size}.obj"
        cloth_file_path = os.path.join(CLOTHES_FOLDER_PATH, cloth_file_name)

        if os.path.exists(cloth_file_path):
            # Store only the file path in session
            session['cloth_file'] = cloth_file_path
            
            # Load and return the cloth data
            cloth_mesh = o3d.io.read_triangle_mesh(cloth_file_path)
            cloth_vertices = np.asarray(cloth_mesh.vertices).tolist()
            cloth_triangles = np.asarray(cloth_mesh.triangles).tolist()

            return jsonify({
                'success': True,
                'cloth_vertices': cloth_vertices,
                'cloth_triangles': cloth_triangles
            })
        else:
            return jsonify({'error': 'Clothing model not found'}), 404
    else:
        return jsonify({'error': 'Invalid cloth type or size'}), 400

@app.route('/customize')
@login_required
def customize():
    avatar_file = session.get('avatar_file')
    
    if not avatar_file:
        flash('Please generate an avatar first')
        return redirect(url_for('index'))
    
    try:
        # Load avatar data
        avatar_mesh = o3d.io.read_triangle_mesh(avatar_file)
        vertices = np.asarray(avatar_mesh.vertices).tolist()
        triangles = np.asarray(avatar_mesh.triangles).tolist()
        
        avatar_data = {
            'vertices': vertices,
            'triangles': triangles
        }
        
        return render_template('customize.html', avatar_data=avatar_data)
        
    except Exception as e:
        print(f"Error in customize route: {str(e)}")
        flash('Error loading avatar data')
        return redirect(url_for('index'))

@app.route('/static/models/hair/<filename>')
def serve_hair_model(filename):
    return send_from_directory('static/models/hair', filename)

@app.route('/static/images/hair/<filename>')
def serve_hair_preview(filename):
    return send_from_directory('static/images/hair', filename)

# Add a route to save customizations
@app.route('/save_customizations', methods=['POST'])
def save_customizations():
    customization_data = request.get_json()
    # Save the customization data to your database or session
    # ... implementation here ...
    
    return jsonify({'success': True})

@app.route('/update_feature', methods=['POST'])
def update_feature():
    data = request.get_json()
    feature_type = data.get('type')
    feature_value = data.get('value')
    
    try:
        # Get the current avatar mesh
        avatar_file = session.get('avatar_file')
        if not avatar_file:
            return jsonify({'error': 'No avatar found'}), 404
            
        avatar_mesh = o3d.io.read_triangle_mesh(avatar_file)
        vertices = np.asarray(avatar_mesh.vertices)
        
        # Update vertices based on feature type
        if feature_type == 'hair':
            # Load the appropriate hair style vertices
            hair_style_file = f'path/to/hair/styles/{feature_value}.obj'
            hair_mesh = o3d.io.read_triangle_mesh(hair_style_file)
            hair_vertices = np.asarray(hair_mesh.vertices)
            
            # Update specific vertex positions for hair
            # You'll need to define which vertices correspond to hair
            hair_vertex_indices = get_hair_vertices()  # Define this function
            vertices[hair_vertex_indices] = hair_vertices
            
        elif feature_type == 'eyes':
            # Similar logic for eyes
            pass
            
        # Update the mesh
        avatar_mesh.vertices = o3d.utility.Vector3dVector(vertices)
        o3d.io.write_triangle_mesh(avatar_file, avatar_mesh)
        
        # Return updated vertex data to client
        return jsonify({
            'success': True,
            'vertices': vertices.tolist()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

@app.route('/static/images/hair/<path:filename>')
def serve_hair_images(filename):
    return send_from_directory('static/images/hair', filename, mimetype='image/jpeg')

@app.route('/static/models/hair/<path:filename>')
def serve_hair_models(filename):
    return send_from_directory('static/models/hair', filename)

if __name__ == '__main__':
    app.run(debug=True)
