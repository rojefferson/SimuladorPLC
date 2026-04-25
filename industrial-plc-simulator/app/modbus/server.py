import threading
import logging
from pymodbus.server import StartTcpServer
from app.modbus.register_store import PLCDataStore

logging.basicConfig()
log = logging.getLogger(__name__)

class ModbusServer:
    def __init__(self, data_store: PLCDataStore, host: str = "127.0.0.1", port: int = 5020):
        self.data_store = data_store
        self.host = host
        self.port = port
        self.server_thread = None
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

    def _run_server(self):
        try:
            print(f"Starting Modbus TCP Server on {self.host}:{self.port}...")
            StartTcpServer(
                context=self.data_store.context,
                address=(self.host, self.port)
            )
        except Exception as e:
            print(f"Modbus Server Error: {e}")
            self.running = False

    def stop(self):
        # PyModbus doesn't have a very clean 'stop' for the sync server 
        # but since it's a daemon thread it will die with the app.
        # For a more robust implementation, one would use the async server.
        self.running = False
