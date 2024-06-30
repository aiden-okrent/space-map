#
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QVector3D, QMatrix4x4, QVector4D
from OpenGL import GLU, GL
from PySide6.QtCore import Signal, QObject, QTimer
from src.scene_modelGL import (
    Object3D,
    Spotlight3D,
    OrbitCamera3D,
    SceneModel,
    Scene1,
    Scene2,
)
import random


class ViewGL(QOpenGLWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.scene1 = Scene1()
        self.scene2 = Scene2()
        self.current_scene = self.scene1

        self.runtime = QTimer()
        self.runtime.timeout.connect(self.update)
        self.runtime.start(1000 / 60)  # 60fps

    def initializeGL(self):
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        self.current_scene.load()

    def swapSceneGL(self):
        self.current_scene.unload()
        self.current_scene = (
            self.scene2 if self.current_scene == self.scene1 else self.scene1
        )
        self.current_scene.load()

    def paintGL(self):
        self.current_scene.draw()

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        self.current_scene.camera.set_perspective(aspect_ratio=width / height)

    def mouseMoveEvent(self, event):
        self.current_scene.camera.mouseMoveEvent.emit(event)
        return super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        self.current_scene.camera.mousePressEvent.emit(event)
        return super().mousePressEvent(event)

    def wheelEvent(self, event):
        self.current_scene.camera.wheelEvent.emit(event)
        return super().wheelEvent(event)

    def keyPressEvent(self, event):
        # swap scene
        if event.key() == 83:
            self.swapSceneGL()  # S key
        return super().keyPressEvent(event)


def main():
    # debug just open a pyside6 window and show the scene
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    view = ViewGL(None)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
