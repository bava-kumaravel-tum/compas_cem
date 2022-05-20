from compas_cem.elements import Edge


class TrailEdge(Edge):
    """
    A trail edge.

    Notes
    -----
    If a plane is defined, it will override the absolute length of the trail edge.
    However, the sign of the length (e.g. the combinatorial state) is preserved.

    TODO: addexplicit combinatorial state to the signature of the constructor.
    """
    def __init__(self, u, v, length, plane=None, **kwargs):
        attrs = {"length": length, "type": "trail", "plane": plane}
        super(TrailEdge, self).__init__(u, v, attrs, **kwargs)
        # TODO
        # self.attributes = {"length": length, "state": state, type": "trail", "plane": plane}

    def __repr__(self):
        """
        """
        st = "{0}(length={1!r}, plane={2!r})"
        return st.format(self.__class__.__name__, self.attributes["length"], self.attributes["plane"])

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
