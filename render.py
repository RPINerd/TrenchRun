"""
"""
import pygame

import config as cfg


def draw_text_centre(screen, text, y, size, colour):
    font = pygame.font.Font(cfg.FONT_STYLE, size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect(center=(cfg.CANVAS_WIDTH // 2, y))
    screen.blit(text_surface, text_rect)


def draw_text_right(screen, text, x, y, size, colour):
    font = pygame.font.Font(cfg.FONT_STYLE, size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect(topright=(x, y))
    screen.blit(text_surface, text_rect)
