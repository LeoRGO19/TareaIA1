from pathlib import Path

from PIL import Image

COLORES_MAPA = {
    (255, 0, 0): "A",  # agente
    (255, 255, 255): "0",  # camino
    (0, 0, 0): "1",  # muro
    (0, 255, 0): "S",  # salida
}


def pixel_art_a_mapa(ruta_imagen):
    img = Image.open(ruta_imagen).convert('RGB')
    ancho, alto = img.size
    resultado = []

    for y in range(alto):
        linea = []
        for x in range(ancho):
            color = img.getpixel((x, y))
            if color not in COLORES_MAPA:
                raise ValueError(
                    f"Color no reconocido en ({x}, {y}): #{color[0]:02X}{color[1]:02X}{color[2]:02X}"
                )
            linea.append(COLORES_MAPA[color])
        resultado.append(" ".join(linea))

    return "\n".join(resultado)

# --- CONFIGURACIÓN Y EJECUCIÓN ---
carpeta_assets = Path(__file__).resolve().parent
archivo_origen = carpeta_assets / 'Corporativo.png'  # Cambia esto por el nombre de tu archivo de Paint
archivo_destino = carpeta_assets / 'mapa_corporativo50x50.txt'

try:
    texto_mapa = pixel_art_a_mapa(archivo_origen)
    
    # Guardar la matriz en un archivo de texto
    with open(archivo_destino, 'w', encoding='utf-8') as f:
        f.write(texto_mapa)
        
    print(f"¡Listo! Tu mapa se ha guardado en '{archivo_destino}'")
    print("\nVista previa del resultado:")
    print(texto_mapa[:500] + "\n...") # Muestra solo los primeros caracteres como muestra
    
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{archivo_origen}'. Verifícalo.")
except Exception as e:
    print(f"Ocurrió un error: {e}")
