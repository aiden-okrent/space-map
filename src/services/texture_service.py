#
import os

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

TEXTURE_DIR = 'assets/textures'

class TextureService:
    """ Texture Service Class, responsible for retrieving and unpacking loading textures for 3D rendering."""
    def __init__(self):
        pass

    def getTexture(self, quality: str, texture_key: str):
        """Returns a loaded texture based on the quality and texture_key."""
        for folder in os.listdir(TEXTURE_DIR):
            if folder == quality:
                for texture in os.listdir(os.path.join(TEXTURE_DIR, folder)):
                    if texture.startswith(texture_key):
                        print(f"Loading texture: {texture}, quality: {quality}")
                        return os.path.join(TEXTURE_DIR, folder, texture)
                break
        return None