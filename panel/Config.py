# -*- coding: utf-8 -*-
import json


class Config:

    def __init__(self, jsonfile):
        # type: (str) -> None
        """
        Initialize the Config object with settings from a JSON file.

        Args:
            jsonfile (str): The name of the JSON configuration file to load from the current directory.

        Attributes:
            data (dict): The parsed JSON data from the configuration file.
            directorio (str): Directory path from the configuration.
            repeticiones (int): Number of repetitions for static images from the configuration.
            repeticiones_gif (int): Number of repetitions for animated GIFs, defaults to repeticiones if not specified.
            ancho (int): Width value from the configuration.
            alto (int): Height value from the configuration.
            panel_hor (int): Horizontal panel value from the configuration.
            panel_ver (int): Vertical panel value from the configuration.
            primer_led (int): First LED position from the configuration.
            velocidad (int): Speed value from the configuration.
            debug (int): Debug flag from the configuration, defaults to 0 if not present.

        Raises:
            FileNotFoundError: If the specified JSON file does not exist.
            json.JSONDecodeError: If the JSON file is malformed.
            KeyError: If required keys are missing from the JSON configuration.
        """
        with open('/home/pi/panel/'+jsonfile, 'r') as f:
            self.data = json.load(f)
        self.directorio = self.data["directorio"]
        self.repeticiones = self.data["repeticiones"]
        self.repeticiones_gif = self.data.get("repeticiones_gif", self.data["repeticiones"])
        self.ancho = self.data["ancho"]
        self.alto = self.data["alto"]
        self.panel_hor = self.data["panel_hor"]
        self.panel_ver = self.data["panel_ver"] 
        self.primer_led = self.data["primer_led"]
        self.posicion_vertical = self.data.get("posicion_vertical", "BOTTOM")
        self.velocidad = self.data["velocidad"]
        self.debug = self.data.get("DEBUG", 0) 