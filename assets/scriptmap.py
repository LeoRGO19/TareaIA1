from PIL import Image

def pixel_art_a_binario(ruta_imagen):
    # Abrir la imagen y convertirla a escala de grises para mayor precisión
    img = Image.open(ruta_imagen).convert('L')
    ancho, alto = img.size
    
    resultado = []
    
    for y in range(alto):
        linea = []
        for x in range(ancho):
            brillo = img.getpixel((x, y))
            
            # En escala de grises, 0 es negro puro y 255 es blanco puro
            # Usamos un umbral de 128 por si hay tonos intermedios
            if brillo < 128:
                caracter = "1"  # Negro
            else:
                caracter = "0"  # Blanco
            
            # Agrega el número seguido de un espacio horizontal
            linea.append(caracter + " ")
            
        # Une los caracteres de la fila y elimina el espacio extra del final
        resultado.append("".join(linea).rstrip())
        
    return "\n".join(resultado)

# --- CONFIGURACIÓN Y EJECUCIÓN ---
archivo_origen = 'LaberintoCuello2.png'  # Cambia esto por el nombre de tu archivo de Paint
archivo_destino = 'mapa_laberinto_cuello_botella.txt'

try:
    texto_binario = pixel_art_a_binario(archivo_origen)
    
    # Guardar la matriz en un archivo de texto
    with open(archivo_destino, 'w', encoding='utf-8') as f:
        f.write(texto_binario)
        
    print(f"¡Listo! Tu matriz de 1s y 0s se ha guardado en '{archivo_destino}'")
    print("\nVista previa del resultado:")
    print(texto_binario[:500] + "\n...") # Muestra solo los primeros caracteres como muestra
    
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{archivo_origen}'. Verifícalo.")
except Exception as e:
    print(f"Ocurrió un error: {e}")
