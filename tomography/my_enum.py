class MyEnum:
    _reverse_dict = None
    @classmethod
    def _build_reverse_dict(cls):
        if not cls._reverse_dict:
            cls._reverse_dict = {getattr(cls, attr): attr for attr in dir(cls) if not attr.startswith("_")}

    @classmethod
    def name(cls, value):
        cls._build_reverse_dict()
        return cls._reverse_dict.get(value, "UNKNOWN")