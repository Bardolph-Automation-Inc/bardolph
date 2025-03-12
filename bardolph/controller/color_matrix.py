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
    Generalized matrix for colors. Each cell is expected to contain a color,
    represented as a list of 4 unsigned, 16-bit integers.

    When a rectangle is used as a parameter to a method, the coordinates are
    inclusive, starting at zero. For example, a rectangle covering an entire
    6x5 matrix would be Rect(top=0, bottom=5, left=0, right=4).
    """

    def __init__(self, height, width):
        self._height = height
        self._width = width
        self._mat = []
        for _ in range(0, height):
            self._mat.append([[0, 0, 0, 0] for __ in range(0, width)])

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
    def new_from_iterable(height, width, srce):
        return ColorMatrix(height, width).set_from_iterable(srce)

    @staticmethod
    def new_from_constant(height, width, init_value):
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
        it = iter(srce)
        for row in range(0, self.height):
            for col in range(0, self.width):
                self._mat[row][col] = next(it)
        return self

    def set_from_constant(self, value):
        for row in range(0, self._height):
            for col in range(0, self._width):
                self._mat[row][col] = value
        return self

    def set_from_matrix(self, srce):
        for row in range(0, self._height):
            for col in range(0, self._width):
                self._mat[row][col] = srce.matrix[row][col]
        return self

    def get_colors(self):
        return [self._standardize_raw(param) for param in self.as_list()]

    def find_replace(self, to_find, replacement):
        for row in range(0, self.height):
            for column in range(0, self.width):
                if self._mat[row][column] == to_find:
                    self._mat[row][column] = replacement.copy()

    def as_list(self):
        return [self._mat[row][column]
                for row in range(0, self.height)
                for column in range(0, self.width)]

    def overlay_color(self, rect: Rect, color) -> None:
        # Set the cells within rect to color.
        self._normalize_rect(rect)
        for row in range(rect.top, rect.bottom + 1):
            for column in range(rect.left, rect.right + 1):
                self._mat[row][column] = color

    def overlay_section(self, rect: Rect, srce) -> None:
        # Copy the contents of srce into the section.
        self._normalize_rect(rect)
        for row in range(rect.top, rect.bottom + 1):
            for column in range(rect.left, rect.right + 1):
                self._mat[row][column] = srce[row][column]

    @staticmethod
    def _standardize_raw(color):
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

    def _normalize_rect(self, rect) -> None:
        """
        Fill in default values if necessary.
        """
        match rect.top is None, rect.bottom is None:
            case True, True:
                rect.top = 0
                rect.bottom = self.height - 1
            case True, False:
                rect.top = rect.bottom
            case False, True:
                rect.bottom = rect.top

        match rect.left is None, rect.right is None:
            case True, True:
                rect.left = 0
                rect.right = self.width - 1
            case True, False:
                rect.left = rect.right
            case False, True:
                rect.right = rect.left
        return rect