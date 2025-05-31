import os
import re
import html
import logging
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Set, Tuple
from dataclasses import dataclass
from pathlib import Path
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from glob import glob
from collections import defaultdict


# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration for the image gallery parser"""
    input_dir: str
    encoding: str = 'utf-8'
    output_dir: str = '.'
    image_extensions: List[str] = None
    
    def __post_init__(self):
        if self.image_extensions is None:
            self.image_extensions = [
                ".jpg", ".jpeg", ".png", ".gif", 
                ".bmp", ".webp", ".svg"
            ]


class ImageGalleryParser:
    """
    Parser for extracting images from HTML files and creating galleries.
    
    This class processes HTML files to find image links, extracts dates
    from Russian text format, and generates an organized HTML gallery.
    """
    
    # Date pattern for Russian date format (e.g., "15 янв 2024")
    DATE_PATTERN = re.compile(r'(\d{1,2})\s([а-я]{3})\s(\d{4})', re.IGNORECASE)
    
    # Russian month abbreviations to numbers
    MONTHS = {
        'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 
        'мая': '05', 'июн': '06', 'июл': '07', 'авг': '08', 
        'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'
    }
    
    def __init__(self, config: Config):
        """
        Initialize the parser with configuration.
        
        Args:
            config: Configuration object with parsing parameters
        """
        self.config = config
        self.photos_by_date: Dict[str, List[str]] = defaultdict(list)
        self.all_links: Set[str] = set()
        
    def extract_date(self, text: str) -> Optional[str]:
        """
        Extract date from Russian text format.
        
        Args:
            text: Text containing date in format "DD MMM YYYY"
        
        Returns:
            Date in format "YYYY.MM.DD" or None if not found
        """
        match = self.DATE_PATTERN.search(text)
        if not match:
            return None
            
        day, mon_rus, year = match.groups()
        month = self.MONTHS.get(mon_rus[:3].lower())
        
        if not month:
            return None
            
        return f"{year}.{month.zfill(2)}.{day.zfill(2)}"
    
    def read_file_with_encoding(self, file_path: str) -> Optional[BeautifulSoup]:
        """
        Read HTML file with multiple encoding attempts.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            BeautifulSoup object or None if file cannot be read
        """
        encodings = ["utf-8", "windows-1251", "cp1252"]
        
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as file:
                    return BeautifulSoup(file, "html.parser")
            except (UnicodeDecodeError, FileNotFoundError) as e:
                logger.debug(f"Failed to read {file_path} with {encoding}: {e}")
                continue
        
        logger.warning(f"Could not read file: {file_path}")
        return None
    
    def is_image_link(self, href: str) -> bool:
        """
        Check if a link points to an image file.
        
        Args:
            href: URL or file path to check
            
        Returns:
            True if the link appears to be an image
        """
        clean_href = href.split('?')[0]  # Remove URL parameters
        ext = os.path.splitext(clean_href)[1].lower()
        return ext in self.config.image_extensions
    
    def find_html_files(self) -> List[str]:
        """
        Find all HTML files in the input directory recursively.
        
        Returns:
            List of HTML file paths
        """
        try:
            html_files = glob(
                os.path.join(self.config.input_dir, "**", "*.html"), 
                recursive=True
            )
            logger.info(f"Found {len(html_files)} HTML files")
            return html_files
        except Exception as e:
            logger.error(f"Error finding HTML files: {e}")
            return []
    
    def process_html_file(self, file_path: str) -> None:
        """
        Process a single HTML file to extract image links.
        
        Args:
            file_path: Path to the HTML file to process
        """
        soup = self.read_file_with_encoding(file_path)
        if not soup:
            return
        
        # Find all anchor tags with href attributes
        for link_tag in soup.find_all("a", href=True):
            href = link_tag["href"].strip()
            
            if not self.is_image_link(href):
                continue
                
            self.all_links.add(href)
            
            # Look for date in the message context
            message = link_tag.find_parent("div", class_="message")
            if message:
                header = message.find("div", class_="message__header")
                if header:
                    date_key = self.extract_date(
                        header.get_text(separator=" ", strip=True)
                    )
                    if date_key:
                        self.photos_by_date[date_key].append(href)
    
    def parse_files(self) -> None:
        """Parse all HTML files and extract image links."""
        html_files = self.find_html_files()
        
        if not html_files:
            logger.warning("No HTML files found to process")
            return
        
        start_time = time.time()
        
        with tqdm(total=len(html_files), desc="Parsing files", unit="file") as pbar:
            for file_path in html_files:
                try:
                    self.process_html_file(file_path)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                finally:
                    pbar.update(1)
        
        # Sort images within each date
        for date in self.photos_by_date:
            self.photos_by_date[date].sort()
        
        elapsed_time = time.time() - start_time
        logger.info(f"Processing completed in {elapsed_time:.2f} seconds")
        logger.info(f"Found {len(self.all_links)} total images")
    
    def generate_html_content(self) -> List[str]:
        """
        Generate HTML content for the gallery.
        
        Returns:
            List of HTML content lines
        """
        html_content = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            "    <meta charset=\"UTF-8\">",
            "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
            "    <title>Image Gallery</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f9f9f9; }",
            "        h1 { text-align: center; margin-bottom: 20px; color: #333; }",
            "        h2 { margin-top: 40px; border-bottom: 2px solid #ccc; padding-bottom: 5px; color: #555; }",
            "        .gallery { display: grid; gap: 20px; padding: 20px; }",
            "        .stats { text-align: center; margin-bottom: 30px; color: #666; }",
            "        @media (min-width: 1200px) { .gallery { grid-template-columns: repeat(12, 1fr); } }",
            "        @media (min-width: 800px) and (max-width: 1199px) { .gallery { grid-template-columns: repeat(10, 1fr); } }",
            "        @media (max-width: 799px) { .gallery { grid-template-columns: repeat(6, 1fr); } }",
            "        .gallery a { position: relative; overflow: hidden; border-radius: 8px; transition: transform 0.3s; }",
            "        .gallery a:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }",
            "        .gallery img { width: 100%; height: auto; display: block; object-fit: cover; }",
            "        .no-images { text-align: center; color: #888; margin-top: 50px; }",
            "    </style>",
            "</head>",
            "<body>",
            "    <h1>Image Gallery</h1>",
            f"    <div class=\"stats\">Total images found: {len(self.all_links)}</div>"
        ]
        
        sorted_dates = sorted(self.photos_by_date.keys())
        
        if not sorted_dates:
            html_content.append("    <div class=\"no-images\">No images found.</div>")
        else:
            for date_key in sorted_dates:
                # Convert YYYY.MM.DD to DD.MM.YYYY for display
                human_date = '.'.join(reversed(date_key.split('.')))
                image_count = len(self.photos_by_date[date_key])
                
                html_content.extend([
                    f"    <h2>{human_date} ({image_count} images)</h2>",
                    "    <div class=\"gallery\">"
                ])
                
                for link in self.photos_by_date[date_key]:
                    safe_link = html.escape(link, quote=True)
                    html_content.append(
                        f"        <a href=\"{safe_link}\" target=\"_blank\">"
                        f"<img src=\"{safe_link}\" alt=\"Image\" loading=\"lazy\"></a>"
                    )
                
                html_content.append("    </div>")
        
        html_content.extend([
            "    <footer style=\"text-align: center; margin-top: 50px; color: #999; font-size: 0.9em;\">",
            f"        Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "    </footer>",
            "</body>",
            "</html>"
        ])
        
        return html_content
    
    def generate_html_gallery(self) -> str:
        """
        Generate HTML gallery file.
        
        Returns:
            Path to the generated HTML file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            self.config.output_dir, 
            f"gallery_{timestamp}.html"
        )
        
        try:
            html_content = self.generate_html_content()
            
            with open(output_file, "w", encoding="utf-8") as out_file:
                out_file.write('\n'.join(html_content))
            
            logger.info(f"Gallery created: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating HTML gallery: {e}")
            raise


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Extract images from HTML files and create organized galleries grouped by date.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s -i /path/to/html/files
  %(prog)s --input-dir ./html_exports --encoding windows-1251
        '''
    )
    
    parser.add_argument(
        '--input-dir', '-i',
        help='Path to directory containing HTML files',
        required=False
    )
    
    parser.add_argument(
        '--encoding', '-e',
        default='utf-8',
        help='File encoding (default: utf-8)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='.',
        help='Output directory for generated gallery (default: current directory)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def validate_input_directory(input_dir: str) -> None:
    """
    Validate that the input directory exists and is accessible.
    
    Args:
        input_dir: Path to validate
        
    Raises:
        SystemExit: If directory is invalid
    """
    if not input_dir:
        logger.error("Input directory not specified")
        exit(1)
        
    if not os.path.isdir(input_dir):
        logger.error(f"Input directory does not exist: {input_dir}")
        exit(1)
        
    if not os.access(input_dir, os.R_OK):
        logger.error(f"Input directory is not readable: {input_dir}")
        exit(1)


def main() -> None:
    """Main entry point for the application."""
    try:
        args = parse_arguments()
        
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Get input directory
        input_dir = args.input_dir
        if not input_dir:
            input_dir = input("Enter path to input directory: ").strip()
        
        validate_input_directory(input_dir)
        
        # Create configuration
        config = Config(
            input_dir=input_dir,
            encoding=args.encoding,
            output_dir=args.output_dir
        )
        
        # Create and run parser
        parser = ImageGalleryParser(config)
        parser.parse_files()
        output_file = parser.generate_html_gallery()
        
        print(f"\n✓ Gallery successfully created: {output_file}")
        print(f"✓ Total images processed: {len(parser.all_links)}")
        print(f"✓ Date groups created: {len(parser.photos_by_date)}")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()