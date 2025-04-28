from qgis.core import QgsPointXY, QgsGeometry, QgsFeature, QgsVectorLayer
from qgis.gui import QgsMapTool
from PyQt5.QtWidgets import QDialog, QMessageBox
from qgis.PyQt import uic
from qgis.utils import iface
import os

# Carrega o arquivo .ui
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'inserir_ponto.ui'))

class PointInsert(QgsMapTool):
    def __init__(self, canvas, dialog):
        super().__init__(canvas)
        self.canvas = canvas
        self.dialog = dialog
        self.last_map_point = None

    def canvasPressEvent(self, event):
        if event.button() == 2:  # 2 é o botão direito do mouse
            self.canvas.unsetMapTool(self)
            return
            
        pos = event.pos()
        self.last_map_point = self.toMapCoordinates(pos)
        
        # Verifica se há uma camada ativa e se está em modo de edição
        layer = iface.activeLayer()
        if not layer:
            QMessageBox.warning(self.dialog, "Aviso", "Nenhuma camada selecionada!")
            return
            
        if not layer.isEditable():
            QMessageBox.warning(self.dialog, "Aviso", "A camada precisa estar em modo de edição!")
            return
            
        self.show_coordinate_input(pos, self.last_map_point)

    def show_coordinate_input(self, pos, map_point):
        if self.dialog is None:
            self.dialog = PointInsertDialog(iface)
            self.dialog.point_confirmed.connect(self.add_point)
        else:
            self.dialog.close()
            self.dialog = None
            return

        self.dialog.eastInput.setPlaceholderText(f"Este (X): {map_point.x():.2f}")
        self.dialog.northInput.setPlaceholderText(f"Norte (Y): {map_point.y():.2f}")
        screen_pos = self.canvas.mapToGlobal(pos)
        self.dialog.move(screen_pos)
        self.dialog.show()
        self.dialog.eastInput.setFocus()

    def add_point(self, east, north):
        try:
            x = float(east)
            y = float(north)
        except ValueError as e:
            iface.messageBar().pushMessage("Erro", "Coordenadas inválidas!", level=1)
            return

        layer = iface.activeLayer()
        if not layer:
            iface.messageBar().pushMessage("Erro", "Nenhuma camada selecionada!", level=1)
            return
            
        if layer.type() != QgsVectorLayer:
            iface.messageBar().pushMessage("Erro", "A camada selecionada não é uma camada vetorial!", level=1)
            return
            
        if not layer.isEditable():
            iface.messageBar().pushMessage("Erro", "A camada precisa estar em modo de edição!", level=1)
            return

        point = QgsPointXY(x, y)
        geometry = QgsGeometry.fromPointXY(point)
        feature = QgsFeature()
        feature.setGeometry(geometry)

        success = layer.addFeature(feature)
        if success:
            layer.commitChanges()
            self.canvas.refresh()
        else:
            layer.rollBack()
            iface.messageBar().pushMessage("Erro", "Falha ao adicionar o ponto à camada!", level=1)

    def deactivate(self):
        if self.dialog is not None:
            self.dialog.close()
        super().deactivate()

class PointInsertDialog(QDialog, FORM_CLASS):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.tool = None
        self.last_map_point = None
        self.dialog = None

        self.setupUi(self)

        # Conecta os botões
        self.confirmButton.clicked.connect(self.on_confirm)
        self.closeButton.clicked.connect(self.close)

    def run(self):
        """Método chamado quando a ferramenta é ativada pelo menu"""
        # Se a ferramenta já existe, apenas reativa
        if self.tool:
            self.canvas.setMapTool(self.tool)
        else:
            self.activate_tool()

    def activate_tool(self):
        if self.tool is None:
            self.tool = PointInsert(self.canvas, self)
        self.canvas.setMapTool(self.tool)

    def on_confirm(self):
        if self.tool:
            east = self.eastInput.text()
            north = self.northInput.text()
            self.tool.add_point(east, north)
            self.close()
        else:
            return

    def unload(self):
        if self.tool:
            self.canvas.unsetMapTool(self.tool)
            self.tool = None

def run(iface):
    """Função para executar a ferramenta de inserção de ponto."""
    tool = PointInsertDialog(iface=iface)
    tool.run()

def unload():
    """Função para limpar recursos quando o plugin for descarregado."""
    pass