"""Numerical checks of the main-text examples, independent of GPU execution."""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, '/private/tmp/atmos-blog-deps')
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
results = {}

# Integrate a uniform incident field over the upper hemisphere.
nodes, weights = np.polynomial.legendre.leggauss(64)
mu = (nodes + 1) / 2
hemisphere = 2 * math.pi * np.dot(weights / 2, mu)
assert abs(hemisphere - math.pi) < 1e-13
results['uniform_hemisphere'] = {'E_over_L': float(hemisphere), 'expected': math.pi}

# A constant local source checks the sign and dimensions of the RTE solution.
beta, source, distance, boundary = 2e-5, 4e-4, 80000., 3.
x = np.linspace(0, distance, 100001)
integral = np.trapezoid(np.exp(-beta * x) * source, x)
closed_source = source * (-math.expm1(-beta * distance)) / beta
assert abs(integral - closed_source) / closed_source < 1e-9
small_beta = 1e-15
limit = source * (-math.expm1(-small_beta * distance)) / small_beta
assert abs(limit - source * distance) / (source * distance) < 1e-9
results['homogeneous_transfer'] = {
    'quadrature_source': float(integral), 'closed_source': closed_source,
    'received_with_boundary': math.exp(-beta * distance) * boundary + closed_source,
    'zero_extinction_limit_relative_error': abs(limit - source * distance) / (source * distance),
}

rb, rt, radius = 6360000., 6420000., 6361000.
rho, H = math.sqrt(radius**2 - rb**2), math.sqrt(rt**2 - rb**2)
horizon = -rho / radius
near, far = radius - rb, radius + rb
assert near == 1000. and far == 12721000.
results['sphere_geometry'] = {
    'downward_roots_m': [near, far], 'horizon_mu': horizon,
    'horizon_depression_deg': math.degrees(math.asin(-horizon)),
    'first_above_ground_T_sample_m': math.sqrt(rb**2 + (H / 63)**2) - rb,
}

optical_length = .5 * 1000.
single_sample = 1. * .6 * .8 * 2e-5 * .5 * .1 * 100.
assert abs(single_sample - 4.8e-5) < 1e-18
results['short_path_examples'] = {
    'equivalent_length_m': optical_length, 'optical_depth': optical_length * 2e-5,
    'single_sample_radiance': single_sample,
}

def tex(value, size):
    return .5 / size + value * (1 - 1 / size)

u = tex(.4, 4)
index = 4 * u - .5
assert abs(u - .425) < 1e-14 and abs(index - 1.2) < 1e-14
results['texel_center_example'] = {'u': u, 'continuous_index': index,
                                    'neighbor_indices': [1, 2], 'weights': [.8, .2]}
endpoints = [.5 - .5 * tex(0, 64), .5 - .5 * tex(1, 64),
             .5 + .5 * tex(1, 64), .5 + .5 * tex(0, 64)]
assert endpoints == [127/256, 1/256, 255/256, 129/256]
results['scattering_mu_endpoints'] = {
    'order': ['down', 'horizon_ground', 'horizon_sky', 'up'], 'u_mu': endpoints,
}
low, high = .6 * .8 - math.sqrt((1-.6**2)*(1-.8**2)), .6 * .8 + math.sqrt((1-.6**2)*(1-.8**2))
assert abs(low) < 1e-14 and abs(high-.96) < 1e-14
results['angle_feasibility_example'] = {'mu': .6, 'mu_s': .8, 'nu_interval': [low, high]}

# Compare two packed trilinear lookups with the expected multilinear value.
def packed_texel(ix, iy, iz):
    block, solar = divmod(ix, 32)
    return 2*block/7 - 1 + 2*solar/31 + 3*iy/127 + 4*iz/31

def trilinear(coord):
    pos = np.array(coord) * np.array([256, 128, 32]) - .5
    base = np.floor(pos).astype(int)
    fraction = pos - base
    value = 0.
    for dz in (0, 1):
        for dy in (0, 1):
            for dx in (0, 1):
                offsets = np.array([dx, dy, dz])
                weight = np.prod(np.where(offsets, fraction, 1-fraction))
                value += weight * packed_texel(*(base + offsets))
    return float(value)

us, um, ur, nu = .5, .75, .25, 0.
q = (nu+1)*7/2
block, fraction = math.floor(q), q-math.floor(q)
coordinates = [((block+us)/8, um, ur), ((block+1+us)/8, um, ur)]
packed = (1-fraction)*trilinear(coordinates[0]) + fraction*trilinear(coordinates[1])
expected = nu + 2*(32*us-.5)/31 + 3*(128*um-.5)/127 + 4*(32*ur-.5)/31
assert abs(packed-expected) < 1e-13
results['packed_interpolation'] = {'coordinates': coordinates, 'nu_fraction': fraction,
                                    'multilinear_value_error': abs(packed-expected)}

# Exact cell areas contrast with the engine's midpoint quadrature.
theta = np.linspace(0, math.pi, 17)
midpoints = (theta[:-1] + theta[1:]) / 2
exact_area = float(np.sum((np.cos(theta[:-1])-np.cos(theta[1:])) * 2*math.pi))
midpoint_area = float(np.sum(np.sin(midpoints)) * (math.pi/16) * 2*math.pi)
assert abs(exact_area-4*math.pi) < 1e-13
results['solid_angle_grid'] = {
    'exact_cell_sum_sr': exact_area, 'midpoint_sum_sr': midpoint_area,
    'midpoint_relative_area_error': midpoint_area/(4*math.pi)-1,
    'equatorial_to_polar_weight_ratio': float(np.sin(midpoints[7])/np.sin(midpoints[0])),
}

# The standard texture lifecycle and the real draw-list chunk sizes.
steps = ['T', 'direct'] + [f'single_{k}' for k in range(32)]
for order in range(2, 6):
    steps += [f'density_{order}_{k}' for k in range(32)]
    steps += [f'irradiance_{order-1}']
    steps += [f'multiple_{order}_{k}' for k in range(32)]
chunks = [steps[k:k+24] for k in range(0, len(steps), 24)]
assert len(steps) == 294 and len(chunks) == 13
assert chunks[0][-1] == 'single_21'
assert chunks[1][0] == 'single_22' and chunks[1][-1] == 'density_2_13'
assert chunks[2][0] == 'density_2_14' and chunks[2][-1] == 'multiple_2_4'
results['frame_schedule'] = {'draw_steps': len(steps), 'recording_frames': len(chunks),
                             'first_three_frame_steps': chunks[:3],
                             'direction_iterations_per_density_stage': 256*128*32*512}

pr, pm = .08, .6
decoded = pr*((2+3)/pr) + pm*(1/pm)
assert abs(decoded-6) < 1e-14
results['phase_encoding_example'] = {'decoded_radiance': decoded}
results['fp16_ratio_example'] = {'exact': math.exp(-21)/math.exp(-20),
                                  'stored_numerator': float(np.float16(math.exp(-21))),
                                  'stored_denominator': float(np.float16(math.exp(-20)))}
assert results['fp16_ratio_example']['stored_numerator'] == 0.
assert results['fp16_ratio_example']['stored_denominator'] == 0.
F = lambda value: -math.expm1(-value)
results['display_order_example'] = {'combine_then_map': F(.5*2+1),
                                     'map_then_combine': .5*F(2)+F(1)}
assert abs(results['display_order_example']['combine_then_map']-.8646647167633873) < 1e-14

# Construct an outside ellipsoid point at a known normal height; recover it.
axes = np.array([6378137., 6356752.314245, 6378137.])
theta0 = math.radians(42)
surface = np.array([axes[0]*math.cos(theta0), axes[1]*math.sin(theta0), 0.])
normal = surface/(axes*axes)
normal /= np.linalg.norm(normal)
point = surface + 1000.*normal
squared = axes*axes
lagrange = (np.linalg.norm(point)-np.min(axes))*np.min(axes)
for iteration in range(6):
    den = squared+lagrange
    f = np.sum(point*point*squared/(den*den))-1
    df = -2*np.sum(point*point*squared/(den*den*den))
    lagrange -= f/df
foot = point*squared/(squared+lagrange)
n = foot/squared
n /= np.linalg.norm(n)
height = np.dot(point-foot, n)
assert abs(height-1000.) < 1e-7
assert np.linalg.norm(foot-surface) < 1e-7
results['ellipsoid_closest_point_float64'] = {
    'height_error_m': float(abs(height-1000.)),
    'surface_point_error_m': float(np.linalg.norm(foot-surface)),
    'note': 'Float64 explanatory geometry; not a bound on the shader float32 error.',
}

target = ROOT/'.article_tools/qa/main_text_examples_validation.json'
target.write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'example_groups': len(results), 'all_checks_passed': True,
                  'output': str(target.relative_to(ROOT))}, ensure_ascii=False))
