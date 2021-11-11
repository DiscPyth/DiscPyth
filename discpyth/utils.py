# Monkey Patched exception creator 😋
def new_error(name: str, output=None) -> Exception:
    def replacedinit(self):  # pylint: disable=unused-argument;
        Exception.__init__(self, output)

    def modifiedinit(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

    # Quick way to create a class
    err = type(str(name), (Exception,), {})
    if output is not None:
        # Replace __init__ if output is defined,
        # better than new_error("Error")("Output")
        # instead new_error("Error", "Output")
        setattr(err, "__init__", replacedinit)
    else:
        setattr(err, "__init__", modifiedinit)
    return err  # type: ignore
