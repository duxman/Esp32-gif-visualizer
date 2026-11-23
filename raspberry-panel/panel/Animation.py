# -*- coding: utf-8 -*-
from PIL import Image  # Use apt-get install python-imaging to install this pip install Pillow
from PIL.Image import Image as ImageType
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

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


class Animation():
    """
    A class for handling image animations on LED panels.
    This class supports two types of animations:
    1. Loading and displaying animated GIF files with their original frames and durations
    2. Generating animation frames by horizontally scrolling static images
    Attributes:
        PIXEL_SHIFT (int): Horizontal pixel shift per frame for scroll animations (default: 5)
        FRAME_DURATION (int): Duration of each generated frame in milliseconds (default: 1000)
        imagen_file (str): Path to the image file
        imagen (Optional[ImageType]): The loaded PIL Image object
        imagen_final (Optional[ImageType]): Final processed image (reserved for future use)
        width (int): Width of the display panel in pixels
        height (int): Height of the display panel in pixels
        frames (list[ImageType]): List of animation frames
        is_animated (bool): Flag indicating if the source is an animated GIF
        frame_durations (list[int]): Duration in milliseconds for each frame
    Methods:
        __init__(fichero, alto, ancho): Initialize the Animation object with file path and panel dimensions
        loadFile(): Load the image file and determine if it's animated or static
        loadAnimatedGif(): Extract all frames and durations from an animated GIF
        generateFrames(): Generate animation frames by scrolling through a static image
    Raises:
        Exception: If the image file cannot be loaded or if the image is smaller than panel dimensions
    Example:
        >>> anim = Animation("image.png", height=32, width=64)
        >>> # Access frames via anim.frames
        >>> # Access frame durations via anim.frame_durations
    """

    PIXEL_SHIFT = 5  # Desplazamiento horizontal en píxeles por frame

    def __init__(self, fichero, alto, ancho, velocidad=0.025):
        # type: (str, int, int, float) -> None
        self.imagen_file = fichero
        self.imagen = None
        self.imagen_final = None
        self.width = ancho
        self.height = alto
        self.frames = []
        self.is_animated = False
        self.frame_durations = []
        # Convertir velocidad de segundos a milisegundos para frame_duration
        self.frame_duration = int(velocidad * 1000)
        logger.info("Imagen : {0} wp = {1} hp = {2} velocidad = {3}s".format(
            fichero, self.width, self.height, velocidad))
        self.loadFile()

    def loadFile(self):
        try:
            self.imagen = Image.open(self.imagen_file)  # type: ignore
            logger.info("Imagen : {0} w = {1} h = {2}".format(self.imagen_file, self.imagen.size[0], self.imagen.size[1]))
            
            if(self.imagen_file.lower().endswith('.gif')):
                # Detectar si es un GIF animado
                if hasattr(self.imagen, 'is_animated') and self.imagen.is_animated:  # type: ignore
                    self.is_animated = True
                    self.loadAnimatedGif()
            else:
                self.generateFrames()
        except:
            raise Exception("Image file %s could not be loaded" % self.imagen_file)

    def loadAnimatedGif(self):
        """
        Load all frames from an animated GIF image.
        This method extracts each frame from an animated GIF and stores them along with
        their respective durations. The frames are converted to RGB format to ensure
        compatibility across different display systems.
        The method populates two instance attributes:
            - self.frames: List containing PIL Image objects for each frame
            - self.frame_durations: List containing the duration (in milliseconds) for each frame
        If the image is not loaded (self.imagen is None), the method returns early without
        processing. In case of any error during frame extraction, the animation flag is
        disabled and an error is logged.
        Raises:
            Exception: Any exception during frame loading is caught, logged, and causes
                       self.is_animated to be set to False.
        Notes:
            - Default frame duration is 100ms if not specified in the GIF
            - All frames are converted to RGB mode regardless of original format
            - Requires self.imagen to be a valid PIL Image object with n_frames attribute
        """
        """Carga todos los frames de un GIF animado"""
        try:
            if self.imagen is None:
                return
            frame_count = self.imagen.n_frames  # type: ignore
            logger.info("GIF animado detectado con {0} frames".format(frame_count))
            
            for frame_num in range(frame_count):
                self.imagen.seek(frame_num)  # type: ignore
                # Convertir a RGB para asegurar compatibilidad
                frame = self.imagen.convert('RGB')
                self.frames.append(frame.copy())
                
                # Obtener duración del frame (en milisegundos)
                duration = self.imagen.info.get('duration', 100)  # type: ignore
                self.frame_durations.append(duration)
            
            logger.info("Cargados {0} frames del GIF".format(len(self.frames)))
        except Exception as e:
            logger.error("Error cargando frames del GIF: {0}".format(e))
            self.is_animated = False

    def generateFrames(self):
        """
        Generates animation frames by horizontally shifting the image.
        This method creates a sequence of frames by cropping sections of the loaded image,
        moving horizontally from left to right. Each frame is the size of the panel (width x height)
        and is shifted by PIXEL_SHIFT pixels from the previous frame.
        The method performs the following steps:
        1. Validates that an image is loaded
        2. Verifies the image is large enough (at least panel width x panel height)
        3. Clears any previously generated frames
        4. Iterates through the image horizontally, cropping frames of panel size
        5. Stores each frame and its duration in respective lists
        Raises:
            Exception: If the loaded image is smaller than the panel dimensions
                (width x height pixels).
        Side Effects:
            - Clears and repopulates self.frames list with PIL Image objects
            - Clears and repopulates self.frame_durations list with duration values
            - Logs the number of generated frames and pixel shift value
        Notes:
            - Requires self.imagen to be a valid PIL Image object
            - Frame cropping starts at x=0 and continues until x + width exceeds image width
            - Each frame duration is set to self.FRAME_DURATION
            - The number of frames depends on image width, panel width, and PIXEL_SHIFT value
        """
        """Genera frames de animación desplazando la imagen horizontalmente"""
        
        if self.imagen is None:
            return
            
        # Verificar que la imagen tenga al menos el tamaño del panel
        #if self.imagen.size[0] < self.width or self.imagen.size[1] < self.height:
        #    raise Exception("Image is too small. Must be at least {0}x{1} pixels".format(self.width, self.height))

        # Limpiar frames previos
        self.frames = []
        self.frame_durations = []
        
        # Si el ancho o alto de la imagen es menor que el del panel, usar el de la imagen
        crop_width = min(self.imagen.size[0], self.width)
        crop_height = min(self.imagen.size[1], self.height)
        
        # Generar frames desplazando la imagen horizontalmente usando crop
        x = 0
        while x + crop_width <= self.imagen.size[0]:
            # Recortar frame del tamaño del panel directamente de la imagen original
            frame = self.imagen.crop((x, 0, x + crop_width, crop_height))
            self.frames.append(frame)
            self.frame_durations.append(self.frame_duration)
            x += self.PIXEL_SHIFT
        
        logger.info("Generados {0} frames con desplazamiento de {1} pixeles".format(len(self.frames), self.PIXEL_SHIFT))
        

