
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import uuid
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import pdfplumber
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

app = Flask(__name__)
app.config['SECRET_KEY'] = 'po-tech-python-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///po_tech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Create upload directories
UPLOAD_FOLDER = 'uploads'
PDF_FOLDER = 'uploads/pdfs'
ANIMATION_FOLDER = 'uploads/animations'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(ANIMATION_FOLDER, exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserPDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    download_count = db.Column(db.Integer, default=0)

class Animation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    animation_type = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    thumbnail_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)

# Animation Functions
class AnimationCreator:
    @staticmethod
    def create_sine_wave_animation():
        fig, ax = plt.subplots(figsize=(12, 8))
        x = np.linspace(0, 4*np.pi, 200)
        line, = ax.plot([], [], 'b-', linewidth=3)
        ax.set_xlim(0, 4*np.pi)
        ax.set_ylim(-2, 2)
        ax.set_title('Smooth Sine Wave Animation', fontsize=18, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f8f9fa')
        
        def animate(frame):
            # Smooth phase shift for fluid motion
            phase = frame * 0.15
            y = np.sin(x + phase) * np.exp(-0.1 * np.abs(x - 2*np.pi))
            line.set_data(x, y)
            return line,
        
        anim = animation.FuncAnimation(fig, animate, frames=300, interval=33, blit=True)
        filename = f"sine_wave_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        anim.save(filepath, writer='pillow', fps=30)
        plt.close()
        return filename

    @staticmethod
    def create_spiral_animation():
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_title('Smooth Spiral Animation', fontsize=18, fontweight='bold')
        ax.set_aspect('equal')
        ax.set_facecolor('#f0f0f0')
        
        line, = ax.plot([], [], 'r-', linewidth=2)
        
        def animate(frame):
            t = np.linspace(0, 4*np.pi, 200)
            r = np.linspace(0.1, 4, 200)
            
            # Smooth rotation
            rotation = frame * 0.1
            x = r * np.cos(t + rotation)
            y = r * np.sin(t + rotation)
            
            line.set_data(x, y)
            return line,
        
        anim = animation.FuncAnimation(fig, animate, frames=200, interval=50, blit=True)
        filename = f"spiral_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        anim.save(filepath, writer='pillow', fps=20)
        plt.close()
        return filename

    @staticmethod
    def create_wave_interference():
        fig, ax = plt.subplots(figsize=(12, 8))
        x = np.linspace(0, 4*np.pi, 300)
        line1, = ax.plot([], [], 'b-', linewidth=2, alpha=0.7, label='Wave 1')
        line2, = ax.plot([], [], 'r-', linewidth=2, alpha=0.7, label='Wave 2')
        line3, = ax.plot([], [], 'g-', linewidth=3, label='Interference')
        
        ax.set_xlim(0, 4*np.pi)
        ax.set_ylim(-3, 3)
        ax.set_title('Wave Interference Animation', fontsize=18, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_facecolor('#f8f9fa')
        
        def animate(frame):
            phase = frame * 0.2
            wave1 = np.sin(x + phase)
            wave2 = np.sin(2*x - phase)
            interference = wave1 + wave2
            
            line1.set_data(x, wave1)
            line2.set_data(x, wave2)
            line3.set_data(x, interference)
            return line1, line2, line3
        
        anim = animation.FuncAnimation(fig, animate, frames=200, interval=50, blit=True)
        filename = f"interference_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        anim.save(filepath, writer='pillow', fps=20)
        plt.close()
        return filename

    @staticmethod
    def create_particle_system():
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_title('Particle System Animation', fontsize=18, fontweight='bold')
        ax.set_facecolor('#000011')
        
        # Create particles
        num_particles = 50
        particles = np.random.rand(num_particles, 2) * [10, 8]
        velocities = (np.random.rand(num_particles, 2) - 0.5) * 0.5
        colors = np.random.rand(num_particles)
        
        scat = ax.scatter(particles[:, 0], particles[:, 1], 
                         s=50, c=colors, cmap='plasma', alpha=0.7)
        
        def animate(frame):
            nonlocal particles, velocities
            
            # Update particle positions
            particles += velocities
            
            # Bounce off walls
            particles[:, 0] = np.where(particles[:, 0] < 0, -particles[:, 0], particles[:, 0])
            particles[:, 0] = np.where(particles[:, 0] > 10, 20 - particles[:, 0], particles[:, 0])
            particles[:, 1] = np.where(particles[:, 1] < 0, -particles[:, 1], particles[:, 1])
            particles[:, 1] = np.where(particles[:, 1] > 8, 16 - particles[:, 1], particles[:, 1])
            
            # Update velocities for smooth motion
            velocities += (np.random.rand(num_particles, 2) - 0.5) * 0.02
            velocities *= 0.99  # Damping
            
            scat.set_offsets(particles)
            return scat,
        
        anim = animation.FuncAnimation(fig, animate, frames=300, interval=33, blit=True)
        filename = f"particles_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        anim.save(filepath, writer='pillow', fps=30)
        plt.close()
        return filename
    
    @staticmethod
    def create_data_visualization(data_points):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Bar chart animation
        categories = ['Math', 'Science', 'English', 'History', 'Art']
        values = data_points if data_points else [85, 92, 78, 88, 90]
        
        bars = ax1.bar(categories, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        ax1.set_title('Student Performance', fontsize=14)
        ax1.set_ylabel('Scores')
        ax1.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value}%', ha='center', va='bottom')
        
        # Pie chart
        ax2.pie(values, labels=categories, autopct='%1.1f%%', startangle=90,
                colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        ax2.set_title('Score Distribution', fontsize=14)
        
        plt.tight_layout()
        filename = f"data_viz_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        return filename
    
    @staticmethod
    def create_educational_banner(title, subtitle):
        # Create a professional educational banner
        width, height = 1200, 400
        img = Image.new('RGB', (width, height), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add gradient background
        for y in range(height):
            color_intensity = int(248 - (y / height) * 50)
            for x in range(width):
                draw.point((x, y), fill=(color_intensity, color_intensity + 5, 255))
        
        # Add title and subtitle
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        
        draw.text((title_x, 120), title, fill='#2c3e50', font=title_font)
        draw.text((subtitle_x, 200), subtitle, fill='#34495e', font=subtitle_font)
        
        # Add decorative elements
        draw.ellipse([50, 50, 150, 150], fill='#3498db', outline='#2980b9', width=3)
        draw.ellipse([width-150, 50, width-50, 150], fill='#e74c3c', outline='#c0392b', width=3)
        
        filename = f"banner_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        img.save(filepath, quality=95)
        return filename
    
    @staticmethod
    def create_smooth_wave_animation():
        """Create smooth multi-wave animation with easing"""
        fig, ax = plt.subplots(figsize=(12, 8))
        x = np.linspace(0, 4*np.pi, 200)
        
        # Initialize multiple wave lines
        line1, = ax.plot([], [], 'b-', linewidth=3, label='Primary Wave', alpha=0.8)
        line2, = ax.plot([], [], 'r-', linewidth=2, label='Harmonic', alpha=0.7)
        line3, = ax.plot([], [], 'g-', linewidth=2, label='Phase Wave', alpha=0.6)
        
        ax.set_xlim(0, 4*np.pi)
        ax.set_ylim(-3, 3)
        ax.set_title('Smooth Multi-Wave Animation', fontsize=18, fontweight='bold')
        ax.set_xlabel('X (radians)', fontsize=14)
        ax.set_ylabel('Amplitude', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        
        # Add background gradient
        ax.set_facecolor('#f8f9fa')
        
        def animate(frame):
            # Smooth easing function
            t = frame / 100.0
            easing = 0.5 * (1 - np.cos(np.pi * (t % 1)))
            
            # Multiple wave equations with phase shifts
            y1 = np.sin(x + t * 2) * (1 + 0.3 * easing)
            y2 = 0.7 * np.sin(2*x + t * 3) * (1 + 0.2 * easing)
            y3 = 0.5 * np.sin(0.5*x - t * 1.5) * (1 + 0.4 * easing)
            
            line1.set_data(x, y1)
            line2.set_data(x, y2)
            line3.set_data(x, y3)
            
            return line1, line2, line3
        
        anim = animation.FuncAnimation(fig, animate, frames=300, interval=50, blit=True, repeat=True)
        filename = f"smooth_wave_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        anim.save(filepath, writer='pillow', fps=24)
        plt.close()
        return filename
    
    @staticmethod
    def create_particle_system():
        """Create animated particle system"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Initialize particles
        n_particles = 50
        particles = np.random.rand(n_particles, 2) * 10
        velocities = (np.random.rand(n_particles, 2) - 0.5) * 0.5
        colors = np.random.rand(n_particles)
        sizes = np.random.rand(n_particles) * 100 + 50
        
        scat = ax.scatter(particles[:, 0], particles[:, 1], c=colors, s=sizes, 
                         alpha=0.7, cmap='viridis')
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_title('Particle System Animation', fontsize=16, fontweight='bold')
        ax.set_facecolor('#1a1a1a')
        
        def animate(frame):
            nonlocal particles, velocities
            
            # Update particle positions
            particles += velocities
            
            # Bounce off walls
            for i in range(n_particles):
                if particles[i, 0] <= 0 or particles[i, 0] >= 10:
                    velocities[i, 0] *= -0.9
                    particles[i, 0] = np.clip(particles[i, 0], 0, 10)
                if particles[i, 1] <= 0 or particles[i, 1] >= 10:
                    velocities[i, 1] *= -0.9
                    particles[i, 1] = np.clip(particles[i, 1], 0, 10)
            
            # Update scatter plot
            scat.set_offsets(particles)
            
            # Add slight rotation to colors
            new_colors = (colors + frame * 0.01) % 1
            scat.set_array(new_colors)
            
            return scat,
        
        anim = animation.FuncAnimation(fig, animate, frames=400, interval=40, blit=True)
        filename = f"particles_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        anim.save(filepath, writer='pillow', fps=25)
        plt.close()
        return filename
    
    @staticmethod
    def create_3d_rotation():
        """Create smooth 3D rotation animation"""
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create 3D data
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        
        def animate(frame):
            ax.clear()
            
            # Smooth rotation
            elevation = 20 + 15 * np.sin(frame * 0.05)
            azimuth = frame * 2
            
            ax.plot_surface(x, y, z, alpha=0.8, cmap='plasma')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('3D Sphere Rotation', fontsize=14, fontweight='bold')
            ax.view_init(elev=elevation, azim=azimuth)
            
            # Set consistent limits
            ax.set_xlim([-1, 1])
            ax.set_ylim([-1, 1])
            ax.set_zlim([-1, 1])
        
        anim = animation.FuncAnimation(fig, animate, frames=180, interval=80)
        filename = f"3d_rotation_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        anim.save(filepath, writer='pillow', fps=15)
        plt.close()
        return filename
    
    @staticmethod
    def create_morphing_shapes():
        """Create smooth morphing geometric shapes"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        def animate(frame):
            ax.clear()
            
            # Parameters for morphing
            t = frame / 100.0
            n_points = 100
            theta = np.linspace(0, 2*np.pi, n_points)
            
            # Morph between circle, square, and triangle
            circle_r = 1
            square_factor = 0.3 * (1 + np.sin(t * 2))
            triangle_factor = 0.3 * (1 + np.cos(t * 3))
            
            # Create morphing radius
            r = circle_r + square_factor * np.abs(np.sin(4 * theta)) + \
                triangle_factor * np.abs(np.sin(3 * theta))
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Create gradient fill
            colors = plt.cm.rainbow(np.linspace(0, 1, n_points))
            
            ax.fill(x, y, alpha=0.7, color=colors[int(t * 20) % len(colors)])
            ax.plot(x, y, 'k-', linewidth=3)
            
            ax.set_xlim(-2, 2)
            ax.set_ylim(-2, 2)
            ax.set_aspect('equal')
            ax.set_title('Morphing Geometric Shapes', fontsize=16, fontweight='bold')
            ax.set_facecolor('#f0f0f0')
            ax.grid(True, alpha=0.3)
        
        anim = animation.FuncAnimation(fig, animate, frames=200, interval=75)
        filename = f"morphing_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        anim.save(filepath, writer='pillow', fps=20)
        plt.close()
        return filename

# Routes
@app.route('/')
def home():
    return jsonify({
        "message": "Po-Tech Python Backend API",
        "version": "1.0.0",
        "features": ["PDF Upload", "Animations", "User Management"],
        "endpoints": {
            "auth": "/api/auth/*",
            "pdf": "/api/pdf/*",
            "animations": "/api/animations/*"
        }
    })

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': {'id': user.id, 'username': user.username, 'email': user.email}
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {'id': user.id, 'username': user.username, 'email': user.email}
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PDF Upload Routes
@app.route('/api/pdf/upload', methods=['POST'])
@jwt_required()
def upload_pdf():
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(PDF_FOLDER, unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Extract PDF metadata
        description = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                if pdf.pages:
                    first_page = pdf.pages[0]
                    text = first_page.extract_text()
                    description = text[:200] + "..." if len(text) > 200 else text
        except Exception as e:
            description = "Could not extract PDF content"
        
        # Save to database
        user_pdf = UserPDF(
            user_id=user_id,
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            category=request.form.get('category', 'General'),
            description=description,
            is_public=request.form.get('is_public', 'false').lower() == 'true'
        )
        db.session.add(user_pdf)
        db.session.commit()
        
        return jsonify({
            'message': 'PDF uploaded successfully',
            'file_id': user_pdf.id,
            'filename': filename,
            'size': file_size,
            'description': description
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdf/my-files', methods=['GET'])
@jwt_required()
def get_user_pdfs():
    try:
        user_id = get_jwt_identity()
        pdfs = UserPDF.query.filter_by(user_id=user_id).order_by(UserPDF.upload_date.desc()).all()
        
        pdf_list = []
        for pdf in pdfs:
            pdf_list.append({
                'id': pdf.id,
                'original_filename': pdf.original_filename,
                'category': pdf.category,
                'description': pdf.description,
                'file_size': pdf.file_size,
                'upload_date': pdf.upload_date.isoformat(),
                'is_public': pdf.is_public,
                'download_count': pdf.download_count
            })
        
        return jsonify({'pdfs': pdf_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdf/download/<int:file_id>', methods=['GET'])
@jwt_required()
def download_pdf(file_id):
    try:
        user_id = get_jwt_identity()
        pdf = UserPDF.query.filter(
            (UserPDF.id == file_id) & 
            ((UserPDF.user_id == user_id) | (UserPDF.is_public == True))
        ).first()
        
        if not pdf:
            return jsonify({'error': 'File not found or access denied'}), 404
        
        # Increment download count
        pdf.download_count += 1
        db.session.commit()
        
        return send_file(pdf.file_path, as_attachment=True, download_name=pdf.original_filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Animation Routes
@app.route('/api/animations/create-sine-wave', methods=['POST'])
@jwt_required()
def create_sine_animation():
    try:
        user_id = get_jwt_identity()
        filename = AnimationCreator.create_sine_wave_animation()
        
        animation = Animation(
            user_id=user_id,
            title="Sine Wave Animation",
            animation_type="mathematical",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': 'Sine wave animation created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/create-chart', methods=['POST'])
@jwt_required()
def create_chart_animation():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        data_points = data.get('data_points', [85, 92, 78, 88, 90])
        
        filename = AnimationCreator.create_data_visualization(data_points)
        
        animation = Animation(
            user_id=user_id,
            title="Data Visualization Chart",
            animation_type="chart",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': 'Chart animation created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/create-banner', methods=['POST'])
@jwt_required()
def create_banner():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        title = data.get('title', 'Educational Banner')
        subtitle = data.get('subtitle', 'Learn and Grow with Po-Tech')
        
        filename = AnimationCreator.create_educational_banner(title, subtitle)
        
        animation = Animation(
            user_id=user_id,
            title=f"Banner: {title}",
            animation_type="banner",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': 'Educational banner created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/view/<int:animation_id>', methods=['GET'])
def view_animation(animation_id):
    try:
        animation = Animation.query.get(animation_id)
        if not animation:
            return jsonify({'error': 'Animation not found'}), 404
        
        # Increment views
        animation.views += 1
        db.session.commit()
        
        return send_file(animation.file_path)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/create-smooth-wave', methods=['POST'])
@jwt_required()
def create_smooth_wave():
    try:
        user_id = get_jwt_identity()
        filename = AnimationCreator.create_smooth_wave_animation()
        
        animation = Animation(
            user_id=user_id,
            title="Smooth Multi-Wave Animation",
            animation_type="advanced_wave",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': 'Smooth wave animation created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/create-particles', methods=['POST'])
@jwt_required()
def create_particle_animation():
    try:
        user_id = get_jwt_identity()
        filename = AnimationCreator.create_particle_system()
        
        animation = Animation(
            user_id=user_id,
            title="Particle System Animation",
            animation_type="particles",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': 'Particle animation created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/create-3d-rotation', methods=['POST'])
@jwt_required()
def create_3d_animation():
    try:
        user_id = get_jwt_identity()
        filename = AnimationCreator.create_3d_rotation()
        
        animation = Animation(
            user_id=user_id,
            title="3D Rotation Animation",
            animation_type="3d_rotation",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': '3D rotation animation created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/create-morphing', methods=['POST'])
@jwt_required()
def create_morphing_animation():
    try:
        user_id = get_jwt_identity()
        filename = AnimationCreator.create_morphing_shapes()
        
        animation = Animation(
            user_id=user_id,
            title="Morphing Shapes Animation",
            animation_type="morphing",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': 'Morphing animation created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/create-spiral', methods=['POST'])
@jwt_required()
def create_spiral_animation():
    try:
        user_id = get_jwt_identity()
        filename = AnimationCreator.create_spiral_animation()
        
        animation = Animation(
            user_id=user_id,
            title="Smooth Spiral Animation",
            animation_type="spiral",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': 'Spiral animation created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/create-interference', methods=['POST'])
@jwt_required()
def create_interference_animation():
    try:
        user_id = get_jwt_identity()
        filename = AnimationCreator.create_wave_interference()
        
        animation = Animation(
            user_id=user_id,
            title="Wave Interference Animation",
            animation_type="interference",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': 'Wave interference animation created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/create-particles', methods=['POST'])
@jwt_required()
def create_particle_animation():
    try:
        user_id = get_jwt_identity()
        filename = AnimationCreator.create_particle_system()
        
        animation = Animation(
            user_id=user_id,
            title="Particle System Animation",
            animation_type="particles",
            file_path=os.path.join(ANIMATION_FOLDER, filename)
        )
        db.session.add(animation)
        db.session.commit()
        
        return jsonify({
            'message': 'Particle system animation created',
            'animation_id': animation.id,
            'filename': filename,
            'url': f'/api/animations/view/{animation.id}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animations/my-animations', methods=['GET'])
@jwt_required()
def get_user_animations():
    try:
        user_id = get_jwt_identity()
        animations = Animation.query.filter_by(user_id=user_id).order_by(Animation.created_at.desc()).all()
        
        animation_list = []
        for anim in animations:
            animation_list.append({
                'id': anim.id,
                'title': anim.title,
                'animation_type': anim.animation_type,
                'created_at': anim.created_at.isoformat(),
                'views': anim.views,
                'is_public': anim.is_public,
                'url': f'/api/animations/view/{anim.id}'
            })
        
        return jsonify({'animations': animation_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    try:
        user_id = get_jwt_identity()
        
        # Get user statistics
        pdf_count = UserPDF.query.filter_by(user_id=user_id).count()
        animation_count = Animation.query.filter_by(user_id=user_id).count()
        total_downloads = db.session.query(db.func.sum(UserPDF.download_count)).filter_by(user_id=user_id).scalar() or 0
        total_views = db.session.query(db.func.sum(Animation.views)).filter_by(user_id=user_id).scalar() or 0
        
        return jsonify({
            'statistics': {
                'pdf_count': pdf_count,
                'animation_count': animation_count,
                'total_downloads': total_downloads,
                'total_views': total_views
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
