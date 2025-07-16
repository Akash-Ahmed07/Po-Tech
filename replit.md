# Po-Tech Educational Platform

## Overview

Po-Tech is a comprehensive educational platform built with Flask that provides digital library services, blogging capabilities, animation creation tools, and study materials. The platform serves as a centralized hub for educational content sharing and learning resources management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with flexible database support (configured for SQLite by default, supports PostgreSQL)
- **Authentication**: Flask-JWT-Extended for token-based authentication
- **File Handling**: Custom file upload system with Werkzeug utilities
- **Email Services**: Flask-Mail with SMTP configuration for user verification

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **CSS Framework**: Bootstrap with dark theme support
- **JavaScript**: Vanilla JavaScript with modern ES6+ features
- **Icons**: Font Awesome for consistent iconography
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Application Structure
- **Modular Design**: Separated concerns with dedicated modules for models, routes, forms, and utilities
- **Template Hierarchy**: Base template system with specialized templates for different sections
- **Static Assets**: Organized CSS, JavaScript, and image resources

## Key Components

### User Management
- User registration with email verification
- Login/logout functionality with session management
- Admin user capabilities for platform management
- Profile management and user statistics

### Content Management Systems
1. **Blog System**: Full-featured blogging with categories, tags, and featured images
2. **Digital Library**: Book upload, categorization, and download functionality
3. **Animation Creator**: Tools for generating educational animations and visualizations
4. **Study Materials**: Organized educational content by academic levels (SSC, HSC, Undergraduate, Masters)

### File Management
- Secure file upload with type validation
- Organized file storage structure
- Image processing for featured content
- PDF handling for educational materials

### Admin Panel
- User management interface
- Content moderation tools
- System statistics dashboard
- Contact message management

## Data Flow

### User Registration Flow
1. User submits registration form
2. System validates user data and creates account
3. Verification email sent to user
4. User clicks verification link to activate account
5. User can access platform features

### Content Creation Flow
1. Authenticated user accesses creation form
2. User uploads content with metadata
3. System validates and processes files
4. Content stored in database with file references
5. Content becomes available in respective sections

### File Upload Process
1. File validation against allowed types and size limits
2. Secure filename generation with UUID
3. File storage in organized directory structure
4. Database record creation with file metadata

## External Dependencies

### Core Dependencies
- **Flask**: Web framework foundation
- **SQLAlchemy**: Database ORM and migrations
- **Werkzeug**: WSGI utilities and security helpers
- **Flask-JWT-Extended**: Authentication and authorization
- **Flask-Mail**: Email functionality for notifications

### Frontend Dependencies
- **Bootstrap**: UI framework with dark theme support
- **Font Awesome**: Icon library
- **Highlight.js**: Code syntax highlighting for blog posts

### Animation and Visualization
- **Matplotlib**: Chart and animation generation
- **NumPy**: Numerical computations for visualizations
- **PIL (Pillow)**: Image processing capabilities

### File Processing
- **PDFPlumber**: PDF content extraction and processing
- **MoviePy**: Video processing for educational content

## Deployment Strategy

### Environment Configuration
- Environment variables for sensitive configuration (database URLs, secret keys, email credentials)
- Development and production configuration separation
- Docker-ready with proper port and host configuration

### Database Strategy
- SQLite for development and small deployments
- PostgreSQL support for production environments
- Database migrations using SQLAlchemy Alembic

### File Storage
- Local file system storage with organized directory structure
- Upload size limits (50MB max) for performance
- File type restrictions for security

### Security Measures
- CSRF protection with Flask-WTF forms
- Password hashing with Werkzeug security utilities
- JWT token-based authentication with expiration
- Secure file upload validation
- Admin role-based access control

### Performance Considerations
- Database connection pooling with pre-ping health checks
- Static file serving optimization
- Image lazy loading in frontend
- Pagination for large content lists

The platform is designed to be scalable, maintainable, and user-friendly, with a focus on educational content delivery and community engagement.