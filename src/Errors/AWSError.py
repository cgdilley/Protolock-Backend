class AWSError(Exception):

    def __init__(self, *args, **kwargs):
        super(AWSError, self).__init__(*args)
        self.kwargs = kwargs
