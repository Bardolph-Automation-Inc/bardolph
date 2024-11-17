import copy


class Rect:
    def __init__(self, top=0, bottom=0, left=0, right=0):
        self.top, self.bottom, self.left, self.right = top, bottom, left, right


class ColorMatrix:
    """
    Generalized matrix for colors, with no specific width or height. Each cell
    is expected to contain a color, represented as a list of 4 unsigned, 16-bit
    integers.

    When a rectangle is used as a parameter to a method, the coordinates are
    inclusive, starting at zero. For example, a rectangle covering an entire
    6x5 matrix would be Rect(top=0, bottom=5, left=0, right=4).
    """

    def __init__(self, height, width):
        """ Set all cells to zero. """
        self._width = width
        self._height = height
        self._mat = [[0] * self._width] * self._height

    @staticmethod
    def new_from_iterable(srce, height, width):
        inst = ColorMatrix(height, width)
        inst.set_from_iterable(srce)
        return inst

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    @property
    def matrix(self):
        return self._mat

    def set_from_iterable(self, srce):
        """ Initialize from one-dimensional, list, tuple, generator, etc. """
        self._mat.clear()
        it = iter(srce)
        for row_count in range(0, self.height):
            row = []
            for column_count in range(0, self.width):
                row.append(next(it))
            self._mat.append(row)

    def set_from_matrix(self, srce):
        self._width = srce.width
        self._height = srce.height
        self._mat = copy.deepcopy(srce.matrix)

    def as_list(self):
        return [self._mat[row][column]
                for row in range(0, self.height)
                for column in range(0, self.width)]

    def overlay_color(self, rect: Rect, color) -> None:
        """ Set the cells within rect to color. """
        for row in range(rect.top, rect.bottom + 1):
            for column in range(rect.left, rect.right + 1):
                self._mat[row][column] = color

    def overlay_submat(self, rect: Rect, srce) -> None:
        """
        Set the cells within the corners to the values in the corresponding
        cells in srce. The content of corners is 4 elements containing first and
        last row, followed by first and last column.
        """
        for row in range(rect.top, rect.bottom + 1):
            for column in range(rect.left, rect.right + 1):
                self._mat[row][column] = srce[row][column]
