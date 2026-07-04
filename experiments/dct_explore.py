import numpy as np
from scipy.fftpack import dct, idct
from PIL import Image

# abre a imagem e pega só o canal R (mais simples pra começar)
img = Image.open("images/original/astronaut.jpg").convert("RGB")
pixels = np.array(img)
canal_r = pixels[:, :, 0].astype(float)

# pega um bloco 8x8 do canto superior esquerdo
bloco = canal_r[0:8, 329:337]

print("Bloco de pixels 8x8:")
print(bloco.astype(int))

# aplica DCT no bloco
coeficientes = dct(dct(bloco.T, norm='ortho').T, norm='ortho')

print("\nCoeficientes DCT:")
print(coeficientes.astype(int))

print("Valor máximo do canal R:", canal_r.max())
print("Onde tem pixels não-zero:", np.argwhere(canal_r > 0)[:5])