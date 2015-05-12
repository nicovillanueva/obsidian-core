class Capture(object):
    """
    Generic Capture entity. Base class
    that both Screenshot and Pdiff can inherit from.
    """
    def __init__(self, img_path):
        if img_path is not None:
            try:
                self.path = img_path
                self.hashvalue = self._set_hash()
            except IOError:
                self.path = None
                self.hashvalue = None

    def _set_hash(self):
        from hashlib import md5
        md5hasher = md5()
        with open(self.path, 'r') as f:
            data = f.read()
            md5hasher.update(data)
        return str(md5hasher.hexdigest())

    def to_string(self):
        entity = ""
        for each in self.__dict__:
            if each[0] != "_":
                entity += "%s: %s \n" % (each, self.__dict__.get(each))
        return entity
