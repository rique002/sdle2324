import hashlib

class ConsistentHashing:
    def __init__(self, servers=None):
        self.ring = dict()
        self.servers = servers if servers else []
        self._create_ring()

    def _create_ring(self):
        for server in self.servers:
            self._add_server_to_ring(server)

    def _add_server_to_ring(self, server):
        for v_node in range(100): 
            hash_value = hashlib.md5(f"{server}_{v_node}".encode()).hexdigest()
            self.ring[hash_value] = server

    def add_server(self, server):
        self.servers.append(server)
        self._add_server_to_ring(server)

    def get_server(self, key):
        hash_value = hashlib.md5(key.encode()).hexdigest()
        relevant_keys = [k for k in self.ring.keys() if k > hash_value]
        relevant_key = min(relevant_keys) if relevant_keys else min(self.ring.keys())
        return self.ring[relevant_key]