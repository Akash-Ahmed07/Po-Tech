from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_mail import Message
from app import db, mail
from models import User, Blog, Book, UserPDF, StudyMaterial, Animation, Contact
from utils.file_handler import allowed_file, save_uploaded_file
from utils.animation import AnimationCreator
from utils.email import send_verification_email
import os
import uuid
from datetime import datetime
import json

def register_routes(app):
    
    @app.route('/')
    def index():
        recent_blogs = Blog.query.filter_by(is_published=True).order_by(Blog.created_at.desc()).limit(3).all()
        popular_books = Book.query.filter_by(is_public=True).order_by(Book.downloads.desc()).limit(6).all()
        return render_template('index.html', recent_blogs=recent_blogs, popular_books=popular_books)

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            contact_msg = Contact(
                name=request.form['name'],
                email=request.form['email'],
                subject=request.form.get('subject', ''),
                message=request.form['message']
            )
            db.session.add(contact_msg)
            db.session.commit()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html')

    # Authentication Routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                if not user.is_verified:
                    flash('Please verify your email before logging in.', 'warning')
                    return redirect(url_for('login'))
                
                session['user_id'] = user.id
                session['username'] = user.username
                session['is_admin'] = user.is_admin
                flash(f'Welcome back, {user.username}!', 'success')
                
                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'error')
        
        return render_template('auth/login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists.', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'error')
                return redirect(url_for('register'))
            
            # Create new user
            verification_token = str(uuid.uuid4())
            user = User(
                username=username,
                email=email,
                verification_token=verification_token
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            send_verification_email(user.email, verification_token)
            flash('Registration successful! Please check your email for verification.', 'success')
            return redirect(url_for('login'))
        
        return render_template('auth/register.html')

    @app.route('/verify/<token>')
    def verify_email(token):
        user = User.query.filter_by(verification_token=token).first()
        if user:
            user.is_verified = True
            user.verification_token = None
            db.session.commit()
            flash('Email verified successfully! You can now log in.', 'success')
        else:
            flash('Invalid verification token.', 'error')
        return redirect(url_for('login'))

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    # Dashboard Routes
    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        user_blogs = Blog.query.filter_by(author_id=user.id).count()
        user_pdfs = UserPDF.query.filter_by(user_id=user.id).count()
        user_animations = Animation.query.filter_by(user_id=user.id).count()
        
        return render_template('dashboard.html', 
                             user=user, 
                             blog_count=user_blogs,
                             pdf_count=user_pdfs,
                             animation_count=user_animations)

    # Blog Routes
    @app.route('/blogs')
    def blog_list():
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Blog.query.filter_by(is_published=True)
        
        if category:
            query = query.filter_by(category=category)
        if search:
            query = query.filter(Blog.title.contains(search) | Blog.content.contains(search))
        
        blogs = query.order_by(Blog.created_at.desc()).paginate(
            page=page, per_page=9, error_out=False)
        
        return render_template('blog/list.html', blogs=blogs, category=category, search=search)

    @app.route('/blog/<int:id>')
    def blog_view(id):
        blog = Blog.query.get_or_404(id)
        # Increment view count
        blog.views += 1
        db.session.commit()
        
        # Get related blogs
        related_blogs = Blog.query.filter(
            Blog.category == blog.category,
            Blog.id != blog.id,
            Blog.is_published == True
        ).limit(3).all()
        
        return render_template('blog/view.html', blog=blog, related_blogs=related_blogs)

    @app.route('/blog/create', methods=['GET', 'POST'])
    def blog_create():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            summary = request.form.get('summary', '')
            category = request.form.get('category', 'general')
            tags = request.form.get('tags', '')
            
            # Handle image upload
            featured_image = None
            if 'featured_image' in request.files:
                file = request.files['featured_image']
                if file and allowed_file(file.filename, ['png', 'jpg', 'jpeg', 'gif']):
                    featured_image = save_uploaded_file(file, 'uploads/blog_images')
            
            blog = Blog(
                title=title,
                content=content,
                summary=summary,
                category=category,
                tags=tags,
                featured_image=featured_image,
                author_id=session['user_id']
            )
            
            db.session.add(blog)
            db.session.commit()
            flash('Blog post created successfully!', 'success')
            return redirect(url_for('blog_view', id=blog.id))
        
        return render_template('blog/create.html')

    # Library Routes
    @app.route('/library')
    def library():
        category = request.args.get('category', 'all')
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        
        query = Book.query.filter_by(is_public=True)
        
        if category != 'all':
            query = query.filter_by(category=category)
        if search:
            query = query.filter(Book.title.contains(search) | Book.author.contains(search))
        
        books = query.order_by(Book.created_at.desc()).paginate(
            page=page, per_page=12, error_out=False)
        
        categories = ['bangladeshi', 'international', 'hsc', 'ssc', 'undergraduate', 'masters']
        
        return render_template('library/books.html', 
                             books=books, 
                             categories=categories, 
                             selected_category=category,
                             search=search)

    @app.route('/library/upload', methods=['GET', 'POST'])
    def library_upload():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            category = request.form['category']
            subject = request.form.get('subject', '')
            description = request.form.get('description', '')
            
            # Handle file uploads
            book_file = None
            cover_image = None
            
            if 'book_file' in request.files:
                file = request.files['book_file']
                if file and allowed_file(file.filename, ['pdf']):
                    book_file = save_uploaded_file(file, 'uploads/books')
            
            if 'cover_image' in request.files:
                file = request.files['cover_image']
                if file and allowed_file(file.filename, ['png', 'jpg', 'jpeg']):
                    cover_image = save_uploaded_file(file, 'uploads/covers')
            
            book = Book(
                title=title,
                author=author,
                category=category,
                subject=subject,
                description=description,
                file_path=book_file,
                cover_image=cover_image,
                uploaded_by=session['user_id']
            )
            
            if book_file:
                # Get file size
                file_path = os.path.join('uploads/books', book_file)
                if os.path.exists(file_path):
                    book.file_size = os.path.getsize(file_path)
            
            db.session.add(book)
            db.session.commit()
            flash('Book uploaded successfully!', 'success')
            return redirect(url_for('library'))
        
        categories = ['bangladeshi', 'international', 'hsc', 'ssc', 'undergraduate', 'masters']
        return render_template('library/upload.html', categories=categories)

    @app.route('/download/book/<int:id>')
    def download_book(id):
        book = Book.query.get_or_404(id)
        if book.file_path:
            file_path = os.path.join('uploads/books', book.file_path)
            if os.path.exists(file_path):
                book.downloads += 1
                db.session.commit()
                return send_file(file_path, as_attachment=True, download_name=f"{book.title}.pdf")
        flash('File not found.', 'error')
        return redirect(url_for('library'))

    # Study Materials Routes
    @app.route('/study/<level>')
    def study_materials(level):
        if level not in ['hsc', 'ssc', 'undergraduate', 'masters']:
            return redirect(url_for('index'))
        
        subject = request.args.get('subject')
        page = request.args.get('page', 1, type=int)
        
        query = StudyMaterial.query.filter_by(level=level, is_active=True)
        
        if subject:
            query = query.filter_by(subject=subject)
        
        materials = query.order_by(StudyMaterial.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False)
        
        # Get unique subjects for this level
        subjects = db.session.query(StudyMaterial.subject).filter_by(
            level=level, is_active=True).distinct().all()
        subjects = [s[0] for s in subjects]
        
        return render_template('study/materials.html', 
                             materials=materials, 
                             level=level,
                             subjects=subjects,
                             selected_subject=subject)

    @app.route('/study/view/<int:id>')
    def study_view(id):
        material = StudyMaterial.query.get_or_404(id)
        material.views += 1
        db.session.commit()
        
        # Get related materials
        related = StudyMaterial.query.filter(
            StudyMaterial.level == material.level,
            StudyMaterial.subject == material.subject,
            StudyMaterial.id != material.id,
            StudyMaterial.is_active == True
        ).limit(3).all()
        
        return render_template('study/view.html', material=material, related=related)

    # Animation Routes
    @app.route('/animations')
    def animation_gallery():
        page = request.args.get('page', 1, type=int)
        animation_type = request.args.get('type')
        
        query = Animation.query.filter_by(is_public=True)
        
        if animation_type:
            query = query.filter_by(animation_type=animation_type)
        
        animations = query.order_by(Animation.created_at.desc()).paginate(
            page=page, per_page=12, error_out=False)
        
        return render_template('animations/gallery.html', animations=animations, selected_type=animation_type)

    @app.route('/animations/create', methods=['GET', 'POST'])
    def animation_create():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            animation_type = request.form['animation_type']
            title = request.form['title']
            description = request.form.get('description', '')
            
            try:
                creator = AnimationCreator()
                
                if animation_type == 'sine_wave':
                    filename = creator.create_sine_wave_animation()
                elif animation_type == 'spiral':
                    filename = creator.create_spiral_animation()
                elif animation_type == 'interference':
                    filename = creator.create_wave_interference()
                elif animation_type == 'particles':
                    filename = creator.create_particle_system()
                elif animation_type == 'data_viz':
                    data_points = request.form.get('data_points', '85,92,78,88,90').split(',')
                    data_points = [int(x.strip()) for x in data_points if x.strip().isdigit()]
                    filename = creator.create_data_visualization(data_points)
                elif animation_type == 'banner':
                    banner_title = request.form.get('banner_title', 'Po-Tech Education')
                    subtitle = request.form.get('subtitle', 'Learning Made Easy')
                    filename = creator.create_educational_banner(banner_title, subtitle)
                else:
                    flash('Invalid animation type.', 'error')
                    return redirect(url_for('animation_create'))
                
                animation = Animation(
                    title=title,
                    animation_type=animation_type,
                    file_path=filename,
                    description=description,
                    user_id=session['user_id']
                )
                
                db.session.add(animation)
                db.session.commit()
                flash('Animation created successfully!', 'success')
                return redirect(url_for('animation_gallery'))
                
            except Exception as e:
                flash(f'Error creating animation: {str(e)}', 'error')
                return redirect(url_for('animation_create'))
        
        return render_template('animations/create.html')

    @app.route('/animation/view/<int:id>')
    def animation_view(id):
        animation = Animation.query.get_or_404(id)
        animation.views += 1
        db.session.commit()
        
        file_path = os.path.join('uploads/animations', animation.file_path)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            flash('Animation file not found.', 'error')
            return redirect(url_for('animation_gallery'))

    # Admin Routes
    @app.route('/admin')
    def admin_dashboard():
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        
        # Statistics
        total_users = User.query.count()
        total_blogs = Blog.query.count()
        total_books = Book.query.count()
        total_animations = Animation.query.count()
        pending_contacts = Contact.query.filter_by(is_read=False).count()
        
        return render_template('admin/dashboard.html',
                             total_users=total_users,
                             total_blogs=total_blogs,
                             total_books=total_books,
                             total_animations=total_animations,
                             pending_contacts=pending_contacts)

    @app.route('/admin/users')
    def admin_users():
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        page = request.args.get('page', 1, type=int)
        users = User.query.paginate(page=page, per_page=20, error_out=False)
        return render_template('admin/users.html', users=users)

    @app.route('/admin/contacts')
    def admin_contacts():
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        page = request.args.get('page', 1, type=int)
        contacts = Contact.query.order_by(Contact.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False)
        return render_template('admin/contacts.html', contacts=contacts)

    @app.route('/admin/contact/<int:id>/mark_read')
    def admin_mark_contact_read(id):
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        
        contact = Contact.query.get_or_404(id)
        contact.is_read = True
        db.session.commit()
        flash('Contact marked as read.', 'success')
        return redirect(url_for('admin_contacts'))

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
