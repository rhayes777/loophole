import pygame

# pygame init
pygame.display.init()

# pygame setup
# (6,0) = all good
print(pygame.init())

BLACK = [0,0,0]
WHITE = [255, 255, 255]

screen = pygame.display.set_mode((800, 600))

image_minim = pygame.image.load("minim.bmp").convert_alpha(screen)

alpha = 75

image_minim.set_alpha(alpha)
image_minim_transparent = image_minim.copy()
image_minim_transparent.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

print(image_minim.get_alpha())

while True:
    screen.fill(WHITE)

    screen.blit(image_minim_transparent, (10, 10))
    pygame.display.flip()

pygame.quit()