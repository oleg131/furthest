import geojsoncontour
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from scipy import interpolate, ndimage
from data.constants import MIN_LAT, MAX_LAT

mpl.use('Agg')

GRID = np.load('./data/grid.npy')
DATA = np.load('./data/values.npy')

WAIT = 0.01
N_COLORS = 10
SIGMA = 4
INTERPOLATION = 'nearest'
N_SPACE = 300
CMAP = plt.get_cmap('viridis')


def get_bins(vmax):
    bins = np.arange(0, 1000, 5)
    bins = bins[:N_COLORS].tolist()
    bins.append(vmax)

    return bins


def get_data_from_grid(lon, lat):
    x0 = GRID[:, 0]
    y0 = GRID[:, 1]

    origin = np.array([lon, lat]).astype(float)

    origin_ix = np.argmin(np.linalg.norm(origin - GRID, axis=1))
    z0 = DATA[origin_ix]

    mask = ~np.isnan(z0)

    x = x0[mask]
    y = y0[mask]
    z = z0[mask]

    x = np.concatenate([x - 360, x, x + 360])
    y = np.tile(y, 3)
    z = np.tile(z, 3)

    x_arr = np.linspace(-180 - 360, 180 + 360, N_SPACE * 3)
    y_arr = np.linspace(MIN_LAT, MAX_LAT, N_SPACE)
    x_mesh, y_mesh = np.meshgrid(x_arr, y_arr)
    z_mesh_int = interpolate.griddata(
        (x, y), z, (x_mesh, y_mesh), method=INTERPOLATION)

    z_mesh = ndimage.gaussian_filter(z_mesh_int, SIGMA)

    vmin = z.min()
    vmax = z.max()

    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        'custom', colors=CMAP.colors, N=N_COLORS)

    # bins = stats.mstats.mquantiles(z, np.linspace(0, 1, N_COLORS + 1))
    # bins = np.histogram(z, N_COLORS)[1]
    # bins = get_bins(vmax)
    bins = np.concatenate([np.arange(0, N_COLORS * 6, 6), [vmax]])
    # bins = np.concatenate([[0, 6, 12, 16, 20], np.linspace(24, vmax, 6)])

    norm = mpl.colors.BoundaryNorm(bins, N_COLORS)
    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    colors = [sm.to_rgba(b) for b in bins[:-1]]

    contour = plt.contourf(
        x_mesh, y_mesh, z_mesh, bins, alpha=0.5, linestyles='None',
        vmin=vmin, vmax=vmax, colors=colors
    )

    geojson = geojsoncontour.contourf_to_geojson(
        contourf=contour,
        ndigits=5,
        stroke_width=1,
        fill_opacity=1
    )

    colormap_ix = np.round(bins).astype(int)
    colormap = [
        [
            '{}-{}'.format(colormap_ix[i], colormap_ix[i + 1]),
            'rgba{}'.format(str(tuple([i * 255 for i in v])))
        ]
        for i, v in enumerate(colors)
    ]

    return {
        'geojson': geojson,
        'colormap': colormap,
        'origin': {
            'lon': x0[origin_ix],
            'lat': y0[origin_ix]
        },
        'grid': GRID.tolist()
    }
