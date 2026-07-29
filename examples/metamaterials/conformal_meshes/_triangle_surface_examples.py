"""Deterministic triangle-mesh patch helpers shared by the surface-mapping examples.

These build and filter triangle-mesh disk patches using only ``pyvcad``'s existing indexed
vertex/triangle arrays, so the examples stay reproducible without a separate core selection
subsystem. Every routine is pure and deterministic: identical inputs always produce identical
vertex ordering, which keeps the free-boundary conformal parameterization and its committed
renders stable.
"""

# STD
import math

# OpenVCAD
import pyvcad as pv


def indexed_grid(width, depth, columns, rows, height):
    """Build an indexed height-field patch centered on the origin.

    Arguments:
      width, depth (float): World extents along X and Y.
      columns, rows (int): Vertex counts per side.
      height (callable): ``height(x, y) -> z`` evaluated at each grid vertex.

    Returns:
      (vertices, triangles): ``vertices`` is a list of ``pv.Vec3``; ``triangles`` is a list of
      ``(i, j, k)`` index triples with consistent winding.
    """
    vertices = []
    for j in range(rows):
        for i in range(columns):
            x = width * (i / (columns - 1) - 0.5)
            y = depth * (j / (rows - 1) - 0.5)
            vertices.append(pv.Vec3(x, y, float(height(x, y))))
    triangles = []
    for j in range(rows - 1):
        for i in range(columns - 1):
            a = j * columns + i
            b = j * columns + i + 1
            c = (j + 1) * columns + i + 1
            d = (j + 1) * columns + i
            triangles.append((a, b, c))
            triangles.append((a, c, d))
    return vertices, triangles


def grid_surface(width, depth, columns, rows, height):
    """Build an ``indexed_grid`` and wrap it as a parameterized ``pv.TriangleMeshSurface``."""
    vertices, triangles = indexed_grid(width, depth, columns, rows, height)
    return pv.TriangleMeshSurface(vertices, triangles)


def indexed_disk(radius, rings, segments, height):
    """Build an indexed circular height-field patch centered on the origin.

    The disk is a center vertex fanned to ``rings`` concentric rings of ``segments`` vertices,
    so its boundary is round. The free-boundary parameterization keeps that round outline, and
    ``CellMap`` trimming terminates any mapped lattice at the true circular edge.

    Arguments:
      radius (float): World radius of the disk.
      rings, segments (int): Ring count and vertices per ring.
      height (callable): ``height(x, y) -> z`` evaluated at each vertex.

    Returns:
      (vertices, triangles): Indexed arrays with consistent upward-facing winding.
    """
    vertices = [pv.Vec3(0.0, 0.0, float(height(0.0, 0.0)))]
    for k in range(1, rings + 1):
        r = radius * k / rings
        for s in range(segments):
            theta = 2.0 * math.pi * s / segments
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            vertices.append(pv.Vec3(x, y, float(height(x, y))))
    triangles = []
    for s in range(segments):
        triangles.append((0, 1 + s, 1 + (s + 1) % segments))
    for k in range(1, rings):
        inner = 1 + (k - 1) * segments
        outer = 1 + k * segments
        for s in range(segments):
            a = inner + s
            b = inner + (s + 1) % segments
            c = outer + (s + 1) % segments
            d = outer + s
            triangles.append((a, d, c))
            triangles.append((a, c, b))
    return vertices, triangles


def disk_surface(radius, rings, segments, height):
    """Build an ``indexed_disk`` and wrap it as a parameterized ``pv.TriangleMeshSurface``."""
    vertices, triangles = indexed_disk(radius, rings, segments, height)
    return pv.TriangleMeshSurface(vertices, triangles)


def triangle_normal(vertices, triangle):
    """Return the unit face normal of one indexed triangle."""
    a = vertices[triangle[0]]
    b = vertices[triangle[1]]
    c = vertices[triangle[2]]
    ux, uy, uz = b.x - a.x, b.y - a.y, b.z - a.z
    vx, vy, vz = c.x - a.x, c.y - a.y, c.z - a.z
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length <= 0.0:
        return (0.0, 0.0, 0.0)
    return (nx / length, ny / length, nz / length)


def select_triangles(vertices, triangles, predicate):
    """Return the subset of triangles whose face normal satisfies ``predicate(nx, ny, nz)``."""
    return [t for t in triangles if predicate(*triangle_normal(vertices, t))]


def _edge_adjacency(triangles):
    """Map each undirected edge to the triangle indices that use it."""
    edges = {}
    for index, triangle in enumerate(triangles):
        for a, b in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
            key = (a, b) if a < b else (b, a)
            edges.setdefault(key, []).append(index)
    return edges


def largest_connected_component(triangles):
    """Return the triangles of the largest edge-connected component.

    Ties are broken deterministically toward the component containing the lowest triangle index.
    """
    edges = _edge_adjacency(triangles)
    neighbors = {index: set() for index in range(len(triangles))}
    for shared in edges.values():
        for first in shared:
            for second in shared:
                if first != second:
                    neighbors[first].add(second)

    visited = [False] * len(triangles)
    best = []
    for seed in range(len(triangles)):
        if visited[seed]:
            continue
        stack = [seed]
        visited[seed] = True
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in neighbors[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
        component.sort()
        if len(component) > len(best):
            best = component
    return [triangles[index] for index in best]


def reindex(vertices, triangles):
    """Compact a triangle subset to only the vertices it uses, preserving vertex order.

    Returns ``(new_vertices, new_triangles)`` with contiguous zero-based indices.
    """
    used = sorted({index for triangle in triangles for index in triangle})
    remap = {old: new for new, old in enumerate(used)}
    new_vertices = [vertices[old] for old in used]
    new_triangles = [(remap[a], remap[b], remap[c]) for (a, b, c) in triangles]
    return new_vertices, new_triangles
