# 3D Avatar Generator and Customization Platform (Zen/CIS-IEEE challenge )

A full-stack web application that generates personalized 3D avatars using conditional Generative Adversarial Networks (cGAN) and allows users to customize their avatars with clothing, hair, and other features.
## 3D Personalized Avatar Customization Interface Demo
Here is an image of the customization interface for the 3D personalized avatar, which corresponds to 15 personalized body measurements and includes virtual try-on features. 
  ![image](https://github.com/user-attachments/assets/4f76e763-717f-4356-9faa-28c6e495fedd)
## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technical Architecture](#technical-architecture)
- [AI Component of the Project: Avatar Generation Using Generative AI](#ai-component-of-the-project:avatar-generation-using-generative-ai)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Technologies Used](#technologies-used)

## Overview

This platform allows users to generate personalized 3D avatars by inputting their body measurements. The system uses a conditional GAN to create accurate 3D point clouds which are then converted into meshes. Users can customize their avatars with various clothing items, hairstyles, and other features through an interactive 3D interface.

## Features

- **User Authentication**
  - Secure login/signup system
  - Session management
  - Password encryption

- **Avatar Generation**
  - Body measurement input form
  - Real-time 3D avatar generation using cGAN
  - Point cloud to mesh conversion

- **Avatar Customization**
  - Multiple clothing options (dresses, skirts, sweaters)
  - Various hairstyles
  - Skin color selection
  - Size customization for clothing
  - Color options for clothing items

- **Interactive 3D Viewer**
  - Real-time 3D rendering
  - Orbit controls for view manipulation
  - Dynamic lighting system

- **Multilingual Support**
  - English and French interfaces
  - Dynamic language switching

## Technical Architecture

### Backend (Flask)
- **Authentication Module** (`app/routes/auth.py`)
  - Handles user registration and login
  - Session management using Flask-Login

- **Avatar Generation** (`app/utils/avatar_processing.py`)
  - cGAN implementation for point cloud generation
  - Point cloud processing and mesh conversion
  - Uses PyTorch for neural network operations

- **Clothing System** (`app/routes/clothing.py`)
  - Manages clothing model loading and customization
  - Handles size and color modifications

### Frontend
- **3D Rendering** (Three.js)
  - Real-time mesh visualization
  - Dynamic model loading and manipulation
  - Custom shader implementations

- **UI Components** (`static/js/`)
  - Modular JavaScript architecture
  - Event handling for customization options
  - Responsive design implementation



## AI Component of the Project: Avatar Generation Using Generative AI

### Avatar Generation Process

#### Conditional GAN (cGAN) Architecture

This project uses a **Conditional GAN (cGAN)**, where the generator and discriminator are conditioned on input data (15 personalized body measurements). Conditioning ensures that the outputs correspond closely to the given measurements.



#### Generator Network

- **Input:** 15 body measurements (e.g., neck girth, waist girth, thigh girth).
- **Process:**
  - Expands input features through multiple fully connected layers.
  - Applies **Group Normalization (GroupNorm)** for stability and convergence.
  - Uses **SiLU** activation functions for improved non-linearity.
- **Output:** A 3D point cloud with 10,000 points representing the avatar's shape.
- **Final Activation:** **Tanh** to normalize the output values between -1 and 1.



#### Discriminator Network

- **Input:** Both real/generated 3D point clouds and the corresponding body measurements.
- **Process:**
  - Extracts features from the 3D point clouds and measurements in parallel paths.
  - Combines these features for a final classification.
  - Uses **Batch Normalization (BatchNorm)** and **LeakyReLU** activation for robust training.
- **Output:** A probability score indicating whether the input point cloud is real or fake.



### Training Process

1. **Discriminator Training:**
   - Evaluates real point clouds paired with real measurements (high "real" probabilities).
   - Evaluates generated point clouds paired with real measurements (low "real" probabilities).
   - Uses **Binary Cross-Entropy Loss (BCE)** for loss calculation.

2. **Generator Training:**
   - Takes body measurements as input to generate a 3D point cloud.
   - Evaluates generated point clouds using the discriminator (aiming for high "real" probabilities).
   - Includes **Chamfer Distance Loss** to measure similarity between generated and real point clouds.
   - Combines **BCE Loss** and **Chamfer Distance** for the total generator loss.



### Dataset and Preprocessing

#### Input Data

- **CSV File:** Contains 15 body measurements per subject.
- **3D Avatar Files:** Corresponding `.obj` files representing ground truth data.

#### Data Pipeline

1. **Normalization:** Measurements are scaled and normalized for input into the generator.
2. **Point Cloud Conversion:** `.obj` files are parsed into point clouds using **PyTorch3D** for real-data comparison.
3. **Padding:** Point clouds are padded to a fixed size (10,000 points) for uniform input dimensions during training.


### Output

The trained **cGAN** generates 3D avatars based on user-provided measurements. The generated avatars are:
- **Highly detailed:** Contain 10,000 points.
- **Tailored to specific measurements.**
- **Ready for virtual try-on applications,** enabling users to visualize clothing fit on their unique body shapes.


 
## Installation

1. 1. Clone the repository:
   ```bash
   git clone https://github.com/Aideveloper-dev/IEEE_CIS_ZEN_challenge.git
   cd IEEE_CIS_ZEN_challenge
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database:
      ```bash
   flask db upgrade
   ```
4. Run the application:
   ```bash
   python run.py
   ```

## API Documentation

### Authentication Endpoints
- `POST /login` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout

### Avatar Endpoints
- `POST /generate` - Generate new avatar
- `POST /update_cloth` - Update clothing
- `POST /update_feature` - Update avatar features

## Technologies Used

### Backend
- Flask
- PyTorch
- Open3D
- SQLAlchemy
- NumPy
- SciPy

### Frontend
- Three.js
- JavaScript (ES6+)
- HTML5
- CSS3
- WebGL

### Database
- SQLite

### Development Tools
- Flask-Compress
- Flask-Login
- Werkzeug
