#
import os

from OpenGL.GL import *
from PySide6.QtGui import QImage

TEXTURE_DIR = 'assets/textures'

class TextureService:
    """ Texture Service Class, responsible for retrieving and unpacking loading textures for 3D rendering."""
    def __init__(self):
        self.textures = {}

    def loadTexture(self, imagePath):
        """Bind a texture from an image file."""
        if imagePath not in self.textures:
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            image = QImage(imagePath)
            image = image.convertToFormat(QImage.Format.Format_RGBA8888)
            image = image.mirrored(False, True)
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                image.width(),
                image.height(),
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                image.bits()
            )
            print(f"Loading texture: {imagePath}")
            self.textures[imagePath] = texture
        return self.textures[imagePath]

    def findTexturePath(self, quality: str, texture_key: str):
        """Finds a texture path based on quality and texture_key."""
        quality_dir = os.path.join(TEXTURE_DIR, quality)
        if os.path.exists(quality_dir):
            for texture_file in os.listdir(quality_dir):
                if texture_file.startswith(texture_key):
                    return os.path.join(quality_dir, texture_file)
        return None

    def getTexture(self, quality: str, texture_key: str):
        """Finds a texture path, loads it if necessary, and returns the texture ID."""
        texture_path = self.findTexturePath(quality, texture_key)
        if texture_path:
            return self.loadTexture(texture_path)
        return None