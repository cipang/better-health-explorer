
# Direction constants for scanning.
DIR_RIGHT = 0
DIR_LEFT = 1
DIR_UP = 2
DIR_DOWN = 3


class Rectangle(object):

    """Define a rectangle which is used for overlap removal.

    This class stores the coordinate of the left-top corner and the size of a
    rectangle. This information is used to calculate new position after running
    an overlap removal process. One may inherit this class to store additional
    values/identifiers along with a rectangle.
    """

    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return "{0}(x={1}, y={2}, width={3}, height={4})".\
            format(type(self).__name__, self.x, self.y, self.width, self.height)

    def __eq__(self, other):
        if other is None:
            return False
        if self is other:
            return True
        try:
            return self.x == other.x and \
                self.y == other.y and \
                self.width == other.width and \
                self.height == other.height
        except Exception:
            return False

    def __hash__(self):
        return hash(repr(self))

    def __ne__(self, other):
        return not self.__eq__(other)


def remove_overlap(rectangles):
    """Change the positions of rectangles so that rectangles do not overlap.

    Note: The new positions overwrites the current x, y values of rectangles.
    Make a copy if you want to preserve the original coordinates.

    :param rectangles: A list of rectangles.
    """
    _right_horizontal_scan(rectangles)
    _left_horizontal_scan(rectangles)
    _up_horizontal_scan(rectangles)
    _down_horizontal_scan(rectangles)


def _mx(r):
    return r.x + r.width


def _my(r):
    return r.y + r.height


def _x(r):
    return r.x


def _y(r):
    return r.y


def _intersects(a, b):
    return _x(a) < _mx(b) and _mx(a) > _x(b) and \
        _y(a) < _my(b) and _my(a) > _y(b)


def _find_ns(entries, arg, dir):
    ns_set = set()
    for e in entries:
        if arg != e and _intersects(e, arg):
            if ((dir == DIR_LEFT and _x(e) < _x(arg)) or
                (dir == DIR_RIGHT and _x(e) >= _x(arg)) or
                (dir == DIR_UP and _y(e) < _y(arg)) or
                (dir == DIR_DOWN and _y(e) >= _y(arg))):
                ns_set.add(e)
    return ns_set


def _find_tns(entries, v, dir):
    tns_set = set()
    old_set = set()
    i = 1
    while True:
        old_set.clear()
        temp_list = list()
        if i == 1:
            nsv = _find_ns(entries, v, dir)
            for u in nsv:
                tns_set.update(_find_ns(entries, u, dir))
            tns_set.update(nsv)
            tns_set.discard(v)
        else:
            old_set.update(tns_set)
            for u in tns_set:
                temp_list.extend(_find_ns(entries, u, dir))
            tns_set.update(temp_list)
            tns_set.discard(v)
            if tns_set == old_set:
                break
        i += 1
    return tns_set


def _right_horizontal_scan(rectangles):
    rectangles.sort(key=lambda k: k.x)
    for vi in rectangles:
        rns = _find_ns(rectangles, vi, DIR_RIGHT)
        if rns:
            rtns = _find_tns(rectangles, vi, DIR_RIGHT)
            f = 0
            for vj in rns:
                fx = abs(_mx(vi) - _x(vj))
                fy = min(abs(_my(vi) - _y(vj)), abs(_y(vi) - _my(vj)))
                delta = min(fx, fy)
                if delta == fx and (delta < f or f == 0):
                    f = delta
            if f != 0:
                for e in rtns:
                    e.x += f


def _left_horizontal_scan(rectangles):
    rectangles.sort(key=lambda k: k.x)
    for vi in reversed(rectangles):
        lns = _find_ns(rectangles, vi, DIR_LEFT)
        if lns:
            ltns = _find_tns(rectangles, vi, DIR_LEFT)
            f = 0
            for vj in lns:
                fx = abs(_x(vi) - _mx(vj))
                fy = min(abs(_y(vi) - _my(vj)), abs(_my(vi) - _y(vj)))
                delta = min(fx, fy)
                if delta == fx and (delta > f or f == 0):
                    f = delta
            if f != 0:
                for e in ltns:
                    e.x -= f


def _up_horizontal_scan(rectangles):
    rectangles.sort(key=lambda k: k.y)
    for vi in reversed(rectangles):
        uns = _find_ns(rectangles, vi, DIR_UP)
        if uns:
            utns = _find_tns(rectangles, vi, DIR_UP)
            f = 0
            for vj in uns:
                fy1 = abs(_my(vi) - _y(vj))
                fy2 = abs(_y(vi) - _my(vj))
                delta = min(fy1, fy2)
                if delta == fy1 and (delta > f or f == 0):
                    f = delta
            if f != 0:
                for e in utns:
                    e.y -= f


def _down_horizontal_scan(rectangles):
    rectangles.sort(key=lambda k: k.y)
    for vi in rectangles:
        dns = _find_ns(rectangles, vi, DIR_DOWN)
        if dns:
            dtns = _find_tns(rectangles, vi, DIR_DOWN)
            f = 0
            for vj in dns:
                fy1 = abs(_y(vi) - _my(vj))
                fy2 = abs(_my(vi) - _y(vj))
                delta = min(fy1, fy2)
                if delta == fy2 and (delta > f or f == 0):
                    f = delta
            if f != 0:
                for e in dtns:
                    e.y += f
