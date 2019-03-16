#!/usr/bin/env python

from control import input
import pygame

pygame.init()
clock = pygame.time.Clock()

controller = input.ArcadeController(pygame)

while True:
    controller.read()
    clock.tick(24)
