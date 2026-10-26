"""Geometry for the flights page: projection, Natural Earth land, great-circle routes.

No dependencies. Land comes from tools/land-110m.json (world-atlas 2.0.2,
Natural Earth 110m, TopoJSON), committed so the build runs offline.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def natural_earth(lon, lat):
    """Natural Earth I projection (Savric et al.), unit scale."""
    p = math.radians(lat)
    l = math.radians(lon)
    p2 = p * p
    p4 = p2 * p2
    x = l * (0.8707 - 0.131979 * p2 + p4 * (-0.013791 + p4 * (0.003971 * p2 - 0.001529 * p4)))
    y = p * (1.007226 + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4)))
    return x, y


class Frame:
    """Projects lon/lat into a viewBox of the given width, cropped to lat/lon bounds."""

    def __init__(self, west, east, south, north, width, project=natural_earth):
        self.project = project
        # sample the bound edges, since lines of longitude curve in this projection
        xs, ys = [], []
        for i in range(41):
            lat = south + (north - south) * i / 40
            lon = west + (east - west) * i / 40
            for x, y in (project(west, lat), project(east, lat), project(lon, south), project(lon, north)):
                xs.append(x)
                ys.append(y)
        self.x0, self.y1 = min(xs), max(ys)
        self.k = width / (max(xs) - self.x0)
        self.width = width
        self.height = round((self.y1 - min(ys)) * self.k, 1)

    def __call__(self, lon, lat):
        x, y = self.project(lon, lat)
        return (x - self.x0) * self.k, (self.y1 - y) * self.k


def _arcs(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    out = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def _ring(arcs, idx):
    pts = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


def plate_carree(lon, lat):
    return lon, lat


def _area(pts):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2


def land_path(frame, min_lat=-58, step=0.6, min_area=4, west=-180, east=180, fmt="{:.0f}"):
    """SVG path for land: Antarctica, rings outside [west, east] and islands under
    `min_area` square units dropped, points closer than `step` units merged."""
    topo = json.loads((HERE / "land-110m.json").read_text(encoding="utf-8"))
    arcs = _arcs(topo)
    parts = []
    for geom in topo["objects"]["land"]["geometries"]:
        polys = geom["arcs"] if geom["type"] == "MultiPolygon" else [geom["arcs"]]
        for poly in polys:
            for idx in poly:
                ring = _ring(arcs, idx)
                # a ring across the 180th meridian (Chukotka) would draw a band
                # across the whole map: unwrap it so no step jumps 360 degrees
                shift, prev, flat = 0, ring[0][0], []
                for lon, lat in ring:
                    if lon - prev > 180:
                        shift -= 360
                    elif prev - lon > 180:
                        shift += 360
                    prev = lon
                    flat.append((lon + shift, lat))
                # then put the bulk of the ring back between -180 and 180
                mid = sorted(lon for lon, _ in flat)[len(flat) // 2]
                k = 360 * round(mid / 360)
                ring = [(lon - k, lat) for lon, lat in flat]
                if max(lat for _, lat in ring) < min_lat:
                    continue
                if max(lon for lon, _ in ring) < west or min(lon for lon, _ in ring) > east:
                    continue
                pts, last = [], None
                for lon, lat in ring:
                    x, y = frame(lon, max(lat, min_lat))
                    if last and abs(x - last[0]) + abs(y - last[1]) < step:
                        continue
                    pts.append((x, y))
                    last = (x, y)
                if len(pts) > 3 and _area(pts) >= min_area:
                    d = [fmt.format(x) + " " + fmt.format(y) for x, y in pts]
                    parts.append("M" + "L".join(d) + "Z")
    return "".join(parts)


def great_circle(frame, a, b, seg_km=150, n=None):
    """Points along the great circle from a=(lon, lat) to b, projected."""
    lo1, la1, lo2, la2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    v1 = (math.cos(la1) * math.cos(lo1), math.cos(la1) * math.sin(lo1), math.sin(la1))
    v2 = (math.cos(la2) * math.cos(lo2), math.cos(la2) * math.sin(lo2), math.sin(la2))
    w = math.acos(max(-1, min(1, sum(p * q for p, q in zip(v1, v2)))))
    n = n or max(2, int(w * 6371 / seg_km))
    pts = []
    for i in range(n + 1):
        t = i / n
        if w < 1e-9:
            v = v1
        else:
            s1, s2 = math.sin((1 - t) * w) / math.sin(w), math.sin(t * w) / math.sin(w)
            v = tuple(s1 * p + s2 * q for p, q in zip(v1, v2))
        lat = math.degrees(math.atan2(v[2], math.hypot(v[0], v[1])))
        lon = math.degrees(math.atan2(v[1], v[0]))
        pts.append(frame(lon, lat))
    return pts


def route_path(pts, fmt="{:.1f}"):
    return "M" + "L".join(fmt.format(x) + " " + fmt.format(y) for x, y in pts)


def graticule(frame, west, east, south, north, every=30):
    """Faint lines of latitude and longitude inside the crop."""
    d = []
    for lon in range(-180, 181, every):
        if west <= lon <= east:
            d.append(route_path([frame(lon, south + (north - south) * i / 30) for i in range(31)]))
    for lat in range(-90, 91, every):
        if south <= lat <= north:
            d.append(route_path([frame(west + (east - west) * i / 60, lat) for i in range(61)]))
    return "".join(d)
