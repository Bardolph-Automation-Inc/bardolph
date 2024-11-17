from bardolph.controller.color_matrix import ColorMatrix


class CandleColorMatrix(ColorMatrix):
    """
    Specialization of ColorMatrix that accounts for the layout of the matrix
    within a Candle Color device and the parameters required by the API.
    """

    def __init__(self):
        super().__init__(6, 5)

    @staticmethod
    def new_from_iterable(srce):
        inst = CandleColorMatrix()
        inst.set_from_iterable(srce)
        return inst

    def get_colors(self):
        return [self._standardize_raw(param) for param in self.as_list()]

    def set_body(self, color):
        """
        Set all of the cells in the body, but not the one on top, to the given
        color.
        """
        for row in range(1, self.height):
            for column in range(0, self.width):
                self._mat[row][column] = color.copy()

    def set_top(self, color):
        """ Set the cell at the top to the given color. """
        m = [color]
        m.extend([[0, 0, 0, 0]] * 4)
        self._mat[0] = m

    def get_body(self):
        """ Return the body colors in a 5x5 matrix. """
        mat = self._mat.copy()
        del mat[0]
        return mat

    def get_top(self):
        return self._mat[0][0]

    def set_body_cell(self, row, column, color):
        self.matrix[row + 1][column] = color

    def get_body_cell(self, row, column):
        return self.matrix[row + 1][column]

    def overlay_color(self, rect, color) -> None:
        """ Overlay the color onto a rectangular section of the body. """
        super().overlay_color(self._normalize_rect(rect), color)

    def overlay_section(self, rect, srce) -> None:
        """
        Overlay a matrix of colors onto a rectangular section of the body.
        """
        super().overlay_submat(self._normalize_rect(rect), srce)

    @staticmethod
    def _standardize_raw(color) -> int:
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

    def _normalize_rect(self, rect):
        """
        Fill in default values if necessary. Then offset the vertical by 1 to
        account for the tip's row.
        """
        match rect.top is None, rect.bottom is None:
            case True, True:
                rect.top = 0
                rect.bottom = self.height - 2
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

        rect.top += 1
        rect.bottom += 1

        return rect
