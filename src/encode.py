import jpegio as jio
from src.utils import text_to_binary, hide_bit, validate_image, DELIMITER


def encode(image_path: str, message: str, output_path: str) -> None:
    """
    Hides a message inside a JPEG image using DCT steganography.
    
    Args:
        image_path: Path to the cover JPEG image
        message: Secret message to hide
        output_path: Path to save the stego image
    
    Raises:
        ValueError: If the image is too large or has insufficient DCT coefficients
    """
    # validate the image before doing anything
    # this raises ValueError with a clear message if the image is not suitable
    validate_image(image_path, message)

    # Load the JPEG file and access its DCT coefficients directly
    jpg = jio.read(image_path)
    channel = jpg.coef_arrays[0]
    height, width = channel.shape

    bits = text_to_binary(message + DELIMITER)
    bit_index = 0

    for y in range(0, height, 8):
        for x in range(0, width, 8):
            if bit_index >= len(bits):
                break
            coef = int(channel[y, x + 1])
            channel[y, x + 1] = hide_bit(coef, bits[bit_index])
            bit_index += 1

    jpg.coef_arrays[0] = channel
    jio.write(jpg, output_path)
    print(f"Saved to: {output_path}")
    print(f"Bits hidden: {bit_index} of {len(bits)}")