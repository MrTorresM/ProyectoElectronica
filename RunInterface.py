# ===========================================================
# runInterface.py
# Sistema de transmisión de datos desde ESP32 (Serial) hacia
# la interfaz HTML mediante WebSocket.
# -----------------------------------------------------------
# Autor:  Equipo de desarrollo (Gabriela Rodríguez, Miguel Roa)
# Colaboración técnica: Asistente Virtual de Manuel
# Fecha:  2025
# Descripción:
#   Este script lanza un servidor HTTP para mostrar la interfaz
#   HTML del interferómetro y un servidor WebSocket para enviar
#   los datos provenientes del ESP32. Incluye detección automática
#   del puerto serial, manejo de reconexión, y control seguro de cierre.
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

# ===========================================================
# === CONFIGURACIÓN GENERAL =================================
# ===========================================================

HTTP_PORT = 8000           # Puerto para la interfaz HTML
WS_PORT = 8765             # Puerto para el WebSocket
BAUD_RATE = 115200         # Velocidad de comunicación serial

# --- Rutas base ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTERFACE_DIR = os.path.join(BASE_DIR, "GUI")
HTML_PATH = "HTML/index.html"

# --- Variables globales ---
httpd = None
ws_clients = set()
stop_event = threading.Event()

# ===========================================================
# === SERVIDOR HTTP PARA LA INTERFAZ WEB ====================
# ===========================================================

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """Maneja solicitudes HTTP y permite cerrar el servidor desde la interfaz."""
    def do_GET(self):
        if self.path == "/cerrar":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"[Sistema] Servidor cerrado correctamente.")
            print("\n[HTTP] Solicitud de cierre recibida. Apagando servidor...")
            threading.Thread(target=detener_servidor).start()
        else:
            super().do_GET()


class CustomTCPServer(socketserver.TCPServer):
    """Servidor TCP personalizado con reutilización de dirección."""
    allow_reuse_address = True


def iniciar_http_server():
    """Inicia el servidor HTTP para servir la interfaz HTML."""
    global httpd
    os.chdir(INTERFACE_DIR)
    handler = CustomHandler
    httpd = CustomTCPServer(("", HTTP_PORT), handler)
    print(f"[HTTP] Servidor corriendo en: http://localhost:{HTTP_PORT}")
    httpd.serve_forever()


def detener_servidor():
    """Detiene de forma segura el servidor HTTP."""
    global httpd
    if httpd:
        httpd.shutdown()
        print("[HTTP] Servidor HTTP detenido correctamente.")
    stop_event.set()


def abrir_interfaz():
    """Abre la interfaz HTML en el navegador predeterminado."""
    time.sleep(2)
    url = f"http://localhost:{HTTP_PORT}/{HTML_PATH}"
    print(f"[Sistema] Abriendo interfaz en navegador: {url}")
    webbrowser.open(url)

# ===========================================================
# === DETECCIÓN Y LECTURA SERIAL DE ESP32 ===================
# ===========================================================

def detectar_puerto_esp32():
    """Detecta automáticamente el puerto donde está conectado el ESP32."""
    print("[Serial] Buscando puerto ESP32...")
    puertos = serial.tools.list_ports.comports()
    for p in puertos:
        if "USB" in p.device or "COM" in p.device or "tty" in p.device:
            print(f"[Serial] ESP32 detectado en: {p.device}")
            return p.device
    print("[Serial] No se detectó ESP32 automáticamente. Conéctalo y reinicia.")
    return None


def reconectar_serial():
    """Intenta reconectar el ESP32 cada cierto tiempo."""
    while not stop_event.is_set():
        puerto = detectar_puerto_esp32()
        if puerto:
            try:
                ser = serial.Serial(puerto, BAUD_RATE, timeout=1)
                print(f"[Serial] Reconectado exitosamente en {puerto}")
                return ser
            except serial.SerialException:
                pass
        print("[Serial] Intentando reconectar en 3 segundos...")
        time.sleep(3)
    return None

# ===========================================================
# === SERVIDOR WEBSOCKET ====================================
# ===========================================================

async def websocket_handler(websocket, path):
    """Gestiona las conexiones WebSocket desde la interfaz web."""
    ws_clients.add(websocket)
    print(f"[WebSocket] Cliente conectado ({len(ws_clients)} total)")
    try:
        async for _ in websocket:
            pass  # No se reciben mensajes desde la interfaz
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        ws_clients.remove(websocket)
        print("[WebSocket] Cliente desconectado")


async def enviar_datos_serial(serial_port):
    """Lee datos del puerto serial y los envía a todos los clientes WebSocket."""
    while not stop_event.is_set():
        try:
            if serial_port.in_waiting > 0:
                linea = serial_port.readline().decode("utf-8").strip()
                if not linea:
                    continue

                try:
                    data = json.loads(linea)
                except json.JSONDecodeError:
                    print(f"[Serial] Línea no válida: {linea}")
                    continue

                if ws_clients:
                    mensaje = json.dumps(data)
                    await asyncio.gather(*[c.send(mensaje) for c in ws_clients])

        except serial.SerialException:
            print("[Error] Conexión serial perdida. Intentando reconexión...")
            serial_port = reconectar_serial()
            if not serial_port:
                print("[Error] No se pudo reconectar el puerto serial.")
                break
        except Exception as e:
            print(f"[Error General] {e}")
            await asyncio.sleep(1)

        await asyncio.sleep(0.05)


async def main_websocket():
    """Inicia el servidor WebSocket y la lectura del puerto serial."""
    puerto_esp = detectar_puerto_esp32()
    if not puerto_esp:
        print("[Sistema] No se pudo abrir el puerto serial.")
        return

    try:
        ser = serial.Serial(puerto_esp, BAUD_RATE, timeout=1)
        print(f"[Serial] Lectura iniciada en {puerto_esp} ({BAUD_RATE} bps)")
    except serial.SerialException as e:
        print(f"[Error Serial] No se pudo abrir el puerto: {e}")
        return

    async with websockets.serve(websocket_handler, "localhost", WS_PORT):
        print(f"[WebSocket] Servidor activo en ws://localhost:{WS_PORT}")
        await enviar_datos_serial(ser)

# ===========================================================
# === EJECUCIÓN PRINCIPAL ===================================
# ===========================================================

if __name__ == "__main__":
    print("===========================================================")
    print("  Sistema de Automatización del Interferómetro de Michelson")
    print("===========================================================\n")
    print("[Sistema] Iniciando servidores HTTP + WebSocket + Serial...\n")

    servidor_thread = threading.Thread(target=iniciar_http_server, daemon=True)
    servidor_thread.start()

    abrir_interfaz()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_websocket())
    except KeyboardInterrupt:
        print("\n[Sistema] Interrupción manual detectada. Cerrando...")
        detener_servidor()
        sys.exit(0)
    except Exception as e:
        print(f"[Sistema] Error inesperado: {e}")
        detener_servidor()
        sys.exit(1)
