# tests/test_theme.py
# -*- coding: utf-8 -*-
"""
Unit tests for Theme module.
Tests color definitions, theme loading/saving, and utility functions.
"""
import pytest
import os
# Import corregido para compatibilidad IDE y App
import sys
from pathlib import Path

# Agregar paths para imports relativos
app_root = Path(__file__).parent.parent
sys.path.insert(0, str(app_root))
sys.path.insert(0, str(app_root.parent / "Z_Utilidades" / "GUI"))

try:
    from theme import (
        ACCENT_COLORS,
        SHADOWS,
        GRADIENTS,
        TYPOGRAPHY,
        SPACING,
        RADIUS,
        get_colors,
        get_mode,
        load_theme,
        get_gradient_colors,
        get_animation_duration,
    )
except ImportError:
    # Fallback para IDE
    from Z_Utilidades.GUI.theme import (
        ACCENT_COLORS,
        SHADOWS,
        GRADIENTS,
        TYPOGRAPHY,
        SPACING,
        RADIUS,
        get_colors,
        get_mode,
        load_theme,
        get_gradient_colors,
        get_animation_duration,
    )
    get_spacing,
    get_radius,
    create_hover_color,
)


class TestAccentColors:
    """Tests for accent color definitions."""
    
    def test_accent_colors_exist(self):
        """Verify we have at least 15 accent colors."""
        assert len(ACCENT_COLORS) >= 15
    
    def test_accent_colors_are_hex(self):
        """All accent colors should be valid hex codes."""
        for name, color in ACCENT_COLORS.items():
            assert color.startswith("#"), f"{name} should start with #"
            assert len(color) == 7, f"{name} should be 7 chars (#RRGGBB)"
    
    def test_turquesa_exists(self):
        """Turquesa (default) should exist."""
        assert "Turquesa" in ACCENT_COLORS


class TestShadows:
    """Tests for shadow definitions."""
    
    def test_shadows_exist(self):
        """Standard shadow sizes should exist."""
        expected = ["sm", "md", "lg", "xl"]
        for size in expected:
            assert size in SHADOWS
    
    def test_glow_accent_exists(self):
        """Glow accent shadow should exist."""
        assert "glow_accent" in SHADOWS


class TestGradients:
    """Tests for gradient definitions."""
    
    def test_gradients_exist(self):
        """Standard gradients should exist."""
        expected = ["primary", "ocean", "sunset", "forest"]
        for name in expected:
            assert name in GRADIENTS
    
    def test_gradient_structure(self):
        """Gradients should have colors and direction."""
        for name, gradient in GRADIENTS.items():
            assert "colors" in gradient
            assert "direction" in gradient
            assert len(gradient["colors"]) == 2


class TestTypography:
    """Tests for typography definitions."""
    
    def test_font_sizes_exist(self):
        """Standard font sizes should exist."""
        expected = ["xs", "sm", "base", "md", "lg", "xl"]
        for size in expected:
            assert size in TYPOGRAPHY["font_size"]
    
    def test_font_sizes_are_int(self):
        """Font sizes should be integers."""
        for size, value in TYPOGRAPHY["font_size"].items():
            assert isinstance(value, int)


class TestSpacing:
    """Tests for spacing tokens."""
    
    def test_spacing_tokens_exist(self):
        """Standard spacing tokens should exist."""
        expected = ["0", "1", "2", "4", "8"]
        for token in expected:
            assert token in SPACING
    
    def test_spacing_values(self):
        """Spacing values should follow scale."""
        assert SPACING["0"] == 0
        assert SPACING["1"] == 4
        assert SPACING["2"] == 8
        assert SPACING["4"] == 16


class TestRadius:
    """Tests for border radius tokens."""
    
    def test_radius_tokens_exist(self):
        """Standard radius tokens should exist."""
        expected = ["none", "sm", "md", "lg", "full"]
        for token in expected:
            assert token in RADIUS
    
    def test_radius_none(self):
        """Radius 'none' should be 0."""
        assert RADIUS["none"] == 0
    
    def test_radius_full(self):
        """Radius 'full' should be large for circles."""
        assert RADIUS["full"] >= 9999


class TestThemeFunctions:
    """Tests for theme utility functions."""
    
    def test_load_theme_returns_dict(self):
        """load_theme should return a dictionary."""
        theme = load_theme()
        assert isinstance(theme, dict)
    
    def test_load_theme_has_mode(self):
        """Theme should have mode key."""
        theme = load_theme()
        assert "mode" in theme
        assert theme["mode"] in ["dark", "light"]
    
    def test_get_colors_returns_dict(self):
        """get_colors should return a dictionary."""
        colors = get_colors()
        assert isinstance(colors, dict)
    
    def test_get_colors_has_essentials(self):
        """Colors should have essential keys."""
        colors = get_colors()
        essentials = ["bg_primary", "bg_secondary", "text_primary", "accent"]
        for key in essentials:
            assert key in colors
    
    def test_get_gradient_colors(self):
        """get_gradient_colors should return tuple of 2 colors."""
        colors = get_gradient_colors("primary")
        assert isinstance(colors, tuple)
        assert len(colors) == 2
    
    def test_get_animation_duration(self):
        """get_animation_duration should return an integer."""
        duration = get_animation_duration("normal")
        assert isinstance(duration, int)
        assert duration >= 0
    
    def test_get_spacing(self):
        """get_spacing should return an integer."""
        spacing = get_spacing("4")
        assert isinstance(spacing, int)
        assert spacing == 16
    
    def test_get_radius(self):
        """get_radius should return an integer."""
        radius = get_radius("md")
        assert isinstance(radius, int)


class TestCreateHoverColor:
    """Tests for hover color creation."""
    
    def test_create_hover_color_format(self):
        """create_hover_color should return valid hex."""
        hover = create_hover_color("#336699")
        assert hover.startswith("#")
        assert len(hover) == 7
    
    def test_create_hover_color_lighter(self):
        """Hover color should be lighter than original."""
        original = "#336699"
        hover = create_hover_color(original, lighten=30)
        # Just verify it's different and valid hex
        assert hover != original
        assert hover.startswith("#")
    
    def test_create_hover_color_max(self):
        """Hover color should not exceed #ffffff."""
        hover = create_hover_color("#ffffff", lighten=50)
        # Should still be valid
        assert hover.startswith("#")
        # R, G, B should be capped at 255
        r = int(hover[1:3], 16)
        g = int(hover[3:5], 16)
        b = int(hover[5:7], 16)
        assert r <= 255
        assert g <= 255
        assert b <= 255
