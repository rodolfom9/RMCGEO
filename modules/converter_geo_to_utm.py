# -*- coding: utf-8 -*-
"""
Módulo de conversão de coordenadas para QGIS 3.34
Implementa diversas funções para conversão entre coordenadas geográficas
e sistemas de projeção como UTM, Lambert, Albers, etc.

Baseado em literatura técnica de cartografia e geodésia.
"""

import math

# Parâmetros dos datums utilizados
DATUM_PARAMS = {
    # id: [nome, semi_eixo, achatamento, deltax, deltay, deltaz]
    0: ["Null", 0.0, 0.0, 0.0, 0.0, 0.0],
    1: ["SAD69", 6378160.0, 0.00335289187, -67.35, 3.88, -38.22],
    2: ["CorregoAlegre", 6378388.0, 0.00336700337, -206.05, 168.28, -3.82],
    3: ["AstroChua", 6378388.0, 0.00336700337, -144.35, 243.37, -33.22],
    4: ["WGS84", 6378137.0, 0.00335281066, 0.0, 0.0, 0.0],
    5: ["SIRGAS2000", 6378137.0, 0.00335281068, 0.0, 0.0, 0.0]
}
class ConversorGeoToUtm:
    def __init__(self, iface):
        """
        Classe principal para o conversor de coordenadas
        
        Args:
            iface: interface do QGIS
        """
        self.iface = iface
        
    def run(self):
        """
        Executa o conversor avançado
        """
        from RMCGEO.modules.conversor_avancado import run as run_conversor
        run_conversor(self.iface)

def geo_to_utm(lat, lon, semi_eixo, achat, hemis, lon_mc):
    """
    Transforma coordenadas geodésicas em coordenadas UTM

    Args:
        lat: latitude em radianos
        lon: longitude em radianos
        semi_eixo: semi-eixo maior do elipsoide
        achat: achatamento do elipsoide
        hemis: hemisfério ("norte" ou "sul")
        lon_mc: meridiano central em radianos

    Returns:
        tuple: (x, y) coordenadas UTM em metros
    """
    # Verifica hemisfério
    if hemis == "norte":
        offy = 0.0
    else:
        offy = 10000000.0

    # Converte Lat Long em UTM
    k0 = 1.0 - (1.0/2500.0)
    equad = 2.0 * achat - pow(achat, 2)
    elinquad = equad / (1.0 - equad)

    aux1 = equad * equad
    aux2 = aux1 * equad
    aux3 = math.sin(2.0 * lat)
    aux4 = math.sin(4.0 * lat)
    aux5 = math.sin(6.0 * lat)
    aux6 = (1.0 - equad/4.0 - 3.0*aux1/64.0 - 5.0*aux2/256.0) * lat
    aux7 = (3.0*equad/8.0 + 3.0*aux1/32.0 + 45.0*aux2/1024.0) * aux3
    aux8 = (15.0*aux1/256.0 + 45.0*aux2/1024.0) * aux4
    aux9 = (35.0*aux2/3072.0) * aux5

    n = semi_eixo / math.sqrt(1.0 - equad * pow(math.sin(lat), 2))
    t = pow(math.tan(lat), 2)
    c = elinquad * pow(math.cos(lat), 2)
    ag = (lon - lon_mc) * math.cos(lat)
    m = semi_eixo * (aux6 - aux7 + aux8 - aux9)

    aux10 = (1.0 - t + c) * pow(ag, 3) / 6.0
    aux11 = (5.0 - 18.0*t + t*t + 72.0*c - 58.0*elinquad) * pow(ag, 5) / 120.0
    aux12 = (5.0 - t + 9.0*c + 4.0*c*c) * pow(ag, 4) / 24.0
    aux13 = (61.0 - 58.0*t + t*t + 600.0*c - 330.0*elinquad) * pow(ag, 6) / 720.0

    x = 500000.0 + k0 * n * (ag + aux10 + aux11)
    y = offy + k0 * (m + n * math.tan(lat) * (ag*ag/2.0 + aux12 + aux13))

    return x, y

def utm_to_geo(x, y, semi_eixo, achat, hemis, lon_mc):
    """
    Transforma coordenadas UTM em coordenadas geodésicas

    Args:
        x: coordenada UTM x (em metros)
        y: coordenada UTM y (em metros)
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide
        hemis: hemisfério ("norte" ou "sul")
        lon_mc: meridiano central em radianos

    Returns:
        tuple: (lat, lon) coordenadas geodésicas em radianos
    """
    # Verifica hemisfério
    if hemis == "norte":
        y = y
    else:
        y = y - 10000000.0

    # Converte UTM para Lat/Long
    k0 = 1.0 - (1.0/2500.0)
    equad = 2.0 * achat - pow(achat, 2)
    elinquad = equad / (1.0 - equad)
    e1 = (1.0 - math.sqrt(1.0-equad)) / (1.0 + math.sqrt(1.0-equad))

    aux1 = equad * equad
    aux2 = aux1 * equad
    aux3 = e1 * e1
    aux4 = e1 * aux3
    aux5 = aux4 * e1

    m = y / k0
    mi = m / (semi_eixo * (1.0-equad/4.0-3.0*aux1/64.0-5.0*aux2/256.0))

    aux6 = (3.0*e1/2.0 - 27.0*aux4/32.0) * math.sin(2.0*mi)
    aux7 = (21.0*aux3/16.0 - 55.0*aux5/32.0) * math.sin(4.0*mi)
    aux8 = (151.0*aux4/96.0) * math.sin(6.0*mi)

    lat1 = mi + aux6 + aux7 + aux8
    c1 = elinquad * pow(math.cos(lat1), 2)
    t1 = pow(math.tan(lat1), 2)
    n1 = semi_eixo / math.sqrt(1.0-equad*pow(math.sin(lat1), 2))
    quoc = pow((1.0-equad*math.sin(lat1)*math.sin(lat1)), 3)
    r1 = semi_eixo * (1.0-equad) / math.sqrt(quoc)
    d = (x - 500000.0) / (n1*k0)

    aux9 = (5.0 + 3.0*t1 + 10.0*c1 - 4.0*c1*c1 - 9.0*elinquad) * pow(d, 4) / 24.0
    aux10 = (61.0 + 90.0*t1 + 298.0*c1 + 45.0*t1*t1 - 252.0*elinquad - 3.0*c1*c1) * pow(d, 6) / 720.0
    aux11 = d - (1.0 + 2.0*t1 + c1) * pow(d, 3) / 6.0
    aux12 = (5.0 - 2.0*c1 + 28.0*t1 - 3.0*c1*c1 + 8.0*elinquad + 24.0*t1*t1) * pow(d, 5) / 120.0

    lat = lat1 - (n1*math.tan(lat1)/r1) * (d*d/2.0 - aux9 + aux10)
    lon = lon_mc + (aux11 + aux12) / math.cos(lat1)

    return lat, lon

def geo_to_lamb(lat, lon, lat0, lon0, lat1, lat2, semi_eixo, achat):
    """
    Transforma coordenadas geodésicas em coordenadas Lambert

    Args:
        lat: latitude em radianos
        lon: longitude em radianos
        lat0: paralelo origem em radianos
        lon0: meridiano origem em radianos
        lat1: paralelo padrão 1 em radianos
        lat2: paralelo padrão 2 em radianos
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide

    Returns:
        tuple: (x, y) coordenadas Lambert em metros
    """
    equad = 2.0 * achat - pow(achat, 2)
    e = math.sqrt(equad)

    m1 = math.cos(lat1) / math.sqrt(1.0 - equad * pow(math.sin(lat1), 2))
    m2 = math.cos(lat2) / math.sqrt(1.0 - equad * pow(math.sin(lat2), 2))
    aux1 = math.sqrt((1.0 - e * math.sin(lat1)) / (1.0 + e * math.sin(lat1)))
    aux2 = math.sqrt((1.0 - e * math.sin(lat2)) / (1.0 + e * math.sin(lat2)))
    aux0 = math.sqrt((1.0 - e * math.sin(lat0)) / (1.0 + e * math.sin(lat0)))
    t1 = ((1.0 - math.tan(lat1/2.0)) / (1.0 + math.tan(lat1/2.0))) / pow(aux1, e)
    t2 = ((1.0 - math.tan(lat2/2.0)) / (1.0 + math.tan(lat2/2.0))) / pow(aux2, e)
    t0 = ((1.0 - math.tan(lat0/2.0)) / (1.0 + math.tan(lat0/2.0))) / pow(aux0, e)

    if lat1 == lat2:
        n = math.sin(lat1)
    else:
        n = (math.log(m1) - math.log(m2)) / (math.log(t1) - math.log(t2))

    f = m1 / (n * pow(t1, n))
    ro0 = semi_eixo * f * pow(t0, n)

    aux = math.sqrt((1.0 - e * math.sin(lat)) / (1.0 + e * math.sin(lat)))
    t = ((1.0 - math.tan(lat/2.0)) / (1.0 + math.tan(lat/2.0))) / pow(aux, e)
    ro = semi_eixo * f * pow(t, n)
    teta = n * (lon - lon0)

    x = ro * math.sin(teta)
    y = ro0 - ro * math.cos(teta)

    return x, y

def lamb_to_geo(x, y, lat0, lon0, lat1, lat2, semi_eixo, achat):
    """
    Transforma coordenadas Lambert em coordenadas geodésicas

    Args:
        x: coordenada Lambert x em metros
        y: coordenada Lambert y em metros
        lat0: paralelo origem em radianos
        lon0: meridiano origem em radianos
        lat1: paralelo padrão 1 em radianos
        lat2: paralelo padrão 2 em radianos
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide

    Returns:
        tuple: (lat, lon) coordenadas geodésicas em radianos
    """
    pi = math.pi
    equad = 2.0 * achat - pow(achat, 2)
    e = math.sqrt(equad)

    m1 = math.cos(lat1) / math.sqrt(1.0 - equad * pow(math.sin(lat1), 2))
    m2 = math.cos(lat2) / math.sqrt(1.0 - equad * pow(math.sin(lat2), 2))
    aux1 = math.sqrt((1.0 - e * math.sin(lat1)) / (1.0 + e * math.sin(lat1)))
    aux2 = math.sqrt((1.0 - e * math.sin(lat2)) / (1.0 + e * math.sin(lat2)))
    aux0 = math.sqrt((1.0 - e * math.sin(lat0)) / (1.0 + e * math.sin(lat0)))
    t1 = ((1.0 - math.tan(lat1/2.0)) / (1.0 + math.tan(lat1/2.0))) / pow(aux1, e)
    t2 = ((1.0 - math.tan(lat2/2.0)) / (1.0 + math.tan(lat2/2.0))) / pow(aux2, e)
    t0 = ((1.0 - math.tan(lat0/2.0)) / (1.0 + math.tan(lat0/2.0))) / pow(aux0, e)

    if lat1 == lat2:
        n = math.sin(lat1)
    else:
        n = (math.log(m1) - math.log(m2)) / (math.log(t1) - math.log(t2))

    f = m1 / (n * pow(t1, n))
    ro0 = semi_eixo * f * pow(t0, n)

    sinal = int(n / abs(n))
    ro = math.sqrt(x*x + (ro0-y)*(ro0-y))
    ro *= sinal
    teta = math.atan(x / (ro0-y))
    t = pow((ro / (semi_eixo * f)), 1.0/n)
    xx = pi/2.0 - 2.0 * math.atan(t)
    aux3 = equad/2.0 + 5.0*equad*equad/24.0 + equad*equad*equad/12.0
    aux4 = 7.0*equad*equad/48.0 + 29.0*equad*equad*equad/240.0
    aux5 = (7.0*equad*equad*equad/120.0) * math.sin(12.0 * math.atan(t))

    lat = xx + aux3 * math.sin(4.0 * math.atan(t)) - aux4 * math.sin(8.0 * math.atan(t)) + aux5
    lon = teta / n + lon0

    return lat, lon

def geo_to_merc(lat, lon, lat1, lon0, semi_eixo, achat):
    """
    Transforma coordenadas geodésicas em coordenadas Mercator

    Args:
        lat: latitude em radianos
        lon: longitude em radianos
        lat1: latitude padrão ou reduzida em radianos
        lon0: meridiano origem em radianos
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide

    Returns:
        tuple: (x, y) coordenadas Mercator em metros
    """
    equad = 2.0 * achat - pow(achat, 2)
    aux1 = (1.0 + math.tan(lat / 2.0)) / (1.0 - math.tan(lat / 2.0))
    aux2 = (equad + equad*equad/4.0 + equad*equad*equad/8.0) * math.sin(lat)
    aux3 = (equad*equad/12.0 + equad*equad*equad/16.0) * math.sin(3.0*lat)
    aux4 = (equad*equad*equad/80.0) * math.sin(5.0*lat)
    aux5 = math.cos(lat1)
    aux6 = 1.0 / math.sqrt(1.0 - equad * pow(math.sin(lat1), 2))

    x = semi_eixo * (lon - lon0) * aux5 * aux6
    y = semi_eixo * (math.log(aux1) - aux2 + aux3 - aux4) * aux5 * aux6

    return x, y

def merc_to_geo(x, y, lat1, lon0, semi_eixo, achat):
    """
    Transforma coordenadas Mercator em coordenadas geodésicas

    Args:
        x: coordenada Mercator x em metros
        y: coordenada Mercator y em metros
        lat1: latitude padrão ou reduzida em radianos
        lon0: meridiano origem em radianos
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide

    Returns:
        tuple: (lat, lon) coordenadas geodésicas em radianos
    """
    pi = math.pi
    equad = 2.0 * achat - pow(achat, 2)

    aux1 = math.cos(lat1)
    aux2 = 1.0 / math.sqrt(1.0 - equad * pow(math.sin(lat1), 2))
    x_scaled = x / (aux1 * aux2)
    y_scaled = y / (aux1 * aux2)
    t = math.exp(-y_scaled / semi_eixo)
    xx = pi/2.0 - 2.0 * math.atan(t)
    aux3 = (equad/2.0 + 5.0*equad*equad/24.0 + equad*equad*equad/12.0) * math.sin(4.0 * math.atan(t))
    aux4 = -(7.0*equad*equad/48.0 + 29.0*equad*equad*equad/240.0) * math.sin(8.0 * math.atan(t))
    aux5 = (7.0*equad*equad*equad/120.0) * math.sin(12.0 * math.atan(t))

    lat = xx + aux3 + aux4 + aux5
    lon = x_scaled / semi_eixo + lon0

    return lat, lon

def geo_to_alb(lat, lon, lat0, lon0, lat1, lat2, semi_eixo, achat):
    """
    Transforma coordenadas geodésicas em coordenadas Albers

    Args:
        lat: latitude em radianos
        lon: longitude em radianos
        lat0: paralelo origem em radianos
        lon0: meridiano origem em radianos
        lat1: paralelo padrão 1 em radianos
        lat2: paralelo padrão 2 em radianos
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide

    Returns:
        tuple: (x, y) coordenadas Albers em metros
    """
    equad = 2.0 * achat - pow(achat, 2)
    e = math.sqrt(equad)

    m1 = math.cos(lat1) / math.sqrt(1.0 - equad * pow(math.sin(lat1), 2))
    m2 = math.cos(lat2) / math.sqrt(1.0 - equad * pow(math.sin(lat2), 2))
    aux1 = math.sin(lat) / (1.0 - equad * pow(math.sin(lat), 2))
    aux10 = math.sin(lat0) / (1.0 - equad * pow(math.sin(lat0), 2))
    aux11 = math.sin(lat1) / (1.0 - equad * pow(math.sin(lat1), 2))
    aux12 = math.sin(lat2) / (1.0 - equad * pow(math.sin(lat2), 2))
    aux2 = math.log((1.0 - e * math.sin(lat)) / (1.0 + e * math.sin(lat)))
    aux20 = math.log((1.0 - e * math.sin(lat0)) / (1.0 + e * math.sin(lat0)))
    aux21 = math.log((1.0 - e * math.sin(lat1)) / (1.0 + e * math.sin(lat1)))
    aux22 = math.log((1.0 - e * math.sin(lat2)) / (1.0 + e * math.sin(lat2)))
    q0 = (1.0 - equad) * (aux10 - (1.0 / (2.0 * e)) * aux20)
    q1 = (1.0 - equad) * (aux11 - (1.0 / (2.0 * e)) * aux21)
    q2 = (1.0 - equad) * (aux12 - (1.0 / (2.0 * e)) * aux22)
    q = (1.0 - equad) * (aux1 - (1.0 / (2.0 * e)) * aux2)
    n = (m1*m1 - m2*m2) / (q2 - q1)
    c = m1*m1 + n*q1
    ro0 = semi_eixo * math.sqrt(c - n*q0) / n
    teta = n * (lon - lon0)
    ro = semi_eixo * math.sqrt(c - n*q) / n

    x = ro * math.sin(teta)
    y = ro0 - ro * math.cos(teta)

    return x, y

def alb_to_geo(x, y, lat0, lon0, lat1, lat2, semi_eixo, achat):
    """
    Transforma coordenadas Albers em coordenadas geodésicas

    Args:
        x: coordenada Albers x em metros
        y: coordenada Albers y em metros
        lat0: paralelo origem em radianos
        lon0: meridiano origem em radianos
        lat1: paralelo padrão 1 em radianos
        lat2: paralelo padrão 2 em radianos
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide

    Returns:
        tuple: (lat, lon) coordenadas geodésicas em radianos
    """
    sinal = int(lat2 / abs(lat2))
    equad = 2.0 * achat - pow(achat, 2)
    e = math.sqrt(equad)

    m1 = math.cos(lat1) / math.sqrt(1.0 - equad * pow(math.sin(lat1), 2))
    m2 = math.cos(lat2) / math.sqrt(1.0 - equad * pow(math.sin(lat2), 2))
    aux10 = math.sin(lat0) / (1.0 - equad * pow(math.sin(lat0), 2))
    aux11 = math.sin(lat1) / (1.0 - equad * pow(math.sin(lat1), 2))
    aux12 = math.sin(lat2) / (1.0 - equad * pow(math.sin(lat2), 2))
    aux20 = math.log((1.0 - e * math.sin(lat0)) / (1.0 + e * math.sin(lat0)))
    aux21 = math.log((1.0 - e * math.sin(lat1)) / (1.0 + e * math.sin(lat1)))
    aux22 = math.log((1.0 - e * math.sin(lat2)) / (1.0 + e * math.sin(lat2)))
    q0 = (1.0 - equad) * (aux10 - (1.0 / (2.0 * e)) * aux20)
    q1 = (1.0 - equad) * (aux11 - (1.0 / (2.0 * e)) * aux21)
    q2 = (1.0 - equad) * (aux12 - (1.0 / (2.0 * e)) * aux22)
    n = (m1*m1 - m2*m2) / (q2 - q1)
    c = m1*m1 + n*q1
    ro0 = semi_eixo * math.sqrt(c - n*q0) / n
    ro = math.sqrt(x*x + (ro0 - y)*(ro0 - y))
    q = (c - (ro*ro*n*n / (semi_eixo*semi_eixo))) / n
    aux = ((1.0 - equad) / (2.0 * e)) * math.log((1.0 - e) / (1.0 + e))
    beta = math.asin(q / (1.0 - aux))
    aux1 = (equad/3.0 + 31.0*equad*equad/180.0 + 517.0*equad*equad*equad/5040.0) * math.sin(2.0*beta)
    aux2 = (23.0*equad*equad/360.0 + 251.0*equad*equad*equad/3780.0) * math.sin(4.0*beta)
    aux3 = (761.0*equad*equad*equad/45360.0) * math.sin(6.0*beta)
    teta = abs(math.atan(x / (ro0 - y)))

    if sinal == 1:
        if x < 0.0:
            teta = -teta

    if sinal == -1:
        if x > 0.0:
            teta *= sinal

    lat = beta + aux1 + aux2 + aux3
    lon = lon0 + (teta / n)

    return lat, lon

def poli_to_geo(x, y, semi_eixo, achat, lat0, lon0):
    """
    Transforma coordenadas policônicas em coordenadas geodésicas

    Args:
        x: coordenada policônica x em metros
        y: coordenada policônica y em metros
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide
        lat0: paralelo origem em radianos
        lon0: meridiano origem em radianos

    Returns:
        tuple: (lat, lon) coordenadas geodésicas em radianos
    """
    equad = 2.0 * achat - pow(achat, 2)

    # Para cálculo de m0
    aux01 = (1.0 - equad/4.0 - 3.0*equad*equad/64.0 - 5.0*equad*equad*equad/256.0) * lat0
    aux02 = (3.0*equad/8.0 + 3.0*equad*equad/32.0 + 45.0*equad*equad*equad/1024.0) * math.sin(2.0*lat0)
    aux03 = (15.0*equad*equad/256.0 + 45.0*equad*equad*equad/1024.0) * math.sin(4.0*lat0)
    aux04 = (35.0*equad*equad*equad/3072.0) * math.sin(6.0*lat0)
    m0 = semi_eixo * (aux01 - aux02 + aux03 - aux04)

    if y == (-m0):
        lat = 0.0
        lon = x / semi_eixo + lon0
        return lat, lon
    else:
        A = (m0 + y) / semi_eixo
        B = ((x*x) / (semi_eixo*semi_eixo)) + (A*A)

        lat2 = A  # Inicializando a latitude para a iteração
        cp = 1.0  # Inicializando para entrar no loop

        while cp > 0.000000001:
            C = (math.sqrt(1.0 - equad * math.sin(lat2) * math.sin(lat2))) * math.tan(lat2)

            # Cálculo de mn
            aux21 = (1.0 - equad/4.0 - 3.0*equad*equad/64.0 - 5.0*equad*equad*equad/256.0) * lat2
            aux22 = (3.0*equad/8.0 + 3.0*equad*equad/32.0 + 45.0*equad*equad*equad/1024.0) * math.sin(2.0*lat2)
            aux23 = (15.0*equad*equad/256.0 + 45.0*equad*equad*equad/1024.0) * math.sin(4.0*lat2)
            aux24 = (35.0*equad*equad*equad/3072.0) * math.sin(6.0*lat2)
            mn = semi_eixo * (aux21 - aux22 + aux23 - aux24)

            # Cálculo de mnl
            aux05 = 1.0 - equad/4.0 - 3.0*equad*equad/64.0 - 5.0*equad*equad*equad/256.0
            aux06 = 2.0 * (3.0*equad/8.0 + 3.0*equad*equad/32.0 + 45.0*equad*equad*equad/1024.0) * math.cos(2.0*lat2)
            aux07 = 4.0 * (15.0*equad*equad/256.0 + 45.0*equad*equad*equad/1024.0) * math.cos(4.0*lat2)
            aux08 = 6.0 * (35.0*equad*equad*equad/3072.0) * math.cos(6.0*lat2)
            mnl = semi_eixo * (aux05 - aux06 + aux07 - aux08)

            Ma = (mn * mn - m0 * m0) / (2.0 * mn)
            Mb = A * (mn + m0) / 2.0
            Mc = B / 2.0

            lat3 = lat2 - (A * C + ((x * x) / (semi_eixo * semi_eixo * C)) - Mb - Ma / math.cos(lat2)) / mnl
            cp = abs(lat3 - lat2)
            lat2 = lat3

        lat = lat2
        lon = lon0 + (math.atan(x * C / (m0 + y)) / math.sin(lat))

        return lat, lon

def geo_to_poli(lat, lon, semi_eixo, achat, lat0, lon0):
    """
    Transforma coordenadas geodésicas em coordenadas policônicas

    Args:
        lat: latitude em radianos
        lon: longitude em radianos
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide
        lat0: paralelo origem em radianos
        lon0: meridiano origem em radianos

    Returns:
        tuple: (x, y) coordenadas policônicas em metros
    """
    equad = 2.0 * achat - pow(achat, 2)

    # Para cálculo de m0
    aux1 = (1.0 - equad/4.0 - 3.0*equad*equad/64.0 - 5.0*equad*equad*equad/256.0) * lat0
    aux2 = (3.0*equad/8.0 + 3.0*equad*equad/32.0 + 45.0*equad*equad*equad/1024.0) * math.sin(2.0*lat0)
    aux3 = (15.0*equad*equad/256.0 + 45.0*equad*equad*equad/1024.0) * math.sin(4.0*lat0)
    aux4 = (35.0*equad*equad*equad/3072.0) * math.sin(6.0*lat0)
    m0 = semi_eixo * (aux1 - aux2 + aux3 - aux4)

    # Para cálculo de m
    aux10 = (1.0 - equad/4.0 - 3.0*equad*equad/64.0 - 5.0*equad*equad*equad/256.0) * lat
    aux20 = (3.0*equad/8.0 + 3.0*equad*equad/32.0 + 45.0*equad*equad*equad/1024.0) * math.sin(2.0*lat)
    aux30 = (15.0*equad*equad/256.0 + 45.0*equad*equad*equad/1024.0) * math.sin(4.0*lat)
    aux40 = (35.0*equad*equad*equad/3072.0) * math.sin(6.0*lat)
    m = semi_eixo * (aux10 - aux20 + aux30 - aux40)

    if lat == 0.0:
        x = semi_eixo * (lon - lon0)
        y = -m0
    else:
        cota = 1.0 / math.tan(lat)
        N = semi_eixo / math.sqrt(1.0 - equad * pow(math.sin(lat), 2))
        x = N * cota * math.sin((lon - lon0) * math.sin(lat))
        y = m - m0 + N * cota * (1.0 - math.cos((lon - lon0) * math.sin(lat)))

    return x, y

def geo_to_cilequi(lat, lon, r, lat1, lon0):
    """
    Transforma coordenadas geodésicas em coordenadas cilíndricas equidistantes

    Args:
        lat: latitude em radianos
        lon: longitude em radianos
        r: raio da esfera
        lat1: paralelo padrão em radianos
        lon0: meridiano origem em radianos

    Returns:
        tuple: (x, y) coordenadas cilíndricas equidistantes em metros
    """
    x = r * (lon - lon0) * math.cos(lat1)
    y = r * lat

    return x, y

def cilequi_to_geo(x, y, r, lat1, lon0):
    """
    Transforma coordenadas cilíndricas equidistantes em coordenadas geodésicas

    Args:
        x: coordenada cilíndrica equidistante x em metros
        y: coordenada cilíndrica equidistante y em metros
        r: raio da esfera
        lat1: paralelo padrão em radianos
        lon0: meridiano origem em radianos

    Returns:
        tuple: (lat, lon) coordenadas geodésicas em radianos
    """
    lat = y / r
    lon = lon0 + (x / (r * math.cos(lat1)))

    return lat, lon

def geo_to_miller(lat, lon, r, lon0):
    """
    Transforma coordenadas geodésicas em coordenadas Miller cilíndricas

    Args:
        lat: latitude em radianos
        lon: longitude em radianos
        r: raio da esfera
        lon0: meridiano origem em radianos

    Returns:
        tuple: (x, y) coordenadas Miller em metros
    """
    lat1 = lat * 4.0 / 5.0
    x = r * (lon - lon0)
    y = r * math.log(math.tan(math.pi/4.0 + lat1/2.0)) * 5.0 / 4.0

    return x, y

def miller_to_geo(x, y, r, lon0):
    """
    Transforma coordenadas Miller cilíndricas em coordenadas geodésicas

    Args:
        x: coordenada Miller x em metros
        y: coordenada Miller y em metros
        r: raio da esfera
        lon0: meridiano origem em radianos

    Returns:
        tuple: (lat, lon) coordenadas geodésicas em radianos
    """
    lat = 5.0 / 4.0 * (2.0 * math.atan(math.exp(y * 4.0 / 5.0 / r)) - math.pi / 2.0)
    lon = lon0 + (x / r)

    return lat, lon

def datum1_to_datum2(semi_eixo, achat, deltax, deltay, deltaz, lat1, lon1, h1, semi_eixo2, achat2, deltax2, deltay2, deltaz2):
    """
    Transforma coordenadas geodésicas de um datum para outro

    Args:
        semi_eixo: semi-eixo maior do elipsóide de origem
        achat: achatamento do elipsóide de origem
        deltax, deltay, deltaz: parâmetros de transformação do datum de origem
        lat1, lon1, h1: coordenadas geodésicas no datum de origem
        semi_eixo2: semi-eixo maior do elipsóide de destino
        achat2: achatamento do elipsóide de destino
        deltax2, deltay2, deltaz2: parâmetros de transformação do datum de destino

    Returns:
        tuple: (lat2, lon2, h2) coordenadas geodésicas no datum de destino em radianos
    """
    # Conversão das componentes geodésicas em componentes cartesianas
    equad = 2.0 * achat - pow(achat, 2)
    N = semi_eixo / math.sqrt(1.0 - equad * pow(math.sin(lat1), 2))

    X = (N + h1) * math.cos(lat1) * math.cos(lon1)
    Y = (N + h1) * math.cos(lat1) * math.sin(lon1)
    Z = (N * (1.0 - equad) + h1) * math.sin(lat1)

    # Aplicação dos parâmetros de transformação
    # Componentes cartesianas no datum WGS 84
    X2 = X - deltax + deltax2
    Y2 = Y - deltay + deltay2
    Z2 = Z - deltaz + deltaz2

    # Conversão das componentes cartesianas em componentes geodésicas
    equad2 = 2.0 * achat2 - pow(achat2, 2)
    e2 = equad2 / (1.0 - equad2)

    p = math.sqrt(X2*X2 + Y2*Y2)
    teta = math.atan(Z2 * semi_eixo2 / (p * semi_eixo2 * (1.0 - equad2)))

    lon2 = math.atan(Y2 / X2)
    
    if X2 < 0.0:
        lon2 += math.pi
    
    lat2 = math.atan((Z2 + e2 * semi_eixo2 * pow(math.sin(teta), 3)) / (p - equad2 * semi_eixo2 * pow(math.cos(teta), 3)))
    N2 = semi_eixo2 / math.sqrt(1.0 - equad2 * pow(math.sin(lat2), 2))
    h2 = p / math.cos(lat2) - N2

    return lat2, lon2, h2

def geo_to_gauss(lat, lon, lon_mc, semi_eixo, achat):
    """
    Transforma coordenadas geodésicas em coordenadas Gauss

    Args:
        lat: latitude em radianos
        lon: longitude em radianos
        lon_mc: longitude do meridiano central em radianos
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide

    Returns:
        tuple: (x, y) coordenadas Gauss em metros
    """
    equad = 2.0 * achat - pow(achat, 2)
    e2 = equad / (1.0 - equad)
    lon0 = lon_mc

    # Cálculo das constantes da projeção
    a0 = 1.0 - equad/4.0 - 3.0*equad*equad/64.0 - 5.0*equad*equad*equad/256.0
    a2 = 3.0/8.0 * (equad + equad*equad/4.0 + 15.0*equad*equad*equad/128.0)
    a4 = 15.0/256.0 * (equad*equad + 3.0*equad*equad*equad/4.0)
    a6 = 35.0/3072.0 * equad*equad*equad

    # Cálculo do arco de meridiano
    s = semi_eixo * (a0*lat - a2*math.sin(2.0*lat) + a4*math.sin(4.0*lat) - a6*math.sin(6.0*lat))

    dl = lon - lon0
    coslat = math.cos(lat)
    sinlat = math.sin(lat)
    coslat2 = coslat * coslat
    nu = semi_eixo / math.sqrt(1.0 - equad * sinlat * sinlat)
    psi = nu / semi_eixo
    psi2 = psi * psi
    psi3 = psi2 * psi
    psi4 = psi3 * psi
    t = math.tan(lat)
    t2 = t * t

    # Cálculo das coordenadas (x,y) na projeção de Gauss
    a = dl * coslat
    a2 = a * a
    a3 = a2 * a
    a4 = a3 * a
    a5 = a4 * a
    a6 = a5 * a

    # Cálculo de x
    t1 = nu * sinlat * coslat * a2 / 2.0
    t2 = nu * sinlat * coslat3 * (4.0*psi2 + psi - t2) * a4 / 24.0
    t3 = nu * sinlat * coslat5 * (8.0*psi4*(11.0-24.0*t2) - 28.0*psi3*(1.0-6.0*t2) + psi2*(1.0-32.0*t2) - psi*2.0*t2 + t4) * a6 / 720.0
    x = s + t1 + t2 + t3

    # Cálculo de y
    coslat3 = coslat2 * coslat
    coslat4 = coslat3 * coslat
    coslat5 = coslat4 * coslat
    t4 = t2 * t2

    t1 = nu * a
    t2 = nu * coslat3 * (psi - t2) * a3 / 6.0
    t3 = nu * coslat5 * (4.0*psi3*(1.0-6.0*t2) + psi2*(1.0+8.0*t2) - psi*2.0*t2 + t4) * a5 / 120.0
    y = t1 + t2 + t3

    return x, y

def gauss_to_geo(x, y, lon_mc, semi_eixo, achat):
    """
    Transforma coordenadas Gauss em coordenadas geodésicas

    Args:
        x: coordenada Gauss x em metros
        y: coordenada Gauss y em metros
        lon_mc: longitude do meridiano central em radianos
        semi_eixo: semi-eixo maior do elipsóide
        achat: achatamento do elipsóide

    Returns:
        tuple: (lat, lon) coordenadas geodésicas em radianos
    """
    equad = 2.0 * achat - pow(achat, 2)
    e2 = equad / (1.0 - equad)
    e4 = e2 * e2
    e6 = e4 * e2
    lon0 = lon_mc

    # Cálculo das constantes da projeção
    a0 = 1.0 - equad/4.0 - 3.0*equad*equad/64.0 - 5.0*equad*equad*equad/256.0
    a2 = 3.0/8.0 * (equad + equad*equad/4.0 + 15.0*equad*equad*equad/128.0)
    a4 = 15.0/256.0 * (equad*equad + 3.0*equad*equad*equad/4.0)
    a6 = 35.0/3072.0 * equad*equad*equad
    
    a_barra = semi_eixo * (1.0 - equad)
    b0 = a0
    b2 = -a2
    b4 = a4
    b6 = -a6

    # Cálculo da latitude de um ponto no elipsóide
    # usando o método de Newton-Raphson
    f = x / a_barra
    lat1 = f
    erro = 1.0
    
    while erro > 1e-10:
        f1 = b0*lat1 - b2*math.sin(2.0*lat1) + b4*math.sin(4.0*lat1) - b6*math.sin(6.0*lat1) - f
        f2 = b0 - 2.0*b2*math.cos(2.0*lat1) + 4.0*b4*math.cos(4.0*lat1) - 6.0*b6*math.cos(6.0*lat1)
        lat2 = lat1 - f1/f2
        erro = abs(lat2-lat1)
        lat1 = lat2
    
    lat = lat1
    coslat = math.cos(lat)
    sinlat = math.sin(lat)
    coslat2 = coslat * coslat
    coslat3 = coslat2 * coslat
    coslat4 = coslat3 * coslat
    coslat5 = coslat4 * coslat
    nu = semi_eixo / math.sqrt(1.0 - equad * sinlat * sinlat)
    psi = nu / semi_eixo
    psi2 = psi * psi
    psi3 = psi2 * psi
    psi4 = psi3 * psi
    t = math.tan(lat)
    t2 = t * t
    t4 = t2 * t2
    
    # Cálculo de lat e lon
    # Cálculo de lat
    b = t / (2.0 * nu * coslat)
    b2 = b * b
    
    t1 = t * (1.0+psi) * y*y / (2.0 * nu*nu)
    t2 = t * (5.0 + 3.0*t2 + 6.0*psi*(1.0-t2) - 6.0*psi2 - 3.0*psi*psi*t2 - 9.0*t2*psi2) * pow(y,4.0) / (24.0 * pow(nu,4.0))
    lat = lat - t1 + t2
    
    # Cálculo de lon
    t1 = y / (nu * coslat)
    t2 = (1.0 + 2.0*t2 + psi) * pow(y,3.0) / (6.0 * pow(nu,3.0) * coslat)
    lon = lon0 + t1 - t2
    
    return lat, lon

def define_mer_cent(lon):
    """
    Define os meridianos centrais da UTM

    Args:
        lon: longitude em radianos

    Returns:
        tuple: (mc1_utm, mc2_utm) com os meridianos centrais em radianos
    """
    # Converte para graus
    long_deg = lon * 180.0 / math.pi
    
    # Normaliza para o intervalo -180 a 180
    while long_deg > 180.0:
        long_deg -= 360.0
    while long_deg < -180.0:
        long_deg += 360.0
    
    # Determina o fuso UTM
    fuso = int((long_deg + 180.0) / 6.0) + 1
    if fuso > 60:
        fuso = 1
    
    # Calcula o meridiano central do fuso
    mc_deg = (fuso - 1) * 6.0 - 177.0
    mc1_utm = mc_deg * math.pi / 180.0
    
    # Calcula o meridiano central do fuso adjacente
    if long_deg > mc_deg:
        mc2_utm = ((fuso) * 6.0 - 177.0) * math.pi / 180.0
    else:
        mc2_utm = ((fuso-2) * 6.0 - 177.0) * math.pi / 180.0
        if mc2_utm < -math.pi:
            mc2_utm += 2.0 * math.pi
    
    return mc1_utm, mc2_utm

def grausDecimais_to_radianos(decimal):
    """
    Converte graus decimais para radianos
    
    Args:
        decimal: valor em graus decimais
        
    Returns:
        float: valor em radianos
    """
    return decimal * math.pi / 180.0

def radianos_to_grausDecimais(radianos):
    """
    Converte radianos para graus decimais
    
    Args:
        radianos: valor em radianos
        
    Returns:
        float: valor em graus decimais
    """
    return radianos * 180.0 / math.pi

def gms_to_decimal(graus, minutos, segundos):
    """
    Converte Graus, Minutos e Segundos para decimal
    
    Args:
        graus: valor em graus
        minutos: valor em minutos
        segundos: valor em segundos
        
    Returns:
        float: valor em graus decimais
    """
    sinal = -1 if graus < 0 else 1
    return sinal * (abs(graus) + minutos/60.0 + segundos/3600.0)

def decimal_to_gms(decimal):
    """
    Converte decimal para Graus, Minutos e Segundos
    
    Args:
        decimal: valor em graus decimais
        
    Returns:
        tuple: (graus, minutos, segundos)
    """
    sinal = -1 if decimal < 0 else 1
    decimal = abs(decimal)
    graus = int(decimal)
    resto = decimal - graus
    minutos = int(resto * 60)
    segundos = (resto * 60 - minutos) * 60
    
    return sinal * graus, minutos, segundos

def get_datum_params(datum_id):
    """
    Retorna os parâmetros do datum a partir do ID
    
    Args:
        datum_id: identificador do datum
        
    Returns:
        dict: parâmetros do datum ou None se não encontrado
    """
    if datum_id in DATUM_PARAMS:
        params = DATUM_PARAMS[datum_id]
        return {
            "nome": params[0],
            "semi_eixo": params[1],
            "achatamento": params[2],
            "deltax": params[3],
            "deltay": params[4], 
            "deltaz": params[5]
        }
    return None


def run(iface):
    """
    Função para iniciar o conversor
    
    Args:
        iface: interface do QGIS
    """
    conversor = ConversorGeoToUtm(iface)
    conversor.run()
