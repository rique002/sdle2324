import hashlib

class ConsistentHashing:
    def __init__(self, servers):
        self.ring = dict()
        self.servers = servers
        self._create_ring()

    def _create_ring(self):
        for server in self.servers:
            for v_node in range(100):  # Assuming 100 virtual nodes per server
                hash_value = hashlib.md5(f"{server}_{v_node}".encode()).hexdigest()
                self.ring[hash_value] = server

    def get_server(self, key):
        hash_value = hashlib.md5(key.encode()).hexdigest()
        # Find the server with the next highest hash value
        relevant_keys = [k for k in self.ring.keys() if k > hash_value]
        relevant_key = min(relevant_keys) if relevant_keys else min(self.ring.keys())
        return self.ring[relevant_key]