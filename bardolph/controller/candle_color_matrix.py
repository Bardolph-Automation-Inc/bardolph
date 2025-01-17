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
        return CandleColorMatrix().set_from_iterable(srce)

    @staticmethod
    def new_from_constant(init_value=None):
        return CandleColorMatrix().set_from_constant(init_value)

    def get_colors(self):
        return [self._standardize_raw(param) for param in self.as_list()]

    def overlay_color(self, rect, color) -> None:
        """ Overlay the color onto a rectangular section of the body. """
        super().overlay_color(self._normalize_rect(rect), color)

    def overlay_section(self, rect, srce) -> None:
        """
        Overlay a matrix of colors onto a rectangular section of the body.
        """
        super().overlay_submat(self._normalize_rect(rect), srce)

    def _normalize_rect(self, rect):
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
