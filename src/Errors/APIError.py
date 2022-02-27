class APIError(Exception):

    def __init__(self, *args, **kwargs):
        super(APIError, self).__init__(*args)
        self.kwargs = kwargs
