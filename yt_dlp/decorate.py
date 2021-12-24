def mtrace(cls):
    def trace(f):
        "Decorate a function to print a message before and after execution."
        def traced(*args, **kw):
            "Print message before and after a function call."
            print("Entering", f.__name__)
            result = f(*args, **kw)
            print("Leaving", f.__name__)
            return result

        return traced

    def callable(o):
        return hasattr(o, "__call__")

    for key, val in cls.__dict__.items():
        if not callable(val):
            continue
        setattr(cls, key, trace(val))
        print("Wrapped", key)

    return cls
