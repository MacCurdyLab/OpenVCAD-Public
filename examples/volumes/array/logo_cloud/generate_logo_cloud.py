"""
Generate the logo cloud volumes for logo_cloud.py: the OpenVCAD logo V grown into a cumulus cloud.

The cloud is built on a regular grid with numpy + scipy only, following the usual recipe for
procedural clouds (sculpted sphere "puffs" plus noise erosion, as in Houdini cloud tools and
Guerrilla's Nubis):

1. Core. The logo's front V ribbon (examples/logo/openvcad_logo.py) is sampled with
   pv.TreeSampler. Its front silhouette is eroded to a centreline sheet and inflated into a round
   tube, so the V has a puffy cross-section instead of the flat ribbon's.
2. Puffs. Generations of spheres are scattered over the surface, each generation smaller and
   sitting on the one before, and smooth-unioned in. This gives cumulus "cauliflower" lobes with
   deep creases between them. Upward-facing puffs grow bigger and downward-facing ones smaller,
   so the top billows and the base stays flatter.
3. Detail. Inverted Worley bumps roughen the lobes, Perlin-Worley noise erodes the rim, a domain
   warp curls everything, and a faint, warped noise halo adds feathered wisps around the edges.
4. Lighting bake. Printed resin doesn't scatter light like water droplets, so the light is baked
   into a 0..1 ``light`` field: Beer-Lambert transmittance toward the sun with a "powder" term,
   sky light from above, and a blurred-density ambient occlusion. logo_cloud.py maps light to
   colour (warm white to cool blue-grey) and density to alpha.

Both fields are written as single-grid VDB files next to this script (logo_cloud_density.vdb and
logo_cloud_light.vdb) with matching transforms, centred on the origin, Y up and the logo facing
+Z, in millimetres. Density fades to zero at least ``edge_clearance`` mm inside the grid on every
side, so the cloud never touches the walls of its own data.

Run it once with the repo .venv (a minute or two at the default voxel size):

    python generate_logo_cloud.py

Set ``text = "OpenVCAD"`` below to write the lettered variant (logo_cloud_text_*.vdb). Besides
pyvcad it needs numpy and scipy (``pip install scipy`` if missing); the text variant uses the
system font named by ``text_font``.
"""
import os
import time

import numpy as np
from scipy import ndimage

import pyvcad as pv

# --- Grid ---------------------------------------------------------------------------------------
voxel = 0.3                 # mm per voxel (~330 voxels across the cloud's long axis)
edge_clearance = 3.0        # density is forced to zero this close to the grid walls (mm)
seed = 7                    # changes every random choice and noise field

# --- Core ---------------------------------------------------------------------------------------
logo_layers = 1             # how many of the logo's ribbons (front first) form the silhouette
core_radius = 5.5           # mm, radius the V's centreline is inflated to (the ribbon is 10 mm wide)
depth_scale = 1.0           # front-to-back size of the core relative to its width

# --- Text (optional) ----------------------------------------------------------------------------
text = ""                   # e.g. "OpenVCAD" adds a cloud of lettering under the V (separate VDBs)
text_height = 20.0          # mm
text_font = "Arial"
text_gap = 12.0             # mm between the bottom of the V and the top of the text
text_core_radius = 2.1      # mm, radius each letter stroke is inflated to (strokes are ~4.5 mm)
text_puff_scale = 0.26      # puffs, warp and wisps on the letters relative to the V's

# --- Puffs --------------------------------------------------------------------------------------
# One row per generation: (smallest radius mm, largest radius mm, spacing as a multiple of radius)
puff_generations = [(6.5, 10.0, 1.15), (3.0, 4.8, 2.0)]
puff_inset = 0.45           # fraction of its radius each puff is sunk below the surface it sits on
puff_blend = 1.0            # mm, smooth-union radius; larger fills the creases between puffs
up_bias = 0.35              # puffs grow by this fraction facing up and shrink facing down

# --- Detail -------------------------------------------------------------------------------------
bump_cell = 2.2             # mm, inverted Worley bumps on every lobe
bump_amplitude = 0.25       # mm
edge_softness = 0.45        # mm, how fuzzy the cloud's rim is (crisp lobes ~0.5, fog ~3)
core_ramp = 3.0             # mm inside the rim at which density reaches 1
detail_cell = 2.2           # mm, Perlin-Worley noise that erodes the rim
erosion = 0.45              # how much detail eats from the rim (0 = none, ~0.7 = very ragged)
wisp_reach = 3.5            # mm the feathered halo extends past the rim
wisp_cell = 3.0             # mm, size of the wisp streaks
wisp_strength = 0.3         # peak density of the wisps

# --- Domain warp --------------------------------------------------------------------------------
warp_scale = 14.0           # mm wavelength of the large curl
warp_amplitude = 1.2        # mm
curl_scale = 3.5            # mm wavelength of the small curl that twists the wisps
curl_amplitude = 0.8        # mm

# --- Lighting bake ------------------------------------------------------------------------------
sun_direction = (-0.85, 0.5, 0.15)  # toward the sun: upper (+Y), front (+Z), left (-X)
extinction = 0.3            # optical depth per mm at density 1
powder = 0.15               # 0 = off, 1 = strong dark sunward rims
sky_extinction = 0.1        # optical depth per mm used for the straight-down sky light
occlusion_radius = 2.0      # mm, blur radius for the ambient-occlusion term
occlusion_strength = 1.8
sun_weight = 0.9            # light = sun_weight * sun + sky_weight * sky * occlusion
sky_weight = 0.3

out_dir = os.path.dirname(os.path.abspath(__file__))
name = "logo_cloud_text" if text else "logo_cloud"
density_path = os.path.join(out_dir, f"{name}_density.vdb")
light_path = os.path.join(out_dir, f"{name}_light.vdb")

rng = np.random.default_rng(seed)
t_start = time.time()


def log(message):
    print(f"[{time.time() - t_start:6.1f}s] {message}", flush=True)


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def remap(x, lo, hi):
    """Linearly map lo..hi to 0..1 and clamp (the Nubis ``remap`` with a 0..1 target)."""
    return np.clip((x - lo) / np.maximum(hi - lo, 1e-6), 0.0, 1.0)


# --- Silhouettes --------------------------------------------------------------------------------
h = voxel


def front_silhouette(node):
    """Sample a node and return its front silhouette as (mask[x, y], xy of mask[0, 0], z centre)."""
    node.prepare(pv.Vec3(h, h, h), 4.0 * h)
    sampler = pv.TreeSampler(node, pv.Vec3(h, h, h), None)
    sx, sy, sz = sampler.sample_dimensions()
    inside = np.asarray(sampler.as_signed_distance_array(None)).reshape(sz, sy, sx).transpose(2, 1, 0) < 0.0
    node_min, _ = node.bounding_box()
    origin = np.array([node_min.x, node_min.y, node_min.z]) - 2.0 * h   # TreeSampler pads two voxels
    mask = inside.any(axis=2)
    solid = np.argwhere(mask)
    lo, hi = solid.min(axis=0), solid.max(axis=0) + 1
    z_cells = np.argwhere(inside.any(axis=(0, 1)))[:, 0]
    return mask[lo[0]:hi[0], lo[1]:hi[1]], origin[:2] + lo * h, origin[2] + 0.5 * (z_cells[0] + z_cells[-1]) * h


# Keep only the front `logo_layers` ribbons; the full stack's silhouette fills in the V's notch
logo_script = os.path.join(out_dir, "..", "..", "..", "logo", "openvcad_logo.py")
source = open(logo_script).read().replace("import pyvcad_rendering as viz", "").replace("viz.Render(root)", "")
source = source.replace("for i in range(layers):", f"for i in range({logo_layers}):")
namespace = {}
exec(compile(source, logo_script, "exec"), namespace)
logo_mask, logo_xy, z_mid = front_silhouette(namespace["root"])

# Each part: (silhouette, xy of its corner, core radius, puff scale)
parts = [(logo_mask, logo_xy, core_radius, 1.0)]
if text:
    # Text glyphs come out rotated 180 degrees in their plane, so turn them upright
    text_node = pv.Rotate(0, 0, 180, pv.Text(text, text_height, 4.0, pv.FontAspect.Bold, text_font))
    text_mask, _, _ = front_silhouette(text_node)
    # Centre the text under the V, text_gap below it, on the same voxel lattice
    offset = np.array([0.5 * (logo_mask.shape[0] - text_mask.shape[0]), -text_gap / h - text_mask.shape[1]])
    parts.append((text_mask, logo_xy + np.round(offset) * h, text_core_radius, text_puff_scale))

# Grid: every part, padded by everything the cloud can grow by
puff_reach = sum(r_max * (1.0 - puff_inset) * (1.0 + up_bias) for _, r_max, _ in puff_generations)
grow = puff_reach + bump_amplitude + wisp_reach + warp_amplitude + curl_amplitude + edge_clearance
pad = int(np.ceil(grow / h))
pad_z = int(np.ceil((core_radius * depth_scale + grow) / h))
xy_min = np.min([xy for _, xy, _, _ in parts], axis=0) - pad * h
xy_max = np.max([xy + np.array(mask.shape) * h for mask, xy, _, _ in parts], axis=0) + pad * h
nx, ny = np.round((xy_max - xy_min) / h).astype(int)
nz = 2 * pad_z + 1
grid_origin = np.array([xy_min[0], xy_min[1], z_mid - pad_z * h])
axes = [(grid_origin[a] + np.arange(n) * h).astype(np.float32) for a, n in enumerate((nx, ny, nz))]
log(f"grid {nx} x {ny} x {nz} = {nx * ny * nz / 1e6:.1f} M voxels at {h} mm")

# --- Core tubes ---------------------------------------------------------------------------------
# Erode each silhouette to (nearly) its centreline and take the 3D distance to that flat sheet:
# strokes become round tubes of the part's core radius and wide areas stay pillow-shaped.
sdf = np.full((nx, ny, nz), np.inf, dtype=np.float32)
puff_scale = np.ones((nx, ny), dtype=np.float32)          # puff size multiplier of the nearest part
nearest = np.full((nx, ny), np.inf, dtype=np.float32)
depth = (axes[2] - z_mid)[None, None, :] / depth_scale
for mask, xy, radius, scale in parts:
    i, j = np.round((xy - xy_min) / h).astype(int)
    silhouette = np.zeros((nx, ny), dtype=bool)
    silhouette[i:i + mask.shape[0], j:j + mask.shape[1]] = mask
    half_width = ndimage.distance_transform_edt(silhouette).max() * h
    sheet = ((ndimage.distance_transform_edt(~silhouette) - ndimage.distance_transform_edt(silhouette)) * h
             + half_width).astype(np.float32)
    puff_scale[sheet < nearest] = scale
    nearest = np.minimum(nearest, sheet)
    sheet = sheet[:, :, None]
    np.minimum(sdf, np.sqrt(np.maximum(sheet, 0.0) ** 2 + depth ** 2) + np.minimum(sheet, 0.0) - radius, out=sdf)
del sheet, silhouette, nearest
log("core done")


# --- Puffs --------------------------------------------------------------------------------------
def smooth_union(a, b, k):
    """Polynomial smooth minimum of two distance fields with blend radius k."""
    t = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b + (a - b) * t - k * t * (1.0 - t)


def scatter_puffs(field, r_min, r_max, spacing):
    """Pick sphere centres on the zero surface of `field`, spaced by about spacing * radius.
    Returns (centre mm, radius mm, blend mm) for each puff, its centre sunk puff_inset * radius below
    the surface. Radii and blends are scaled by the puff scale of the part the puff sits on."""
    near = np.argwhere(np.abs(field) < 0.5 * h)
    near = near[rng.permutation(len(near))[:30000]]
    normals = np.stack([np.gradient(field, axis=a)[tuple(near.T)] for a in range(3)], axis=1)
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-6)
    scale = puff_scale[near[:, 0], near[:, 1]]
    radii = rng.uniform(r_min, r_max, len(near)) * scale * (1.0 + up_bias * normals[:, 1])
    surface = np.stack([axes[a][near[:, a]] for a in range(3)], axis=1)
    keep = []
    keep_s, keep_r = np.empty((0, 3)), np.empty(0)
    for i, (point, radius) in enumerate(zip(surface, radii)):
        # Space the puffs by where they touch the surface; their sunk centres crowd together
        if np.all(np.linalg.norm(keep_s - point, axis=1) > spacing * 0.5 * (keep_r + radius)):
            keep.append(i)
            keep_s, keep_r = np.vstack([keep_s, point]), np.append(keep_r, radius)
    centres = surface[keep] - puff_inset * radii[keep, None] * normals[keep]
    return list(zip(centres, radii[keep], puff_blend * scale[keep]))


for r_min, r_max, spacing in puff_generations:
    puffs = scatter_puffs(sdf, r_min, r_max, spacing)
    for centre, radius, blend in puffs:
        reach = radius + blend + h
        lo = [max(int((centre[a] - reach - grid_origin[a]) / h), 0) for a in range(3)]
        hi = [min(int((centre[a] + reach - grid_origin[a]) / h) + 2, n) for a, n in enumerate((nx, ny, nz))]
        box = tuple(slice(l, u) for l, u in zip(lo, hi))
        dx = axes[0][box[0]] - centre[0]
        dy = axes[1][box[1]] - centre[1]
        dz = axes[2][box[2]] - centre[2]
        sphere = np.sqrt(dx[:, None, None] ** 2 + dy[None, :, None] ** 2 + dz[None, None, :] ** 2) - radius
        sdf[box] = smooth_union(sdf[box], sphere, blend)
    log(f"{len(puffs)} puffs of {r_min}-{r_max} mm")


# --- Noise --------------------------------------------------------------------------------------
# Both noises evaluate on the regular grid: per-cell data is computed once and gathered back to
# the voxels with open-mesh indexing, which keeps everything vectorised and memory-light.
def worley(cell, period=16):
    """F1 Worley distance on the grid, normalised so 1 is a cell width. Feature points come from a
    periodic table (period cells per axis), so the pattern tiles."""
    features = rng.random((period, period, period, 3), dtype=np.float32)
    cell_idx = [np.floor(a / cell).astype(np.int64) for a in axes]
    local = [a / cell - c for a, c in zip(axes, cell_idx)]
    best = np.full((nx, ny, nz), np.inf, dtype=np.float32)
    for ox in (-1, 0, 1):
        ix = (cell_idx[0] + ox) % period
        dx = local[0] - ox
        for oy in (-1, 0, 1):
            iy = (cell_idx[1] + oy) % period
            dy = local[1] - oy
            for oz in (-1, 0, 1):
                iz = (cell_idx[2] + oz) % period
                dz = local[2] - oz
                f = features[np.ix_(ix, iy, iz)]
                d2 = (dx[:, None, None] - f[..., 0]) ** 2
                d2 += (dy[None, :, None] - f[..., 1]) ** 2
                d2 += (dz[None, None, :] - f[..., 2]) ** 2
                np.minimum(best, d2, out=best)
    return np.sqrt(best)


def perlin(cell, period=32):
    """Classic gradient noise on the grid, roughly in -1..1."""
    g = rng.normal(size=(period, period, period, 3)).astype(np.float32)
    g /= np.linalg.norm(g, axis=-1, keepdims=True)
    cell_idx = [np.floor(a / cell).astype(np.int64) for a in axes]
    local = [a / cell - c for a, c in zip(axes, cell_idx)]
    fade = [t * t * t * (t * (t * 6 - 15) + 10) for t in local]
    out = np.zeros((nx, ny, nz), dtype=np.float32)
    for ox in (0, 1):
        ix = (cell_idx[0] + ox) % period
        wx = fade[0] if ox else 1 - fade[0]
        for oy in (0, 1):
            iy = (cell_idx[1] + oy) % period
            wy = fade[1] if oy else 1 - fade[1]
            for oz in (0, 1):
                iz = (cell_idx[2] + oz) % period
                wz = fade[2] if oz else 1 - fade[2]
                grad = g[np.ix_(ix, iy, iz)]
                dot = grad[..., 0] * (local[0] - ox)[:, None, None]
                dot += grad[..., 1] * (local[1] - oy)[None, :, None]
                dot += grad[..., 2] * (local[2] - oz)[None, None, :]
                out += dot * (wx[:, None, None] * wy[None, :, None] * wz[None, None, :])
    return out * 1.6


def fbm(noise, cell, octaves, gain):
    total, weight, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        total = total + weight * noise(cell / 2 ** o)
        norm += weight
        weight *= gain
    return total / norm


def warp(field, offsets):
    """Resample a grid field at voxel positions displaced by offsets (3, nx, ny, nz) in mm."""
    out = np.empty_like(field)
    for x0 in range(0, nx, 64):           # chunked to keep the coordinate arrays small
        x1 = min(x0 + 64, nx)
        coords = np.indices((x1 - x0, ny, nz), dtype=np.float32)
        coords[0] += x0
        coords += offsets[:, x0:x1] / h
        out[x0:x1] = ndimage.map_coordinates(field, coords, order=1, mode="nearest")
    return out


# --- Cloud density ------------------------------------------------------------------------------
# Warps, bumps and wisps shrink with the puffs, so small lettering keeps its shape
part_scale = puff_scale[:, :, None]
large_warp = np.stack([perlin(warp_scale) for _ in range(3)]) * (warp_amplitude * part_scale)
small_warp = np.stack([perlin(curl_scale) for _ in range(3)]) * (curl_amplitude * part_scale)
sdf = warp(sdf, large_warp + small_warp)
del large_warp
log("warp done")

# Inverted Worley bumps push every lobe out into smaller cauliflower knobs
bumps = fbm(lambda c: 1.0 - worley(c), bump_cell, 2, 0.5)
sdf -= bump_amplitude * part_scale * (bumps - bumps.mean()) / bumps.std()
del bumps

# Crisp rim, full density core_ramp mm inside it
density = smoothstep(edge_softness * part_scale, -core_ramp * part_scale, sdf)

# Perlin-Worley detail erodes mostly where the cloud is thin, leaving a ragged rim
detail_worley = fbm(lambda c: 1.0 - worley(c), detail_cell, 2, 0.5)
detail_perlin = fbm(perlin, detail_cell * 1.5, 2, 0.5) * 0.5 + 0.5
detail = remap(detail_worley * 0.7 + detail_perlin * 0.3, 0.15, 0.95)
del detail_worley, detail_perlin
density = remap(density, erosion * (1.0 - detail) * (1.0 - density) ** 0.5, 1.0)
del detail
log("erosion done")

# Feathered wisps: stretched, curl-warped noise streaks in a thin halo outside the rim
streaks = warp(fbm(perlin, wisp_cell, 3, 0.55), small_warp * 3.0)
streaks = remap(streaks, 0.3, 0.8) ** 1.5
halo = smoothstep(wisp_reach * part_scale, 0.0, sdf) * (sdf > 0.0)
density = np.maximum(density, (wisp_strength * halo * streaks).astype(np.float32))
del streaks, halo, small_warp, sdf, part_scale

# Clear buffer: nothing within edge_clearance of the grid walls
ramp = [smoothstep(0.0, edge_clearance, np.minimum(np.arange(n), np.arange(n)[::-1]) * h - 0.5 * edge_clearance)
        for n in (nx, ny, nz)]
density *= (ramp[0][:, None, None] * ramp[1][None, :, None] * ramp[2][None, None, :]).astype(np.float32)
density = density.astype(np.float32)
density[density < 1e-3] = 0.0
log(f"density: {np.count_nonzero(density) / density.size * 100:.1f}% of voxels occupied")


# --- Lighting bake ------------------------------------------------------------------------------
def optical_depth_toward(direction, sigma):
    """Optical depth from every voxel to the outside, marching toward `direction`.

    Sweeps slice by slice along the dominant axis of the direction; each slice inherits the
    previous slice's optical depth, shifted sideways by the lateral component (bilinear)."""
    direction = np.asarray(direction, dtype=np.float64)
    direction /= np.linalg.norm(direction)
    axis = int(np.argmax(np.abs(direction)))
    step = 1 if direction[axis] > 0 else -1
    lateral = [a for a in range(3) if a != axis]
    shift = [direction[a] / abs(direction[axis]) for a in lateral]    # voxels per slice
    ds = h / abs(direction[axis])                                     # path length per slice (mm)

    rho = np.moveaxis(density, axis, 0)
    tau = np.zeros_like(rho)
    order = range(rho.shape[0] - 1, -1, -1) if step > 0 else range(rho.shape[0])
    previous = np.zeros(rho.shape[1:], dtype=np.float32)
    for i in order:
        # The slice one step toward the light sits `shift` voxels over, so look up previous at +shift
        upstream = ndimage.shift(previous, (-shift[0], -shift[1]), order=1, mode="constant", cval=0.0)
        toward = rho[i + step] if 0 <= i + step < rho.shape[0] else 0.0
        previous = upstream + sigma * ds * 0.5 * (rho[i] + toward)
        tau[i] = previous
    return np.moveaxis(tau, 0, axis)


tau_sun = optical_depth_toward(sun_direction, extinction)
sun = np.exp(-tau_sun) * (1.0 - powder * np.exp(-2.0 * tau_sun))   # "powder": thin sunward rims scatter less
del tau_sun
sky = np.exp(-optical_depth_toward((0.0, 1.0, 0.0), sky_extinction))
occlusion = np.exp(-occlusion_strength * ndimage.gaussian_filter(density, occlusion_radius / h))
light = np.clip(sun_weight * sun + sky_weight * sky * occlusion, 0.0, 1.0)
light = ndimage.gaussian_filter(light, 0.6).astype(np.float32)   # soften slice-march aliasing
del sun, sky, occlusion
light[density <= 0.0] = 0.0                          # keep the light grid as sparse as the density
log("lighting done")

# --- Save ---------------------------------------------------------------------------------------
# Both grids get the same origin, centred on the grid, so they stay aligned in logo_cloud.py
origin = pv.Vec3(*[-(n - 1) * h / 2.0 for n in (nx, ny, nz)])
pv.vdb_loader.save_float_volume(pv.FloatVolume.from_array(density, h, origin=origin), density_path, "density")
pv.vdb_loader.save_float_volume(pv.FloatVolume.from_array(light, h, origin=origin), light_path, "light")
for path in (density_path, light_path):
    log(f"wrote {path} ({os.path.getsize(path) / 1e6:.1f} MB)")
