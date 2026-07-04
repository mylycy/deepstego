import jpegio as jio
from src.utils import binary_to_text, extract_bit, text_to_binary, DELIMITER


def decode(image_path: str) -> str:
    """
    Extracts a hidden message from a JPEG image using DCT steganography.
    
    Args:
        image_path: Path to the stego JPEG image
    
    Returns:
        The hidden message, or empty string if none found
    """
    # Load the JPEG file and access its DCT coefficients directly
    # jpegio reads the raw DCT coefficients without converting to pixels
    jpg = jio.read(image_path)

    # coef_arrays[0] is the Y (luminance) channel
    # JPEG uses YCbCr color space instead of RGB
    # Y = brightness, Cb/Cr = color — we hide data in Y because it's the most stable
    channel = jpg.coef_arrays[0]
    height, width = channel.shape

    # accumulate extracted bits here
    bits = ""

    # convert the delimiter string to binary so we can detect it in the bit stream
    delimiter_bits = text_to_binary(DELIMITER)

    # iterate over every 8x8 block in the image
    # JPEG divides images into 8x8 blocks and applies DCT to each one
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            # read the coefficient at position [0,1] of this block
            # in the full matrix, block [y,x]'s coefficient [0,1] is at column x+1
            coef = int(channel[y, x + 1])

            # extract the bit hidden in this coefficient (based on parity)
            bits += extract_bit(coef)

            # check if we've accumulated enough bits to contain the delimiter
            if delimiter_bits in bits:
                # split at the delimiter and return only the message part
                text_bits = bits.split(delimiter_bits)[0]
                return binary_to_text(text_bits)

    # delimiter not found — no hidden message in this image
    return ""