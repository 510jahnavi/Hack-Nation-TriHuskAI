"""
Color analysis and brand color matching
"""

import cv2
import numpy as np
from colorthief import ColorThief
from PIL import Image
import webcolors
from typing import List, Optional, Tuple

from app.models.schemas import ColorAnalysis, BrandKit


class ColorMatcher:
    """Analyzes colors and matches them against brand guidelines"""
    
    def analyze_colors(
        self,
        image_path: str,
        brand_kit: Optional[BrandKit] = None
    ) -> ColorAnalysis:
        """
        Extract and analyze colors from image
        
        Args:
            image_path: Path to image
            brand_kit: Brand guidelines with color palette
            
        Returns:
            ColorAnalysis with color metrics
        """
        # Extract dominant colors
        dominant_colors = self._extract_dominant_colors(image_path, count=5)
        
        # Get full color palette
        color_palette = self._extract_color_palette(image_path)
        
        # Calculate brand color match if brand kit provided
        brand_color_match = 0.0
        if brand_kit and brand_kit.primary_colors:
            brand_color_match = self._calculate_brand_match(
                dominant_colors, brand_kit.primary_colors
            )
        
        # Calculate color harmony
        color_harmony = self._calculate_color_harmony(dominant_colors)
        
        return ColorAnalysis(
            dominant_colors=[self._rgb_to_hex(c) for c in dominant_colors],
            color_palette=[self._rgb_to_hex(c) for c in color_palette],
            brand_color_match=brand_color_match,
            color_harmony=color_harmony
        )
    
    def _extract_dominant_colors(
        self,
        image_path: str,
        count: int = 5
    ) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using k-means clustering"""
        # Load image
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Reshape image to list of pixels
        pixels = img.reshape(-1, 3)
        pixels = np.float32(pixels)
        
        # K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(
            pixels, count, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )
        
        # Convert to integers
        centers = np.uint8(centers)
        
        # Sort by frequency
        label_counts = np.bincount(labels.flatten())
        sorted_indices = np.argsort(label_counts)[::-1]
        
        dominant_colors = [tuple(centers[i]) for i in sorted_indices]
        
        return dominant_colors
    
    def _extract_color_palette(self, image_path: str) -> List[Tuple[int, int, int]]:
        """Extract color palette using ColorThief"""
        try:
            color_thief = ColorThief(image_path)
            palette = color_thief.get_palette(color_count=6, quality=1)
            return palette
        except Exception as e:
            print(f"Error extracting palette: {e}")
            return []
    
    def _calculate_brand_match(
        self,
        image_colors: List[Tuple[int, int, int]],
        brand_colors: List[str]
    ) -> float:
        """
        Calculate how well image colors match brand colors
        
        Returns score from 0 to 1
        """
        if not brand_colors:
            return 0.0
        
        # Convert brand colors to RGB
        brand_rgb = [self._hex_to_rgb(c) for c in brand_colors]
        
        # For each brand color, find closest match in image
        matches = []
        for brand_color in brand_rgb:
            closest_distance = min(
                self._color_distance(brand_color, img_color)
                for img_color in image_colors
            )
            # Normalize distance (max distance is ~441 for RGB)
            similarity = 1 - (closest_distance / 441.0)
            matches.append(similarity)
        
        # Return average similarity
        return round(sum(matches) / len(matches), 3)
    
    def _calculate_color_harmony(
        self,
        colors: List[Tuple[int, int, int]]
    ) -> float:
        """
        Calculate color harmony score
        Based on color theory principles
        """
        if len(colors) < 2:
            return 1.0
        
        # Convert to HSV for better harmony analysis
        hsv_colors = [self._rgb_to_hsv(c) for c in colors]
        
        # Check for complementary, analogous, or triadic harmonies
        harmony_score = 0.0
        
        for i in range(len(hsv_colors)):
            for j in range(i + 1, len(hsv_colors)):
                hue_diff = abs(hsv_colors[i][0] - hsv_colors[j][0])
                
                # Complementary (opposite on color wheel)
                if 160 <= hue_diff <= 200:
                    harmony_score += 0.3
                
                # Analogous (adjacent on color wheel)
                elif hue_diff <= 30:
                    harmony_score += 0.2
                
                # Triadic (120 degrees apart)
                elif 110 <= hue_diff <= 130 or 230 <= hue_diff <= 250:
                    harmony_score += 0.25
        
        # Normalize
        max_pairs = len(colors) * (len(colors) - 1) / 2
        harmony_score = min(harmony_score / max_pairs, 1.0) if max_pairs > 0 else 0.5
        
        return round(harmony_score, 3)
    
    @staticmethod
    def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string"""
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def _rgb_to_hsv(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSV"""
        r, g, b = [x / 255.0 for x in rgb]
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        
        # Saturation
        s = 0 if max_val == 0 else (diff / max_val)
        
        # Value
        v = max_val
        
        return (h, s, v)
    
    @staticmethod
    def _color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculate Euclidean distance between two RGB colors"""
        return np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))
