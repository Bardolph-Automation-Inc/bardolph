import copy


class Rect:
    def __init__(self, top=0, bottom=0, left=0, right=0):
        self.top, self.bottom, self.left, self.right = top, bottom, left, right

    def __eq__(self, other):
        if isinstance(other, Rect):
            return (self.top == other.top and self.bottom == other.bottom
                    and self.left == other.left and self.right == other.right)
        return False

    def __repr__(self):
        return 'Rect({}, {}, {}, {})'.format(
            self.top, self.bottom, self.left, self.right)


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
        self._mat = [[0] * width] * height

    def __str__(self):
        ret_value = ''
        for row in range(0, self._height):
            ret_value += 'Row {:1d}:\n'.format(row)
            for column in range(0, self._width):
                color = self._mat[row][column]
                if color is None:
                    ret_value += 'None '
                else:
                    ret_value += '{:1d}: '.format(column)
                    for x in color:
                        ret_value += ('{:8d} '.format(int(x)))
                ret_value += '\n'
        return ret_value

    @staticmethod
    def new_from_iterable(srce, height, width):
        return ColorMatrix(height, width).set_from_iterable(srce)

    @staticmethod
    def new_from_constant(height, width, init_value=None):
        return ColorMatrix(height, width).set_from_constant(init_value)

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
        return self

    def set_from_constant(self, value):
        """ Set every elmement to the same color. """
        self._mat.clear()
        for _ in range(0, self.height):
            self._mat.append([value] * self.width)
        return self

    def set_from_matrix(self, srce):
        self._width = srce.width
        self._height = srce.height
        self._mat = copy.deepcopy(srce.matrix)
        return self

    def find_replace(self, to_find, replacement):
        for row in range(0, self.height):
            for column in range(0, self.width):
                if self._mat[row][column] == to_find:
                    self._mat[row][column] = replacement.copy()

    def apply_transform(self, fn):
        for row in range(0, self.height):
            for column in range(0, self.width):
                value = self._mat[row][column]
                if value is not None:
                    self._mat[row][column] = fn(value)

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

    @staticmethod
    def _standardize_raw(color):
        # Keep all elements within the range expected by the bulb.
        if color is None:
            return None
        raw_color = []
        for param in color:
            if param < 0.0:
                param = 0
            elif param > 65535.0:
                param = 65535
            else:
                param = round(param)
            raw_color.append(param)
        return raw_color
