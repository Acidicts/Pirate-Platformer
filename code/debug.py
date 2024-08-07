import pygame

pygame.init()

font = pygame.font.Font(None, 30)


def debug_display(info, x=10, y=10):
    display_surf = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, (255, 255, 255))
    debug_rect = debug_surf.get_rect(topleft=(x, y))

    pygame.draw.rect(display_surf, (0, 0, 0), debug_rect)
    display_surf.blit(debug_surf, debug_rect)
