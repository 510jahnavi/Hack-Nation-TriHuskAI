"""
Image quality analysis using OpenCV
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple

from app.models.schemas import VisualAnalysis


class ImageAnalyzer:
    """Analyzes image quality using computer vision techniques"""
    
    def analyze_quality(self, image_path: str) -> VisualAnalysis:
        """
        Analyze image quality metrics
        
        Args:
            image_path: Path to image file
            
        Returns:
            VisualAnalysis with quality metrics
        """
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Get resolution
        height, width = img.shape[:2]
        aspect_ratio = f"{width}:{height}"
        
        # Analyze sharpness
        sharpness = self._calculate_sharpness(img)
        
        # Analyze composition
        composition = self._analyze_composition(img)
        
        # Check for watermarks (simple detection)
        has_watermark = self._detect_watermark(img)
        
        # Check for compression artifacts
        has_artifacts = self._detect_artifacts(img)
        
        return VisualAnalysis(
            sharpness=sharpness,
            composition=composition,
            has_watermark=has_watermark,
            has_artifacts=has_artifacts,
            resolution={"width": width, "height": height},
            aspect_ratio=aspect_ratio
        )
    
    def _calculate_sharpness(self, img: np.ndarray) -> float:
        """
        Calculate image sharpness using Laplacian variance
        Higher values indicate sharper images
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Normalize to 0-1 scale (empirical threshold: 100 is decent, 500+ is sharp)
        sharpness_score = min(laplacian_var / 500.0, 1.0)
        
        return round(sharpness_score, 3)
    
    def _analyze_composition(self, img: np.ndarray) -> float:
        """
        Analyze composition quality using rule of thirds and balance
        """
        height, width = img.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Divide image into 9 sections (rule of thirds)
        h_third = height // 3
        w_third = width // 3
        
        sections = []
        for i in range(3):
            for j in range(3):
                section = gray[i*h_third:(i+1)*h_third, j*w_third:(j+1)*w_third]
                sections.append(section.mean())
        
        # Good composition has varied intensity across sections
        # but not too extreme
        std_dev = np.std(sections)
        composition_score = min(std_dev / 50.0, 1.0)  # Normalize
        
        # Also check if image is not too dark or too bright
        overall_brightness = gray.mean()
        brightness_penalty = 0
        if overall_brightness < 50 or overall_brightness > 200:
            brightness_penalty = 0.2
        
        final_score = max(0, composition_score - brightness_penalty)
        
        return round(final_score, 3)
    
    def _detect_watermark(self, img: np.ndarray) -> bool:
        """
        Simple watermark detection
        Looks for semi-transparent overlays or text in corners
        """
        height, width = img.shape[:2]
        
        # Check corners for potential watermarks
        corner_size = min(height, width) // 8
        corners = [
            img[0:corner_size, 0:corner_size],  # Top-left
            img[0:corner_size, -corner_size:],  # Top-right
            img[-corner_size:, 0:corner_size],  # Bottom-left
            img[-corner_size:, -corner_size:]   # Bottom-right
        ]
        
        # Simple heuristic: check if corners have significantly different
        # characteristics than the center (potential watermark)
        center = img[height//3:2*height//3, width//3:2*width//3]
        center_std = np.std(center)
        
        for corner in corners:
            corner_std = np.std(corner)
            # If corner is much more uniform than center, might be watermark
            if corner_std < center_std * 0.5 and corner_std > 5:
                return True
        
        return False
    
    def _detect_artifacts(self, img: np.ndarray) -> bool:
        """
        Detect compression artifacts or noise
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply high-pass filter to detect noise/artifacts
        kernel = np.array([[-1, -1, -1],
                          [-1,  8, -1],
                          [-1, -1, -1]])
        filtered = cv2.filter2D(gray, -1, kernel)
        
        # High variance in filtered image indicates artifacts
        artifact_level = filtered.var()
        
        # Threshold for artifact detection (empirical)
        return artifact_level > 1000
    
    def extract_text_regions(self, image_path: str) -> list:
        """
        Extract regions that likely contain text
        Useful for checking message clarity
        """
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Use MSER (Maximally Stable Extremal Regions) for text detection
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        # Filter and return bounding boxes
        text_boxes = []
        for region in regions:
            x, y, w, h = cv2.boundingRect(region)
            # Filter out very small or very large regions
            if 10 < w < img.shape[1] * 0.8 and 10 < h < img.shape[0] * 0.3:
                text_boxes.append((x, y, w, h))
        
        return text_boxes
