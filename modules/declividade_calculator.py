# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DeclividadeCalculator
                                 A QGIS plugin
 Calculadora de declividade com diferentes unidades e classificação
                             -------------------
        begin                : 2024-03-20
        copyright            : (C) 2024 by Rodolfo
        email                : seu-email@example.com
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

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis
import os
import math

# Corrigir a importação de QDoubleValidator
from qgis.PyQt.QtGui import QDoubleValidator

# Carrega o arquivo .ui
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '..', 'ui', 'declividade_calculator.ui'))

class DeclividadeCalculator(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)
        
        # Conectar sinais
        self.calcularButton.clicked.connect(self.calcular)
        self.limparButton.clicked.connect(self.limpar)
        self.fecharButton.clicked.connect(self.close)
        
        # Configurar validação de entrada
        self.distanciaInput.setValidator(QDoubleValidator(0.0, 999999.0, 2))
        self.desnivelInput.setValidator(QDoubleValidator(-999999.0, 999999.0, 2))
        
        # Inicializar campos
        self.limpar()

    def calcular(self):
        """Calcula a declividade e mostra o resultado"""
        try:
            # Obter valores de entrada
            distancia = float(self.distanciaInput.text().replace(',', '.'))
            desnivel = float(self.desnivelInput.text().replace(',', '.'))
            
            # Verificar valores válidos
            if distancia <= 0:
                self.iface.messageBar().pushMessage(
                    "Erro",
                    "A distância deve ser maior que zero!",
                    level=Qgis.Warning,
                    duration=3
                )
                return
                
            # Calcular declividade em porcentagem
            declividade_percent = (desnivel / distancia) * 100
            
            # Calcular declividade em graus
            declividade_graus = math.degrees(math.atan(desnivel / distancia))
            
            # Calcular razão
            if desnivel != 0:
                razao = distancia / abs(desnivel)
            else:
                razao = float('inf')
            
            # Obter unidade selecionada
            unidade = self.unidadeCombo.currentText()
            
            # Formatar resultado
            resultado = ""
            if unidade == "Porcentagem (%)":
                resultado = f"Declividade: {declividade_percent:.2f}%"
            elif unidade == "Graus (°)":
                resultado = f"Declividade: {declividade_graus:.2f}°"
            else:  # Razão (1:X)
                if razao == float('inf'):
                    resultado = "Declividade: 1:∞ (plano)"
                else:
                    resultado = f"Declividade: 1:{razao:.2f}"
            
            # Mostrar resultado
            self.resultadoText.setPlainText(resultado)
            
            # Classificar declividade
            self.classificar_declividade(declividade_percent)
            
        except ValueError:
            self.iface.messageBar().pushMessage(
                "Erro",
                "Por favor, insira valores numéricos válidos!",
                level=Qgis.Warning,
                duration=3
            )
        except Exception as e:
            self.iface.messageBar().pushMessage(
                "Erro",
                f"Ocorreu um erro: {str(e)}",
                level=Qgis.Critical,
                duration=3
            )

    def classificar_declividade(self, declividade_percent):
        """Classifica a declividade segundo a EMBRAPA"""
        classificacao = ""
        
        if declividade_percent < 3:
            classificacao = "Plano (0-3%)"
        elif 3 <= declividade_percent < 8:
            classificacao = "Suave Ondulado (3-8%)"
        elif 8 <= declividade_percent < 13:
            classificacao = "Ondulado (8-13%)"
        elif 13 <= declividade_percent < 20:
            classificacao = "Fortemente Ondulado (13-20%)"
        elif 20 <= declividade_percent < 45:
            classificacao = "Montanhoso (20-45%)"
        else:
            classificacao = "Escarpado (>45%)"
        
        # Adicionar informações adicionais
        info = f"Classificação: {classificacao}\n\n"
        info += "Classificação segundo EMBRAPA:\n"
        info += "- Plano (0-3%): Terrenos planos, ideais para agricultura mecanizada\n"
        info += "- Suave Ondulado (3-8%): Permite mecanização com algumas restrições\n"
        info += "- Ondulado (8-13%): Mecanização limitada, risco de erosão moderado\n"
        info += "- Fortemente Ondulado (13-20%): Mecanização muito limitada, alto risco de erosão\n"
        info += "- Montanhoso (20-45%): Mecanização inviável, muito suscetível à erosão\n"
        info += "- Escarpado (>45%): Terreno muito íngreme, risco muito alto de erosão"
        
        self.classificacaoText.setPlainText(info)

    def limpar(self):
        """Limpa todos os campos"""
        self.distanciaInput.clear()
        self.desnivelInput.clear()
        self.resultadoText.clear()
        self.classificacaoText.clear()
        self.unidadeCombo.setCurrentIndex(0)

def run(iface):
    """Função para executar a calculadora de declividade"""
    dialog = DeclividadeCalculator(iface)
    dialog.show()
    dialog.exec_() 