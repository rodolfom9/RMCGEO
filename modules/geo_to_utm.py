# -*- coding: utf-8 -*-
"""
/***************************************************************************
 classnomeDialog
                                 A QGIS plugin
 Conversor de Graus e Graus Decimais para UTM
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2025-03-20
        git sha              : $Format:%H$
        copyright            : (C) 2025 by rodolfo
        email                : email
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtGui import QIcon
from qgis._core import QgsProject
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPointXY
import math

# Carrega o arquivo .ui
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'geografica-utm.ui'))  # Ajuste o nome do arquivo .ui se necessário


class GeoToUtm(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None, iface=None):
        """Constructor."""
        super(GeoToUtm, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        self.clipboard = QApplication.clipboard()

        # Configurar os widgets
        self.setup_widgets()

        # Conexões dos sinais dos botões
        self.buttonconvertg.clicked.connect(self.atualizar_coordenadas_gms)
        self.buttonconvertd.clicked.connect(self.atualizar_coordenadas_decimal)
        self.copyqline_x.clicked.connect(self.copy_x)
        self.copyqline_y.clicked.connect(self.copy_y)
        self.copyqline_z.clicked.connect(self.copy_z)

        # Conectar a mudança de datum para atualizar o status
        self.datum_saida.currentTextChanged.connect(self.update_datum_info)

        # Configurar ícones dos botões de cópia
        self.copyqline_x.setIcon(QIcon(':/images/themes/default/mActionEditCopy.svg'))
        self.copyqline_y.setIcon(QIcon(':/images/themes/default/mActionEditCopy.svg'))
        self.copyqline_z.setIcon(QIcon(':/images/themes/default/mActionEditCopy.svg'))

        # Configurar tooltips
        self.lat_input.setToolTip("Digite a latitude em GMS (ex: 23 30 45)")
        self.lon_input.setToolTip("Digite a longitude em GMS (ex: 46 15 30)")
        self.alt_input.setToolTip("Digite a altitude em metros")
        self.latd_input.setToolTip("Digite a latitude em graus decimais (ex: -23.5125)")
        self.lond_input.setToolTip("Digite a longitude em graus decimais (ex: -46.2583)")
        self.altd_input.setToolTip("Digite a altitude em metros")
        self.buttonconvertg.setToolTip("Converter coordenadas GMS para UTM")
        self.buttonconvertd.setToolTip("Converter coordenadas decimais para UTM")
        self.copyqline_x.setToolTip("Copiar Easting")
        self.copyqline_y.setToolTip("Copiar Northing")
        self.copyqline_z.setToolTip("Copiar Zona UTM")
        self.datum_saida.setToolTip("Escolha o datum de referência")
        self.utm_zone_combo.setToolTip("Escolha o fuso UTM")

        # Desabilitar os QLineEdit de saída
        self.alt_input.setEnabled(False)
        self.altd_input.setEnabled(False)

    def setup_widgets(self):
        """Configura os widgets necessários para conversão UTM."""
        # Configurar os combos de datum com opções fixas
        self.datum_entrada.clear()
        self.datum_saida.clear()
        self.datum_entrada.addItems(["SIRGAS2000", "WGS84", "SAD69"])
        self.datum_saida.addItems(["SIRGAS2000", "WGS84", "SAD69"])
        self.datum_entrada.setCurrentText("WGS84")
        self.datum_saida.setCurrentText("SIRGAS2000")

        # Conectar a mudança de datum para atualizar o status
        self.datum_saida.currentTextChanged.connect(self.update_datum_info)

        # Configurar utm_zone_combo
        self.update_utm_zones(self.datum_saida.currentText())

    def update_utm_zones(self, datum):
        """Atualiza as zonas UTM no combo box com base no datum selecionado."""
        self.utm_zone_combo.clear()

        # Zonas específicas para SIRGAS2000
        sirgas_zones = [
            "17S", "18S", "19S", "20S", "21S", "22S", "23S", "24S", "25S",
            "17N", "18N", "19N", "20N", "21N", "22N"
        ]

        # Zonas específicas para SAD69
        sad69_zones = [
            "17S", "18S", "19S", "20S", "21S", "22S", "23S", "24S", "25S",
            "17N", "18N", "19N", "20N", "21N", "22N"
        ]

        # Todas as zonas para WGS84
        wgs84_zones = [f"{i}N" for i in range(1, 61)] + [f"{i}S" for i in range(1, 61)]

        # Selecionar as zonas com base no datum
        if datum == "SIRGAS2000":
            self.utm_zone_combo.addItems(sirgas_zones)
            self.utm_zone_combo.setCurrentText("22S")
            self.iface.statusBarIface().showMessage(f"Zonas SIRGAS2000 carregadas: {sirgas_zones}", 5000)
        elif datum == "SAD69":
            self.utm_zone_combo.addItems(sad69_zones)
            self.utm_zone_combo.setCurrentText("22S")
            self.iface.statusBarIface().showMessage(f"Zonas SAD69 carregadas: {sad69_zones}", 5000)
        elif datum == "WGS84":
            self.utm_zone_combo.addItems(wgs84_zones)
            self.utm_zone_combo.setCurrentText("22S")
            self.iface.statusBarIface().showMessage("Zonas WGS84 carregadas (1N-60N, 1S-60S)", 5000)
        else:
            self.iface.statusBarIface().showMessage(f"Datum desconhecido: {datum}", 5000)

    def update_datum_info(self, datum):
        """Atualiza a barra de status e as zonas UTM quando o datum muda."""
        epsg_map = {
            "SIRGAS2000": "EPSG:4674",
            "WGS84": "EPSG:4326",
            "SAD69": "EPSG:4618"
        }
        self.iface.statusBarIface().showMessage(f"Datum selecionado: {datum} ({epsg_map[datum]})", 3000)
        self.update_utm_zones(datum)

    def geografica_para_utm(self, lat, lon, datum_entrada, datum_saida):
        """Converte geodésicas para UTM usando os datums de entrada e saída selecionados."""
        # Mapeamento de datums para códigos EPSG geográficos
        datum_crs_map = {
            "SIRGAS2000": "EPSG:4674",  # Datum SIRGAS2000, lat/lon
            "WGS84": "EPSG:4326",       # Datum WGS84, lat/lon
            "SAD69": "EPSG:4618"        # Datum SAD69, lat/lon
        }

        # Mapeamento de fusos UTM SIRGAS2000 (destino)
        utm_zones_sirgas = {
            "17N": "EPSG:5332", "18N": "EPSG:5333", "19N": "EPSG:5334",
            "17S": "EPSG:31977", "18S": "EPSG:31978", "19S": "EPSG:31979",
            "20S": "EPSG:31980", "21S": "EPSG:31981", "22S": "EPSG:31982",
            "23S": "EPSG:31983", "24S": "EPSG:31984", "25S": "EPSG:31985",
            "20N": "EPSG:31974", "21N": "EPSG:31975", "22N": "EPSG:31976"
        }

        # Mapeamento de fusos UTM SAD69 (destino)
        utm_zones_sad69 = {
            "17S": "EPSG:29187", "18S": "EPSG:29188", "19S": "EPSG:29189",
            "20S": "EPSG:29190", "21S": "EPSG:29191", "22S": "EPSG:29192",
            "23S": "EPSG:29193", "24S": "EPSG:29194", "25S": "EPSG:29195",
            "18N": "EPSG:29168", "19N": "EPSG:29169", "20N": "EPSG:29170",
            "21N": "EPSG:29171", "22N": "EPSG:29172", "17N": "EPSG:5463"
        }

        # Primeiro, converter do datum de entrada para o datum de saída
        src_crs = QgsCoordinateReferenceSystem(datum_crs_map[datum_entrada])
        dest_crs = QgsCoordinateReferenceSystem(datum_crs_map[datum_saida])

        if not src_crs.isValid():
            raise ValueError(f"CRS de origem inválido: {datum_crs_map[datum_entrada]}")
        if not dest_crs.isValid():
            raise ValueError(f"CRS de destino inválido: {datum_crs_map[datum_saida]}")

        # Transformar do datum de entrada para o datum de saída
        transform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
        point = transform.transform(QgsPointXY(float(lon), float(lat)))
        
        # Agora converter para UTM usando o datum de saída
        zone_str = self.utm_zone_combo.currentText()
        zone = int(zone_str[:-1])
        hemisphere = zone_str[-1]

        # Escolher o CRS de destino UTM com base no datum de saída
        if datum_saida == "SIRGAS2000":
            utm_crs_id = utm_zones_sirgas.get(zone_str, f"EPSG:{32600 + zone if hemisphere == 'N' else 32700 + zone}")
        elif datum_saida == "WGS84":
            utm_crs_id = f"EPSG:{32600 + zone if hemisphere == 'N' else 32700 + zone}"
        elif datum_saida == "SAD69":
            utm_crs_id = utm_zones_sad69.get(zone_str, f"EPSG:{32600 + zone if hemisphere == 'N' else 32700 + zone}")
        else:
            raise ValueError(f"Datum desconhecido: {datum_saida}")

        utm_crs = QgsCoordinateReferenceSystem(utm_crs_id)
        if not utm_crs.isValid():
            raise ValueError(f"CRS UTM inválido: {utm_crs_id}")

        # Transformar para UTM
        transform = QgsCoordinateTransform(dest_crs, utm_crs, QgsProject.instance())
        point_utm = transform.transform(point)

        return f"{zone}{hemisphere}", point_utm.x(), point_utm.y()

    def atualizar_coordenadas_gms(self):
        """Converte coordenadas GMS para UTM."""
        try:
            lat = self.lat_input.text() or "0"
            lon = self.lon_input.text() or "0"
            datum_entrada = self.datum_entrada.currentText()
            datum_saida = self.datum_saida.currentText()

            if " " in lat:
                lat = self.gms_para_decimal(lat)
            else:
                lat = float(lat)
            if " " in lon:
                lon = self.gms_para_decimal(lon)
            else:
                lon = float(lon)

            zone, easting, northing = self.geografica_para_utm(lat, lon, datum_entrada, datum_saida)
            self.x_output.setText(f"{easting:.8f}")
            self.y_output.setText(f"{northing:.8f}")
            self.z_output.setText(zone)
        except ValueError as e:
            self.iface.statusBarIface().showMessage(f"Erro: {str(e)}", 5000)

    def atualizar_coordenadas_decimal(self):
        """Converte coordenadas decimais para UTM."""
        try:
            lat = self.latd_input.text() or "0"
            lon = self.lond_input.text() or "0"
            datum_entrada = self.datum_entrada.currentText()
            datum_saida = self.datum_saida.currentText()

            lat = float(lat)
            lon = float(lon)

            zone, easting, northing = self.geografica_para_utm(lat, lon, datum_entrada, datum_saida)
            self.x_output.setText(f"{easting:.8f}")
            self.y_output.setText(f"{northing:.8f}")
            self.z_output.setText(zone)
        except ValueError as e:
            self.iface.statusBarIface().showMessage(f"Erro: Entrada inválida nos campos decimais - {str(e)}", 5000)

    def gms_para_decimal(self, gms_str):
        """Converte coordenada GMS para grau decimal."""
        partes = gms_str.strip().split()
        if len(partes) != 3:
            raise ValueError("Entrada inválida! Use o formato: 'grau minuto segundo'.")
        graus, minutos, segundos = map(float, partes)
        sinal = -1 if graus < 0 else 1
        decimal = abs(graus) + (minutos / 60) + (segundos / 3600)
        return sinal * decimal

    def copy_x(self):
        """Copia o valor de x_output (Easting) para a área de transferência."""
        try:
            s = self.x_output.text()
            self.clipboard.setText(s)
            self.iface.statusBarIface().showMessage(f"'{s}' Copiado para a Area de Transferencia", 3000)
        except AttributeError as e:
            self.iface.statusBarIface().showMessage(f"Erro: {str(e)}", 5000)

    def copy_y(self):
        """Copia o valor de y_output (Northing) para a área de transferência."""
        try:
            s = self.y_output.text()
            self.clipboard.setText(s)
            self.iface.statusBarIface().showMessage(f"'{s}' Copiado para a Area de Transferencia", 3000)
        except AttributeError as e:
            self.iface.statusBarIface().showMessage(f"Erro: {str(e)}", 5000)

    def copy_z(self):
        """Copia o valor de z_output (Zona) para a área de transferência."""
        try:
            s = self.z_output.text()
            self.clipboard.setText(s)
            self.iface.statusBarIface().showMessage(f"'{s}' Copiado para a Area de Transferencia", 3000)
        except AttributeError as e:
            self.iface.statusBarIface().showMessage(f"Erro: {str(e)}", 5000)

    def reset_fields(self):
        """Redefine todos os campos de entrada e saída para valores padrão."""
        self.lat_input.setText("")
        self.lon_input.setText("")
        self.alt_input.setText("")
        self.latd_input.setText("")
        self.lond_input.setText("")
        self.altd_input.setText("")
        self.x_output.setText("")
        self.y_output.setText("")
        self.z_output.setText("")

def run(iface):
    """Função para executar o diálogo de conversão geográfica para UTM."""
    dlg = GeoToUtm(iface=iface)
    dlg.reset_fields()
    dlg.show()
    dlg.exec_()

def unload():
    """Função para limpar recursos quando o plugin for descarregado."""
    pass