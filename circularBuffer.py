class circularBuffer():
    def __init__(size):
        this.size = size
        this.buffer = [0 for i in range(size)]
        this.head = 0
        this.tail = -1

    def get(index):
        return buffer[(head + index) % size]

    def add(input):
        tail += 1
        tail %= size
        if tail == head:
            head += 1
            head %= size

    def capacity():
        return ((tail + size - head) % size) + 1

    