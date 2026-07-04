from PIL import Image
import numpy as np

import struct

def get_jpeg_quality(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    # procura pelo marcador de quantização JPEG (FFD8...FFDB)
    idx = data.find(b'\xff\xdb')
    if idx == -1:
        return "Não encontrado"
    # o valor de qualidade está codificado na tabela de quantização
    qtable = data[idx+4:idx+68]
    quality = 100 - (qtable[0] // 2)
    return quality

print("Qualidade JPEG WhatsApp:", get_jpeg_quality(
    "images/whatsapp/WhatsApp Image 2026-06-25 at 11.42.06 PM.jpeg"
))

original = Image.open("images/original/248-2000x2000.jpg").convert("RGB")
whatsapp = Image.open("images/whatsapp/WhatsApp Image 2026-06-25 at 11.42.06 PM.jpeg").convert("RGB")

print("Original:")
print("  Tamanho:", original.size)

print("WhatsApp:")
print("  Tamanho:", whatsapp.size)

print("Original:", original.size)
print("WhatsApp:", whatsapp.size)
print("Tamanhos iguais?", original.size == whatsapp.size)

if original.size != whatsapp.size:
    ratio_largura = whatsapp.size[0] / original.size[0]
    ratio_altura = whatsapp.size[1] / original.size[1]
    print(f"Ratio largura: {ratio_largura:.4f}")
    print(f"Ratio altura: {ratio_altura:.4f}")
else:
    print("Sem redimensionamento — imagem chegou intacta")