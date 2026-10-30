import asyncio
import math
import random
import os
from asyncua import Client

class MockReader:
    def __init__(self, machine):
        self.machine = machine
        self.n = 0
    async def read(self):
        self.n += 1
        values = {}
        for key, setting in self.machine['_variables'].items():
            if setting.get('mock_type') == 'bool':
                values[key] = self.n % 12 != 0
            elif key == 'cycle_count':
                values[key] = self.n // 6
            else:
                lo, hi = float(setting.get('mock_min', 0)), float(setting.get('mock_max', 100))
                values[key] = round((lo + hi) / 2 + (hi-lo) * .25 * math.sin(self.n / 8) + random.uniform(-1, 1), 3)
        await asyncio.sleep(0)
        return values

class OPCUAReader:
    def __init__(self, machine):
        self.machine = machine
        self.client = None
    async def connect(self):
        self.client = Client(self.machine['endpoint'], timeout=10)
        await self.client.set_security_string(self.machine['security'])
        user = self.machine.get('username_env')
        password = self.machine.get('password_env')
        if user:
            self.client.set_user(os.environ[user])
        if password:
            self.client.set_password(os.environ[password])
        await self.client.connect()
    async def close(self):
        if self.client:
            try:
                await self.client.disconnect()
            finally:
                self.client = None
    async def read(self):
        if self.client is None:
            await self.connect()
        result = {}
        try:
            for key, cfg in self.machine['_variables'].items():
                value = await self.client.get_node(cfg['node_id']).read_value()
                if isinstance(value, (int, float, str, bool)) or value is None:
                    result[key] = value
                else:
                    # No silent coercion of complex/unknown data structures.
                    raise TypeError(f'{key} unsupported OPC UA value type: {type(value).__name__}')
            return result
        except Exception:
            await self.close()
            raise
