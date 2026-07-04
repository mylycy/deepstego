# WhatsApp DCT Steganography

Hide secret messages inside JPEG images that survive WhatsApp compression.

## What is this?

Steganography is the art of hiding a message inside an innocent-looking file.
This project hides messages inside JPEG images using **DCT (Discrete Cosine Transform) steganography** - a technique that embeds data directly in the frequency coefficients of the image, making it survive WhatsApp's compression pipeline.


## How it works

JPEG images are not stored as raw pixels. Instead, they are divided into **8x8 pixel blocks**, and each block is transformed using DCT into a matrix of frequency coefficients.

- **Top-left coefficients** = low frequency = preserved by JPEG compression
- **Bottom-right coefficients** = high frequency = discarded by JPEG compression

One bit is hidden per block by modifying the **parity** of the `[0,1]` coefficient:

- Even coefficient = bit `0`
- Odd coefficient = bit `1`

Since the modification happens directly on JPEG coefficients (not pixels), the hidden data survives WhatsApp's recompression.

For a deeper explanation of each step, see below.

---

### Step 1: Text to bits

Every character in the message is converted to a sequence of 0s and 1s.
Each character becomes exactly 8 bits (one byte):

```
'H' → 01001000
'i' → 01101001
"Hi" → 0100100001101001
```

### Step 2: How JPEG stores images

**1. Divide into 8x8 blocks**
The image is cut into small 8x8 pixel squares:
```
┌────────┬────────┬────────┐
│ block  │ block  │ block  │
│  0,0   │  0,1   │  0,2   │
├────────┼────────┼────────┤
│ block  │ block  │ block  │
│  1,0   │  1,1   │  1,2   │
└────────┴────────┴────────┘
```

**2. Apply DCT (Discrete Cosine Transform)**
Each 8x8 block of pixels is transformed into an 8x8 matrix of frequency coefficients.
Think of it like an equalizer on a stereo — instead of describing sound sample by sample,
it describes how much bass, mid, and treble are present.

DCT does the same for images:

```
Pixels (what you see)       DCT Coefficients (how JPEG stores it)

154 152 148 144 ...         820  -30   12   -8  ...
156 150 149 145 ...    →      5    2   -8    3  ...
155 153 147 143 ...          -3    1    4   -2  ...
150 148 144 140 ...           2   -1   -2    1  ...
```

**3. Discard high-frequency coefficients**

```
┌─────────────────────────────┐
│ [0,0]  [0,1]  [0,2]  [0,3] │
│  DC    ← low frequency →    │
│ [1,0]                       │
│  ↑                          │
│ low                         │
│ freq                        │
│  ↓                          │
│ [3,0]          [3,3]  ...   │
│              high frequency │
│                  ↓          │
│              discarded      │
└─────────────────────────────┘
```

- `[0,0]` = DC coefficient = average brightness of the block (always preserved)
- `[0,1]`, `[1,0]` = low frequency = gentle variations (preserved)
- Bottom-right corner = high frequency = fine details (discarded by compression)

**Why this matters:**
LSB steganography modifies pixel values directly.
When JPEG recompresses the image, all coefficients are recalculated from scratch —
the pixel modifications are lost.

DCT steganography modifies the coefficients directly.
Since JPEG preserves low-frequency coefficients, the hidden data survives.

### Step 3: Hiding bits in coefficients

The `[0,1]` coefficient of each 8x8 block is used to hide one bit.
The technique is called **parity modulation**:

```
even coefficient → represents bit 0
odd  coefficient → represents bit 1
```

To hide a bit, the current parity is checked and adjusted if needed:

```
Target: bit 1, coefficient is -30 (even):
  -30 is even → parity is 0 → incorrect
  changed to -29 (odd) → parity is 1 → correct ✓

Target: bit 0, coefficient is 12 (even):
  12 is even → parity is 0 → already correct ✓
  no change needed
```

The modification is at most ±1 — completely invisible to the human eye.

### Step 4: Delimiter

A special delimiter string is appended to the message before hiding:

```
original message:         "Hello!"
message with delimiter:   "Hello!#####END#####"
```

The decoder extracts bits one block at a time, converts them back to text,
and stops as soon as the delimiter is found.

### Step 5: Why textured images work better

Not all coefficients survive WhatsApp's recompression.
Coefficients considered too small (close to zero) are discarded.

In a flat/dark image (like a black background), most `[0,1]` coefficients are zero
or very small — they get zeroed out during recompression, destroying the hidden data.

In a textured image (natural photo with details, colors, patterns),
the `[0,1]` coefficients are naturally larger — they survive recompression,
and the hidden data remains intact.

```
Flat image:     [0,1] = 1  → zeroed by WhatsApp → data lost ✗
Textured image: [0,1] = 47 → preserved by WhatsApp → data survives ✓
```

The encoder validates the image before hiding:
it counts how many blocks have non-zero `[0,1]` coefficients
and rejects the image if there are not enough for the message.

## Research findings

| Finding | Details |
|---|---|
| Size threshold | WhatsApp resizes images larger than **1600px** on any side |
| Aspect ratio | WhatsApp preserves the original aspect ratio when resizing |
| JPEG quality | WhatsApp uses high JPEG quality (~100) — minimal color loss |
| DCT steganography | SURVIVES WhatsApp when using textured images ≤ 1600px |
| LSB steganography | Does NOT survive WhatsApp |

## Requirements

- Python 3.12+
- Linux or Mac (Windows requires Visual C++ Build Tools for jpegio)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourname/stego-research.git
cd stego-research

# Create virtual environment (required on Linux/Mac)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Hide a message

```python
from src.encode import encode

encode(
    image_path="photo.jpg",
    message="secret message",
    output_path="stego.jpg"
)
```

### Reveal a message

```python
from src.decode import decode

message = decode("stego.jpg")
print(message)
```

### Image requirements

- Format: JPEG
- Maximum size: 1600x1600 pixels
- Must have texture/detail (not solid colors or very dark images)

## Run tests

```bash
python3 -m unittest tests.test_stego
```

## Project structure

```
stego-research/
├── src/
│   ├── encode.py
│   ├── decode.py
│   └── utils.py
├── tests/
│   └── test_stego.py
├── experiments/
│   ├── analysis.py
│   ├── dct_explore.py
│   ├── dct_stego.py
│   └── decode_dct.py
├── images/
│   ├── covers/
│   └── stego/
├── .github/
│   └── workflows/
│       └── tests.yml
├── requirements.txt
└── .gitignore
```

## Versioning

### Version 1 (current)
- DCT steganography that survives WhatsApp compression
- Automatic image validation
- 10 automated tests
- GitHub Actions CI

**Known limitations:**
- Only works with textured JPEG images ≤ 1600px
- Images with large dark/flat regions may fail

### Version 2 (planned)
- Repetition code (each bit repeated 3x)
- Improved compatibility with less textured images

### Version 3 (planned)
- Dynamic coefficient selection per image
- Works with virtually any JPEG image

## Contributing

This is an open research project. Contributions, issues, and experiments are welcome.
If you test this on Instagram or other platforms, please open an issue with your findings.

## License

MIT