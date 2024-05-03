#
import os

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PySide6.QtGui import QImage

TEXTURE_DIR = 'assets\textures'

class TextureService:
    """ Texture Service Class, responsible for retrieving and unpacking loading textures for 3D rendering."""
    def __init__(self):
        pass

    def getTextures(self, quality: str):
        """Returns a dictionary of loaded of textures based on the quality which corresponds to a folder of images in the 'assets\textures' directory"""
        for folder in os.listdir(TEXTURE_DIR):
            if folder == quality:
                textures = {}
                for texture in os.listdir(os.path.join(TEXTURE_DIR, folder)):
                    texture_key = texture.split("_")[0]
                    textures[texture_key] = self.build(os.path.join(TEXTURE_DIR, folder, texture))
                return textures
            else:
                continue
        return None

    def build(self, imagePath):
        """Build a texture from an image file."""
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
        return texture