#
from typing import overload, Union
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QVector3D, QMatrix4x4, QVector4D, QMouseEvent
from OpenGL import GLU, GL
from PySide6.QtCore import Qt, Signal, QObject, QPoint
import random
import math
import numpy as np


class Object3D(QMatrix4x4, QObject):
    """An Object3D is a class meant to give basic functionality for positioning in the opengl scene. Internal state is the QMatrix4x4.
    Scale is relative to a unit sphere, so a scale of (1, 1, 1) is the default size."""

    attributeChanged: Signal = Signal()

    def __init__(self, name="", parent=None):
        self.name = name
        self.parent = parent
        QMatrix4x4.__init__(self)
        QObject.__init__(self)

        self.setToIdentity()
        self.visible = True
        self.lighting = True
        self.color = QVector4D(random.random(), random.random(), random.random(), 1.0)

        self.attributeChanged.connect(self.update)

    def update(self):  # only upon changes to self
        return None

    @property
    def position(self) -> QVector3D:
        return self.column(3).toVector3D()

    @position.setter
    def position(self, xyz: QVector3D) -> None:
        self.setColumn(3, xyz.toVector4D())
        self.attributeChanged.emit()
        return None

    @property
    def scale(self) -> QVector3D:
        x = self.column(0).toVector3D().length()
        y = self.column(1).toVector3D().length()
        z = self.column(2).toVector3D().length()
        return QVector3D(x, y, z)

    @scale.setter
    def scale(self, xyz: QVector3D) -> None:

        self.setColumn(
            0, QVector4D(self.column(0).toVector3D().normalized() * xyz.x(), 0)
        )
        self.setColumn(
            1, QVector4D(self.column(1).toVector3D().normalized() * xyz.y(), 0)
        )
        self.setColumn(
            2, QVector4D(self.column(2).toVector3D().normalized() * xyz.z(), 0)
        )

        self.attributeChanged.emit()
        return None

    def apply_matrix(self) -> None:
        GL.glMultMatrixf(np.array(self.data(), dtype=np.float32))
        return None


class SphereObject(Object3D):

    @Object3D.scale.setter
    def scale(self, xyz: QVector3D) -> None:
        if isinstance(xyz, (int, float)):
            xyz = QVector3D(xyz, xyz, xyz)
        Object3D.scale = xyz
        return None

    def draw(self):
        if self.visible:
            (
                GL.glEnable(GL.GL_LIGHTING)
                if self.lighting
                else GL.glDisable(GL.GL_LIGHTING)
            )
            GL.glPushMatrix()
            self.apply_matrix()
            # GL.glTranslatef(*self.position.toTuple())
            # GL.glRotatef(90, 1, 0, 0)
            GL.glColor4f(*self.color.toTuple())
            # GL.glScalef(*self.scale.toTuple())
            quadric = GLU.gluNewQuadric()
            GLU.gluSphere(quadric, 1, 32, 32)
            GL.glPopMatrix()


class CubeObject(Object3D):
    def __init__(self, name, parent=None):
        self.vertices = [
            QVector3D(-1.0, -1.0, 1.0),  # Front face
            QVector3D(1.0, -1.0, 1.0),
            QVector3D(1.0, 1.0, 1.0),
            QVector3D(-1.0, 1.0, 1.0),
            QVector3D(-1.0, -1.0, -1.0),  # Back face
            QVector3D(-1.0, 1.0, -1.0),
            QVector3D(1.0, 1.0, -1.0),
            QVector3D(1.0, -1.0, -1.0),
        ]

        self.indices = [
            0,
            1,
            2,
            2,
            3,
            0,  # Front face
            4,
            5,
            6,
            6,
            7,
            4,  # Back face
            4,
            0,
            3,
            3,
            5,
            4,  # Left face
            1,
            7,
            6,
            6,
            2,
            1,  # Right face
            3,
            2,
            6,
            6,
            5,
            3,  # Top face
            4,
            7,
            1,
            1,
            0,
            4,  # Bottom face
        ]

        self.normals = [
            QVector3D(0.0, 0.0, 1.0),  # Front face
            QVector3D(0.0, 0.0, -1.0),  # Back face
            QVector3D(-1.0, 0.0, 0.0),  # Left face
            QVector3D(1.0, 0.0, 0.0),  # Right face
            QVector3D(0.0, 1.0, 0.0),  # Top face
            QVector3D(0.0, -1.0, 0.0),  # Bottom face
        ]

        super().__init__(name, parent)

    def draw(self):
        if self.visible:
            (
                GL.glEnable(GL.GL_LIGHTING)
                if self.lighting
                else GL.glDisable(GL.GL_LIGHTING)
            )
            GL.glPushMatrix()

            self.apply_matrix()

            # GL.glTranslatef(*self.position.toTuple())
            GL.glColor4f(*self.color.toTuple())
            # GL.glScalef(*self.scale.toTuple())

            GL.glBegin(GL.GL_TRIANGLES)
            for i in range(0, len(self.indices), 3):
                for j in range(3):
                    index = self.indices[i + j]
                    normal = self.normals[index // 6]
                    vertex = self.vertices[index]
                    GL.glNormal3f(*normal.toTuple())
                    GL.glVertex3f(*vertex.toTuple())
            GL.glEnd()
            GL.glPopMatrix()


class PointerObject3D(CubeObject):
    """A PointObject3D is an Object3D that has a point in space to look at, and a point in space to look from, and an up vector. It is used for cameras AND ALSO lights."""

    def __init__(self, name, parent):
        super().__init__(name, parent)

    def look_data(self) -> tuple[QVector3D, QVector3D, QVector3D]:
        """Returns a tuple of the eye, center, and up vectors."""
        matrix = self.inverted()[0]
        eye = matrix.column(3).toVector3D()
        forward = -matrix.column(2).toVector3D()
        center = eye + forward
        up = matrix.column(1).toVector3D().normalized()
        return (
            eye.x(),
            eye.y(),
            eye.z(),
            center.x(),
            center.y(),
            center.z(),
            up.x(),
            up.y(),
            up.z(),
        )

    def look_at(self, eye: QVector3D, center: QVector3D, up: QVector3D) -> None:
        self.setToIdentity()
        self.lookAt(eye, center, up)
        return None

    def draw(self):  # build every frame
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GLU.gluLookAt(*self.look_data())
        super().draw()
        return None

    def update(self):  # only upon changes to self
        super().update()
        return None


class Camera3D(PointerObject3D):
    """The Camera inherits from PointerObject3D and adds functionality for perspective projection. The perspective projection is stored as another QMatrix4x4 object."""

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.projection = QMatrix4x4()  # represents the camera lens
        self.active = False
        self.color = QVector4D(1, 0.5, 0, 1)  # orange
        self.fov = 45
        self.scale = QVector3D(0.1, 0.1, 0.1)
        self.aspect_ratio = 1
        self.near_plane = 0.1
        self.far_plane = 1000
        self.visible = False

    def set_perspective(self, **kwargs) -> None:

        self.fov = kwargs.get("fov", self.fov)
        self.aspect_ratio = kwargs.get("aspect_ratio", self.aspect_ratio)
        self.near_plane = kwargs.get("near_plane", self.near_plane)
        self.far_plane = kwargs.get("far_plane", self.far_plane)

        self.projection.setToIdentity()
        self.projection.perspective(
            self.fov, self.aspect_ratio, self.near_plane, self.far_plane
        )
        self.attributeChanged.emit()

    def draw(self):  # build every frame
        if self.active:
            # GL.glPushMatrix()
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GL.glMultMatrixf(self.projection.data())
            GL.glMatrixMode(GL.GL_MODELVIEW)
            super().draw()
        return None

    def update(self):  # only upon changes to self
        super().update()
        return None


class OrbitCamera3D(Camera3D):
    """The OrbitCamera3D is a camera that adds functionality for orbiting around a point in space, effectively keeping a radius from the center of length distance."""

    mouseMoveEvent: Signal = Signal(QMouseEvent)
    mousePressEvent: Signal = Signal(QMouseEvent)
    wheelEvent: Signal = Signal(QMouseEvent)

    def __init__(self, name, parent=None):
        self.mousePos = QPoint(0, 0)
        self.theta = 0.0
        self.phi = 0.0
        self.distance = 10.0
        super().__init__(name, parent)

        self.phi_clamp = (-89, 89)
        self.distance_clamp = (0.1, 100.0)

        self.mouseMoveEvent.connect(self.onMouseMove)
        self.mousePressEvent.connect(self.onMousePress)
        self.wheelEvent.connect(self.onMouseWheel)

    def onMouseMove(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            dx = event.x() - self.mousePos.x()
            dy = event.y() - self.mousePos.y()

            rot_y = QMatrix4x4()
            rot_y.rotate(dx / 2, 0, 1, 0)

            rot_x = QMatrix4x4()
            rot_x.rotate(dy / 2, 1, 0, 0)

            # self *= rot_y
            # self *= rot_x

            self.theta += dx / 2
            self.phi += dy / 2
            self.phi = max(min(self.phi, self.phi_clamp[1]), self.phi_clamp[0])

        self.mousePos = event.pos()
        self.update_matrix()
        return None

    def onMousePress(self, event: QMouseEvent) -> None:
        self.mousePos = event.pos()
        return None

    def onMouseWheel(self, event: QMouseEvent) -> None:
        delta = event.angleDelta().y() / 120
        self.distance *= 1 - delta / 10

        self.distance = max(
            min(self.distance, self.distance_clamp[1]), self.distance_clamp[0]
        )

        # forward = QVector3D(self.matrix(2, 0), self.matrix(2, 1), self.matrix(2, 2)).normalized()
        # eye = QVector3D(self.matrix(0, 3), self.matrix(1, 3), self.matrix(2, 3)) - forward * delta

        # forward = self.column(2).toVector3D().normalized()
        # eye = self.column(3).toVector3D() - forward * delta

        # self.look_at(eye, QVector3D(0, 0, 0), QVector3D(0, 0, 1))

        # translation = QMatrix4x4()
        # translation.translate(QVector3D(0, 0, self.distance))
        # self *= translation

        self.update_matrix()
        return None

    def update_matrix(self) -> QVector3D:

        self.setToIdentity()
        self.translate(0, 0, -self.distance)
        self.rotate(self.phi, 1, 0, 0)
        self.rotate(self.theta, 0, 1, 0)
        return None

    def draw(self):  # build every frame
        super().draw()
        return None

    def update(self):  # only upon changes to self
        self.update_matrix()
        super().update()
        return None


class Spotlight3D(PointerObject3D):
    def __init__(self, id=0, parent=None):
        self.id = getattr(GL, f"GL_LIGHT{id}")
        self.visible = False
        self.enabled = True
        self.color = QVector4D(1, 1, 0, 1)  # yellow
        self.ambient = QVector4D(0.2, 0.2, 0.2, 1)  # pale grey
        self.specular = QVector4D(1, 1, 1, 1)
        self.diffuse = QVector4D(1, 1, 1, 1)

        GL.glEnable(self.id)
        super().__init__(str(self.id), parent)

    def draw(self):  # build every frame
        if self.enabled:
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLightfv(self.id, GL.GL_POSITION, self.position.toTuple())
            GL.glLightfv(self.id, GL.GL_AMBIENT, self.ambient.toTuple())
            GL.glLightfv(self.id, GL.GL_DIFFUSE, self.diffuse.toTuple())
            GL.glLightfv(self.id, GL.GL_SPECULAR, self.specular.toTuple())
        super().draw()
        return None

    def update(self):  # only upon changes to self
        super().update()
        return None


class SceneModel(QObject):
    attributeChanged: Signal = Signal()

    root: Object3D = Object3D("root")
    lights: list[Spotlight3D] = []
    objects: list[Object3D] = []

    def __init__(self):
        super().__init__()
        self.camera = None
        self.loaded = False

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        self.attributeChanged.emit()
        return None

    def setCurrentCamera(self, camera: Camera3D) -> None:
        self.camera = camera
        return None

    def load(self):
        self.loaded = True
        return None

    def unload(self):
        self.loaded = False
        return None

    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        return None


class Scene1(SceneModel):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setCurrentCamera(OrbitCamera3D("camera"))

    def load(self):
        super().load()
        self.camera.active = True
        self.camera.look_at(QVector3D(0, 0, 20), QVector3D(0, 0, 0), QVector3D(0, 1, 0))

        self.lights.append(Spotlight3D(0))
        self.lights[0].position = QVector3D(0, 0, 20)
        self.lights[0].ambient = QVector4D(0.2, 0.2, 0.2, 1)  # ambient

        for i in range(20):
            obj = SphereObject(f"sphere_{i}")
            obj.translate(
                random.uniform(-10, 10),
                random.uniform(-10, 10),
                random.uniform(-10, 10),
            )
            self.objects.append(obj)

    def unload(self):
        super().unload()
        self.camera.active = False
        return None

    def draw(self):
        super().draw()
        self.camera.draw()  # capture every frame

        for light in self.lights:
            light.draw()

        for obj in self.objects:

            obj.translate(
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
            )

            obj.draw()  # build every frame
        return None


class Scene2(SceneModel):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.camera = OrbitCamera3D("camera")

    def load(self):
        super().load()
        self.camera.look_at(QVector3D(0, 0, 20), QVector3D(0, 0, 0), QVector3D(0, 1, 0))

        self.lights.append(Spotlight3D(0))
        self.lights[0].position = QVector3D(0, 0, 20)
        self.lights[0].ambient = QVector4D(0.2, 0.2, 0.2, 1)

        for i in range(20):
            obj = CubeObject(f"cube_{i}")
            obj.translate(
                random.uniform(-10, 10),
                random.uniform(-10, 10),
                random.uniform(-10, 10),
            )
            self.objects.append(obj)

    def drawScene(self):
        super().drawScene()
        self.camera.draw()

        for light in self.lights:
            light.draw()

        for obj in self.objects:
            obj.translate(
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
                random.uniform(-0.05, 0.05),
            )
            obj.draw()
        return None

    def endScene(self):
        # cleanup and delete all objects
        for obj in self.objects:
            del obj
        self.objects = []

        for light in self.lights:
            del light
        self.lights = []

        del self.camera
        self.camera = None

        self.deleteLater()

        return None
