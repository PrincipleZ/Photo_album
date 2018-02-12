class Album(object):

    def __init__(self, name, id, description):
        self.name = name
        self.herf = "../" + str(id)
        self.description = description
