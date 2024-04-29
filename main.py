#!/usr/bin/env python3

import pygame as pg
import math
import scipy
import random
from scipy.constants import *
from sys import exit

WIDTH, HEIGHT = 800, 900

G = gravitational_constant

BLACK = (29, 12, 12)
WHITE = (223, 223, 223)
DEBUG_COL = (12, 148, 125, 100)
DEBUG_COL1 = (126, 255, 90, 100)
PLAYER_COL = (107, 117, 255)
HEAD_COL = (255, 0, 0)


class Player:
    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        self.size = WIDTH / 20
        self.player = pg.Rect(0, 0, self.size, self.size)
        self.screen = screen
        self.width = 4
        self.borderRad = 5
        self.surface = pg.Surface((self.player.width, self.player.height), pg.SRCALPHA)
        rect = self.surface.get_rect()
        rect.center = (self.x, self.y)
        self.rotSurfVal = 0
        self.mvmtX = [0, 0]  # +/-
        self.mvmtY = [0, 0]  # +/-
        self.speedConst = 2
        self.angSpeed = 6
        self.speedVec = (
            pg.Vector2(
                -math.sin(degree * self.rotSurfVal), math.cos(degree * self.rotSurfVal)
            )
            * self.speedConst
        )
        self.acceleration = 0.1
        self.maxSpeed = self.speedConst + 4

    def draw(self):
        # self.surface.fill(DEBUG_COL)
        self.speedVec = (
            pg.Vector2(
                -math.sin(degree * self.rotSurfVal), math.cos(degree * self.rotSurfVal)
            )
            * self.speedConst
        )
        pg.draw.rect(self.surface, PLAYER_COL, self.player, self.width, self.borderRad)
        lilOffset = 4
        headLeft = (
            self.player.topleft[0] + lilOffset,
            self.player.topleft[1] + lilOffset,
        )
        headRight = (
            self.player.topright[0] - lilOffset,
            self.player.topright[1] + lilOffset,
        )
        pg.draw.line(self.surface, HEAD_COL, headLeft, headRight, self.width)
        surface = pg.transform.rotate(self.surface, self.rotSurfVal)
        copySurf = surface.copy()
        copySurf.fill(DEBUG_COL)
        self.rotatedRect = surface.get_rect(center=(self.x, self.y))
        # print(self.rotatedRect.topleft)  # for debug
        self.screen.blit(surface, self.rotatedRect)
        self.screen.blit(copySurf, self.rotatedRect)

    def move_player(self):
        # update angles or the player
        if self.mvmtX[0] == 1:
            self.rotSurfVal -= self.angSpeed
        if self.mvmtX[1] == 1:
            self.rotSurfVal += self.angSpeed
        # check for motion and angle
        if self.mvmtY[0] == 1:
            if self.x <= WIDTH and self.x >= 0 and self.y <= HEIGHT and self.y >= 0:
                if self.speedVec.length() < self.maxSpeed:
                    self.speedConst += self.acceleration
                self.x -= self.speedVec.x
                self.y += self.speedVec.y
            elif self.x > WIDTH:
                self.x = WIDTH
            elif self.x < 0:
                self.x = 0
            elif self.y > HEIGHT:
                self.y = HEIGHT
            elif self.y < 0:
                self.y = 0
        if self.mvmtY[1] == 1:
            if self.x <= WIDTH and self.x >= 0 and self.y <= HEIGHT and self.y >= 0:
                if self.speedVec.length() < self.maxSpeed:
                    self.speedConst += self.acceleration
                self.x += self.speedVec.x
                self.y -= self.speedVec.y
            elif self.x > WIDTH:
                self.x = WIDTH
            elif self.x < 0:
                self.x = 0
            elif self.y > HEIGHT:
                self.y = HEIGHT
            elif self.y < 0:
                self.y = 0

    def reset_acceleration(self):
        self.speedConst = 2


class Bullet:
    def __init__(self, player: Player):
        self.player = player
        self.size = 5
        self.screen = player.screen
        self.width = 2
        self.borderRad = 5
        self.pass_val = True
        self.isShot = False

    def match_pos_w_player(self):
        self.x = self.player.x
        self.y = self.player.y

    def draw(self):
        self.rect = pg.Rect(self.x, self.y, self.size, self.size)
        pg.draw.rect(self.screen, HEAD_COL, self.rect, self.width, self.borderRad)

    def move(self):
        self.speed = 2

        if self.pass_val:
            self.vec = self.player.speedVec * self.speed
            self.pass_val = False

        self.x += self.vec.x
        self.y -= self.vec.y


class Body:
    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        self.size = random.randint(30, 80)
        self.screen: pg.Surface = screen
        self.width = random.randint(1, 6)
        self.borderRad = random.randint(2, 30)
        self.rotSurfVal = random.random() * 360
        self.mass = 1.5**self.size
        self.t = 0
        self.color = WHITE

    def draw(self):
        # self.surface.fill(DEBUG_COL)
        self.player = pg.Rect(0, 0, self.size, self.size)
        self.surface = pg.Surface((self.player.width, self.player.height), pg.SRCALPHA)
        rect = self.surface.get_rect()
        rect.center = (self.x, self.y)
        pg.draw.rect(self.surface, self.color, self.player, self.width, self.borderRad)
        surface = pg.transform.rotate(self.surface, self.rotSurfVal)
        self.rotatedRect = surface.get_rect(center=(self.x, self.y))
        self.screen.blit(surface, self.rotatedRect)

    def calc_F(self, other):
        return G * (self.mass * other.mass) / self.calc_dist(other)

    def calc_dist(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return dx**2 + dy**2

    def calcMoveSpeedToOther(self, other):
        a = self.calc_F(other) / self.mass
        v = 0.5 * a * self.t**2
        self.t += 0.001
        vecVal = pg.Vector2(other.x - self.x, other.y - self.y).normalize()
        print(vecVal)
        return vecVal * v

    def moveToOther(self, other):
        speed = self.calcMoveSpeedToOther(other)
        self.x += speed.x
        self.y += speed.y


#### GAME CONSTANTS ####

body_num = 10


#### ************** ####


def check_collision(r1: pg.Rect, r2: pg.Rect):
    return r1.colliderect(r2)


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.player = Player(WIDTH / 2, HEIGHT / 2, self.screen)
        self.bodyArr = []
        self.player.bullets = [Bullet(self.player) for i in range(100)]
        self.bCount = 0

        for i in range(body_num):
            randomXVal = random.randint(30, WIDTH - 30)
            randomYVal = random.randint(30, HEIGHT - 30)
            self.bodyArr.append(Body(randomXVal, randomYVal, self.screen))
            # print(self.bodyArr[i].player)

    def run(self):
        ele1 = self.bodyArr[random.randint(0, len(self.bodyArr) - 1)]
        ele2 = self.bodyArr[random.randint(0, len(self.bodyArr) - 1)]
        ele1.color = DEBUG_COL
        ele2.color = DEBUG_COL1
        while True:
            self.screen.fill(BLACK)
            self.player.draw()
            self.player.move_player()
            for ele in self.bodyArr:
                dummy: Body = ele
                dummy.draw()
            
            ## test for gravitation ##


            if ele1 != ele2:
                ele1.moveToOther(ele2)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_w:
                        self.player.mvmtY[1] = 1
                    if event.key == pg.K_s:
                        self.player.mvmtY[0] = 1
                    if event.key == pg.K_a:
                        self.player.mvmtX[1] = 1
                    if event.key == pg.K_d:
                        self.player.mvmtX[0] = 1
                    if event.key == pg.K_SPACE:
                        try:
                            self.player.bullets[self.bCount].isShot = True
                            self.player.bullets[self.bCount].match_pos_w_player()
                            self.bCount += 1
                        except:
                            print("Bullet Finished")
                if event.type == pg.KEYUP:
                    if event.key == pg.K_w:
                        self.player.mvmtY[1] = 0
                        self.player.reset_acceleration()
                    if event.key == pg.K_s:
                        self.player.mvmtY[0] = 0
                        self.player.reset_acceleration()
                    if event.key == pg.K_a:
                        self.player.mvmtX[1] = 0
                    if event.key == pg.K_d:
                        self.player.mvmtX[0] = 0

            for bullet in self.player.bullets:
                if bullet.isShot == True:
                    bullet.draw()
                    bullet.move()
                    for dummy in self.bodyArr:
                        if check_collision(bullet.rect, dummy.rotatedRect):
                            print(f"collision with  {self.bodyArr.index(dummy)}")
                            self.bodyArr.pop(self.bodyArr.index(dummy))

            pg.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    Game().run()
