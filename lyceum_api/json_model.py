class AnnotatedJson(object):
    @staticmethod
    def default_extractor(data, field_name):
        return data.get(field_name)

    def __init__(self, data):
        default_extractor = AnnotatedJson.default_extractor
        for attr, ann in self.__annotations__.items():
            extract = getattr(self, '_extract_' + attr, default_extractor)
            value = extract(data, attr)
            if value is not None:
                setattr(self, attr, value)
