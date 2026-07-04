import jpegio as jio

# Delimiter used to mark the end of a hidden message
# The encoder appends this to the message before hiding
# The decoder stops extracting bits when it finds this sequence
DELIMITER = "#####END#####"

def validate_image(image_path: str, message: str) -> None:
    """
    Validates that the image is suitable for DCT steganography.
    Raises ValueError with a clear message if validation fails.
    """
    jpg = jio.read(image_path)
    channel = jpg.coef_arrays[0]
    height, width = channel.shape

    # check 1: WhatsApp resizes images larger than 1600px
    if max(width, height) > 1600:
        raise ValueError("Image is too large. Maximum size is 1600x1600 pixels.")

    # check 2: count available blocks and compare with bits needed
    bits_needed = len(text_to_binary(message + DELIMITER))
    available_blocks = 0
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            if channel[y, x + 1] != 0:
                available_blocks += 1

    if available_blocks < bits_needed:
        raise ValueError(
            f"Image has insufficient DCT coefficients. "
            f"Need {bits_needed} blocks, but only {available_blocks} available. "
            f"Use a photo with more texture and detail."
        )

def text_to_binary(text: str) -> str:
    """Converts a string into a sequence of bits (0s and 1s).
    
    Each character is encoded as UTF-8 bytes, then each byte
    is represented as 8 binary digits (e.g. 'H' -> '01001000').
    """
    binary_chars = []

    # encode the string to bytes using UTF-8
    # this handles regular characters, accents, emojis, etc.
    for byte in text.encode("utf-8"):
        # format each byte as exactly 8 binary digits
        # :08b means: binary format, minimum 8 digits, padded with zeros
        binary_chars.append(f"{byte:08b}")

    # join all 8-bit chunks into one long string
    return "".join(binary_chars)


def binary_to_text(binary: str) -> str:
    """Converts a sequence of bits back into a string.
    
    This is the exact reverse of text_to_binary.
    """
    # split the bit string into chunks of 8 (one chunk = one byte)
    chunks = [binary[i:i+8] for i in range(0, len(binary), 8)]

    # convert each 8-bit chunk from binary string to integer
    # int(chunk, 2) means: parse chunk as a base-2 (binary) number
    numbers = [int(chunk, 2) for chunk in chunks]

    # convert the list of integers to a bytes object
    # then decode back to a UTF-8 string
    return bytes(numbers).decode("utf-8")


def hide_bit(coef: int, bit: str) -> int:
    """Hides a single bit inside a DCT coefficient using parity.
    
    Strategy:
        even coefficient = bit 0
        odd  coefficient = bit 1
    
    If the coefficient already has the correct parity, it is unchanged.
    Otherwise, we add 1 to flip the parity.
    """
    bit_int = int(bit)

    # check if the current parity already matches the bit we want to hide
    if coef % 2 == bit_int:
        return coef       # already correct, no change needed

    return coef + 1       # flip parity by adding 1


def extract_bit(coef: int) -> str:
    """Extracts the bit hidden in a DCT coefficient.
    
    Reads the parity of the coefficient:
        even -> '0'
        odd  -> '1'
    
    Uses abs() to handle negative coefficients correctly.
    """
    return str(abs(coef) % 2)