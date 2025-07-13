
const express = require('express');
const mysql = require('mysql2');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const session = require('express-session');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use('/uploads', express.static('uploads'));

app.use(session({
  secret: 'po-tech-secret-key',
  resave: false,
  saveUninitialized: false
}));

app.use(passport.initialize());
app.use(passport.session());

// Database connection
const db = mysql.createConnection({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'po_tech'
});

// Create database tables
db.execute(`
  CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255),
    google_id VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
`);

db.execute(`
  CREATE TABLE IF NOT EXISTS blogs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id INT,
    author_name VARCHAR(255),
    featured_image VARCHAR(255),
    likes INT DEFAULT 0,
    views INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id)
  )
`);

db.execute(`
  CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    category ENUM('bangladeshi', 'international', 'hsc', 'ssc', 'undergraduate', 'masters'),
    description TEXT,
    file_url VARCHAR(255),
    cover_image VARCHAR(255),
    downloads INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
`);

db.execute(`
  CREATE TABLE IF NOT EXISTS study_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    level ENUM('hsc', 'ssc'),
    subject VARCHAR(255),
    chapter VARCHAR(255),
    video_url VARCHAR(255),
    description TEXT,
    views INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
`);

db.execute(`
  CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
`);

// Create default admin
const defaultAdminPassword = bcrypt.hashSync('Unitedsylhet90', 10);
db.execute(
  'INSERT IGNORE INTO admins (username, password) VALUES (?, ?)',
  ['admin', defaultAdminPassword]
);

// File upload configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage: storage });

// Email configuration
const transporter = nodemailer.createTransporter({
  service: 'gmail',
  auth: {
    user: 'groweasy25@gmail.com',
    pass: process.env.EMAIL_PASSWORD
  }
});

// Google OAuth configuration
passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: "/auth/google/callback"
}, async (accessToken, refreshToken, profile, done) => {
  try {
    const [existing] = await db.promise().execute(
      'SELECT * FROM users WHERE google_id = ?',
      [profile.id]
    );

    if (existing.length > 0) {
      return done(null, existing[0]);
    }

    const [result] = await db.promise().execute(
      'INSERT INTO users (name, email, google_id, is_verified) VALUES (?, ?, ?, ?)',
      [profile.displayName, profile.emails[0].value, profile.id, true]
    );

    const [newUser] = await db.promise().execute(
      'SELECT * FROM users WHERE id = ?',
      [result.insertId]
    );

    return done(null, newUser[0]);
  } catch (error) {
    return done(error, null);
  }
}));

passport.serializeUser((user, done) => {
  done(null, user.id);
});

passport.deserializeUser(async (id, done) => {
  try {
    const [user] = await db.promise().execute(
      'SELECT * FROM users WHERE id = ?',
      [id]
    );
    done(null, user[0]);
  } catch (error) {
    done(error, null);
  }
});

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Authentication routes
app.post('/api/register', async (req, res) => {
  try {
    const { name, email, password } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10);
    const verificationToken = jwt.sign({ email }, 'verification-secret');

    await db.promise().execute(
      'INSERT INTO users (name, email, password, verification_token) VALUES (?, ?, ?, ?)',
      [name, email, hashedPassword, verificationToken]
    );

    // Send verification email
    const mailOptions = {
      from: 'groweasy25@gmail.com',
      to: email,
      subject: 'Verify Your Email - Po-Tech',
      html: `<p>Click <a href="http://localhost:${PORT}/verify/${verificationToken}">here</a> to verify your email.</p>`
    };

    await transporter.sendMail(mailOptions);

    res.json({ success: true, message: 'Registration successful. Please check your email for verification.' });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Registration failed' });
  }
});

app.post('/api/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const [users] = await db.promise().execute(
      'SELECT * FROM users WHERE email = ?',
      [email]
    );

    if (users.length === 0) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const user = users[0];
    if (!user.is_verified) {
      return res.status(401).json({ success: false, message: 'Please verify your email first' });
    }

    const passwordMatch = await bcrypt.compare(password, user.password);
    if (!passwordMatch) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const token = jwt.sign({ userId: user.id }, 'jwt-secret');
    res.json({ success: true, token, user: { id: user.id, name: user.name, email: user.email } });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Login failed' });
  }
});

// Google OAuth routes
app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

app.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    res.redirect('/');
  }
);

// Blog routes
app.get('/api/blogs', async (req, res) => {
  try {
    const [blogs] = await db.promise().execute(
      'SELECT * FROM blogs ORDER BY created_at DESC'
    );
    res.json(blogs);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch blogs' });
  }
});

app.post('/api/blogs', upload.single('image'), async (req, res) => {
  try {
    const { title, content, author_name } = req.body;
    const featured_image = req.file ? req.file.filename : null;

    await db.promise().execute(
      'INSERT INTO blogs (title, content, author_name, featured_image) VALUES (?, ?, ?, ?)',
      [title, content, author_name, featured_image]
    );

    res.json({ success: true, message: 'Blog published successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Failed to publish blog' });
  }
});

// Books routes
app.get('/api/books/:category', async (req, res) => {
  try {
    const [books] = await db.promise().execute(
      'SELECT * FROM books WHERE category = ?',
      [req.params.category]
    );
    res.json(books);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch books' });
  }
});

// Study materials routes
app.get('/api/study/:level', async (req, res) => {
  try {
    const [materials] = await db.promise().execute(
      'SELECT * FROM study_materials WHERE level = ? ORDER BY subject, chapter',
      [req.params.level]
    );
    res.json(materials);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch study materials' });
  }
});

// Admin routes
app.post('/api/admin/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const [admins] = await db.promise().execute(
      'SELECT * FROM admins WHERE username = ?',
      [username]
    );

    if (admins.length === 0) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const admin = admins[0];
    const passwordMatch = await bcrypt.compare(password, admin.password);
    if (!passwordMatch) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const token = jwt.sign({ adminId: admin.id }, 'admin-jwt-secret');
    res.json({ success: true, token });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Login failed' });
  }
});

// Middleware to verify admin token
const verifyAdminToken = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ message: 'Access denied' });
  }

  try {
    const decoded = jwt.verify(token, 'admin-jwt-secret');
    req.adminId = decoded.adminId;
    next();
  } catch (error) {
    res.status(401).json({ message: 'Invalid token' });
  }
};

// Admin CRUD operations
app.post('/api/admin/books', verifyAdminToken, upload.fields([
  { name: 'file', maxCount: 1 },
  { name: 'cover', maxCount: 1 }
]), async (req, res) => {
  try {
    const { title, author, category, description } = req.body;
    const file_url = req.files.file ? req.files.file[0].filename : null;
    const cover_image = req.files.cover ? req.files.cover[0].filename : null;

    await db.promise().execute(
      'INSERT INTO books (title, author, category, description, file_url, cover_image) VALUES (?, ?, ?, ?, ?, ?)',
      [title, author, category, description, file_url, cover_image]
    );

    res.json({ success: true, message: 'Book added successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Failed to add book' });
  }
});

app.post('/api/admin/study-materials', verifyAdminToken, async (req, res) => {
  try {
    const { title, level, subject, chapter, video_url, description } = req.body;

    await db.promise().execute(
      'INSERT INTO study_materials (title, level, subject, chapter, video_url, description) VALUES (?, ?, ?, ?, ?, ?)',
      [title, level, subject, chapter, video_url, description]
    );

    res.json({ success: true, message: 'Study material added successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Failed to add study material' });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
