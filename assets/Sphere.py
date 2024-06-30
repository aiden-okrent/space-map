import math
from OpenGL import GL


class Sphere:
    MIN_SECTOR_COUNT = 3
    MIN_STACK_COUNT = 2

    def __init__(self, radius, sectors, stacks, smooth):
        self.radius = radius
        self.sector_count = max(sectors, self.MIN_SECTOR_COUNT)
        self.stack_count = max(stacks, self.MIN_STACK_COUNT)
        self.smooth = smooth
        self.interleaved_stride = 32
        self.vertices = []
        self.normals = []
        self.tex_coords = []
        self.indices = []
        self.line_indices = []
        self.interleaved_vertices = []

        self.set(radius, sectors, stacks, smooth)

    def set(self, radius, sectors, stacks, smooth):
        self.radius = radius
        self.sector_count = max(sectors, self.MIN_SECTOR_COUNT)
        self.stack_count = max(stacks, self.MIN_STACK_COUNT)
        self.smooth = smooth

        if smooth:
            self.build_vertices_smooth()
        else:
            self.build_vertices_flat()

    def set_radius(self, radius):
        if radius != self.radius:
            self.set(radius, self.sector_count, self.stack_count, self.smooth)

    def set_sector_count(self, sectors):
        if sectors != self.sector_count:
            self.set(self.radius, sectors, self.stack_count, self.smooth)

    def set_stack_count(self, stacks):
        if stacks != self.stack_count:
            self.set(self.radius, self.sector_count, stacks, self.smooth)

    def set_smooth(self, smooth):
        if self.smooth == smooth:
            return

        self.smooth = smooth
        if smooth:
            self.build_vertices_smooth()
        else:
            self.build_vertices_flat()

    def reverse_normals(self):
        for i in range(0, len(self.normals), 3):
            self.normals[i] *= -1
            self.normals[i + 1] *= -1
            self.normals[i + 2] *= -1

            # Update interleaved array
            j = (i // 3) * 8 + 3
            self.interleaved_vertices[j] = self.normals[i]
            self.interleaved_vertices[j + 1] = self.normals[i + 1]
            self.interleaved_vertices[j + 2] = self.normals[i + 2]

        # Also reverse triangle windings
        for i in range(0, len(self.indices), 3):
            self.indices[i], self.indices[i + 2] = self.indices[i + 2], self.indices[i]

    def print_self(self):
        print("===== Sphere =====")
        print(f"        Radius: {self.radius}")
        print(f"  Sector Count: {self.sector_count}")
        print(f"   Stack Count: {self.stack_count}")
        print(f"Smooth Shading: {'true' if self.smooth else 'false'}")
        print(f"Triangle Count: {self.get_triangle_count()}")
        print(f"   Index Count: {self.get_index_count()}")
        print(f"  Vertex Count: {self.get_vertex_count()}")
        print(f"  Normal Count: {self.get_normal_count()}")
        print(f"TexCoord Count: {self.get_tex_coord_count()}")

    def draw(self):
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
        GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        GL.glVertexPointer(
            3, GL.GL_FLOAT, self.interleaved_stride, self.interleaved_vertices
        )
        GL.glNormalPointer(
            GL.GL_FLOAT, self.interleaved_stride, self.interleaved_vertices[3:]
        )
        GL.glTexCoordPointer(
            2, GL.GL_FLOAT, self.interleaved_stride, self.interleaved_vertices[6:]
        )

        GL.glDrawElements(
            GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, self.indices
        )

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
        GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)

    def draw_lines(self, line_color):
        GL.glColor4fv(line_color)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_DIFFUSE, line_color)

        GL.glDisable(GL.GL_LIGHTING)
        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, self.vertices)

        GL.glDrawElements(
            GL.GL_LINES, len(self.line_indices), GL.GL_UNSIGNED_INT, self.line_indices
        )

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_TEXTURE_2D)

    def draw_with_lines(self, line_color):
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glPolygonOffset(1.0, 1.0)
        self.draw()
        GL.glDisable(GL.GL_POLYGON_OFFSET_FILL)

        self.draw_lines(line_color)

    def clear_arrays(self):
        self.vertices.clear()
        self.normals.clear()
        self.tex_coords.clear()
        self.indices.clear()
        self.line_indices.clear()
        self.interleaved_vertices.clear()

    def build_vertices_smooth(self):
        self.clear_arrays()
        pi = math.pi

        for i in range(self.stack_count + 1):
            stack_angle = pi / 2 - i * pi / self.stack_count
            xy = self.radius * math.cos(stack_angle)
            z = self.radius * math.sin(stack_angle)

            for j in range(self.sector_count + 1):
                sector_angle = j * 2 * pi / self.sector_count
                x = xy * math.cos(sector_angle)
                y = xy * math.sin(sector_angle)
                self.add_vertex(x, y, z)
                nx, ny, nz = x / self.radius, y / self.radius, z / self.radius
                self.add_normal(nx, ny, nz)
                s, t = j / self.sector_count, i / self.stack_count
                self.add_tex_coord(s, t)

        for i in range(self.stack_count):
            k1 = i * (self.sector_count + 1)
            k2 = k1 + self.sector_count + 1
            for j in range(self.sector_count):
                if i != 0:
                    self.add_indices(k1, k2, k1 + 1)
                if i != self.stack_count - 1:
                    self.add_indices(k1 + 1, k2, k2 + 1)
                self.line_indices.append(k1)
                self.line_indices.append(k2)
                if i != 0:
                    self.line_indices.append(k1)
                    self.line_indices.append(k1 + 1)
                k1 += 1
                k2 += 1

        self.build_interleaved_vertices()

    def build_vertices_flat(self):
        self.clear_arrays()
        pi = math.pi
        tmp_vertices = []

        for i in range(self.stack_count + 1):
            stack_angle = pi / 2 - i * pi / self.stack_count
            xy = self.radius * math.cos(stack_angle)
            z = self.radius * math.sin(stack_angle)

            for j in range(self.sector_count + 1):
                sector_angle = j * 2 * pi / self.sector_count
                x = xy * math.cos(sector_angle)
                y = xy * math.sin(sector_angle)
                s, t = j / self.sector_count, i / self.stack_count
                tmp_vertices.append((x, y, z, s, t))

        for i in range(self.stack_count):
            vi1 = i * (self.sector_count + 1)
            vi2 = (i + 1) * (self.sector_count + 1)

            for j in range(self.sector_count):
                v1 = tmp_vertices[vi1]
                v2 = tmp_vertices[vi2]
                v3 = tmp_vertices[vi1 + 1]
                v4 = tmp_vertices[vi2 + 1]

                if i == 0:
                    self.add_vertex(v1[0], v1[1], v1[2])
                    self.add_vertex(v2[0], v2[1], v2[2])
                    self.add_vertex(v4[0], v4[1], v4[2])
                    self.add_tex_coord(v1[3], v1[4])
                    self.add_tex_coord(v2[3], v2[4])
                    self.add_tex_coord(v4[3], v4[4])
                    n = self.compute_face_normal(
                        v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v4[0], v4[1], v4[2]
                    )
                    for _ in range(3):
                        self.add_normal(n[0], n[1], n[2])
                    self.add_indices(
                        len(self.vertices) // 3 - 3,
                        len(self.vertices) // 3 - 2,
                        len(self.vertices) // 3 - 1,
                    )
                    self.line_indices.append(len(self.vertices) // 3 - 3)
                    self.line_indices.append(len(self.vertices) // 3 - 2)

                elif i == self.stack_count - 1:
                    self.add_vertex(v1[0], v1[1], v1[2])
                    self.add_vertex(v2[0], v2[1], v2[2])
                    self.add_vertex(v3[0], v3[1], v3[2])
                    self.add_tex_coord(v1[3], v1[4])
                    self.add_tex_coord(v2[3], v2[4])
                    self.add_tex_coord(v3[3], v3[4])
                    n = self.compute_face_normal(
                        v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2]
                    )
                    for _ in range(3):
                        self.add_normal(n[0], n[1], n[2])
                    self.add_indices(
                        len(self.vertices) // 3 - 3,
                        len(self.vertices) // 3 - 2,
                        len(self.vertices) // 3 - 1,
                    )
                    self.line_indices.append(len(self.vertices) // 3 - 3)
                    self.line_indices.append(len(self.vertices) // 3 - 2)
                    self.line_indices.append(len(self.vertices) // 3 - 3)
                    self.line_indices.append(len(self.vertices) // 3 - 1)

                else:
                    self.add_vertex(v1[0], v1[1], v1[2])
                    self.add_vertex(v2[0], v2[1], v2[2])
                    self.add_vertex(v3[0], v3[1], v3[2])
                    self.add_vertex(v4[0], v4[1], v4[2])
                    self.add_tex_coord(v1[3], v1[4])
                    self.add_tex_coord(v2[3], v2[4])
                    self.add_tex_coord(v3[3], v3[4])
                    self.add_tex_coord(v4[3], v4[4])
                    n = self.compute_face_normal(
                        v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2]
                    )
                    for _ in range(4):
                        self.add_normal(n[0], n[1], n[2])
                    self.add_indices(
                        len(self.vertices) // 3 - 4,
                        len(self.vertices) // 3 - 3,
                        len(self.vertices) // 3 - 2,
                    )
                    self.add_indices(
                        len(self.vertices) // 3 - 2,
                        len(self.vertices) // 3 - 3,
                        len(self.vertices) // 3 - 1,
                    )
                    self.line_indices.append(len(self.vertices) // 3 - 4)
                    self.line_indices.append(len(self.vertices) // 3 - 3)
                    self.line_indices.append(len(self.vertices) // 3 - 4)
                    self.line_indices.append(len(self.vertices) // 3 - 2)

        self.build_interleaved_vertices()

    def build_interleaved_vertices(self):
        self.interleaved_vertices = []
        for i in range(len(self.vertices) // 3):
            self.interleaved_vertices.extend(self.vertices[i * 3 : i * 3 + 3])
            self.interleaved_vertices.extend(self.normals[i * 3 : i * 3 + 3])
            self.interleaved_vertices.extend(self.tex_coords[i * 2 : i * 2 + 2])

    def add_vertex(self, x, y, z):
        self.vertices.extend([x, y, z])

    def add_normal(self, nx, ny, nz):
        self.normals.extend([nx, ny, nz])

    def add_tex_coord(self, s, t):
        self.tex_coords.extend([s, t])

    def add_indices(self, i1, i2, i3):
        self.indices.extend([i1, i2, i3])

    def compute_face_normal(self, x1, y1, z1, x2, y2, z2, x3, y3, z3):
        epsilon = 1e-6
        normal = [0.0, 0.0, 0.0]
        ex1, ey1, ez1 = x2 - x1, y2 - y1, z2 - z1
        ex2, ey2, ez2 = x3 - x1, y3 - y1, z3 - z1
        nx, ny, nz = ey1 * ez2 - ez1 * ey2, ez1 * ex2 - ex1 * ez2, ex1 * ey2 - ey1 * ex2
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length > epsilon:
            length_inv = 1.0 / length
            normal = [nx * length_inv, ny * length_inv, nz * length_inv]
        return normal
