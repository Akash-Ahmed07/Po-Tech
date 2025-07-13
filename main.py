
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
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.linspace(0, 2*np.pi, 100)
        line, = ax.plot([], [], 'b-', linewidth=2)
        ax.set_xlim(0, 2*np.pi)
        ax.set_ylim(-1.5, 1.5)
        ax.set_title('Sine Wave Animation', fontsize=16)
        ax.grid(True, alpha=0.3)
        
        def animate(frame):
            y = np.sin(x + frame/10)
            line.set_data(x, y)
            return line,
        
        anim = animation.FuncAnimation(fig, animate, frames=200, interval=50, blit=True)
        filename = f"sine_wave_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(ANIMATION_FOLDER, filename)
        anim.save(filepath, writer='pillow', fps=20)
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
