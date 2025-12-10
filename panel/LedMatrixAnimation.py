# -*- coding: utf-8 -*-
# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys
import logging
import os
from logging.handlers import RotatingFileHandler

from Animation import Animation
from AnimationServer import AnimationServer
from Config import Config
from Panel import Panel
import glob

# Configurar logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'animation_panel.log')
    # RotatingFileHandler: máximo 25MB por archivo, mantener 5 backups
    handler = RotatingFileHandler(log_file, maxBytes=25*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)



class MainClass():

    def __init__(self, config):
        # type: (Config) -> None
        """
        Initialize the LedMatrixAnimation with the provided configuration.

        Args:
            config (Config): Configuration object containing the following attributes:
                - ancho: Width of the LED matrix panel
                - alto: Height of the LED matrix panel
                - primer_led: Position of the first LED
                - panel_ver: Vertical panel configuration
                - panel_hor: Horizontal panel configuration
                - velocidad: Animation speed/velocity

        Attributes:
            config (Config): Stored configuration object
            panel (Panel): Panel instance created with configuration parameters
            animation_server (AnimationServer): Server for managing animations
            panel_matriz: Calculated matrix representation of the panel

        Note:
            This method also calls buscarFicheros() to search for animation files
            during initialization.
        """
        self.config = config
        self.panel = Panel(config.ancho, config.alto, config.primer_led, config.panel_ver, config.panel_hor, config.posicion_vertical)
        logger.info("Panel initialized")
        self.animation_server = AnimationServer(self.panel, self.config.velocidad)
        logger.info("Animation server initialized")
        self.panel_matriz = self.panel.calculateMatrix()
        logger.info("Panel matrix calculated")        
        self.ficheros = []
        logger.info("Searching for files...")
        self.buscarFicheros()
        logger.info("File search completed.")
    

    def buscarFicheros(self):
        """
        Search for image files in the configured directory.

        This method scans the directory specified in self.config.directorio for PNG and GIF files,
        storing the full paths of all matching files in the self.ficheros attribute.

        The method performs two searches:
        1. Searches for all PNG files (*.png)
        2. Searches for all GIF files (*.gif) and extends the existing list

        Returns:
            None: The results are stored in self.ficheros instance attribute.

        Side Effects:
            Modifies self.ficheros by replacing it with a new list containing all found PNG files,
            then extending it with all found GIF files.
        """
        self.ficheros = glob.glob(self.config.directorio + "/*.png")
        logger.info("Found PNG files: {0}".format(self.ficheros))
        self.ficheros.extend(glob.glob(self.config.directorio + "/*.gif"))
        logger.info("Found GIF files: {0}".format(self.ficheros))

    def start(self):
        """
        Starts the LED matrix animation loop.

        This method continuously cycles through all image files in the configured directory,
        creating animations from each image and displaying them on the LED matrix panel.
        For each image, the animation is repeated based on the configured number of repetitions.

        The method runs indefinitely until interrupted by KeyboardInterrupt or SystemExit.

        Behavior:
            - Iterates through all files in self.ficheros
            - Creates an Animation object for each file with dimensions based on panel configuration
            - Repeats each animation according to self.config.repeticiones
            - Uses test mode (startAnimationTest) if debug mode is enabled, otherwise uses normal mode
            - Logs each step of the process

        Raises:
            KeyboardInterrupt: Caught and logged when user interrupts execution
            SystemExit: Caught and logged when system exit is requested

        Notes:
            - This method blocks execution and runs in an infinite loop
            - Animation dimensions are calculated as: height = alto * panel_ver, width = ancho * panel_hor
            - Debug mode (config.debug == 1) uses startAnimationTest instead of startAnimation
        """
        try:
            logger.info("Starting animation loop...")
            
            # Test de paneles individuales (solo en modo no-DEBUG)
            if self.config.debug == 0:
                logger.info("Ejecutando test de paneles...")
                self.animation_server.testPanels(self.panel)
            
            while(1):
                for imagen in self.ficheros:
                    logger.info("preparamos imagen {0}".format(imagen))
                    animation = Animation(imagen, self.panel.altura_total,self.panel.ancho_total,self.config.velocidad)
                    logger.info("Animation created for image {0}".format(imagen))
                    # Usar repeticiones_gif para GIFs, repeticiones para imagenes estaticas
                    repeticiones = self.config.repeticiones_gif if animation.is_animated else self.config.repeticiones
                    logger.info("Repetitions for this animation: {0}".format(repeticiones))
                    for i in range(repeticiones):
                        logger.info("Animation created for image {0}".format(imagen))
                        if self.config.debug == 1:
                            logger.info("Modo DEBUG activado - usando startAnimationTest")
                            self.animation_server.startAnimationTest(animation, self.panel)
                        else:
                            logger.info("Iniciando animación {0}, repetición {1}/{2}".format(imagen, i+1, repeticiones))
                            self.animation_server.startAnimation(animation, self.panel)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Stopped")

def main():
    """
    Entry point for the LED Matrix Animation application.

    This function initializes the application by:
    1. Loading configuration from 'configuracion.json'
    2. Creating a MainClass instance with the loaded configuration
    3. Starting the main application loop

    The function serves as the primary entry point and orchestrates the startup
    sequence of the LED Matrix Animation system.

    Raises:
        FileNotFoundError: If 'configuracion.json' is not found
        JSONDecodeError: If the configuration file is not valid JSON
        Exception: Any exceptions raised during MainClass initialization or startup
    """
    config = Config("configuracion.json")
    logger.info("config loaded")
    main = MainClass(config)
    logger.info("main initialized")
    main.start()

if __name__ == '__main__':
    main()





