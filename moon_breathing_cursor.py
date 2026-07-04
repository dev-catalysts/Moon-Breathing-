import sys
import math
import time
import random
import json
import os
from PySide6.QtWidgets import (QApplication, QWidget, QSlider, QLabel,
                                QPushButton, QVBoxLayout, QHBoxLayout,
                                QFrame, QSystemTrayIcon, QMenu,
                                QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QTimer, QPointF, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QPainterPath,
                            QRadialGradient, QCursor, QIcon, QPixmap,
                            QLinearGradient, QFont, QAction)

from pynput import mouse as pynput_mouse
from pynput import keyboard as pynput_kb

# ─── Constants ───────────────────────────────────────────────────────────────

FPS = 60
ALPHA_BUCKETS = 6
INTERP_STEPS = 4
MIN_TRAIL_DIST_SQ = 9
MAX_SPARKS = 60
MAX_CRESCENTS = 30

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'moon_cursor_settings.json')

# ─── Color Presets ───────────────────────────────────────────────────────────

COLOR_PRESETS = {
    'Purple': {
        'smoke': [(160,50,255),(120,30,220),(80,15,180),(50,8,140),(30,5,100)],
        'trail': [(80,10,180),(110,25,230),(150,60,255),(190,120,255),(220,200,255)],
        'glow_center': (220,180,255), 'glow_edge': (130,40,255),
        'orb': (198,182,255),
        'spark': (190,100,255), 'accent': (255,210,50),
        'crescent_warm': (255,250,220), 'crescent_cool': (245,235,255),
        'crescent_glow_warm': (255,140,0), 'crescent_glow_cool': (190,80,255),
        'shockwave_a': (180,70,255), 'shockwave_b': (255,160,0),
        'magic': (255,45,85), 'magic_light': (255,120,160),
        'magic_mid': (255,75,115), 'magic_spoke': (255,55,95),
        'magic_inner': (255,90,135), 'magic_dot': (255,200,220),
        'magic_glow': [(255,30,70),(200,15,55),(140,8,35)],
        'btn': '#A855F7', 'btn_hover': '#9333EA',
    },
    'Blue': {
        'smoke': [(50,120,255),(30,80,220),(15,50,180),(8,30,140),(5,15,100)],
        'trail': [(10,40,180),(25,80,230),(60,130,255),(120,170,255),(200,220,255)],
        'glow_center': (180,210,255), 'glow_edge': (40,100,255),
        'orb': (182,200,255),
        'spark': (100,160,255), 'accent': (50,255,210),
        'crescent_warm': (220,240,255), 'crescent_cool': (200,230,255),
        'crescent_glow_warm': (0,180,255), 'crescent_glow_cool': (80,120,255),
        'shockwave_a': (70,130,255), 'shockwave_b': (0,200,255),
        'magic': (45,120,255), 'magic_light': (120,170,255),
        'magic_mid': (75,140,255), 'magic_spoke': (55,110,255),
        'magic_inner': (90,150,255), 'magic_dot': (200,220,255),
        'magic_glow': [(30,70,255),(15,45,200),(8,25,140)],
        'btn': '#3B82F6', 'btn_hover': '#2563EB',
    },
    'Crimson': {
        'smoke': [(255,50,80),(220,30,60),(180,15,40),(140,8,30),(100,5,20)],
        'trail': [(180,10,30),(230,25,50),(255,60,90),(255,120,150),(255,200,210)],
        'glow_center': (255,180,190), 'glow_edge': (255,40,80),
        'orb': (255,182,192),
        'spark': (255,100,130), 'accent': (255,210,50),
        'crescent_warm': (255,230,230), 'crescent_cool': (255,220,230),
        'crescent_glow_warm': (255,80,100), 'crescent_glow_cool': (255,50,80),
        'shockwave_a': (255,70,100), 'shockwave_b': (255,160,60),
        'magic': (255,45,85), 'magic_light': (255,120,160),
        'magic_mid': (255,75,115), 'magic_spoke': (255,55,95),
        'magic_inner': (255,90,135), 'magic_dot': (255,200,220),
        'magic_glow': [(255,30,70),(200,15,55),(140,8,35)],
        'btn': '#EF4444', 'btn_hover': '#DC2626',
    },
    'Cyan': {
        'smoke': [(50,220,255),(30,180,220),(15,140,180),(8,100,140),(5,70,100)],
        'trail': [(10,140,180),(25,180,230),(60,210,255),(120,230,255),(200,245,255)],
        'glow_center': (180,240,255), 'glow_edge': (40,200,255),
        'orb': (182,240,255),
        'spark': (100,230,255), 'accent': (255,255,100),
        'crescent_warm': (220,250,255), 'crescent_cool': (200,245,255),
        'crescent_glow_warm': (0,220,255), 'crescent_glow_cool': (80,200,255),
        'shockwave_a': (70,220,255), 'shockwave_b': (0,255,200),
        'magic': (45,200,255), 'magic_light': (120,230,255),
        'magic_mid': (75,210,255), 'magic_spoke': (55,190,255),
        'magic_inner': (90,215,255), 'magic_dot': (200,240,255),
        'magic_glow': [(30,200,255),(15,150,200),(8,100,140)],
        'btn': '#06B6D4', 'btn_hover': '#0891B2',
    },
    'Gold': {
        'smoke': [(255,180,50),(220,140,30),(180,100,15),(140,70,8),(100,50,5)],
        'trail': [(180,100,10),(230,150,25),(255,190,60),(255,210,120),(255,240,200)],
        'glow_center': (255,230,180), 'glow_edge': (255,160,40),
        'orb': (255,220,182),
        'spark': (255,200,100), 'accent': (255,100,50),
        'crescent_warm': (255,250,220), 'crescent_cool': (255,240,210),
        'crescent_glow_warm': (255,180,0), 'crescent_glow_cool': (255,140,50),
        'shockwave_a': (255,180,70), 'shockwave_b': (255,220,100),
        'magic': (255,160,45), 'magic_light': (255,200,120),
        'magic_mid': (255,180,75), 'magic_spoke': (255,150,55),
        'magic_inner': (255,175,90), 'magic_dot': (255,230,200),
        'magic_glow': [(255,140,30),(200,100,15),(140,65,8)],
        'btn': '#F59E0B', 'btn_hover': '#D97706',
    },
    'Emerald': {
        'smoke': [(50,220,120),(30,180,90),(15,140,70),(8,100,50),(5,70,35)],
        'trail': [(10,140,60),(25,180,80),(60,220,120),(120,240,160),(200,255,220)],
        'glow_center': (180,255,210), 'glow_edge': (40,200,100),
        'orb': (182,255,200),
        'spark': (100,240,150), 'accent': (255,255,100),
        'crescent_warm': (220,255,230), 'crescent_cool': (210,255,225),
        'crescent_glow_warm': (50,255,120), 'crescent_glow_cool': (80,220,130),
        'shockwave_a': (70,230,120), 'shockwave_b': (100,255,150),
        'magic': (45,200,100), 'magic_light': (120,240,160),
        'magic_mid': (75,210,120), 'magic_spoke': (55,190,100),
        'magic_inner': (90,215,130), 'magic_dot': (200,255,220),
        'magic_glow': [(30,200,70),(15,150,45),(8,100,30)],
        'btn': '#10B981', 'btn_hover': '#059669',
    },
}

# ─── Settings ────────────────────────────────────────────────────────────────

class Settings:
    def __init__(self):
        self.smoke_intensity = 50
        self.trail_length = 50
        self.color_name = 'Purple'
        self.start_on_startup = False
        self.load()

    @property
    def colors(self):
        return COLOR_PRESETS.get(self.color_name, COLOR_PRESETS['Purple'])

    @property
    def trail_lifetime(self):
        return 0.3 + (self.trail_length / 100.0) * 1.7

    @property
    def max_trail(self):
        return 30 + int((self.trail_length / 100.0) * 120)

    @property
    def max_smoke(self):
        return 20 + int((self.smoke_intensity / 100.0) * 130)

    @property
    def smoke_spawn_chance(self):
        return 0.25 + (self.smoke_intensity / 100.0) * 0.55

    @property
    def smoke_speed_divisor(self):
        return 30 - (self.smoke_intensity / 100.0) * 22

    def load(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                d = json.load(f)
            self.smoke_intensity = d.get('smoke_intensity', 50)
            self.trail_length = d.get('trail_length', 50)
            self.color_name = d.get('color_name', 'Purple')
            self.start_on_startup = d.get('start_on_startup', False)
        except Exception:
            pass

    def save(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump({
                    'smoke_intensity': self.smoke_intensity,
                    'trail_length': self.trail_length,
                    'color_name': self.color_name,
                    'start_on_startup': self.start_on_startup,
                }, f, indent=2)
        except Exception:
            pass


# ─── Trail Point ─────────────────────────────────────────────────────────────

class TrailPoint:
    __slots__ = ('x', 'y', 'time')
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.time = time.time()


# ─── Smoke Particle ─────────────────────────────────────────────────────────

class SmokeParticle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'size', 'life', 'decay', 'intensity')

    def __init__(self, x, y, intensity=1.0):
        spread = 10 * intensity
        self.x = x + (random.random() - 0.5) * spread
        self.y = y + (random.random() - 0.5) * spread
        self.vx = (random.random() - 0.5) * 0.5 * intensity
        self.vy = (random.random() - 0.5) * 0.5 - 0.15
        self.size = 12 + random.random() * 14 + 4 * intensity
        self.life = 1.0
        self.decay = 0.020 + random.random() * 0.014
        self.intensity = min(intensity, 2.0)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.97
        self.vy *= 0.97
        self.size += 0.4
        self.life -= self.decay

    def draw(self, painter, smoke_colors):
        if self.life <= 0:
            return
        r = self.size * (0.5 + 0.5 * self.life)
        a = self.life * self.life
        k = self.intensity

        grad = QRadialGradient(self.x, self.y, r)
        grad.setColorAt(0.0,  QColor(*smoke_colors[0], min(255, int(75 * a * k))))
        grad.setColorAt(0.25, QColor(*smoke_colors[1], min(255, int(50 * a * k))))
        grad.setColorAt(0.55, QColor(*smoke_colors[2], min(255, int(30 * a * k))))
        grad.setColorAt(0.80, QColor(*smoke_colors[3], min(255, int(12 * a * k))))
        grad.setColorAt(1.0,  QColor(*smoke_colors[4], 0))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QPointF(self.x, self.y), r, r)


# ─── Crescent Particle ──────────────────────────────────────────────────────

class CrescentParticle:
    def __init__(self, x, y, size, angle, speed, drift_x, drift_y, hue=None):
        self.x = x;  self.y = y
        self.size = size;  self.angle = angle;  self.speed = speed
        self.drift_x = drift_x;  self.drift_y = drift_y
        self.life = 1.0
        self.decay = 0.02 + random.random() * 0.015
        if hue is None:
            self.is_yellow = random.random() < 0.85
        else:
            self.is_yellow = (hue == "yellow")

    def update(self):
        self.x += self.drift_x;  self.y += self.drift_y
        self.angle += self.speed;  self.life -= self.decay

    def draw(self, painter, unit_path, colors):
        if self.life <= 0:
            return
        size = self.size * self.life
        if size < 1:
            return

        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.angle)
        painter.scale(size, size)

        glow_rgb = colors['crescent_glow_warm'] if self.is_yellow else colors['crescent_glow_cool']
        glow_color = QColor(*glow_rgb, int(65 * self.life))
        painter.setPen(QPen(glow_color, 0.35))
        painter.setBrush(glow_color)
        painter.drawPath(unit_path)

        core_rgb = colors['crescent_warm'] if self.is_yellow else colors['crescent_cool']
        core_color = QColor(*core_rgb, int(255 * self.life))
        painter.setPen(Qt.NoPen)
        painter.setBrush(core_color)
        painter.drawPath(unit_path)

        painter.restore()


# ─── Click Crescent ──────────────────────────────────────────────────────────

class ClickCrescent:
    def __init__(self, cx, cy, size_start, size_end, angle_start,
                 angle_speed, dist_end, delay, is_yellow):
        self.cx = cx;  self.cy = cy
        self.size_start = size_start;  self.size_end = size_end
        self.angle_start = angle_start;  self.angle_speed = angle_speed
        self.dist_end = dist_end;  self.delay = delay
        self.is_yellow = is_yellow
        self.age = 0;  self.lifetime = 20;  self.life = 1.0

    def update(self):
        if self.delay > 0:
            self.delay -= 1;  return True
        self.age += 1
        if self.age >= self.lifetime:
            return False
        self.life = 1.0 - self.age / self.lifetime
        return True

    def draw(self, painter, unit_path, colors):
        if self.delay > 0 or self.life <= 0:
            return
        t = self.age / self.lifetime
        ease = 1.0 - (1.0 - t) ** 3
        size = self.size_start + (self.size_end - self.size_start) * ease
        dist = self.dist_end * ease
        angle = self.angle_start + self.angle_speed * ease
        rad = math.radians(angle)
        x = self.cx + math.cos(rad) * dist
        y = self.cy + math.sin(rad) * dist

        painter.save()
        painter.translate(x, y)
        painter.rotate(angle)
        painter.scale(size, size)

        glow_rgb = colors['crescent_glow_warm'] if self.is_yellow else colors['crescent_glow_cool']
        glow = QColor(*glow_rgb, int(85 * self.life))
        painter.setPen(QPen(glow, 0.45));  painter.setBrush(glow)
        painter.drawPath(unit_path)

        body_rgb = colors['shockwave_b'] if self.is_yellow else colors['spark']
        body = QColor(*body_rgb, int(180 * self.life))
        painter.setPen(QPen(body, 0.15));  painter.setBrush(body)
        painter.drawPath(unit_path)

        core_rgb = colors['crescent_warm'] if self.is_yellow else colors['crescent_cool']
        core = QColor(*core_rgb, int(255 * self.life))
        painter.setPen(Qt.NoPen);  painter.setBrush(core)
        painter.drawPath(unit_path)

        painter.restore()


# ─── Shockwave Ring ──────────────────────────────────────────────────────────

class ShockwaveRing:
    def __init__(self, cx, cy, max_radius, is_yellow):
        self.cx = cx;  self.cy = cy
        self.radius = 2.0;  self.max_radius = max_radius
        self.life = 1.0;  self.decay = 0.05
        self.is_yellow = is_yellow

    def update(self):
        self.radius += (self.max_radius - self.radius) * 0.12
        self.life -= self.decay
        return self.life > 0

    def draw(self, painter, colors):
        if self.life <= 0:
            return
        painter.save()
        base_rgb = colors['shockwave_b'] if self.is_yellow else colors['shockwave_a']
        base = QColor(*base_rgb)
        painter.setPen(QPen(
            QColor(base.red(), base.green(), base.blue(), int(80 * self.life)),
            3.0 * self.life))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(self.cx, self.cy), self.radius, self.radius)
        painter.setPen(QPen(QColor(255, 255, 255, int(220 * self.life)),
                            1.0 * self.life))
        painter.drawEllipse(QPointF(self.cx, self.cy), self.radius, self.radius)
        painter.restore()


# ─── Spark Particle ──────────────────────────────────────────────────────────

class SparkParticle:
    def __init__(self, x, y, vx, vy, max_size, color_type="purple"):
        self.x = x;  self.y = y;  self.vx = vx;  self.vy = vy
        self.size = random.random() * max_size + 0.8
        self.life = 1.0
        self.decay = 0.02 + random.random() * 0.02
        self.color_type = color_type

    def update(self):
        self.x += self.vx;  self.y += self.vy
        self.vy += 0.08;  self.vx *= 0.98;  self.life -= self.decay

    def draw(self, painter, colors):
        if self.life <= 0:
            return
        r = self.size * self.life
        if self.color_type == "purple":
            c = QColor(*colors['spark'], int(255 * self.life))
        elif self.color_type == "yellow":
            c = QColor(*colors['accent'], int(255 * self.life))
        else:
            c = QColor(255, 255, 255, int(255 * self.life))
        painter.setPen(Qt.NoPen)
        painter.setBrush(c)
        painter.drawEllipse(QPointF(self.x, self.y), r, r)


# ─── Magic Circle ────────────────────────────────────────────────────────────

class MagicCircle:
    def __init__(self, cx, cy):
        self.cx = cx;  self.cy = cy
        self.age = 0;  self.lifetime = 38;  self.max_radius = 42
        self.rotation = random.random() * 360
        self.rot_speed = 4.5 if random.random() < 0.5 else -4.5
        self._hex_c = [math.cos(math.radians(i * 60)) for i in range(6)]
        self._hex_s = [math.sin(math.radians(i * 60)) for i in range(6)]
        self._tri_c = [math.cos(math.radians(i * 120 + 30)) for i in range(3)]
        self._tri_s = [math.sin(math.radians(i * 120 + 30)) for i in range(3)]

    def update(self):
        self.age += 1;  self.rotation += self.rot_speed
        return self.age < self.lifetime

    def draw(self, painter, colors):
        t = self.age / self.lifetime
        scale = min(1.0, t / 0.10)
        a_mult = 1.0 if t < 0.55 else (1.0 - t) / 0.45
        r = self.max_radius * scale
        ba = int(160 * a_mult)

        mg = colors['magic_glow']

        painter.save()
        painter.translate(self.cx, self.cy)

        gr = r * 1.35
        grad = QRadialGradient(0, 0, gr)
        grad.setColorAt(0.0, QColor(*mg[0], int(55 * a_mult)))
        grad.setColorAt(0.5, QColor(*mg[1], int(18 * a_mult)))
        grad.setColorAt(1.0, QColor(*mg[2], 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QPointF(0, 0), gr, gr)

        painter.save()
        painter.rotate(self.rotation)

        painter.setPen(QPen(QColor(*colors['magic'], ba), 2.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(0, 0), r, r)

        painter.setPen(QPen(QColor(*colors['magic_mid'], int(ba * 0.8)), 1.3))
        painter.drawEllipse(QPointF(0, 0), r * 0.72, r * 0.72)

        painter.setPen(QPen(QColor(*colors['magic_spoke'], int(ba * 0.55)), 0.8))
        for i in range(6):
            painter.drawLine(QPointF(0, 0),
                             QPointF(self._hex_c[i] * r * 0.95,
                                     self._hex_s[i] * r * 0.95))

        painter.setPen(QPen(QColor(*colors['magic_light'], ba), 0.9))
        for i in range(6):
            painter.drawEllipse(
                QPointF(self._hex_c[i] * r, self._hex_s[i] * r), 2.8, 2.8)

        painter.restore()

        painter.save()
        painter.rotate(-self.rotation * 1.6)
        painter.setPen(QPen(QColor(*colors['magic_inner'], int(ba * 0.7)), 1.0))
        painter.setBrush(Qt.NoBrush)
        ir = r * 0.42
        painter.drawEllipse(QPointF(0, 0), ir, ir)
        for i in range(3):
            i2 = (i + 1) % 3
            painter.drawLine(
                QPointF(self._tri_c[i] * ir, self._tri_s[i] * ir),
                QPointF(self._tri_c[i2] * ir, self._tri_s[i2] * ir))
        painter.restore()

        cr = r * 0.14
        cg = QRadialGradient(0, 0, cr)
        cg.setColorAt(0.0, QColor(*colors['magic_dot'], int(210 * a_mult)))
        cg.setColorAt(1.0, QColor(*colors['magic'], 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(cg))
        painter.drawEllipse(QPointF(0, 0), cr, cr)

        painter.restore()


# ─── Splash Popup (Animated Intro) ───────────────────────────────────────────

class SplashPopup(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(520, 300)
        self._center_on_screen()

        # Animation state
        self._anim_tick = 0
        self._particles = []
        self._progress = 0.0
        for _ in range(18):
            self._particles.append({
                'x': random.random() * 520,
                'y': random.random() * 300,
                'vx': (random.random() - 0.5) * 0.6,
                'vy': -0.3 - random.random() * 0.5,
                'size': 1.5 + random.random() * 2.5,
                'alpha': 0.3 + random.random() * 0.7,
                'hue': random.choice(['purple', 'gold', 'pink'])
            })

        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 520, 300)
        self.container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:0.3 #141428, stop:0.7 #110f22, stop:1 #0a0914);
                border-radius: 28px;
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #A855F7, stop:0.3 #EC4899, stop:0.6 #8B5CF6, stop:1 #3B82F6);
            }
        """)

        # Pulsing glow shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(168, 85, 247, 140))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        self._shadow = shadow

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 28, 36, 24)
        layout.setAlignment(Qt.AlignCenter)

        # Moon decoration with glow
        dec_lbl = QLabel("✦  🌙  ✦")
        dec_lbl.setStyleSheet("""
            QLabel {
                font-size: 32px;
                color: #FFD700;
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
                border: none;
            }
        """)
        dec_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(dec_lbl)
        layout.addSpacing(6)

        # Main credit: "Made by Umang Sharma"
        team_lbl = QLabel("Made by Umang Sharma")
        team_lbl.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: 800;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: transparent;
                border: none;
            }
        """)
        team_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(team_lbl)
        layout.addSpacing(2)

        # Dev tag: "dev.catalyst"
        dev_lbl = QLabel("dev.catalyst")
        dev_lbl.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 700;
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A855F7, stop:0.5 #EC4899, stop:1 #F59E0B);
                font-family: 'Consolas', 'Cascadia Code', monospace;
                background: transparent;
                border: none;
                letter-spacing: 3px;
            }
        """)
        dev_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev_lbl)
        self._dev_lbl = dev_lbl
        layout.addSpacing(8)

        # Subtitle
        sub_lbl = QLabel("Moon Breathing Cursor  •  Premium Edition")
        sub_lbl.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: 600;
                color: #7070a0;
                letter-spacing: 2px;
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
                border: none;
            }
        """)
        sub_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub_lbl)
        layout.addSpacing(14)

        # Animated progress bar
        self._progress_frame = QFrame()
        self._progress_frame.setFixedHeight(4)
        self._progress_frame.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.06);
                border-radius: 2px;
                border: none;
            }
        """)
        layout.addWidget(self._progress_frame)

        self.setWindowOpacity(0.0)

        # Fade-in animation
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)

        # Fade-out animation
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(700)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InQuad)
        self.fade_out.finished.connect(self._on_fade_out_finished)

        self.fade_in.start()

        # Animation timer for particles, glow pulse, and progress bar
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start(1000 // 40)  # 40 FPS for smooth animation

        # Hold + fade out
        self.hold_timer = QTimer(self)
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self.fade_out.start)
        self.hold_timer.start(3200)

    def _animate(self):
        self._anim_tick += 1

        # Pulse the shadow glow
        pulse = math.sin(self._anim_tick * 0.08) * 0.5 + 0.5
        blur = 50 + int(pulse * 25)
        alpha = 120 + int(pulse * 60)
        # Color cycle between purple and pink
        r = int(168 + pulse * 67)   # 168 -> 235
        g = int(85 - pulse * 17)    # 85 -> 68
        b = int(247 - pulse * 80)   # 247 -> 167
        self._shadow.setBlurRadius(blur)
        self._shadow.setColor(QColor(min(r, 255), max(g, 0), max(b, 0), min(alpha, 255)))

        # Update dev.catalyst label color cycle
        hue_shift = (self._anim_tick * 2) % 360
        color = QColor.fromHsv(hue_shift, 180, 255)
        self._dev_lbl.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 700;
                color: {color.name()};
                font-family: 'Consolas', 'Cascadia Code', monospace;
                background: transparent;
                border: none;
                letter-spacing: 3px;
            }}
        """)

        # Progress bar animation
        self._progress = min(1.0, self._progress + 0.008)

        # Update particles
        for p in self._particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['y'] < -5:
                p['y'] = 305
                p['x'] = random.random() * 520
            if p['x'] < -5 or p['x'] > 525:
                p['x'] = random.random() * 520

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw floating particles
        for p in self._particles:
            alpha = int(p['alpha'] * 255 * 0.6)
            if p['hue'] == 'purple':
                color = QColor(168, 85, 247, alpha)
            elif p['hue'] == 'gold':
                color = QColor(255, 215, 0, alpha)
            else:
                color = QColor(236, 72, 153, alpha)

            grad = QRadialGradient(p['x'], p['y'], p['size'] * 2)
            grad.setColorAt(0.0, color)
            grad.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawEllipse(QPointF(p['x'], p['y']), p['size'] * 2, p['size'] * 2)

            # Core dot
            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.drawEllipse(QPointF(p['x'], p['y']), p['size'] * 0.4, p['size'] * 0.4)

        # Draw progress bar fill
        if self._progress > 0.01:
            bar_x = 36
            bar_y = 300 - 24 - 4
            bar_w = (520 - 72) * self._progress
            bar_h = 4

            # Gradient fill for progress bar
            bar_grad = QLinearGradient(bar_x, bar_y, bar_x + (520 - 72), bar_y)
            t = self._anim_tick * 0.03
            bar_grad.setColorAt(0.0, QColor(168, 85, 247, 220))
            bar_grad.setColorAt(0.5, QColor(236, 72, 153, 220))
            bar_grad.setColorAt(1.0, QColor(59, 130, 246, 220))

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(bar_grad))

            path = QPainterPath()
            path.addRoundedRect(bar_x, bar_y, bar_w, bar_h, 2, 2)
            painter.drawPath(path)

            # Glow on progress bar tip
            tip_x = bar_x + bar_w
            tip_grad = QRadialGradient(tip_x, bar_y + 2, 8)
            tip_grad.setColorAt(0.0, QColor(255, 255, 255, 160))
            tip_grad.setColorAt(1.0, QColor(168, 85, 247, 0))
            painter.setBrush(QBrush(tip_grad))
            painter.drawEllipse(QPointF(tip_x, bar_y + 2), 8, 8)

        painter.end()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2,
                  (screen.height() - self.height()) // 2)

    def _on_fade_out_finished(self):
        self._anim_timer.stop()
        self.close()
        self.callback()


# ─── Settings Panel (Premium Dark UI) ────────────────────────────────────────

class SettingsPanel(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self._drag_pos = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 540)

        self._build_ui()
        self._center_on_screen()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2,
                  (screen.height() - self.height()) // 2)

    # ── Build UI ─────────────────────────────────────────────────────────

    def _build_ui(self):
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 400, 540)
        self.container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:0.5 #16162a, stop:1 #111122);
                border-radius: 18px;
                border: 1px solid rgba(255,255,255,0.07);
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(24, 18, 24, 22)
        layout.setSpacing(14)

        # ── Title bar ──
        title_bar = QHBoxLayout()
        title_icon = QLabel("☽")
        title_icon.setStyleSheet("font-size:24px; color:#FFD700; background:transparent; border:none;")
        title_lbl = QLabel("Moon Breathing Cursor")
        title_lbl.setStyleSheet(
            "font-size:17px; font-weight:bold; color:#e0d0ff;"
            "font-family:'Segoe UI',sans-serif; background:transparent; border:none;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton { background:transparent; color:#666; font-size:15px;
                          border-radius:15px; border:none; }
            QPushButton:hover { background:#ff4466; color:white; }
        """)
        close_btn.clicked.connect(self.hide)
        title_bar.addWidget(title_icon)
        title_bar.addSpacing(6)
        title_bar.addWidget(title_lbl)
        title_bar.addStretch()
        title_bar.addWidget(close_btn)
        layout.addLayout(title_bar)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background:rgba(255,255,255,0.06); border:none;")
        layout.addWidget(sep)

        # ── Smoke Intensity ──
        layout.addWidget(self._make_section("🌫  Smoke Intensity",
                                            self._build_smoke_section()))

        # ── Trail Length ──
        layout.addWidget(self._make_section("✨  Trail Length",
                                            self._build_trail_section()))

        # ── Color Theme ──
        layout.addWidget(self._make_section("🎨  Color Theme",
                                            self._build_color_section()))

        # ── System ──
        layout.addWidget(self._make_section("⚙  System",
                                            self._build_system_section()))

        layout.addStretch()

        # ── Bottom buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        min_btn = QPushButton("  Minimize to Tray  ")
        min_btn.setStyleSheet("""
            QPushButton { background:rgba(168,85,247,0.12); color:#c0a0f0;
                border:1px solid rgba(168,85,247,0.25); border-radius:10px;
                padding:10px 18px; font-size:12px; font-weight:bold;
                font-family:'Segoe UI',sans-serif; }
            QPushButton:hover { background:rgba(168,85,247,0.28);
                border:1px solid rgba(168,85,247,0.45); }
        """)
        min_btn.clicked.connect(self.hide)

        quit_btn = QPushButton("  Quit  ")
        quit_btn.setStyleSheet("""
            QPushButton { background:rgba(239,68,68,0.10); color:#f08080;
                border:1px solid rgba(239,68,68,0.22); border-radius:10px;
                padding:10px 18px; font-size:12px; font-weight:bold;
                font-family:'Segoe UI',sans-serif; }
            QPushButton:hover { background:rgba(239,68,68,0.28);
                border:1px solid rgba(239,68,68,0.45); }
        """)
        quit_btn.clicked.connect(QApplication.quit)

        btn_row.addWidget(min_btn)
        btn_row.addWidget(quit_btn)
        layout.addLayout(btn_row)

    # ── Section helpers ──────────────────────────────────────────────────

    def _make_section(self, title, content_widget):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background:rgba(255,255,255,0.025); border-radius:14px;
                     border:1px solid rgba(255,255,255,0.04); }
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(16, 12, 16, 14)
        lay.setSpacing(8)

        lbl = QLabel(title)
        lbl.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#c0b0e0;"
            "font-family:'Segoe UI',sans-serif; background:transparent; border:none;")
        lay.addWidget(lbl)
        lay.addWidget(content_widget)
        return frame

    _SLIDER_QSS = """
        QSlider::groove:horizontal { height:6px; background:#2a2a3a; border-radius:3px; }
        QSlider::handle:horizontal { width:18px; height:18px; margin:-6px 0;
            background:qradialgradient(cx:0.5,cy:0.5,radius:0.5,fx:0.5,fy:0.3,
                stop:0 #e0d0ff, stop:0.7 #A855F7, stop:1 #7C3AED);
            border-radius:9px; border:2px solid rgba(255,255,255,0.18); }
        QSlider::handle:horizontal:hover {
            background:qradialgradient(cx:0.5,cy:0.5,radius:0.5,fx:0.5,fy:0.3,
                stop:0 #f0e0ff, stop:0.7 #C084FC, stop:1 #A855F7); }
        QSlider::sub-page:horizontal { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #7C3AED, stop:1 #A855F7); border-radius:3px; }
    """

    _LABEL_QSS = ("color:#8080a0; font-size:11px; font-family:'Segoe UI',sans-serif;"
                  "background:transparent; border:none;")
    _VALUE_QSS = ("color:#d0c0f0; font-size:12px; font-weight:bold;"
                  "font-family:'Segoe UI',sans-serif; background:transparent; border:none;")

    def _build_smoke_section(self):
        w = QWidget()
        w.setStyleSheet("background:transparent; border:none;")
        lay = QVBoxLayout(w);  lay.setContentsMargins(0,0,0,0);  lay.setSpacing(4)

        self.smoke_slider = QSlider(Qt.Horizontal)
        self.smoke_slider.setRange(0, 100)
        self.smoke_slider.setValue(self.settings.smoke_intensity)
        self.smoke_slider.setStyleSheet(self._SLIDER_QSS)

        row = QHBoxLayout();  row.setContentsMargins(0,0,0,0)
        lo = QLabel("Subtle");  lo.setStyleSheet(self._LABEL_QSS)
        self.smoke_val = QLabel(f"{self.settings.smoke_intensity}%")
        self.smoke_val.setStyleSheet(self._VALUE_QSS)
        self.smoke_val.setAlignment(Qt.AlignCenter)
        hi = QLabel("Intense");  hi.setStyleSheet(self._LABEL_QSS)
        hi.setAlignment(Qt.AlignRight)
        row.addWidget(lo);  row.addWidget(self.smoke_val);  row.addWidget(hi)

        lay.addWidget(self.smoke_slider)
        lay.addLayout(row)

        self.smoke_slider.valueChanged.connect(self._on_smoke)
        return w

    def _build_trail_section(self):
        w = QWidget()
        w.setStyleSheet("background:transparent; border:none;")
        lay = QVBoxLayout(w);  lay.setContentsMargins(0,0,0,0);  lay.setSpacing(4)

        self.trail_slider = QSlider(Qt.Horizontal)
        self.trail_slider.setRange(0, 100)
        self.trail_slider.setValue(self.settings.trail_length)
        self.trail_slider.setStyleSheet(self._SLIDER_QSS)

        row = QHBoxLayout();  row.setContentsMargins(0,0,0,0)
        lo = QLabel("Short");  lo.setStyleSheet(self._LABEL_QSS)
        self.trail_val = QLabel(f"{self.settings.trail_length}%")
        self.trail_val.setStyleSheet(self._VALUE_QSS)
        self.trail_val.setAlignment(Qt.AlignCenter)
        hi = QLabel("Long");  hi.setStyleSheet(self._LABEL_QSS)
        hi.setAlignment(Qt.AlignRight)
        row.addWidget(lo);  row.addWidget(self.trail_val);  row.addWidget(hi)

        lay.addWidget(self.trail_slider)
        lay.addLayout(row)

        self.trail_slider.valueChanged.connect(self._on_trail)
        return w

    def _build_color_section(self):
        w = QWidget()
        w.setStyleSheet("background:transparent; border:none;")
        lay = QHBoxLayout(w);  lay.setContentsMargins(0,0,0,0);  lay.setSpacing(10)

        self.color_btns = {}
        for name in COLOR_PRESETS:
            btn = QPushButton()
            btn.setFixedSize(44, 44)
            btn.setToolTip(name)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            self.color_btns[name] = btn
            btn.clicked.connect(lambda _, n=name: self._on_color(n))
            lay.addWidget(btn)
        lay.addStretch()

        self._refresh_color_btns()
        return w

    def _build_system_section(self):
        w = QWidget()
        w.setStyleSheet("background:transparent; border:none;")
        lay = QHBoxLayout(w);  lay.setContentsMargins(0,0,0,0)

        lbl = QLabel("Start on Windows startup")
        lbl.setStyleSheet("color:#b0a0c0; font-size:12px; font-family:'Segoe UI',sans-serif;"
                          "background:transparent; border:none;")

        self.startup_btn = QPushButton()
        self.startup_btn.setCheckable(True)
        self.startup_btn.setChecked(self.settings.start_on_startup)
        self.startup_btn.setFixedSize(64, 30)
        self.startup_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.startup_btn.clicked.connect(self._on_startup)
        self._refresh_toggle()

        lay.addWidget(lbl);  lay.addStretch();  lay.addWidget(self.startup_btn)
        return w

    # ── Callbacks ─────────────────────────────────────────────────────────

    def _on_smoke(self, v):
        self.settings.smoke_intensity = v
        self.smoke_val.setText(f"{v}%")
        self.settings.save()

    def _on_trail(self, v):
        self.settings.trail_length = v
        self.trail_val.setText(f"{v}%")
        self.settings.save()

    def _on_color(self, name):
        self.settings.color_name = name
        self._refresh_color_btns()
        self.settings.save()

    def _on_startup(self):
        self.settings.start_on_startup = self.startup_btn.isChecked()
        self._refresh_toggle()
        self._set_startup(self.settings.start_on_startup)
        self.settings.save()

    # ── Refresh helpers ──────────────────────────────────────────────────

    def _refresh_color_btns(self):
        for name, btn in self.color_btns.items():
            p = COLOR_PRESETS[name]
            sel = (name == self.settings.color_name)
            border = "3px solid #fff" if sel else "3px solid transparent"
            btn.setStyleSheet(f"""
                QPushButton {{ background:{p['btn']}; border-radius:22px; border:{border}; }}
                QPushButton:hover {{ background:{p['btn_hover']};
                    border:3px solid rgba(255,255,255,0.5); }}
            """)

    def _refresh_toggle(self):
        on = self.startup_btn.isChecked()
        if on:
            self.startup_btn.setText("ON")
            self.startup_btn.setStyleSheet("""
                QPushButton { background:#A855F7; color:white; border-radius:15px;
                    font-weight:bold; font-size:11px; border:none; }
                QPushButton:hover { background:#9333EA; }
            """)
        else:
            self.startup_btn.setText("OFF")
            self.startup_btn.setStyleSheet("""
                QPushButton { background:#2a2a3a; color:#666; border-radius:15px;
                    font-weight:bold; font-size:11px; border:1px solid #3a3a4a; }
                QPushButton:hover { background:#353548; }
            """)

    def _set_startup(self, enable):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run",
                                0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
            app_name = "MoonBreathingCursor"
            if enable:
                if getattr(sys, 'frozen', False):
                    cmd = f'"{sys.executable}"'
                else:
                    cmd = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass

    # ── Draggable window ─────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def paintEvent(self, event):
        # Draw rounded clip for the container
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.end()


# ─── Main Overlay ────────────────────────────────────────────────────────────

class MoonBreathingOverlay(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.SubWindow |
            Qt.WindowTransparentForInput
        )

        screen = QApplication.primaryScreen()
        sz = screen.size()
        self.setGeometry(0, 0, sz.width(), sz.height())

        # Pre-compute unit crescent path
        self.unit_path = QPainterPath()
        self.unit_path.addEllipse(-1.0, -1.0, 2.0, 2.0)
        cutout = QPainterPath()
        cutout.addEllipse(-0.78 + 0.42, -0.78, 0.78 * 2, 0.78 * 2)
        self.unit_path = self.unit_path.subtracted(cutout)

        # Particle lists
        self.trail = []
        self.smoke = []
        self.crescents = []
        self.sparks = []
        self.click_crescents = []
        self.shockwaves = []
        self.magic_circles = []

        self.last_mouse_pos = QCursor.pos()
        self.click_count = 0           # counter instead of boolean

        # Listeners
        self.mouse_listener = pynput_mouse.Listener(on_click=self._on_click)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()

        self.kb_listener = pynput_kb.Listener(on_press=self._on_key)
        self.kb_listener.daemon = True
        self.kb_listener.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(1000 // FPS)

    # ── Input ────────────────────────────────────────────────────────────

    def _on_click(self, x, y, button, pressed):
        if pressed and button == pynput_mouse.Button.left:
            self.click_count += 1

    def _on_key(self, key):
        if key == pynput_kb.Key.esc:
            QApplication.quit()

    # ── Game loop ────────────────────────────────────────────────────────

    def game_loop(self):
        now = time.time()
        curr = QCursor.pos()
        cx, cy = curr.x(), curr.y()
        s = self.settings
        max_trail = s.max_trail
        max_smoke = s.max_smoke
        trail_lt = s.trail_lifetime

        # 1. Trail update
        if curr != self.last_mouse_pos:
            if (not self.trail or
                    (cx - self.trail[-1].x) ** 2 +
                    (cy - self.trail[-1].y) ** 2 > MIN_TRAIL_DIST_SQ):
                self.trail.append(TrailPoint(cx, cy))
                if len(self.trail) > max_trail:
                    self.trail = self.trail[-max_trail:]

            # Smoke
            dist = math.hypot(cx - self.last_mouse_pos.x(),
                              cy - self.last_mouse_pos.y())
            speed_div = max(6.0, s.smoke_speed_divisor)
            smoke_count = 1 + int(dist / speed_div)
            intensity = 1.0 + min(dist / 12.0, 3.0) * 0.3
            for _ in range(smoke_count):
                if len(self.smoke) < max_smoke and random.random() < s.smoke_spawn_chance:
                    spread = min(dist * 0.4, 30)
                    ox = (random.random() - 0.5) * spread
                    oy = (random.random() - 0.5) * spread
                    self.smoke.append(SmokeParticle(cx + ox, cy + oy, intensity))

            # Sparks
            if len(self.sparks) < MAX_SPARKS:
                for _ in range(2):
                    vx = (random.random() - 0.5) * 2.0
                    vy = (random.random() - 0.5) * 2.0 - 0.5
                    self.sparks.append(SparkParticle(
                        cx, cy, vx, vy, max_size=2.2,
                        color_type="purple" if random.random() < 0.7 else "yellow"))

            # Trail crescents
            if len(self.crescents) < MAX_CRESCENTS and random.random() < 0.22:
                self.crescents.append(CrescentParticle(
                    cx + (random.random() - 0.5) * 8,
                    cy + (random.random() - 0.5) * 8,
                    size=6 + random.random() * 7,
                    angle=random.random() * 360,
                    speed=random.random() * 4 - 2,
                    drift_x=(random.random() - 0.5) * 0.8,
                    drift_y=(random.random() - 0.5) * 0.8,
                    hue="purple" if random.random() < 0.5 else "yellow"))

        self.last_mouse_pos = curr
        self.trail = [p for p in self.trail if now - p.time < trail_lt]

        # 2. Click handling — process ALL queued clicks
        clicks = self.click_count
        self.click_count = 0
        for _ in range(clicks):
            self.magic_circles.append(MagicCircle(cx, cy))

            self.shockwaves.append(ShockwaveRing(cx, cy, 18.0, False))
            self.shockwaves.append(ShockwaveRing(cx, cy, 28.0, True))

            for i in range(4):
                self.click_crescents.append(ClickCrescent(
                    cx, cy, 3, 10 + random.random() * 4,
                    i * 90, 100.0 + random.random() * 60.0,
                    14 + random.random() * 6, i, (i % 2 == 0)))

            for _ in range(5):
                if len(self.smoke) < max_smoke:
                    self.smoke.append(SmokeParticle(
                        cx + (random.random() - 0.5) * 16,
                        cy + (random.random() - 0.5) * 16,
                        intensity=1.5))

            for _ in range(8):
                spd = 1.0 + random.random() * 2.0
                a = random.random() * math.pi * 2
                self.sparks.append(SparkParticle(
                    cx, cy, math.cos(a) * spd, math.sin(a) * spd,
                    2.0, "yellow" if random.random() < 0.6 else "purple"))

        # 3. Update particles
        self.smoke = [p for p in self.smoke if (p.update() or True) and p.life > 0]
        self.crescents = [c for c in self.crescents if (c.update() or True) and c.life > 0]
        self.sparks = [p for p in self.sparks if (p.update() or True) and p.life > 0]
        self.click_crescents = [c for c in self.click_crescents if c.update()]
        self.shockwaves = [w for w in self.shockwaves if w.update()]
        self.magic_circles = [m for m in self.magic_circles if m.update()]

        self.update()

    # ── Catmull-Rom spline ───────────────────────────────────────────────

    def _build_smooth_trail(self):
        n = len(self.trail)
        if n < 2:
            return []
        pts = []
        for i in range(n - 1):
            p0 = self.trail[max(0, i - 1)]
            p1 = self.trail[i]
            p2 = self.trail[min(n - 1, i + 1)]
            p3 = self.trail[min(n - 1, i + 2)]
            for s in range(INTERP_STEPS):
                t = s / INTERP_STEPS;  t2 = t * t;  t3 = t2 * t
                x = 0.5 * ((2 * p1.x) +
                            (-p0.x + p2.x) * t +
                            (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 +
                            (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3)
                y = 0.5 * ((2 * p1.y) +
                            (-p0.y + p2.y) * t +
                            (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 +
                            (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3)
                tv = p1.time + (p2.time - p1.time) * t
                pts.append((x, y, tv))
        last = self.trail[-1]
        pts.append((last.x, last.y, last.time))
        return pts

    # ── Trail renderer ───────────────────────────────────────────────────

    def _draw_trail(self, painter, now):
        smooth = self._build_smooth_trail()
        if len(smooth) < 2:
            return

        trail_lt = self.settings.trail_lifetime
        tc = self.settings.colors['trail']
        paths = [QPainterPath() for _ in range(ALPHA_BUCKETS)]

        for i in range(1, len(smooth)):
            x0, y0, _ = smooth[i - 1]
            x1, y1, t1 = smooth[i]
            age = now - t1
            life = max(0.0, 1.0 - age / trail_lt)
            b = min(int(life * ALPHA_BUCKETS), ALPHA_BUCKETS - 1)
            if b < 0:
                continue
            paths[b].moveTo(x0, y0)
            paths[b].lineTo(x1, y1)

        for b in range(ALPHA_BUCKETS):
            if paths[b].isEmpty():
                continue
            a = (b + 0.5) / ALPHA_BUCKETS

            # 5 blended glow layers
            painter.setPen(QPen(QColor(*tc[0], int(18 * a)),
                max(3.0, 28.0 * a), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(paths[b])

            painter.setPen(QPen(QColor(*tc[1], int(32 * a)),
                max(2.5, 20.0 * a), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(paths[b])

            painter.setPen(QPen(QColor(*tc[2], int(60 * a)),
                max(1.8, 13.0 * a), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(paths[b])

            painter.setPen(QPen(QColor(*tc[3], int(110 * a)),
                max(1.0, 7.0 * a), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(paths[b])

            painter.setPen(QPen(QColor(*tc[4], int(160 * a)),
                max(0.6, 3.0 * a), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(paths[b])

    # ── Paint ────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        now = time.time()
        colors = self.settings.colors
        trail_lt = self.settings.trail_lifetime

        # 1. Smoke
        sc = colors['smoke']
        for s in self.smoke:
            s.draw(painter, sc)

        # 2. Trail
        self._draw_trail(painter, now)

        # Cursor ambient orb
        if self.trail:
            tip = self.trail[-1]
            tl = max(0.0, 1.0 - (now - tip.time) / trail_lt)
            if tl > 0.1:
                rad = 26
                grad = QRadialGradient(tip.x, tip.y, rad)
                grad.setColorAt(0.0, QColor(*colors['orb'], int(90 * tl)))
                grad.setColorAt(1.0, QColor(*colors['glow_edge'], 0))
                painter.setBrush(QBrush(grad))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPointF(tip.x, tip.y), rad, rad)

        # 3. Magic circles
        for mc in self.magic_circles:
            mc.draw(painter, colors)

        # 4. Shockwaves
        for sw in self.shockwaves:
            sw.draw(painter, colors)

        # 5. Click crescents
        for c in self.click_crescents:
            c.draw(painter, self.unit_path, colors)

        # 6. Trail crescents
        for c in self.crescents:
            c.draw(painter, self.unit_path, colors)

        # 7. Sparks
        for sp in self.sparks:
            sp.draw(painter, colors)

        # 8. Cursor decoration
        self._draw_cursor_decorations(painter, colors)

    # ── Cursor decoration ────────────────────────────────────────────────

    def _draw_cursor_decorations(self, painter, colors):
        curr = QCursor.pos()
        cx, cy = curr.x(), curr.y()
        t = time.time()

        rad = 16
        grad = QRadialGradient(cx, cy, rad)
        grad.setColorAt(0.0, QColor(*colors['glow_center'], 100))
        grad.setColorAt(1.0, QColor(*colors['glow_edge'], 0))
        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - rad, cy - rad, rad * 2, rad * 2)

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(t * 150.0)
        painter.translate(11.0, 0)
        painter.rotate(t * 100.0)
        painter.scale(5.0, 5.0)

        painter.setBrush(QColor(*colors['crescent_warm'], 230))
        painter.setPen(QPen(QColor(*colors['crescent_glow_warm'], 180), 0.16))
        painter.drawPath(self.unit_path)
        painter.restore()

    # ── Cleanup ──────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self.mouse_listener.stop()
        self.kb_listener.stop()
        event.accept()


# ─── Tray Icon ───────────────────────────────────────────────────────────────

def create_tray_icon():
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(3, 3, 26, 26)
    cutout = QPainterPath()
    cutout.addEllipse(11, 1, 22, 22)
    path = path.subtracted(cutout)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(255, 215, 0))
    p.drawPath(path)
    p.end()
    return QIcon(pixmap)


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    settings = Settings()

    overlay = MoonBreathingOverlay(settings)
    overlay.show()

    panel = SettingsPanel(settings)

    splash = SplashPopup(panel.show)
    splash.show()

    # System tray
    tray = QSystemTrayIcon(create_tray_icon(), app)

    tray_menu = QMenu()
    tray_menu.setStyleSheet("""
        QMenu { background:#1e1e2e; color:#d0c0f0; border:1px solid #333;
                border-radius:8px; padding:6px; font-family:'Segoe UI'; }
        QMenu::item { padding:8px 24px; border-radius:4px; }
        QMenu::item:selected { background:#A855F7; color:white; }
    """)

    settings_action = QAction("⚙  Settings", tray_menu)
    settings_action.triggered.connect(panel.show)
    tray_menu.addAction(settings_action)

    tray_menu.addSeparator()

    quit_action = QAction("✕  Quit", tray_menu)
    quit_action.triggered.connect(QApplication.quit)
    tray_menu.addAction(quit_action)

    tray.setContextMenu(tray_menu)
    tray.activated.connect(lambda reason: panel.show()
                           if reason == QSystemTrayIcon.DoubleClick else None)
    tray.setToolTip("Moon Breathing Cursor")
    tray.show()

    sys.exit(app.exec())
