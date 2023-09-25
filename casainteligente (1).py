from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import messagebox

accion_previa = None

# --- Command ---

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class CambiarEstadoDispositivo(Command):
    def __init__(self, casa, dispositivo):
        self.casa = casa
        self.dispositivo = dispositivo
        self.estado_anterior = None

    def execute(self):
        self.estado_anterior = self.casa.dispositivos[self.dispositivo]
        self.casa.dispositivos[self.dispositivo] = not self.estado_anterior

    def undo(self):
        self.casa.dispositivos[self.dispositivo] = self.estado_anterior

class EncenderDispositivo(CambiarEstadoDispositivo):
    def execute(self):
        self.estado_anterior = self.casa.dispositivos[self.dispositivo]
        self.casa.dispositivos[self.dispositivo] = True

    def undo(self):
        self.casa.dispositivos[self.dispositivo] = self.estado_anterior

class ApagarDispositivo(CambiarEstadoDispositivo):
    def execute(self):
        self.estado_anterior = self.casa.dispositivos[self.dispositivo]
        self.casa.dispositivos[self.dispositivo] = False

    def undo(self):
        self.casa.dispositivos[self.dispositivo] = self.estado_anterior

class ModoVacaciones(Command):
    def __init__(self, casa):
        self.casa = casa
        self.comandos = [
            EncenderDispositivo(casa, 'Seguros puertas'),
            EncenderDispositivo(casa, 'Estereo'),
            EncenderDispositivo(casa, 'Cámaras'),
            EncenderDispositivo(casa, 'Alarmas'),

             
            
            EncenderDispositivo(casa, 'Luz cuartos'),
            EncenderDispositivo(casa, 'Luz sala'),
            EncenderDispositivo(casa, 'Luz cocina'),
            EncenderDispositivo(casa, 'Luz comedor')
        ]

    def execute(self):
        self.casa.en_modo_vacaciones = True  # Establecer al inicio
        for comando in self.comandos:
            comando.execute()
        self.casa.notificar_observadores("Modo Vacaciones Activado")
        self.casa.notificar_observadores("Sistema de iluminación: Luces en modo aleatorio para simular presencia")
        self.casa.en_modo_vacaciones = False  # Restablecer al final

    def undo(self):
        self.casa.en_modo_vacaciones = True  # Establecer al inicio
        for comando in reversed(self.comandos):
            comando.undo()
        self.casa.notificar_observadores("Modo Vacaciones Desactivado")
        self.casa.en_modo_vacaciones = False  # Restablecer al final


# --- Observer ---

class Observer(ABC):
    @abstractmethod
    def update(self, mensaje: str):
        pass

class DispositivoSeguridad(Observer):
    def update(self, mensaje: str):
        if mensaje == "Modo Vacaciones Activado":
            print("Dispositivo de Seguridad: Activando cámaras y alarmas.")
        elif mensaje == "Modo Vacaciones Desactivado":
            print("Dispositivo de Seguridad: Desactivando cámaras y alarmas.")

class SistemaClimatizacion(Observer):
    def update(self, mensaje: str):
        if mensaje == "Modo Vacaciones Activado":
            print("Sistema de Climatización: Modo ahorro activado.")
        elif mensaje == "Modo Vacaciones Desactivado":
            print("Sistema de Climatización: Restableciendo configuración anterior.")

class SistemaIluminacion(Observer):
    def update(self, mensaje: str):
        if mensaje == "Modo Vacaciones Activado":
            print("Sistema de Iluminación: Luces en modo aleatorio para simular presencia.")
        elif mensaje == "Modo Vacaciones Desactivado":
            print("Sistema de Iluminación: Restableciendo configuración anterior.")



# --- Factory ---

class DispositivoFactory:
    def crear_dispositivo(self, tipo):
        if tipo == "seguridad":
            return DispositivoSeguridad()
        elif tipo == "climatizacion":
            return SistemaClimatizacion()
        elif tipo == "iluminacion":
            return SistemaIluminacion()
        else:
            raise ValueError("Tipo de dispositivo no reconocido")



# --- Decorator ---

class DispositivoDecorator(Observer):
    def __init__(self, dispositivo):
        self._dispositivo = dispositivo

    def update(self, mensaje: str):
        self._dispositivo.update(mensaje)

class DispositivoConSonido(DispositivoDecorator):
    def update(self, mensaje: str):
        super().update(mensaje)
        print("Sonido: Emitiendo sonido correspondiente al mensaje.")



# --- CasaInteligente y Singleton ---

class CasaInteligente:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(CasaInteligente, cls).__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(self):
        if self._inicializado:
            return
        
        self.en_modo_vacaciones = False
        self.acciones = []  # Pila para almacenar acciones realizadas
        self.dispositivos = {
            'Luz cuartos': False,
            'Luz sala': False,
            'Luz cocina': False,
            'Luz comedor': False,
            'Estereo': False,
            'Televisión': False,
            'Alexa': False,
            'Persianas': False,
            'Aire acondicionado': False,
            'Seguros puertas': False,
            'Cámaras': False,
            'Alarmas': False,
            'Modo Vacaciones': False
        }
        self.observadores = []  # Lista para almacenar observadores
        self._inicializado = True

    def ejecutar_accion(self, comando):
        comando.execute()
        self.acciones.append(comando)

    def undo(self):
        if not self.acciones:
            print("No hay acciones para deshacer.")
            return

        comando = self.acciones.pop()
        comando.undo()

    def mostrar_estado(self):
        print("Estado actual de los dispositivos:")
        for dispositivo, estado in self.dispositivos.items():
            estado_str = 'encendido' if estado else 'apagado'
            print(f"{dispositivo}: {estado_str}")

    def registrar_observador(self, observador):
        self.observadores.append(observador)

    def remover_observador(self, observador):
        self.observadores.remove(observador)

    def notificar_observadores(self, mensaje: str):
        for observador in self.observadores:
            observador.update(mensaje)

    def estado_dispositivos(self):
        return self.dispositivos.copy()

    def set_estado_dispositivo(self, dispositivo, estado):
        if dispositivo in self.dispositivos:
            self.dispositivos[dispositivo] = estado

    def toggle_estado_dispositivo(self, dispositivo):
        if dispositivo in self.dispositivos:
            self.dispositivos[dispositivo] = not self.dispositivos[dispositivo]

    def notificar_observadores(self, mensaje):
        # Permitimos los mensajes específicos de Modo Vacaciones sin importar el estado.
        if "Modo Vacaciones" not in mensaje and self.en_modo_vacaciones:
            return
        for observador in self.observadores:
            observador.update(mensaje)

# --- Interfaz Gráfica y lógica principal ---

historial_acciones = []  # Lista para guardar el historial de acciones

def actualizar_estado_dispositivos():
    estados = casa.estado_dispositivos()
    for dispositivo, estado in estados.items():
        estado_str = "ON" if estado else "OFF"
        color = "green" if estado else "red"
        dispositivos_estado_labels[dispositivo].config(text=f"{dispositivo}: {estado_str}", fg=color, font=("Arial", 10, "bold"))
        
def toggle_dispositivo(dispositivo):
    comando = CambiarEstadoDispositivo(casa, dispositivo)
    casa.ejecutar_accion(comando)
    actualizar_estado_dispositivos()

def undo():
    casa.undo()
    messagebox.showinfo("UNDO", "Comando deshecho.")
    actualizar_estado_dispositivos()

def deshacer_accion():
    global casa
    global accion_previa

    if historial_acciones:  # Verificar si hay acciones en el historial
        # Obtener y eliminar la última acción del historial
        ultimo_dispositivo_modificado, estado_anterior = historial_acciones.pop()

        # Restaurar el estado anterior del dispositivo
        casa.set_estado_dispositivo(ultimo_dispositivo_modificado, estado_anterior)

        actualizar_estado_dispositivos()


def toggle_modo_vacaciones():
    """Función para cambiar el estado del modo vacaciones."""
    if "Modo Vacaciones" not in casa.dispositivos:
        casa.dispositivos["Modo Vacaciones"] = False

    if not casa.dispositivos["Modo Vacaciones"]:
        comando = ModoVacaciones(casa)
        casa.ejecutar_accion(comando)
        print("Modo Vacaciones Activado")
        print("Dispositivo de Seguridad: Activando cámaras y alarmas.")
        print("Sonido: Emitiendo sonido correspondiente al mensaje.")
        print("Sistema de Climatización: Modo ahorro activado.")
        print("Sistema de Iluminación: Luces en modo aleatorio para simular presencia.")
    else:
        casa.undo()  # Deshacer el último comando que debería ser el ModoVacaciones.
        print("Modo Vacaciones Desactivado")
        print("Dispositivo de Seguridad: Desactivando cámaras y alarmas.")
        print("Sonido: Emitiendo sonido correspondiente al mensaje.")
        print("Sistema de Climatización: Restableciendo configuración anterior.")      
        print("Sistema de Iluminación: Restableciendo configuración anterior.") 

    casa.dispositivos["Modo Vacaciones"] = not casa.dispositivos["Modo Vacaciones"]
    actualizar_estado_dispositivos()


if __name__ == "__main__":
    casa = CasaInteligente()

    # Factory: Crear dispositivos
    factory = DispositivoFactory()
    dispositivo_seguridad = factory.crear_dispositivo("seguridad")
    dispositivo_climatizacion = factory.crear_dispositivo("climatizacion")
    dispositivo_iluminacion = factory.crear_dispositivo("iluminacion")

    # Decorator: Agregar funcionalidad adicional
    dispositivo_seguridad_con_sonido = DispositivoConSonido(dispositivo_seguridad)

    # Registrar observadores
    casa.registrar_observador(dispositivo_seguridad_con_sonido)
    casa.registrar_observador(dispositivo_climatizacion)
    casa.registrar_observador(dispositivo_iluminacion)

    ventana = tk.Tk()
    ventana.title("Control de Casa Inteligente")

    boton_undo = tk.Button(ventana, text="Deshacer Última Acción", command=undo)
    boton_undo.pack()

    # Aquí incorporamos la creación de los botones y etiquetas para mostrar el estado de los dispositivos
    dispositivos_frame = tk.Frame(ventana)
    dispositivos_frame.pack(pady=20)

    dispositivos_estado_labels = {}
    for dispositivo in casa.dispositivos:
        label = tk.Label(dispositivos_frame, text=f"{dispositivo}: ---")
        label.pack(anchor="w")
        boton = tk.Button(dispositivos_frame, text=f"{dispositivo}", command=lambda disp=dispositivo: toggle_dispositivo(disp))
        boton.pack(anchor="w", pady=5)
        dispositivos_estado_labels[dispositivo] = label

    boton_modo_vacaciones = tk.Button(ventana, text="Modo Vacaciones", command=toggle_modo_vacaciones)
    boton_modo_vacaciones.pack(pady=10)

    actualizar_estado_dispositivos()

    ventana.mainloop()