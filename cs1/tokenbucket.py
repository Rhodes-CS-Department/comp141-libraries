import time


class TokenBucket:

    def __init__(self, tokens, time_unit):
        self.tokens = tokens
        self.time_unit = time_unit
        self.bucket = tokens
        self.last_check = time.time()

    def consume(self):
        if (self.bucket < 1):
            time.wait(self.time_unit / self.tokens)
            self.bucket = self.bucket + 1

        if (self.bucket > self.tokens):
            self.bucket = self.tokens
        else:
            self.bucket = self.bucket - 1

    def put_token(self):
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current

        """ Replenish the bucket """
        self.bucket = self.bucket + \
                time_passed * (self.tokens / self.time_unit)
