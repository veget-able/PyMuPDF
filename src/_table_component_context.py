"""Evidence that a valid grid is a component of a chart or device diagram.

Called only for independent-region admission. Reuses finder CHARS, original
drawing paths and image occurrences from the existing raster-rule producer.
Missing context is not negative evidence. No extraction, model or GT access.
"""
import math
import re
import unicodedata
from ._table_append_context import grid_cell_texts


def _percentage(text):
    text = unicodedata.normalize('NFKC', text).replace('٪', '%').replace('٫', '.')
    text = ''.join(str(unicodedata.decimal(c)) if c.isdecimal() else c for c in text)
    if not re.fullmatch(r'\s*\d+(?:[.,]\d+)?\s*%\s*', text):
        return None
    return float(text.strip().rstrip('%').strip().replace(',', '.')) / 100


def _matching_fill(cell, paths, tolerance):
    return any(p.get('fill') is not None
               and max(abs(a-b) for a,b in zip(cell,p['rect'])) <= tolerance
               for p in paths)


def _shared_axis(boxes, paths):
    """Short, regular perpendicular ticks spanning the common horizontal scale."""
    x0 = boxes[0][0]; x1 = boxes[0][2]; width = x1-x0
    height = max(b[3]-b[1] for b in boxes)
    bottom = max(b[3] for b in boxes)
    top = min(b[1] for b in boxes)
    rows = {}
    for p in paths:
        if 's' not in p['type']:
            continue
        for item in p['items']:
            if item[0] != 'l':
                continue
            a,b = item[1:3]
            length = abs(a[1]-b[1])
            y = (a[1]+b[1])/2
            if (abs(a[0]-b[0]) <= .005*width and .05*height <= length <= .5*height
                    and (bottom <= y <= bottom+2*height or top-2*height <= y <= top)
                    and x0-.01*width <= a[0] <= x1+.01*width):
                rows.setdefault(round(y/max(height*.1,1e-6)), []).append(a[0])
    for xs in rows.values():
        xs = sorted(set(round(x/width,4) for x in xs))
        gaps = [b-a for a,b in zip(xs,xs[1:])]
        if (len(xs) >= 4 and abs(xs[0]-x0/width) <= .02
                and abs(xs[-1]-x1/width) <= .02 and min(gaps)>0
                and max(gaps) <= 1.1*min(gaps)):
            return True
    return False


def stacked_bars(candidates, chars, paths, *, cell_texts=None):
    plausible = []
    for index,(bbox,grid,picture) in enumerate(candidates):
        if not picture or len(grid) != 1:
            continue
        cells = cell_texts[index] if cell_texts is not None else grid_cell_texts(grid,chars)
        if len(cells) < 2 or any(not t for c,t in cells):
            continue
        width = bbox[2]-bbox[0]; height = bbox[3]-bbox[1]
        if width <= 0 or height <= 0:
            continue
        values = [_percentage(t) for c,t in cells]
        if any(v is None for v in values) or abs(sum(values)-1) > .025:
            continue
        if any(abs((c[2]-c[0])/width-v) > .025 for (c,t),v in zip(cells,values)):
            continue
        if not all(_matching_fill(c,paths,.03*height) for c,t in cells):
            continue
        plausible.append((index,bbox,tuple((c[2]-bbox[0])/width for c,t in cells[:-1])))
    found = set()
    for index,box,breaks in plausible:
        width=box[2]-box[0]; height=box[3]-box[1]
        peers=[p for p in plausible if abs(p[1][0]-box[0]) <= .01*width
               and abs(p[1][2]-box[2]) <= .01*width
               and .8*height <= p[1][3]-p[1][1] <= 1.2*height
               and abs(p[1][1]-box[1]) <= 12*height
               and (p[0]==index or p[1][1]>=box[3] or p[1][3]<=box[1])]
        variable=any(len(b)==len(breaks) and any(abs(a-c)>.05 for a,c in zip(b,breaks))
                     for _,_,b in peers)
        if len(peers)>=2 and variable and _shared_axis([p[1] for p in peers],paths):
            found.add(index)
    return found


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


def _contains(box,point):
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def device_state_grids(candidates, chars, paths, image_boxes, *, cell_texts=None):
    if len(image_boxes)<3:
        return set()
    connectors=_connector_segments(paths, orthogonal=True)
    if len(connectors)<2:
        return set()
    plausible=[]
    for index,(box,grid,picture) in enumerate(candidates):
        if not picture or not grid or max(map(len,grid),default=0)<2:
            continue
        texts=cell_texts[index] if cell_texts is not None else grid_cell_texts(grid,chars)
        occupied=[(c,t) for c,t in texts if t]
        if len(occupied)<2 or not all(len(t)==1 and t.isalpha() for c,t in occupied):
            continue
        width=box[2]-box[0]; height=box[3]-box[1]
        links=[]
        for i,image in enumerate(image_boxes):
            iw=image[2]-image[0]; ih=image[3]-image[1]; cx=(image[0]+image[2])/2
            overlap=max(0,min(image[3],box[3])-max(image[1],box[1]))
            # An adjacent device occurrence, not an image enclosing the table.
            if not (iw >= .25*width and ih >= .5*height
                    and overlap >= .5*height and (cx<box[0] or cx>box[2])
                    and min(abs(cx-box[0]),abs(cx-box[2])) <= width):
                continue
            for a,b in connectors:
                if _contains(image,b):
                    a,b=b,a
                if not _contains(image,a) or _contains(image,b):
                    continue
                for j,remote in enumerate(image_boxes):
                    if (j!=i and _contains(remote,b) and not _contains(remote,a)
                            and (remote[3] < image[1] or remote[1] > image[3])):
                        links.append((i,j))
        if links:
            plausible.append((index,box,len(grid),max(map(len,grid)),links))
    found=set()
    for index,box,rows,cols,links in plausible:
        h=box[3]-box[1]; w=box[2]-box[0]
        for other,peer,pr,pc,peer_links in plausible:
            if (other==index or rows!=pr or cols!=pc
                    or abs(box[1]-peer[1])>.2*h or abs((peer[2]-peer[0])-w)>.2*w
                    or abs((peer[3]-peer[1])-h)>.2*h):
                continue
            if any(i!=pi for i,j in links for pi,pj in peer_links):
                found.add(index)
    return found


def arrowed_curve_grid(box, grid, paths, triangles):
    """Opposite grid borders are directed paths, with curved links inside.

    A grid of diagram labels is not a table solely because each slot has text.
    Require positive graphics evidence, not particular mathematical words.
    """
    if len(grid) != 1:
        return False
    x0,y0,x1,y1=box
    h=y1-y0
    if h<=0:
        return False
    top=bottom=False
    for a,b,c,d in triangles:
        if x0 <= (a+c)/2 <= x1:
            top |= b <= y0+.1*h and d >= y0-.1*h
            bottom |= b <= y1+.1*h and d >= y1-.1*h
    if not (top and bottom):
        return False
    for path in paths:
        if 's' not in path['type']:
            continue
        # A non-straight cubic connector that travels inside the alleged grid.
        for item in path['items']:
            if item[0]!='c':
                continue
            points=item[1:]
            a,b,c,d=points
            curve=max(abs((d[0]-a[0])*(p[1]-a[1])-(d[1]-a[1])*(p[0]-a[0]))
                      for p in (b,c))
            if curve <= 1e-6:
                continue
            if all(x0 <= p[0] <= x1 and y0-.1*h <= p[1] <= y1+.1*h for p in points):
                return True
    return False


def circuit_component(box, paths):
    """Two parallel plates with opposite outward leads at their interiors.

    Capacitor/battery topology is positive diagram evidence. Parallel table
    rules alone, or rules meeting at their corners, are not sufficient.
    Called only for candidates lacking tabular content support.
    """
    segments=[(a,b) for a,b in _connector_segments(paths, orthogonal=True)
              if max(a[0],b[0])>=box[0] and min(a[0],b[0])<=box[2]
              and max(a[1],b[1])>=box[1] and min(a[1],b[1])<=box[3]]
    for axis in (0,1):
        lines=[]
        for a,b in segments:
            # (coordinate across a plate, low/high along the plate)
            x=(a[axis]+b[axis])/2
            low,high=sorted((a[1-axis],b[1-axis]))
            if high>low and abs(a[axis]-b[axis]) <= .01*(high-low):
                lines.append((x,low,high))
        for j,(x,lo,hi) in enumerate(lines):
            for xx,ll,hh in lines[j+1:]:
                length=min(hi-lo,hh-ll); tol=.1*length
                if not .05*length <= abs(xx-x) <= .8*length:
                    continue
                center=((lo+hi)+(ll+hh))/4
                if abs((lo+hi)/2-(ll+hh)/2)>.2*length:
                    continue
                if not _contains(box, (x,center) if axis==0 else (center,x)):
                    continue
                if not _contains(box, (xx,center) if axis==0 else (center,xx)):
                    continue
                left,right=sorted((x,xx))
                def outward(plate,sign):
                    for a,b in segments:
                        for end,far in ((a,b),(b,a)):
                            if (abs(end[axis]-plate)<=tol
                                    and abs(end[1-axis]-center)<=.25*length
                                    and abs(far[1-axis]-end[1-axis])<=tol
                                    and sign*(far[axis]-plate)>=length):
                                return True
                    return False
                if outward(left,-1) and outward(right,1):
                    return True
    return False


def component_vetoes(candidates, chars, paths, image_boxes, *, cell_texts=None,
                     content_support=None, triangles=None):
    if cell_texts is None:
        cell_texts=[grid_cell_texts(grid,chars) for bbox,grid,picture in candidates]
    result={i:'repeated_value_encoded_bars' for i in stacked_bars(candidates,chars,paths,cell_texts=cell_texts)}
    result.update({i:'device_owned_state_grids'
                   for i in device_state_grids(candidates,chars,paths,image_boxes,cell_texts=cell_texts)})
    if triangles is None:
        from ._table_append_context import graphic_primitives
        triangles,_=graphic_primitives(paths)
    result.update({i:'directed_curved_diagram_grid' for i,(box,grid,picture) in enumerate(candidates)
                   if arrowed_curve_grid(box,grid,paths,triangles)})
    if content_support is not None:
        result.update({i:'circuit_plates_and_leads_without_table_content'
                       for i,(box,grid,picture) in enumerate(candidates)
                       if not content_support[i] and circuit_component(box,paths)})
    return result
