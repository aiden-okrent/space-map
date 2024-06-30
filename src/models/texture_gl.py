#
import os
from config.paths import TEXTURES
from OpenGL import GL
from PySide6.QtGui import QImage


class TexturesGL:
    """TexturesGL Class, responsible for retrieving and unpacking loading textures for 3D rendering."""

    def __init__(self):
        self.textures = {}

    def loadTexture(self, imagePath):
        """Bind a texture from an image file."""
        if imagePath not in self.textures:
            GL.glMatrixMode(GL.GL_TEXTURE)
            texture = GL.glGenTextures(1)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            image = QImage(imagePath)
            image = image.convertToFormat(QImage.Format.Format_RGBA8888)
            image = image.mirrored(False, True)
            GL.glTexImage2D(
                GL.GL_TEXTURE_2D,
                0,
                GL.GL_RGBA,
                image.width(),
                image.height(),
                0,
                GL.GL_RGBA,
                GL.GL_UNSIGNED_BYTE,
                image.bits(),
            )
            GL.glMatrixMode(GL.GL_MODELVIEW)

            self.textures[imagePath] = texture
        return texture

    def findTexturePath(self, quality: str, texture: str):
        """Finds a texture path based on quality and texture."""
        quality_dir = os.path.join(TEXTURES, quality)
        if os.path.exists(quality_dir):
            for texture_file in os.listdir(quality_dir):
                if texture_file.startswith(texture):
                    return os.path.join(quality_dir, texture_file)
        return None

    def getTexture(self, quality: str, texture: str):
        """Finds a texture path, loads it if necessary, and returns the texture ID."""
        texture_path = self.findTexturePath(quality, texture)
        if texture_path:
            return self.loadTexture(texture_path)
        return None
