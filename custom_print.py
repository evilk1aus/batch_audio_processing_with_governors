def custom_print(*args, **kwargs):
    kwargs.setdefault('end', '\r\n')
    print(*args, **kwargs)
