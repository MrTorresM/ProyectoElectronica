# ===========================================================
# runInterface.py
# Sistema de transmisión de datos desde ESP32 (Serial) hacia
# la interfaz HTML mediante WebSocket.
# ===========================================================

import subprocess
import webbrowser
import os
import time
import threading
import http.server
import socketserver
import signal
import sys
import asyncio
import json
import serial
import serial.tools.list_ports
import websockets

# ---------- Configuración General ----------
HTTP_PORT = 8000
WS_PORT = 8765  # Puerto WebSocket (para interfaz)
BAUD_RATE = 115200

# Rutas base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTERFACE_DIR = os.path.join(BASE_DIR, "GUI")
HTML_PATH = "HTML/index.html"

httpd = None
ws_clients = set()
stop_event = threading.Event()

# ===========================================================
# === SERVIDOR HTTP PARA LA INTERFAZ WEB ====================
# ===========================================================

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/cerrar":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"[Sistema] Servidor cerrado correctamente.")
            print("[Sistema] Solicitud de cierre recibida. Apagando servidor...")
            threading.Thread(target=detener_servidor).start()
        else:
            super().do_GET()

class CustomTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def iniciar_http_server():
    global httpd
    os.chdir(INTERFACE_DIR)
    handler = CustomHandler
    httpd = CustomTCPServer(("", HTTP_PORT), handler)
    print(f"[Sistema] Servidor HTTP corriendo en http://localhost:{HTTP_PORT} ...")
    httpd.serve_forever()

def detener_servidor():
    global httpd
    if httpd:
        httpd.shutdown()
        print("[Sistema] Servidor detenido.")
    stop_event.set()

def abrir_interfaz():
    time.sleep(2)
    url = f"http://localhost:{HTTP_PORT}/{HTML_PATH}"
    print(f"[Sistema] Abriendo interfaz en navegador: {url}")
    webbrowser.open(url)

# ===========================================================
# === DETECCIÓN Y LECTURA SERIAL DE ESP32 ===================
# ===========================================================

def detectar_puerto_esp32():
    print("[Sistema] Buscando puerto ESP32...")
    puertos = serial.tools.list_ports.comports()
    for p in puertos:
        if "USB" in p.device or "COM" in p.device or "tty" in p.device:
            print(f"[Sistema] ESP32 detectado en: {p.device}")
            return p.device
    print("[Sistema] No se detectó ESP32 automáticamente. Configura el puerto manualmente.")
    return None

# ===========================================================
# === SERVIDOR WEBSOCKET ====================================
# ===========================================================

async def websocket_handler(websocket, path):
    ws_clients.add(websocket)
    print(f"[WebSocket] Cliente conectado ({len(ws_clients)} total)")
    try:
        async for _ in websocket:
            pass  # No se reciben mensajes desde el cliente
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        ws_clients.remove(websocket)
        print("[WebSocket] Cliente desconectado")

async def enviar_datos_serial(serial_port):
    while not stop_event.is_set():
        try:
            if serial_port.in_waiting > 0:
                linea = serial_port.readline().decode("utf-8").strip()
                if not linea:
                    continue
                try:
                    data = json.loads(linea)
                except json.JSONDecodeError:
                    continue  # ignora líneas no válidas

                if ws_clients:
                    mensaje = json.dumps(data)
                    await asyncio.gather(*[c.send(mensaje) for c in ws_clients])
        except Exception as e:
            print(f"[Error Serial] {e}")
            await asyncio.sleep(1)
        await asyncio.sleep(0.05)

async def main_websocket():
    puerto_esp = detectar_puerto_esp32()
    if not puerto_esp:
        print("[Sistema] No se pudo abrir el puerto serial.")
        return

    try:
        ser = serial.Serial(puerto_esp, BAUD_RATE, timeout=1)
        print(f"[Sistema] Lectura Serial iniciada en {puerto_esp} ({BAUD_RATE} bps)")
    except serial.SerialException as e:
        print(f"[Sistema] Error abriendo puerto serial: {e}")
        return

    async with websockets.serve(websocket_handler, "localhost", WS_PORT):
        print(f"[Sistema] Servidor WebSocket corriendo en ws://localhost:{WS_PORT}")
        await enviar_datos_serial(ser)

# ===========================================================
# === EJECUCIÓN PRINCIPAL ===================================
# ===========================================================

if __name__ == "__main__":
    print("[Sistema] Iniciando servidor HTTP + WebSocket + Serial...\n")

    servidor_thread = threading.Thread(target=iniciar_http_server, daemon=True)
    servidor_thread.start()
    abrir_interfaz()

    # Ejecutar bucle principal WebSocket/Serial
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_websocket())
    except KeyboardInterrupt:
        print("\n[Sistema] Interrupción manual detectada. Cerrando...")
        detener_servidor()
        sys.exit(0)
