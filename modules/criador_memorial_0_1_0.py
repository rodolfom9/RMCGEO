# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MemorialDescritivo
                                 A QGIS plugin
 Este plugin gera memoriais descritivos a partir de camadas vetoriais
                              -------------------
        begin                : 2025-04-14
        git sha              : $Format:%H$
        copyright            : (C) 2025
        email                : dev@example.com
 ***************************************************************************/
"""

import os
import time
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDialog
from qgis.core import QgsProject, QgsMapLayer, QgsWkbTypes, QgsMessageLog
from PyQt5 import uic

ui_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'ui', 'criador_memorial_0_1_0.ui'))
FORM_CLASS, _ = uic.loadUiType(ui_path)

class MemorialDescritivo010(QDialog, FORM_CLASS):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor."""
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.setupUi(self)
        
        # Inicializar atributos
        self.debug_mode = True
        
        # Definir data atual
        data_atual = QDate.currentDate()
        self.edit_data.setDate(data_atual)
        
        # Conectar sinais
        self.conectar_sinais()
        
        # Adicionar mensagem inicial de debug
        self.adicionar_debug("Plugin Memorial Descritivo inicializado")
        
        # Gerar conteúdo da aba "Como Utilizar"
        self.gerar_conteudo_como_utilizar()

    def conectar_sinais(self):
        """Connects UI signals."""
        self.adicionar_debug("Conectando sinais da UI...")
        self.input_layer_poligono.currentIndexChanged.connect(self.on_camada_selecionada)
        self.btn_sair.clicked.connect(self.reject)
        self.adicionar_debug("Sinais conectados com sucesso")

    def gerar_conteudo_como_utilizar(self):
        """Gera o conteúdo HTML explicativo."""
        html = """
        <html>
        <body>
            <h1>Como Utilizar o Plugin Memorial Descritivo</h1>
            <p>O plugin está em desenvolvimento. Na versão atual, você pode selecionar uma camada de polígonos.</p>
            <h2>Passos para Utilização</h2>
            <p>1. Selecione uma camada vetorial de polígonos no campo 'Camada Poligono'.</p>
        </body>
        </html>
        """
        self.texto_como_utilizar.setHtml(html)

    def log(self, message, level=0):
        """Log function with different levels."""
        if self.debug_mode:
            prefix = "MemorialDescritivo: "
            if level == 0:
                QgsMessageLog.logMessage(f"{prefix}{message}", "Memorial Descritivo", level=0)
                print(f"INFO: {prefix}{message}")
            elif level == 1:
                QgsMessageLog.logMessage(f"{prefix}{message}", "Memorial Descritivo", level=1)
                print(f"WARNING: {prefix}{message}")
            elif level == 2:
                QgsMessageLog.logMessage(f"{prefix}{message}", "Memorial Descritivo", level=2)
                print(f"CRITICAL: {prefix}{message}")

    def adicionar_debug(self, mensagem):
        """Adiciona mensagem na área de debug."""
        if self.debug_mode:
            timestamp = time.strftime("%H:%M:%S")
            self.texto_debug.append(f"[{timestamp}] {mensagem}")

    def on_camada_selecionada(self):
        """Handles layer selection changes."""
        self.adicionar_debug("Camada selecionada alterada")
        layer_id = self.input_layer_poligono.currentData()
        if not layer_id:
            self.adicionar_debug("Nenhuma camada selecionada")
            return
        layer = QgsProject.instance().mapLayer(layer_id)
        if not layer:
            self.adicionar_debug("Camada não encontrada")
            return
        self.adicionar_debug(f"Camada selecionada: {layer.name()}")

    def atualizar_camadas_disponiveis(self):
        """Atualiza a lista de camadas vetoriais disponíveis."""
        self.log("Atualizando lista de camadas vetoriais disponíveis")
        self.input_layer_poligono.clear()
        self.input_layer_poligono.addItem("Selecione uma camada", None)
        camadas = QgsProject.instance().mapLayers().values()
        for camada in camadas:
            if (camada.type() == QgsMapLayer.VectorLayer and 
                camada.geometryType() == QgsWkbTypes.PolygonGeometry):
                self.input_layer_poligono.addItem(camada.name(), camada.id())
        self.log(f"Encontradas {self.input_layer_poligono.count() - 1} camadas de polígonos")

    def run(self):
        """Executa o plugin."""
        self.log("Iniciando o plugin Memorial Descritivo")
        self.adicionar_debug("Método run() chamado")
        self.atualizar_camadas_disponiveis()
        self.show()
        result = self.exec_()
        if result:
            self.log("Diálogo aceito")
        else:
            self.log("Diálogo cancelado")