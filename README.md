# HTML Image Gallery Parser

A Python tool for extracting image links from HTML files and generating organized galleries grouped by date. Particularly useful for processing HTML exports from messaging applications or chat archives.

## Features

- 🔍 Recursively scans HTML files for image links
- 📅 Extracts dates from Russian text format and groups images by date
- 🖼️ Generates responsive HTML galleries with hover effects
- 🌐 Handles multiple file encodings (UTF-8, Windows-1251, CP1252)
- 📊 Provides detailed statistics and progress tracking
- 🎯 Supports various image formats (JPG, PNG, GIF, WebP, SVG, etc.)

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Manual Installation

```bash
pip install beautifulsoup4 tqdm lxml
```

## Usage

### Command Line Interface

```bash
# Basic usage
python image_gallery_parser.py -i /path/to/html/files

# Specify encoding and output directory
python image_gallery_parser.py -i ./html_exports -e windows-1251 -o ./output

# Enable verbose logging
python image_gallery_parser.py -i ./html_files --verbose
```

### Interactive Mode

If you don't specify an input directory, the tool will prompt you:

```bash
python image_gallery_parser.py
# Enter path to input directory: /path/to/your/html/files
```

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--input-dir` | `-i` | Path to directory containing HTML files | Required |
| `--encoding` | `-e` | File encoding | `utf-8` |
| `--output-dir` | `-o` | Output directory for generated gallery | Current directory |
| `--verbose` | `-v` | Enable verbose logging | Disabled |

## Output

The tool generates an HTML gallery file named `gallery_YYYYMMDD_HHMMSS.html` with:

- **Responsive grid layout** that adapts to screen size
- **Date-grouped sections** with image counts
- **Hover effects** and smooth transitions
- **Lazy loading** for better performance
- **Statistics** showing total images found

### Example Output Structure

```
Gallery Generated on 2024-01-15
├── 15.01.2024 (25 images)
├── 14.01.2024 (18 images)
└── 13.01.2024 (32 images)
```

## Supported File Formats

- **Images**: JPG, JPEG, PNG, GIF, BMP, WebP, SVG
- **HTML encoding**: UTF-8, Windows-1251, CP1252
- **Date formats**: Russian date format (e.g., "15 янв 2024")

## How It Works

1. **File Discovery**: Recursively finds all HTML files in the specified directory
2. **Content Parsing**: Uses BeautifulSoup to parse HTML and find image links
3. **Date Extraction**: Looks for Russian date patterns in message headers
4. **Gallery Generation**: Creates a responsive HTML gallery grouped by date
5. **Output**: Saves the gallery with timestamp and provides statistics

## Examples

### Processing Chat Exports

```bash
# Process Telegram chat exports
python image_gallery_parser.py -i ./telegram_exports

# Process with specific encoding
python image_gallery_parser.py -i ./chat_backup -e windows-1251
```

### Batch Processing

```bash
# Process multiple directories
for dir in export1 export2 export3; do
    python image_gallery_parser.py -i "$dir" -o "./galleries"
done
```

## Configuration

The tool can be configured by modifying the `Config` class or extending it:

```python
from image_gallery_parser import Config, ImageGalleryParser

config = Config(
    input_dir="/path/to/html",
    encoding="utf-8",
    output_dir="./galleries",
    image_extensions=[".jpg", ".png", ".gif"]  # Custom extensions
)

parser = ImageGalleryParser(config)
parser.parse_files()
parser.generate_html_gallery()
```

## Troubleshooting

### Common Issues

**No images found**
- Check if HTML files contain anchor tags with image links
- Verify the date format matches Russian pattern (DD MMM YYYY)
- Enable verbose mode with `-v` for detailed logging

**Encoding errors**
- Try different encodings: `-e windows-1251` or `-e cp1252`
- The tool automatically attempts multiple encodings

**Permission errors**
- Ensure read access to input directory
- Ensure write access to output directory

### Logging

Enable verbose logging to see detailed processing information:

```bash
python image_gallery_parser.py -i ./html_files --verbose
```

## Development

### Project Structure

```
├── image_gallery_parser.py  # Main application
├── requirements.txt         # Dependencies
├── README.md               # Documentation
├── .gitignore             # Git ignore rules
└── tests/                 # Unit tests (optional)
```

### Running Tests

```bash
python -m pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v1.0.0
- Initial release
- Basic HTML parsing and gallery generation
- Russian date format support
- Multiple encoding support
- Responsive gallery layout
