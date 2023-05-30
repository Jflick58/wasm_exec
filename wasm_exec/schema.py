class Result:
    def __init__(self, result, mem_size, data_len, consumed):
        self.text = result.strip()
        self.mem_size = mem_size
        self.data_len = data_len
        self.fuel_consumed = consumed
