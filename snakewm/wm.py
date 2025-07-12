"""
Snake Window Manager - ModernGL Version
"""

import os
import sys
import importlib
import numpy as np
import moderngl
from moderngl_window.context.base import BaseWindow
import evdev  # Ensure BR2_PACKAGE_PYTHON_EVDEV=y in defconfig
import freetype as ft  # Add BR2_PACKAGE_PYTHON_FREETYPE_PY=y (custom package)

TESTMODE = __name__ == "__main__"

if TESTMODE:
    from appmenu.appmenupanel import AppMenuPanel
    from snakebg.bg import SnakeBG
    from snakebg.bgmenu import SnakeBGMenu
else:
    from snakewm.appmenu.appmenupanel import AppMenuPanel
    from snakewm.snakebg.bg import SnakeBG
    from snakewm.snakebg.bgmenu import SnakeBGMenu

os.environ['EGL_PLATFORM'] = 'drm'
os.environ['MESA_GL_VERSION_OVERRIDE'] = '4.3'  # Adjust based on hardware

class SnakeWM(BaseWindow):
    SCREEN = None
    DIMS = None
    BG_COLOR = (0.0, 0.5, 0.5)  # Teal blue for modern look

    # Paint properties (modernized with shaders)
    PAINT = False
    PAINT_RADIUS = 10.0
    PAINT_COLOR = 0
    PAINT_COLOR_LIST = [
        (1.0, 1.0, 1.0), (0.75, 0.75, 0.75), (0.5, 0.5, 0.5), (0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0), (0.0, 0.5, 0.0), (0.5, 0.5, 0.0), (0.0, 0.5, 0.5),
        (1.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 0.0, 0.5), (1.0, 0.0, 1.0),
        (0.0, 0.0, 1.0), (0.0, 0.0, 0.5), (0.0, 1.0, 1.0), (1.0, 1.0, 0.0),
    ]
    PAINT_SHAPE = 0
    NUM_SHAPES = 3

    # Dynamic BG and menu
    DYNBG = None
    DYNBG_MENU = None

    # Focused window
    FOCUS = None

    # Apps tree
    APPS = {}
    APPMENU = None

    # Font for text rendering (modern UI)
    FONT = None
    FONT_TEXTURES = {}  # Cache glyph textures

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # DRM setup with fallback
        try:
            self.drm_fd = os.open('/dev/dri/card0', os.O_RDWR)
            self.ctx = moderngl.create_context(standalone=True, require=430)
        except OSError:
            # Fallback to software context if DRM fails
            self.ctx = moderngl.create_context(standalone=True, backend='egl')  # Or 'glx' if X is available
            print("Warning: DRM failed, using fallback context")

        # Get screen dimensions (assume from DRM or fallback)
        self.DIMS = (1920, 1080)  # Replace with actual query if possible (use pydrm)

        # Basic shader for colored quads (modern: with gradient uniform)
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 430
                in vec2 in_vert;
                in vec3 in_color;
                out vec3 v_color;
                uniform mat4 model;
                void main() {
                    gl_Position = model * vec4(in_vert, 0.0, 1.0);
                    v_color = in_color;
                }
            ''',
            fragment_shader='''
                #version 430
                in vec3 v_color;
                out vec4 f_color;
                void main() {
                    f_color = vec4(v_color, 1.0);
                }
            '''
        )

        # Background gradient quad
        self.bg_vertices = self.ctx.buffer(np.array([
            -1.0, -1.0, 0.0, 0.5, 1.0,  # Bottom-left
            1.0, -1.0, 0.0, 0.2, 0.8,   # Bottom-right
            -1.0, 1.0, 0.1, 0.1, 0.5,   # Top-left
            1.0, 1.0, 0.0, 0.0, 0.3,    # Top-right (darker blue gradient)
        ], dtype='f4'))

        self.bg_vao = self.ctx.vertex_array(self.prog, self.bg_vertices, 'in_vert in_color')

        # Input devices
        self.keyboard = evdev.InputDevice('/dev/input/event0')  # Keyboard event
        self.mouse = evdev.InputDevice('/dev/input/event1')  # Mouse event

        # Populate apps tree
        apps_path = os.path.dirname(os.path.abspath(__file__)) + "/apps"
        self.iter_dir(self.APPS, apps_path)

        # Load font for text (modern UI fonts)
        self.FONT = ft.Face('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')  # Assume font in system
        self.FONT.set_pixel_sizes(0, 24)  # Size 24

        # Modern UI: Windows as list of dicts (position, size, color, texture for content)
        self.windows = []

    @staticmethod
    def iter_dir(tree, path):
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f, "__init__.py")):
                tree[f] = None
            elif os.path.isdir(os.path.join(path, f)):
                tree[f] = {}
                SnakeWM.iter_dir(tree[f], os.path.join(path, f))

    def loadapp(self, app, params=None):
        if not TESTMODE:
            app = "snakewm." + app

        _app = importlib.import_module(app)

        try:
            # Apps now return a 'window' dict with pos, size, color, content func
            window = _app.load(params)  # Assume apps updated to return dict
            self.windows.append(window)
        except:
            self.ctx.finish()

    def appmenu_load(self, app):
        if self.APPMENU is not None:
            self.APPMENU = None  # Close menu (no destroy, as no Pygame UI)

        self.loadapp(app)

    def set_bg_color(self, color):
        self.BG_COLOR = color

    def set_bg_image(self, file):
        # Load image to texture (use PIL or built-in, assume PIL added)
        import PIL.Image
        img = PIL.Image.open(file)
        self.bg_texture = self.ctx.texture(img.size, 3, img.tobytes())
        # Update shader to use texture uniform

    def render_text(self, text, pos, color):
        # Simple glyph rendering (modern: cache textures)
        for char in text:
            if char not in self.FONT_TEXTURES:
                self.FONT.load_char(char)
                glyph = self.FONT.glyph
                bitmap = glyph.bitmap
                tex_data = np.array(bitmap.buffer, dtype='u1').reshape(bitmap.rows, bitmap.width)
                tex = self.ctx.texture((bitmap.width, bitmap.rows), 1, tex_data.tobytes())
                self.FONT_TEXTURES[char] = tex

            # Draw textured quad at pos for char
            # ... (implement quad with texture shader)
            pos = (pos[0] + self.FONT.advance.x / 64, pos[1])

    def render(self):
        self.ctx.clear(*self.BG_COLOR)

        # Render background gradient
        self.prog['model'].value = np.eye(4)  # Identity matrix
        self.bg_vao.render(moderngl.TRIANGLE_STRIP)

        # Render windows (modern: with shadow shader)
        for window in self.windows:
            # Draw window quad with border/shadow
            # Example shader uniform for position/size
            model = np.eye(4)
            model = np.translate(model, window['pos'][0] / self.DIMS[0] * 2 - 1, window['pos'][1] / self.DIMS[1] * 2 - 1, 0)
            model = np.scale(model, window['size'][0] / self.DIMS[0], window['size'][1] / self.DIMS[1], 1)
            self.prog['model'].value = model.flatten()
            self.vao.render(moderngl.TRIANGLE_STRIP)  # Assume vao for window quad

            # Render window content (app.draw())
            if 'content' in window:
                window['content'](self.ctx)

            # Render title/text
            self.render_text(window['title'], window['pos'], (1.0, 1.0, 1.0))

        # Render menu if open (modern: semi-transparent list with shadow)
        if self.APPMENU:
            # Draw menu quad
            # List items with text
            for i, item in enumerate(self.menu_items):
                self.render_text(item, (100, 100 + i * 30), (1.0, 1.0, 1.0))

        # Paint mode (modern: draw shapes with shaders)
        if self.PAINT:
            mpos = self.mouse_pos  # From mouse event
            color = self.PAINT_COLOR_LIST[self.PAINT_COLOR]
            if self.PAINT_SHAPE == 0:  # Circle
                # Draw circle quad approximation
                pass  # Implement circle shader or tesselate
            # Similarly for square/triangle

        if self.DYNBG:
            self.DYNBG.draw(self.ctx)  # Assume updated to ModernGL

    def run(self):
        self.running = True
        while self.running:
            # Poll input
            for event in self.keyboard.read():
                if event.type == evdev.ecodes.EV_KEY and event.value == 1:  # Key down
                    if event.code == evdev.ecodes.KEY_LEFTMETA:
                        if self.APPMENU is None:
                            self.APPMENU = True  # Toggle menu
                        else:
                            self.APPMENU = None
                    if event.code == evdev.ecodes.KEY_LALT:
                        # Handle Alt combinations
                        pass

            # Mouse events
            for event in self.mouse.read():
                if event.type == evdev.ecodes.EV_ABS:
                    # Update mouse pos
                    pass

            self.render()
            self.ctx.finish()  # Swap implicitly or manual DRM flip

if __name__ == '__main__':
    wm = SnakeWM()
    wm.run()