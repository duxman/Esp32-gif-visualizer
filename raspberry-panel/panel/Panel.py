# -*- coding: utf-8 -*-
from venv import logger


class Panel():

    def __init__(self, width, height, side="LEFT", paneles_vertical=1, paneles_horizontal=1, vertical_position="BOTTOM"):
        # type: (int, int, str, int, int, str) -> None
        self.width = width
        self.height = height
        self.side = side
        self.vertical_position = vertical_position
        self.paneles_vertical = paneles_vertical
        self.paneles_horizontal = paneles_horizontal
        self.matriz = []
        
        if self.side == "LEFT":
            self.incrementar = False
        else:
            self.incrementar = True

        self.total_leds = (width * paneles_horizontal) * (height * paneles_vertical)
        logger.info("Total LEDs in panel: {0}".format(self.total_leds))
        self.total_leds_panel = width * height
        logger.info("Total LEDs per single panel: {0}".format(self.total_leds_panel))
        self.altura_total = height * paneles_vertical
        logger.info("Total height of panel: {0}".format(self.altura_total))
        self.ancho_total = width * paneles_horizontal
        logger.info("Total width of panel: {0}".format(self.ancho_total))


    def calculateMatrix(self):
        self.matriz = []
        
        # Log de configuración de paneles
        logger.info("=== Calculando matriz de paneles ===")
        logger.info("Paneles horizontales: {0}, Paneles verticales: {1}".format(self.paneles_horizontal, self.paneles_vertical))
        logger.info("Tamaño por panel: {0}x{1} LEDs".format(self.width, self.height))
        logger.info("Tamaño total: {0}x{1} LEDs".format(self.ancho_total, self.altura_total))
        logger.info("Total LEDs por panel: {0}".format(self.total_leds_panel))
        logger.info("Total LEDs: {0}".format(self.total_leds))
        logger.info("Primer LED: {0}, Posicion vertical: {1}".format(self.side, self.vertical_position))
        
        # Calcular la matriz primero sin considerar vertical_position
        # Luego invertir si es necesario
        matriz_temp = []
        
        # Iterar por cada panel vertical (de abajo hacia arriba)
        for panel_v in range(self.paneles_vertical):
            # Para cada fila dentro de este panel vertical
            for fila_en_panel in range(self.height):
                # Determinar si esta fila va hacia adelante o hacia atrás (serpentina)
                if self.side == "LEFT":
                    ir_adelante = (fila_en_panel % 2) == 0
                else:
                    ir_adelante = (fila_en_panel % 2) == 1
                
                # Generar los indices para esta fila en un solo panel
                if ir_adelante:
                    rangeMatrixLine = list(range(fila_en_panel * self.width, (fila_en_panel + 1) * self.width))
                else:
                    rangeMatrixLine = list(range((fila_en_panel + 1) * self.width - 1, fila_en_panel * self.width - 1, -1))
                
                # Aplicar el offset para cada panel horizontal en esta fila
                fila_completa = []
                for panel_h in range(self.paneles_horizontal):
                    # Calcular el offset base del panel
                    offset_panel = (panel_v * self.paneles_horizontal + panel_h) * self.total_leds_panel
                    
                    # Sumar el offset a cada LED de la linea
                    line = list(map(lambda x: x + offset_panel, rangeMatrixLine))
                    fila_completa.extend(line)
                    
                    # Log detallado de cada panel
                    panel_num = panel_v * self.paneles_horizontal + panel_h
                    fila_global = panel_v * self.height + fila_en_panel
                    logger.info("Panel[{0}] (V:{1},H:{2}) - Fila:{3}, Offset:{4}, Rango LED:{5}-{6}".format(
                        panel_num, panel_v, panel_h, fila_global, offset_panel, min(line), max(line)))
                
                matriz_temp.append(fila_completa)
        
        # Si vertical_position es BOTTOM, invertir el orden de las filas
        if self.vertical_position == "BOTTOM":
            matriz_temp.reverse()
            logger.info("Orden de filas invertido (BOTTOM)")
        
        # Aplanar la matriz temporal a la matriz final
        for fila in matriz_temp:
            self.matriz.extend(fila)

        logger.info("=== Matriz calculada con {0} indices totales ===".format(len(self.matriz)))
        return self.matriz