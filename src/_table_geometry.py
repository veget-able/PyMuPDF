"""Shared interval/stroke geometry; no table admission decisions."""
import math


def _coverage(intervals, start, end):
    if end <= start:
        return 0.
    total, cursor = 0., start
    for a, b in sorted(intervals):
        a, b = max(a, start), min(b, end)
        if b > max(a, cursor):
            total += b - max(a, cursor)
        cursor = max(cursor, b)
    return total / (end - start)


def _connector_segments(paths, *, orthogonal=False):
    """Oblique strokes and equivalent thin filled quadrilaterals, not frames."""
    segments=[]
    for p in paths:
        lines=[(tuple(i[1]),tuple(i[2])) for i in p['items'] if i[0]=='l']
        if 's' in p['type']:
            segments.extend((a,b) for a,b in lines if orthogonal or (abs(a[0]-b[0])>.1 and abs(a[1]-b[1])>.1))
        if p.get('fill') is None or len(p['items'])!=4 or len(lines)!=4:
            continue
        vertices={pt for line in lines for pt in line}
        if len(vertices)!=4 or any(sum(pt in line for line in lines)!=2 for pt in vertices):
            continue
        ranked=sorted(lines,key=lambda ab:math.dist(*ab),reverse=True)
        (a,b),(c,d)=ranked[:2]
        length=math.dist(a,b)
        if not length or math.dist(*ranked[2]) > .08*length:
            continue
        if math.dist(a,c)+math.dist(b,d) > math.dist(a,d)+math.dist(b,c):
            c,d=d,c
        start=tuple((a[k]+c[k])/2 for k in (0,1))
        end=tuple((b[k]+d[k])/2 for k in (0,1))
        if orthogonal or (abs(start[0]-end[0])>.1 and abs(start[1]-end[1])>.1):
            segments.append((start,end))
    return segments
