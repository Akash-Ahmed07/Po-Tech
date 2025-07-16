import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import uuid
import os

class AnimationCreator:
    def __init__(self):
        self.output_dir = 'uploads/animations'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_sine_wave_animation(self):
        """Create smooth sine wave animation"""
        fig, ax = plt.subplots(figsize=(12, 8))
        x = np.linspace(0, 4*np.pi, 200)
        line, = ax.plot([], [], 'b-', linewidth=3)
        ax.set_xlim(0, 4*np.pi)
        ax.set_ylim(-2, 2)
        ax.set_title('Smooth Sine Wave Animation', fontsize=18, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f8f9fa')
        
        def animate(frame):
            phase = frame * 0.15
            y = np.sin(x + phase) * np.exp(-0.1 * np.abs(x - 2*np.pi))
            line.set_data(x, y)
            return line,
        
        anim = animation.FuncAnimation(fig, animate, frames=300, interval=33, blit=True)
        filename = f"sine_wave_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(self.output_dir, filename)
        anim.save(filepath, writer='pillow', fps=30)
        plt.close()
        return filename

    def create_spiral_animation(self):
        """Create smooth spiral animation"""
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
            rotation = frame * 0.1
            x = r * np.cos(t + rotation)
            y = r * np.sin(t + rotation)
            line.set_data(x, y)
            return line,
        
        anim = animation.FuncAnimation(fig, animate, frames=200, interval=50, blit=True)
        filename = f"spiral_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(self.output_dir, filename)
        anim.save(filepath, writer='pillow', fps=20)
        plt.close()
        return filename

    def create_wave_interference(self):
        """Create wave interference animation"""
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
        filepath = os.path.join(self.output_dir, filename)
        anim.save(filepath, writer='pillow', fps=20)
        plt.close()
        return filename

    def create_particle_system(self):
        """Create particle system animation"""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_title('Particle System Animation', fontsize=18, fontweight='bold')
        ax.set_facecolor('#000011')
        
        num_particles = 50
        particles = np.random.rand(num_particles, 2) * [10, 8]
        velocities = (np.random.rand(num_particles, 2) - 0.5) * 0.5
        colors = np.random.rand(num_particles)
        
        scat = ax.scatter(particles[:, 0], particles[:, 1], 
                         s=50, c=colors, cmap='plasma', alpha=0.7)
        
        def animate(frame):
            nonlocal particles, velocities
            
            particles += velocities
            
            # Bounce off walls
            particles[:, 0] = np.where(particles[:, 0] < 0, -particles[:, 0], particles[:, 0])
            particles[:, 0] = np.where(particles[:, 0] > 10, 20 - particles[:, 0], particles[:, 0])
            particles[:, 1] = np.where(particles[:, 1] < 0, -particles[:, 1], particles[:, 1])
            particles[:, 1] = np.where(particles[:, 1] > 8, 16 - particles[:, 1], particles[:, 1])
            
            velocities += (np.random.rand(num_particles, 2) - 0.5) * 0.02
            velocities *= 0.99
            
            scat.set_offsets(particles)
            return scat,
        
        anim = animation.FuncAnimation(fig, animate, frames=300, interval=33, blit=True)
        filename = f"particles_{uuid.uuid4().hex[:8]}.gif"
        filepath = os.path.join(self.output_dir, filename)
        anim.save(filepath, writer='pillow', fps=30)
        plt.close()
        return filename
    
    def create_data_visualization(self, data_points):
        """Create static data visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        categories = ['Math', 'Science', 'English', 'History', 'Art']
        values = data_points if data_points else [85, 92, 78, 88, 90]
        
        bars = ax1.bar(categories, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        ax1.set_title('Student Performance', fontsize=14)
        ax1.set_ylabel('Scores')
        ax1.set_ylim(0, 100)
        
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value}%', ha='center', va='bottom')
        
        ax2.pie(values, labels=categories, autopct='%1.1f%%', startangle=90,
                colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        ax2.set_title('Score Distribution', fontsize=14)
        
        plt.tight_layout()
        filename = f"data_viz_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        return filename
    
    def create_educational_banner(self, title, subtitle):
        """Create educational banner"""
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
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, quality=95)
        return filename
