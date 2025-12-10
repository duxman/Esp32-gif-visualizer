# -*- coding: utf-8 -*-
import time
import logging
import os
import platform
from logging.handlers import RotatingFileHandler
from PIL import Image

# Configurar logger primero
logger = logging.getLogger(__name__)
if not logger.handlers:
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'animation_panel.log')
    # RotatingFileHandler: máximo 25MB por archivo, mantener 5 backups
    handler = RotatingFileHandler(log_file, maxBytes=25*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Solo importar librerías de hardware si no estamos en Windows
if platform.system() != 'Windows':
    try:
        import neopixel # type: ignore
        import board # type: ignore
        HARDWARE_AVAILABLE = True
    except ImportError:
        HARDWARE_AVAILABLE = False
        logger.warning("Librerías de hardware no disponibles")
else:
    HARDWARE_AVAILABLE = False
    neopixel = None
    board = None
    logger.info("Ejecutando en Windows - modo simulación activado")

# See https://learn.adafruit.com/neopixels-on-raspberry-pi/software
#sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
#sudo python3 -m pip install --force-reinstall adafruit-blinka
from Animation import Animation
from Panel import Panel


class AnimationServer():
    """
    AnimationServer class for controlling and animating LED panels.
    This class manages LED strip animations using NeoPixel hardware or simulation mode.
    It handles initialization of the LED hardware, color conversion between different formats,
    and playback of animations either on physical hardware or in test mode.
        velocidad (float): Animation playback speed in seconds. Default is 0.075.
        panel (Panel): Reference to the Panel object containing LED configuration and matrix mapping.
        LedPin (int): GPIO pin number connected to the LED pixels (must support PWM). Default is 18.
        LedFreqHz (int): LED signal frequency in hertz. Default is 800000 (800kHz).
        LedDma (int): DMA channel for signal generation. Default is 5.
        LedBrigh (int): LED brightness level (0-255). Default is 255.
        LedInvert (bool): Whether to invert the signal for NPN transistor level shift. Default is False.
    Methods:
        __init__(panel, velocidad): Initialize the AnimationServer with panel and speed configuration.
        allonecolour(strip, colour): Fill the entire LED strip with a single color.
        colour(r, g, b): Convert RGB values to GRB format for NeoPixel compatibility.
        colourrgb(r, g, b): Convert RGB to GRB array format.
        colourTuple(rgbTuple): Convert RGB tuple to integer color value.
        colourTupleRGB(rgbTuple): Return RGB tuple as-is.
        startAnimation(animation, panel): Play animation on physical LED hardware.
        startAnimationTest(animation, panel): Display animation in graphical windows for testing.
        - Automatically detects hardware availability and falls back to simulation mode if needed.
        - Supports both hardware playback and visual testing without physical LEDs.
        - Uses GRB color ordering for NeoPixel LED strips.
        - Handles graceful shutdown on KeyboardInterrupt and SystemExit.
        >>> panel = Panel(width=16, height=16)
        >>> server = AnimationServer(panel, velocidad=0.1)
        >>> animation = Animation.load("animation.gif")
        >>> server.startAnimation(animation, panel)"""

    # Class constants
    LedPin = 18  # GPIO pin connected to the pixels (must support PWM!).
    LedFreqHz = 800000  # LED signal frequency in hertz (usually 800khz)
    LedDma = 5  # DMA channel to use for generating signal (try 5)
    LedBrigh = 255  # Set to 0 for darkest and 255 for brightest
    LedInvert = False  # True to invert the signal (when using NPN transistor level shift)

    def __init__(self, panel, velocidad):
        # type: (Panel, float) -> None
        """
        Initialize the AnimationServer with a panel and animation speed.
        Args:
            panel (Panel): The LED panel object containing configuration and total LED count.
            velocidad (float): The speed/velocity at which animations should run.
        Attributes:
            velocidad (float): Stores the animation speed.
            panel (Panel): Reference to the LED panel object.
            LedStrip (neopixel.NeoPixel or None): NeoPixel LED strip controller instance if hardware
                is available, None otherwise.
        Notes:
            - If HARDWARE_AVAILABLE is True, initializes the NeoPixel LED strip on GPIO pin D18
              with GRB color order and auto_write disabled.
            - If hardware is not available, runs in simulation mode with LedStrip set to None.
            - Logs initialization status to the logger.
        """

        self.velocidad=velocidad
        self.panel = panel
        
        # Solo inicializar hardware si está disponible
        if HARDWARE_AVAILABLE:
            self.LedStrip = neopixel.NeoPixel(board.D18, panel.total_leds,auto_write=False)  # type: ignore
            ORDER = neopixel.GRB # type: ignore
            logger.info("inicilizamos ledstrip {0}".format(panel.total_leds))
        else:
            self.LedStrip = None
            logger.info("Modo simulación - hardware no disponible")
        
        #self.LedStrip = neopixel.NeoPixel(self.LedPin, panel.total_leds, auto_write=False)
        #self.LedStrip = neopixel.NeoPixel(board.D18, panel.total_leds)

    def allonecolour(self, strip, colour):
        """
        Paint the entire LED strip with a single color.

        Args:
            strip: The LED strip object to be painted. Must support fill() and show() methods.
            colour: The color to apply to the entire strip. Should be in a format compatible with the strip's fill() method (e.g., RGB tuple or hex value).

        Returns:
            None

        Example:
            allonecolour(strip, (255, 0, 0))  # Fills the strip with red color
        """
        # Paint the entire matrix one colour
        strip.fill(colour)
        strip.show()
    
    def testPanels(self, panel: Panel):
        """
        Prueba cada panel individualmente encendiendolo con un color distinto.
        Panel 0: Rojo, Panel 1: Verde, Panel 2: Azul, Panel 3: Amarillo
        """
        if not HARDWARE_AVAILABLE or self.LedStrip is None:
            logger.warning("Hardware no disponible")
            return
        
        colores = [
            (255, 0, 0),    # Panel 0: Rojo
            (0, 255, 0),    # Panel 1: Verde
            (0, 0, 255),    # Panel 2: Azul
            (255, 255, 0)   # Panel 3: Amarillo
        ]
        
        try:
            logger.info("=== Test de paneles individuales === {0} paneles".format(panel.paneles_vertical * panel.paneles_horizontal))            
            for panel_num in range( panel.paneles_vertical * panel.paneles_horizontal):
                # Apagar todos los LEDs
                self.LedStrip.fill((0, 0, 0))
                
                # Encender solo el panel actual
                led_inicio = panel_num * panel.total_leds_panel
                led_fin = (panel_num + 1) * panel.total_leds_panel
                
                color = colores[panel_num]
                logger.info("Encendiendo Panel {0} ({1} color) - LEDs {2} a {3}".format(
                    panel_num, ["Rojo", "Verde", "Azul", "Amarillo"][panel_num], led_inicio, led_fin-1))
                
                for led_id in range(led_inicio, led_fin):
                    self.LedStrip[led_id] = self.colourTuple(color)
                
                self.LedStrip.show()
                time.sleep(2)  # Mantener encendido 2 segundos
            
            # Apagar todo al final
            self.LedStrip.fill((0, 0, 0))
            self.LedStrip.show()
            logger.info("=== Test completado ===")
            
        except (KeyboardInterrupt, SystemExit):
            logger.info("Test interrumpido")

    def colour(self, r, g, b):
        """
        Convert RGB color values to GRB format for Neopixel compatibility.

        This method takes RGB color values and converts them to the GRB format required
        by Neopixel LEDs. It uses British spelling ('colour') as the method name.

        Args:
            r (int): Red color component (0-255)
            g (int): Green color component (0-255)
            b (int): Blue color component (0-255)

        Returns:
            The return value of colourTuple() with the color values reordered as [g, r, b]
        """
        # Fix for Neopixel RGB->GRB, also British spelling
        return self.colourTuple([g, r, b])

    def colourrgb(self, r, g, b):
        """
        Convert RGB color values to GRB format for NeoPixel LEDs.

        This method handles the color channel reordering required by NeoPixel LEDs,
        which use GRB (Green-Red-Blue) format instead of the standard RGB format.

        Args:
            r (int): Red color value (0-255)
            g (int): Green color value (0-255)
            b (int): Blue color value (0-255)

        Returns:
            list: A list containing color values in GRB order [green, red, blue]

        Example:
            >>> colourrgb(255, 0, 0)  # Red in RGB
            [0, 255, 0]  # Converts to GRB format
        """
        # Fix for Neopixel RGB->GRB, also British spelling
        return [g, r, b]

    def colourTuple(self, rgbTuple):
        """
        Convert an RGB tuple to a single integer representation.

        This method takes an RGB tuple and converts it to a single integer value
        by rearranging the color components and bit-shifting them into a combined
        integer format.

        Args:
            rgbTuple (tuple): A tuple containing three integer values representing
                              RGB color components in the order (G, R, B).
                              Each component should be in the range 0-255.

        Returns:
            int: An integer representation of the color where green is in the
                 most significant byte, red in the middle byte, and blue in the
                 least significant byte (GRB format).

        Note:
            The input tuple is expected in (G, R, B) order, which is then
            rearranged to create a GRB integer format.
        """
        red = rgbTuple[1]
        green = rgbTuple[0]
        blue = rgbTuple[2]
        RGBint = (green << 16) + (red << 8) + blue
        return RGBint

    def colourTupleRGB(self, rgbTuple):
        """
        Convert an RGB tuple to a tuple of RGB values.
        Args:
            rgbTuple (tuple): A tuple containing three elements representing RGB values (red, green, blue).
        Returns:
            tuple: A tuple containing the red, green, and blue values in the format (red, green, blue).
        Example:
            >>> colourTupleRGB((255, 128, 0))
            (255, 128, 0)
        """
        red = rgbTuple[0]
        green = rgbTuple[1]
        blue = rgbTuple[2]

        return ( red,green, blue)

    def startAnimation(self, animation: Animation, panel: Panel):
        """
        Start playing an animation on the LED strip hardware.
        This method iterates through all frames of the provided animation and displays
        them on the LED strip connected to the specified panel. Each frame is displayed
        for its configured duration.
        Args:
            animation (Animation): The animation object containing frames and frame durations
                                  to be displayed on the LED strip.
            panel (Panel): The panel object containing the LED matrix mapping used to 
                          translate frame pixel positions to physical LED positions.
        Returns:
            None
        Raises:
            KeyboardInterrupt: When the user interrupts the animation playback.
            SystemExit: When the system requests termination of the animation.
        Notes:
            - If hardware is not available or LedStrip is None, a warning is logged and
              the method returns early.
            - Frame duration is taken from animation.frame_durations (in milliseconds) or
              defaults to self.velocidad if not specified.
            - The LED strip is cleared (filled with black) before rendering each frame.
            - Only non-zero color pixels are written to the LED strip.
        """
        # And here we go.

        if not HARDWARE_AVAILABLE or self.LedStrip is None:
            logger.warning("Hardware no disponible, usa startAnimationTest() en su lugar")
            return

        try:
            logger.info("Iniciamos reproduccion con {0} frames".format(len(animation.frames)))
            logger.info("Velocidad reproduccion {0}".format(self.velocidad))
            logger.info("Frame size: {0}x{1}, Panel size: {2}x{3}".format(
                animation.frames[0].width if animation.frames else 0,
                animation.frames[0].height if animation.frames else 0,
                panel.ancho_total, panel.altura_total))
            
            # Iterar a través de todos los frames
            for frame_index, frame in enumerate(animation.frames):
                # Obtener la duración del frame (en segundos)
                frame_duration = animation.frame_durations[frame_index] / 1000.0 if frame_index < len(animation.frame_durations) else self.velocidad
                
                # Limpiar el strip
                self.LedStrip.fill((0, 0, 0))
                
                # Contador de LEDs encendidos por panel
                leds_por_panel = [0, 0, 0, 0]
                
                # Iterar por cada pixel del frame usando coordenadas x,y
                for y in range(frame.height):
                    for x in range(frame.width):
                        # Calcular el indice en la matriz del panel
                        matrix_index = y * panel.ancho_total + x
                        
                        # Verificar que el indice este dentro del rango
                        if matrix_index < len(panel.matriz):
                            # Obtener el color del pixel en el frame
                            pixel_color = frame.getpixel((x, y))
                            
                            # Solo pintar si el color no es negro (0,0,0)
                            if self.colourTuple(pixel_color) != 0:
                                led_id = panel.matriz[matrix_index]
                                self.LedStrip[led_id] = self.colourTuple(pixel_color)
                                
                                # Contar LEDs por panel
                                panel_num = led_id // panel.total_leds_panel
                                if panel_num < len(leds_por_panel):
                                    leds_por_panel[panel_num] += 1

                self.LedStrip.show()
                
                # Log de LEDs encendidos por panel en el primer frame
                if frame_index == 0:
                    logger.info("Frame 0 - LEDs encendidos por panel: P0={0}, P1={1}, P2={2}, P3={3}".format(
                        leds_por_panel[0], leds_por_panel[1], leds_por_panel[2], leds_por_panel[3]))
                
                time.sleep(frame_duration)

        except (KeyboardInterrupt, SystemExit):
            logger.info("Stopped")

    def startAnimationTest(self, animation: Animation, panel: Panel):
        """
        Función de prueba para visualizar una animación en ventanas gráficas en lugar de LEDs.
        Esta función itera a través de todos los frames de una animación y los muestra
        en ventanas separadas, escalados para mejor visualización. Es útil para
        depuración y pruebas sin necesidad de hardware LED físico.
        Args:
            animation (Animation): Objeto Animation que contiene los frames a mostrar
                                  y sus duraciones asociadas.
            panel (Panel): Objeto Panel (no utilizado en el modo test, pero mantenido
                          por compatibilidad con la interfaz).
        Returns:
            None
        Raises:
            KeyboardInterrupt: Capturado cuando el usuario interrumpe la ejecución.
            SystemExit: Capturado cuando se solicita la salida del sistema.
        Notes:
            - Cada frame se escala 10x usando interpolación NEAREST para mantener
              la apariencia pixelada.
            - Las duraciones de los frames se leen desde animation.frame_durations
              (en milisegundos) y se convierten a segundos.
            - Si no hay duración especificada para un frame, se usa self.velocidad
              como valor por defecto.
            - Los frames se muestran en ventanas emergentes secuenciales.
            - La función registra información de progreso mediante logger.
        """
        """Función de prueba que muestra los frames en una ventana gráfica en lugar de en LEDs"""
        
        try:
            logger.info("Modo TEST: Mostrando {0} frames en ventana".format(len(animation.frames)))
            logger.info("Velocidad reproduccion {0}".format(self.velocidad))
            
            # Iterar a través de todos los frames
            for frame_index, frame in enumerate(animation.frames):
                # Obtener la duración del frame (en segundos)
                frame_duration = animation.frame_durations[frame_index] / 1000.0 if frame_index < len(animation.frame_durations) else self.velocidad
                
                # Escalar el frame para mejor visualización (multiplicar por 10)
                display_frame = frame.resize((frame.width * 10, frame.height * 10), Image.Resampling.NEAREST) 
                
                # Mostrar el frame
                display_frame.show(title="Frame {0}/{1}".format(frame_index + 1, len(animation.frames)))
                
                logger.info("Mostrando frame {0}/{1}".format(frame_index + 1, len(animation.frames)))
                
                # Simular el tiempo de espera
                time.sleep(frame_duration)
            
            logger.info("Test completado")

        except (KeyboardInterrupt, SystemExit):
            logger.info("Stopped")