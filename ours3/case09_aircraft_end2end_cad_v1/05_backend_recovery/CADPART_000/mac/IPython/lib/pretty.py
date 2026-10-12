class RepresentationPrinter:
    def text(self, value):
        return None

    def begin_group(self, *args, **kwargs):
        return None

    def end_group(self, *args, **kwargs):
        return None

    def breakable(self, *args, **kwargs):
        return None

    def pretty(self, value):
        return repr(value)


def pretty(value):
    return repr(value)
