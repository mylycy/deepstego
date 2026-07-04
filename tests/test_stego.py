import unittest
import numpy as np
from PIL import Image
from src.utils import text_to_binary, binary_to_text, hide_bit, extract_bit
from src.encode import encode
from src.decode import decode

TEST_COVER = "images/covers/test_cover.jpg"
TEST_STEGO = "images/stego/test_stego.jpg"


class TestUtils(unittest.TestCase):

    def test_text_to_binary(self):
        result = text_to_binary("Hi")
        self.assertEqual(result, "0100100001101001")

    def test_binary_to_text(self):
        result = binary_to_text("0100100001101001")
        self.assertEqual(result, "Hi")

    def test_roundtrip_text(self):
        original = "Hello WhatsApp!"
        self.assertEqual(binary_to_text(text_to_binary(original)), original)

    def test_hide_bit(self):
        self.assertEqual(hide_bit(17, '0'), 18)
        self.assertEqual(hide_bit(17, '1'), 17)
        self.assertEqual(hide_bit(16, '0'), 16)
        self.assertEqual(hide_bit(16, '1'), 17)

    def test_extract_bit(self):
        self.assertEqual(extract_bit(17), '1')
        self.assertEqual(extract_bit(16), '0')
        self.assertEqual(extract_bit(-2), '0')
        self.assertEqual(extract_bit(-3), '1')


class TestEncodeDecode(unittest.TestCase):

    def setUp(self):
        """Creates a synthetic test image before each test."""
        pixels = np.random.randint(0, 255, (600, 600, 3), dtype=np.uint8)
        img = Image.fromarray(pixels)
        img.save(TEST_COVER)

    def tearDown(self):
        """Removes test images after each test."""
        import os
        for f in [TEST_COVER, TEST_STEGO]:
            if os.path.exists(f):
                os.remove(f)

    def test_simple_message(self):
        encode(TEST_COVER, "Hello!", TEST_STEGO)
        result = decode(TEST_STEGO)
        self.assertEqual(result, "Hello!")

    def test_message_with_accents(self):
        encode(TEST_COVER, "Olá, você!", TEST_STEGO)
        result = decode(TEST_STEGO)
        self.assertEqual(result, "Olá, você!")

    def test_long_message(self):
        message = "A" * 100
        encode(TEST_COVER, message, TEST_STEGO)
        result = decode(TEST_STEGO)
        self.assertEqual(result, message)


class TestValidation(unittest.TestCase):

    def test_rejects_large_image(self):
        # creates a 2000x2000 image (above 1600px threshold)
        pixels = np.random.randint(0, 255, (2000, 2000, 3), dtype=np.uint8)
        img = Image.fromarray(pixels)
        img.save("images/covers/test_large.jpg")

        with self.assertRaises(ValueError):
            encode("images/covers/test_large.jpg", "Hello!", "images/stego/test.jpg")

    def test_rejects_image_with_no_texture(self):
        # creates a completely black image (no DCT coefficients)
        pixels = np.zeros((600, 600, 3), dtype=np.uint8)
        img = Image.fromarray(pixels)
        img.save("images/covers/test_black.jpg")

        with self.assertRaises(ValueError):
            encode("images/covers/test_black.jpg", "Hello!", "images/stego/test.jpg")

    def tearDown(self):
        import os
        for f in ["images/covers/test_large.jpg", 
                  "images/covers/test_black.jpg",
                  "images/stego/test.jpg"]:
            if os.path.exists(f):
                os.remove(f)
if __name__ == "__main__":
    unittest.main()