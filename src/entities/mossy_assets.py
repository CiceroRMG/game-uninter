import pygame, os, sys
try:
    from .. import settings
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import settings  # type: ignore

_COMP_CACHE = {}

def _load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return None

def extract_components(filename: str, min_w=16, min_h=16, max_components=64):
    key = (filename, min_w, min_h, max_components)
    if key in _COMP_CACHE:
        return _COMP_CACHE[key]
    path = os.path.join(settings.IMG_DIR, 'Mossy Tileset', filename)
    if not os.path.exists(path):
        _COMP_CACHE[key] = []
        return []
    sheet = _load_image(path)
    if sheet is None:
        _COMP_CACHE[key] = []
        return []
    mask = pygame.mask.from_surface(sheet)
    comps = []
    done = 0
    if hasattr(mask, 'connected_components'):
        try:
            for comp in mask.connected_components():
                rects = comp.get_bounding_rects()
                if not rects:
                    continue
                r = rects[0]
                if r.width < min_w or r.height < min_h:
                    continue
                surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                surf.blit(sheet, (0,0), r)
                comps.append(surf)
                done += 1
                if done >= max_components:
                    break
        except Exception:
            pass
    if not comps:
        w,h = mask.get_size()
        visited = [[False]*w for _ in range(h)]
        dirs = ((1,0),(-1,0),(0,1),(0,-1))
        for y in range(h):
            for x in range(w):
                if done >= max_components:
                    break
                if visited[y][x] or not mask.get_at((x,y)):
                    continue
                stack=[(x,y)]; visited[y][x]=True
                pixels=[]
                minx=maxx=x; miny=maxy=y
                while stack:
                    cx,cy = stack.pop()
                    pixels.append((cx,cy))
                    if cx<minx: minx=cx
                    if cx>maxx: maxx=cx
                    if cy<miny: miny=cy
                    if cy>maxy: maxy=cy
                    for dx,dy in dirs:
                        nx,ny = cx+dx, cy+dy
                        if 0<=nx<w and 0<=ny<h and not visited[ny][nx] and mask.get_at((nx,ny)):
                            visited[ny][nx]=True
                            stack.append((nx,ny))
                rect = pygame.Rect(minx,miny,maxx-minx+1,maxy-miny+1)
                if rect.width < min_w or rect.height < min_h:
                    continue
                surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                surf.blit(sheet, (0,0), rect)
                comps.append(surf); done +=1
    _COMP_CACHE[key] = comps
    return comps
