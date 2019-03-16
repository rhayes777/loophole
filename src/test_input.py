#!/usr/bin/env python

import pygame

from control import input

pygame.init()
clock = pygame.time.Clock()


def button_listener(button):
    print button


controller = input.ArcadeController(pygame, button_listener)

while True:
    controller.read()
    clock.tick(24)
