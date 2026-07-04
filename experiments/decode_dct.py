"""
decode_dct.py — DCT Steganography with jpegio (Intermediate Version — Deprecated)

This was our second attempt at DCT steganography, now using jpegio to read
and write DCT coefficients directly in the JPEG file.

Problem discovered here:
    We only hid bits in non-zero coefficients (if coef != 0).
    But the encoder and decoder counted non-zero coefficients differently
    after the modifications, causing misalignment.

    Example:
        Encoder: coef was 0, we skipped it
        After modification of nearby coefficients, that coef became non-zero
        Decoder: now sees it as non-zero and extracts a bit from it
        Result: bits are misaligned, message is corrupted

Fix applied in src/encode.py and src/decode.py:
    Process ALL coefficients at position [0,1] of each block,
    regardless of whether they are zero or not.
    This guarantees encoder and decoder always stay in sync.
"""

import jpegio as jio

DELIMITER = "#####END#####"


def text_to_binary(text: str) -> str:
    """Converts a string to a sequence of bits."""
    binary_chars = []
    for byte in text.encode("utf-8"):
        binary_chars.append(f"{byte:08b}")
    return "".join(binary_chars)


def binary_to_text(binary: str) -> str:
    """Converts a sequence of bits back to a string."""
    chunks = [binary[i:i+8] for i in range(0, len(binary), 8)]
    numbers = [int(chunk, 2) for chunk in chunks]
    return bytes(numbers).decode("utf-8")


def hide_bit(coef: int, bit: str) -> int:
    """Hides a bit in a DCT coefficient using parity."""
    bit_int = int(bit)
    if coef % 2 == bit_int:
        return coef
    return coef + 1


def extract_bit(coef: int) -> str:
    """Extracts a bit from a DCT coefficient using parity."""
    return str(abs(coef) % 2)


def encode_dct(image_path: str, message: str, output_path: str) -> None:
    """
    Hides a message in a JPEG image using DCT coefficients via jpegio.
    
    WARNING: This version skips zero coefficients, which causes misalignment
    with the decoder. Use src/encode.py for the correct implementation.
    """
    jpg = jio.read(image_path)
    channel = jpg.coef_arrays[0]
    height, width = channel.shape

    bits = text_to_binary(message + DELIMITER)
    bit_index = 0

    for y in range(0, height, 8):
        for x in range(0, width, 8):
            if bit_index >= len(bits):
                break
            coef = channel[y, x + 1]