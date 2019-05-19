#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 16:38:21 2018

@author: nicolas

Tiene 4 funciones.
1) configImagen
2) configCamara
3) adquirirImagen
4) adquirirNumero
--> 2 y 3 son para usar con camara web
--> 1 y 4 se pueden usar con imagenes en el disco
"""

import numpy as np
import cv2
from OCRauxiliar import convGris, mat2img, elegirCoord, setupROI, binarizar,\
     CargarBaseReescalar, comparar, mostrarWebcam, cutROI, binarizarUnaImagen
#     posibilidadesPorcentaje, suavizarImagen, fragmentDigitos, metodoSegmentos,

def configImagen(img):
    """
    Función para elegir ROI de una imagen del disco.
    Devuelve: coordenadas, cantidad de dígitos y los números de la base escalados.
    """
    fotoDif = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    # Recortar región de interés
    c_t = elegirCoord(fotoDif) # Coordenadas de referencia
    N = int(input("\n --> Inserte número de dígitos >> "))
    
    # Recortar ROI
    imROI = cutROI(fotoDif, c_t)
    #Binarizar
    imROI_bin = binarizarUnaImagen(imROI, mostrar=True)
    # Recortar y segmentar
    digitos = setupROI(imROI_bin, N, c_t)
#    # Binarización de prueba
#    binarizar(digitos, mostrar=True)
    # Cargar base
    num_base = CargarBaseReescalar("./img/numeros_base.png", digitos, mostrar=True)

    return c_t, N, num_base

def configCamara(cap):
    """
    Función para setear ROI usando cámara web.
    cap es una instancia VideoCapture del módulo cv2 (la cámara)
    """
    print("--- JediCapture 1.0 -- Seven Segment Optical Character Recognition ---")
    print("\n IMPORTANTE: cuando aparezca una figura, cerrarla presionando 'q' para que continúe el programa.")
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0) # Turn off autofocus
    print("[*] Objeto de cámara creado")
    # - - - - - - - - - - - - - - - - - - - - - - - -
    print("\n --> Montar display apagado...")
    mostrarWebcam(cap)
    ret, fondo = cap.read()
    imgApagado = convGris(fondo) #imagen float 32
    print("Fondo capturado.")
    # - - - - - - - - - - - - - - - - - - - - - - - -
    print("\n --> Encender display y presionar 'q' para adquirir primera imagen...")
    mostrarWebcam(cap)
    # Primeros pasos: eljo ROI y numero de digitos y cargo base
    ret, imagen = cap.read()
    imgPrendido = convGris(imagen) #imagen float 32
    print("Foto con dígitos capturada.")
    
    #%% - - - - - - - - - - - - - - - - - - - - - - - -
    
    fotoDif = mat2img(np.abs(imgApagado - imgPrendido)) #imagen uint8
    # Recortar región de interés
    c_t = elegirCoord(fotoDif) # Coordenadas de referencia
    N = int(input("\n --> Inserte número de dígitos >> "))
    # Recortar y segmentar
    digitos = setupROI(fotoDif, N, c_t)
    # Binarización de prueba
    binarizar(digitos, mostrar=True)
    # Cargar base
    num_base = CargarBaseReescalar("./img/numeros_base.png", digitos, mostrar=True)

    return imgApagado, c_t, N, num_base

def adquirirImagen(cap, imgApagado):
    """
    Función para capturar imagen de la cámara web
    """
    # Clear the buffer before reading
    for i in range(5):
        ret, imagen = cap.read()
    if not(ret):
        print("Error de adquisición...")
    imgPrendido = convGris(imagen) # Out: imagen float 32
    # Restarlas para marcar diferencias
    fotoDif = mat2img(np.abs(imgApagado - imgPrendido)) # Out: imagen uint8
    return fotoDif

def adquirirNumero(fotoDif, c_t, N, num_base, size):
    """
    Función que devuelve los resultados de dígitos posibles de la imagen fotoDif.
    """
    # Tomo el ROI de la foto en base a configImagen: c_t, N y num_base
    imROI = cutROI(fotoDif,c_t,mostrar=True)
    # Binarizo el ROI copmleto, con un método adaptativo
    imROI_bin = binarizarUnaImagen(imROI, size=size, mostrar=True)
    # Segmentación de dígitos
    digitos_bin = setupROI(imROI_bin, N, c_t, mostrar=True)

    res_posibles, confianzas = comparar(digitos_bin, num_base, mostrar=False)
    return res_posibles, confianzas