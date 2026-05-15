class S3Config:
    def __init__(self, bucket):
        self.bucket = bucket

class S3Resource:
    def __init__(self, config):
        self.config = config
