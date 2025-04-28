# -*- coding: utf-8 -*-
import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QComboBox
from qgis.core import Qgis, QgsWkbTypes, QgsProject, QgsFeatureRequest, QgsGeometry, QgsMapLayer

# Carrega o arquivo .ui
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'pega_linha.ui'))

class ToggleLigaLinha(QDialog, FORM_CLASS):
    # Variável de classe para rastrear o estado global
    _is_active = False
    _connected_layer = None  # Armazena a camada conectada para desconexão

    def __init__(self, iface):
        """Inicializa o plugin."""
        QDialog.__init__(self)
        FORM_CLASS.__init__(self)

        self.iface = iface
        self.action = None
        self._attribute_callback = None

        self.setupUi(self)  # Configura a UI diretamente na instância
        
        # Conectar botões
        if hasattr(self, "btn_toggle"):
            self.btn_toggle.clicked.connect(self.toggle_action)
        if hasattr(self, "btn_close"):
            self.btn_close.clicked.connect(self.close)

        # Configurar os QComboBox
        self.setup_layer_combos()
        self.setup_field_combos()

        # Conectar mudanças nas camadas para atualizar os campos
        self.combo_layer_linha.currentIndexChanged.connect(self.update_field_combo_linha)
        self.combo_layer_ponto.currentIndexChanged.connect(self.update_field_combo_ponto)

        # Atualizar a UI com base no estado global
        self.update_ui()

    def setup_layer_combos(self):
        """Preenche os QComboBox com as camadas disponíveis."""
        layers = QgsProject.instance().mapLayers().values()
        self.combo_layer_linha.clear()
        self.combo_layer_ponto.clear()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.geometryType() == QgsWkbTypes.LineGeometry:
                    self.combo_layer_linha.addItem(layer.name(), layer)
                elif layer.geometryType() == QgsWkbTypes.PointGeometry:
                    self.combo_layer_ponto.addItem(layer.name(), layer)

    def setup_field_combos(self):
        """Preenche os QComboBox com os campos das camadas selecionadas."""
        self.update_field_combo_linha()
        self.update_field_combo_ponto()

    def update_field_combo_linha(self):
        """Atualiza os campos da camada de linha selecionada."""
        layer = self.combo_layer_linha.currentData()
        self.combo_field_linha.clear()
        if layer:
            for field in layer.fields():
                self.combo_field_linha.addItem(field.name(), field.name())
            idx = self.combo_field_linha.findText('COD')
            if idx != -1:
                self.combo_field_linha.setCurrentIndex(idx)

    def update_field_combo_ponto(self):
        """Atualiza os campos da camada de ponto selecionada."""
        layer = self.combo_layer_ponto.currentData()
        self.combo_field_ponto.clear()
        if layer:
            for field in layer.fields():
                self.combo_field_ponto.addItem(field.name(), field.name())
            idx = self.combo_field_ponto.findText('COD')
            if idx != -1:
                self.combo_field_ponto.setCurrentIndex(idx)

    def get_selected_layer(self, combo):
        """Obtém a camada selecionada em um QComboBox."""
        return combo.currentData()

    def update_ui(self):
        """Atualiza a UI com base no estado global."""
        if ToggleLigaLinha._is_active:
            self.btn_toggle.setText("Desativar")
            self.label_status.setText("Status: Ativado")
        else:
            self.btn_toggle.setText("Ativar")
            self.label_status.setText("Status: Desativado")

    def toggle_action(self):
        """Alterna o status da funcionalidade e fecha a janela."""
        camada_linha = self.get_selected_layer(self.combo_layer_linha)
        if not camada_linha:
            self.iface.statusBarIface().showMessage("Erro: Camada de linha não selecionada.", 5000)
            return

        ToggleLigaLinha._is_active = not ToggleLigaLinha._is_active
        if ToggleLigaLinha._is_active:
            ToggleLigaLinha._connected_layer = camada_linha
            # Armazena o callback como uma função lambda para garantir a desconexão correta
            self._attribute_callback = lambda fid, fieldIdx, newValue: self.on_attribute_changed(fid, fieldIdx, newValue)
            camada_linha.attributeValueChanged.connect(self._attribute_callback)
            self.iface.messageBar().pushMessage(
                "Sucesso", "Funcionalidade ativada: linhas serão conectadas ao editar o campo selecionado.",
                level=Qgis.Info)
        else:
            if ToggleLigaLinha._connected_layer and self._attribute_callback:
                try:
                    ToggleLigaLinha._connected_layer.attributeValueChanged.disconnect(self._attribute_callback)
                except TypeError as e:
                    pass  # Log para depuração
            ToggleLigaLinha._connected_layer = None
            self._attribute_callback = None
            self.iface.messageBar().pushMessage(
                "Sucesso", "Funcionalidade desativada.", level=Qgis.Info)

        self.update_ui()
        self.close()

    def atualizar_geometria_linha(self, layer, fid, valor):
        """Atualiza a geometria da linha para se conectar ao ponto correspondente."""
        camada_ponto = self.get_selected_layer(self.combo_layer_ponto)
        if not camada_ponto:
            self.iface.statusBarIface().showMessage("Aviso: Camada de ponto não selecionada.", 5000)
            return

        field_ponto = self.combo_field_ponto.currentText()
        expr = f'"{field_ponto}" = \'{valor}\''
        request = QgsFeatureRequest().setFilterExpression(expr)
        ponto_destino = next(camada_ponto.getFeatures(request), None)

        if not ponto_destino:
            self.iface.statusBarIface().showMessage(f"Aviso: Nenhum ponto com {field_ponto} = {valor}", 5000)
            return

        linha = layer.getFeature(fid)
        geom = linha.geometry()
        coords = geom.asPolyline() if not geom.isMultipart() else geom.asMultiPolyline()[0]

        if not coords or len(coords) < 1:
            self.iface.statusBarIface().showMessage(f"Aviso: Linha {fid} sem geometria válida.", 5000)
            return

        ponto_inicio = coords[0]
        nova_geom = QgsGeometry.fromPolylineXY([ponto_inicio, ponto_destino.geometry().asPoint()])
        layer.dataProvider().changeGeometryValues({fid: nova_geom})
        layer.triggerRepaint()
        self.iface.statusBarIface().showMessage(f"Linha {fid} conectada ao ponto {field_ponto} = {valor}", 5000)

    def on_attribute_changed(self, fid, fieldIdx, newValue):
        """Verifica se o campo selecionado foi alterado e atualiza a linha."""
        if not ToggleLigaLinha._is_active:
            return

        camada_linha = self.get_selected_layer(self.combo_layer_linha)
        if not camada_linha or fieldIdx >= camada_linha.fields().count():
            return

        field_name = camada_linha.fields()[fieldIdx].name()
        if field_name == self.combo_field_linha.currentText() and newValue:
            self.atualizar_geometria_linha(camada_linha, fid, newValue)

    def run(self):
        """Exibe a UI do módulo."""
        self.show()
        self.exec_()

    def close(self):
        """Fecha a UI de forma simples."""
        super().close()  # Apenas chama o close() da classe base

    def disconnect(self):
        try:
            self.iface.mapCanvas().xyCoordinates.connect(self.show_coordinates)
        except Exception as e:
            pass