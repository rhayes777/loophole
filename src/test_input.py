#!/usr/bin/env bash

from control import input
import pygame

pygame.init()
clock = pygame.time.Clock()

controller = input.ArcadeController()

while True:
    controller.read()
    clock.tick(24)
