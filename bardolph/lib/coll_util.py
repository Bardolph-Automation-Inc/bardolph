def cvt_enum(from_enum, to_cls):
    return cvt_string(from_enum.name, to_cls)

def cvt_string(name, to_cls):
    return to_cls[name]

def dict_zip(keys, values):
    assert len(keys) == len(values)
    return {key: value for key, value in zip(keys, values)}
