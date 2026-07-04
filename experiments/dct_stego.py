import numpy as np
from scipy.fftpack import dct, idct
from PIL import Image

DELIMITER = "#####END#####"

def text_to_binary(text: str) -> str:
    binary_chars = []
    for byte in text.encode("utf-8"):
        binary_chars.append(f"{byte:08b}")
    return "".join(binary_chars)

def esconde_bit_em_coeficiente(coef: float, bit: str) -> float:
    valor = round(coef)
    paridade = valor % 2
    bit_int = int(bit)
    
    if paridade == bit_int:
        return float(valor)
    else:
        return float(valor + 1)
    
def extrai_bit_de_coeficiente(coef: float) -> str:
    valor = round(coef)
    return str(valor % 2)

def encode_dct(image_path: str, message: str, output_path: str):
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img, dtype=float)
    
    # pega só o canal R por enquanto
    canal = pixels[:, :, 0]
    altura, largura = canal.shape
    
    bits = text_to_binary(message + DELIMITER)  # converte mensagem em bits (você já sabe fazer isso)
    bit_index = 0

    for y in range(0, altura, 8):
        for x in range(0, largura, 8):
            if bit_index >= len(bits):
                break
            
            bloco = canal[y:y+8, x:x+8]
            
            # aplica DCT
            coefs = dct(dct(bloco.T, norm='ortho').T, norm='ortho')

            if y == 0 and x == 329:  # bloco onde tem pixels de verdade
                print("Coeficiente [0,1]:", coefs[0,1])
                print("Coeficiente [1,0]:", coefs[1,0])
                print("Coeficiente [0,0]:", coefs[0,0])
            
            # esconde bit no coeficiente [0,1]
            coefs[0, 1] = esconde_bit_em_coeficiente(coefs[0, 1], bits[bit_index])
            bit_index += 1
            
            # aplica DCT inversa
            bloco_novo = idct(idct(coefs.T, norm='ortho').T, norm='ortho')
            canal[y:y+8, x:x+8] = bloco_novo

    pixels[:, :, 0] = canal
    resultado = Image.fromarray(pixels.astype(np.uint8))
    resultado.save(output_path)
    print(f"Salvo em: {output_path}")
    print("Primeiros 50 bits da mensagem:", bits[:50])

if __name__ == "__main__":
    print(esconde_bit_em_coeficiente(17.3, '0'))
    print(esconde_bit_em_coeficiente(17.3, '1'))
    print(esconde_bit_em_coeficiente(16.7, '0'))
    print(esconde_bit_em_coeficiente(16.7, '1'))

    c = esconde_bit_em_coeficiente(17.3, '0')
    print("Escondeu 0, extraiu:", extrai_bit_de_coeficiente(c))

    c = esconde_bit_em_coeficiente(17.3, '1')
    print("Escondeu 1, extraiu:", extrai_bit_de_coeficiente(c))

    encode_dct("images/original/astronaut.jpg", "Hello WhatsApp!", "images/original/stego_dct.png")
