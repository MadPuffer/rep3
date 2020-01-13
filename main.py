import random

import pygame

pygame.init()
screen = pygame.display.set_mode((768, 630))
clock = pygame.time.Clock()

# Bulat: переменные для корректного поворота спрайтов
south = 0
east = 90
north = 180
west = 270

# Bulat: танки, уничтоженные в данный момент
destroyed_player = []

# Bulat: переменные времени для респауна каждого из игроков
respawn_green_tick = 0
respawn_sand_tick = 0

# Bulat: музыка
pygame.mixer.music.load('music.wav')
pygame.mixer.music.play(-1)


# Bulat: функция загрузки изображений
def load_image(name, colorkey=None):
    image = pygame.image.load(f'sprites/{name}').convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# Bulat: функция генерации объектов
def create_objects():
    objects.add(Object(load_image('crateMetal.png', -1), 448, 256))


# Bulat: класс интерфейса
class UI(pygame.sprite.Sprite):
    def __init__(self, img, x, y, type, tank):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        self.area = screen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type
        self.tank = tank

    def update(self, *args):
        if self.type == 'HPBar':
            self.image = pygame.transform.scale(self.image, (int(376 * (self.tank.health / 120)), 47))
        elif self.type == 'ArmorBar':
            self.image = pygame.transform.scale(self.image, (int(377 * (self.tank.armor / 80)), 14))


# Bulat: класс поля
class Tile(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        self.area = screen.get_rect()
        self.rect.x = x
        self.rect.y = y


# Bulat: класс объектов
class Object(pygame.sprite.Sprite):
    def __init__(self, img, x, y, for_time=False, living_time=600, destroyable=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.for_time = for_time
        self.living_time = living_time
        self.tick = 0
        self.destroyable = destroyable

    def update(self):
        if self.for_time:
            self.tick += 1
            if self.tick == self.living_time:
                self.kill()


# Bulat: эффекты
class Particle(pygame.sprite.Sprite):
    def __init__(self, img, x, y, tank, type):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hitanimcount = 0
        self.explosionanimcount = 0
        self.shotanimcount = 0
        self.images = []
        self.tank = tank
        self.type = type
        self.direction = south

    def rotation(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        if self.type == 'hit':
            self.hitanimcount += 1
            self.image = self.images[self.hitanimcount // 8]
            self.image = pygame.transform.scale(self.image, (30, 30))
            if self.tank.direction == north or self.tank.direction == south:
                self.rect.x = self.tank.rect.x + 9
                self.rect.y = self.tank.rect.y + 12
            else:
                self.rect.x = self.tank.rect.x + 12
                self.rect.y = self.tank.rect.y + 9
            if self.hitanimcount == 63:
                self.kill()
        elif self.type == 'explosion':
            self.explosionanimcount += 2
            self.image = pygame.transform.scale(self.images[self.explosionanimcount // 8], (83, 80))
            self.rect.x = self.tank.rect.x - 15
            self.rect.y = self.tank.rect.y - 15
            if self.explosionanimcount > 61:
                self.kill()
        elif self.type == 'shot':
            self.shotanimcount += 1
            self.image = pygame.transform.scale(images[self.shotanimcount // 6], (50, 50))

            if self.shotanimcount == 29:
                self.kill()
            self.rotation(self.direction - self.tank.direction)
            self.direction = self.tank.direction
            if self.direction == north:
                self.rect.x = self.tank.rect.x - 4
                self.rect.y = self.tank.rect.y - 45
                self.rotation(180)
            elif self.direction == south:
                self.rect.x = self.tank.rect.x - 3
                self.rect.y = self.tank.rect.y + 45
            elif self.direction == east:
                self.rect.x = self.tank.rect.x - 47
                self.rect.y = self.tank.rect.y - 2
                self.rotation(-90)
            elif self.direction == west:
                self.rect.x = self.tank.rect.x + 43
                self.rect.y = self.tank.rect.y - 4
                self.rotation(90)


# Bulat: игроки
class Player(pygame.sprite.Sprite):
    def __init__(self, img, x, y, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        self.area = screen.get_rect()
        self.color = color
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

        self.health = 120
        self.armor = 80
        self.speed = 1
        self.reload = 0
        self.reloading = False
        self.can_shoot = True
        self.resist_count = 0
        self.resist = True

        self.direction = south

        self.moving_left = False
        self.moving_right = False
        self.moving_top = False
        self.moving_down = False

    # Bulat: функция поворота
    def rotation(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self):

        if self.moving_top and self.rect.y != 0:
            self.rect.y -= self.speed
        if self.moving_down and self.rect.y != 576:
            self.rect.y += self.speed
        if self.moving_right and self.rect.x != 768:
            self.rect.x += 1
        if self.moving_left and self.rect.x != 0:
            self.rect.x -= 1

        if pygame.sprite.spritecollideany(self, objects):
            if self.direction == north:
                self.moving_top = False
            elif self.direction == south:
                self.moving_down = False
            elif self.direction == west:
                self.moving_right = False
            elif self.direction == east:
                self.moving_left = False

        if self.health <= 0:
            self.get_destroyed()

        if self.reloading:
            self.reload += 1

        # Bulat: откат перезарядки
        if self.reload == 45:
            self.reload = 0
            self.can_shoot = True
            self.reloading = False

        # Bulat: бессмертие в первые 3 секунды после появления
        if self.resist_count < 180:
            self.resist_count += 1
        else:
            self.resist = False

    # Bulat: функция уничтожения
    def get_destroyed(self):
        explosion = Particle(pygame.transform.scale(load_image('Explosion_A.png', -1), (1, 1)),
                             self.rect.x, self.rect.y, self, 'explosion')

        explosion.images = [load_image('Explosion_A.png', -1), load_image('Explosion_B.png', -1),
                            load_image('Explosion_C.png', -1), load_image('Explosion_D.png', -1),
                            load_image('Explosion_E.png', -1), load_image('Explosion_F.png', -1),
                            load_image('Explosion_G.png', -1), load_image('Explosion_H.png', -1)]
        particles.add(explosion)
        global destroyed_player
        destroyed_player.append(self.color)
        body = Object(load_image('tankBody_dark_outline.png'), self.rect.x, self.rect.y,
                      for_time=True, destroyable=False)
        global objects
        objects.add(body)
        ui.remove(i for i in ui if i.tank == self)
        self.kill()


# Bulat: класс снарядов
class Bullet(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        self.area = screen.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.damage = 40
        self.speed = 10
        self.direction = ''

    # Bulat: функция поворота
    def rotation(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        if self.direction == north:
            self.rect.y -= self.speed
        elif self.direction == south:
            self.rect.y += self.speed
        elif self.direction == east:
            self.rect.x -= self.speed
        elif self.direction == west:
            self.rect.x += self.speed
        if self.rect.x > 770 or self.rect.x < 0 or self.rect.y > 580 or self.rect.y < 0:
            self.kill()

        # Bulat: проверка на столкновение с игроком
        if pygame.sprite.spritecollideany(self, players):
            # Bulat: танк, в который угодил снаряд
            hitted_tank = pygame.sprite.spritecollideany(self, players)
            # Bulat: создание эффекта
            hit = Particle(pygame.transform.scale(load_image('flash00.png', -1), (1, 1)), self.x, self.y,
                           hitted_tank, 'hit')
            images = [load_image('flash00.png', -1), load_image('flash01.png', -1),
                      load_image('flash02.png', -1), load_image('flash03.png', -1),
                      load_image('flash04.png', -1), load_image('flash05.png', -1), load_image('flash06.png', -1),
                      load_image('flash07.png', -1), load_image('flash08.png', -1)]
            hit.images = images
            particles.add(hit)
            # Bulat: нанесение урона танку
            hitted_tank.health -= self.damage * 0.4 if hitted_tank.resist is False else 0
            hitted_tank.armor -= self.damage * 0.6 if hitted_tank.resist is False else 0
            if hitted_tank.armor < 0:
                hitted_tank.health += hitted_tank.armor
                hitted_tank.armor = 0
            self.kill()


class Bonus(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        super().__init__()
        self.count = 0
        x = 762
        y = 573
        self.x = random.randrange(x)
        self.y = random.randrange(y)
        self.images = ["barrelRed_top.png", "barrelRed_top.png",
                       "barrelGreen_top.png"]
        bs = ['bulletBlue2.png', 'bulletRed1_outline.png', 'bulletDark2_outline.png']
        self.image = pygame.transform.scale(load_image(random.choice(self.images), -1), (1, 1))
        self.rect = self.image.get_rect()
        self.image_bonus = load_image(random.choice(bs), -1)
        self.rect.x = 0
        self.rect.y = 0
        self.time = 0
        self.choosed_image = load_image(random.choice(self.images), -1)

    def update(self):
        self.time += 1
        if self.time >= 210:
            self.rect.x = x
            self.rect.y = y
            self.image = self.choosed_image
        if pygame.sprite.spritecollideany(self, bullets):
            self.image = self.image_bonus
        if pygame.sprite.spritecollideany(self, players):
            pygame.sprite.spritecollideany(self, players).speed = 2
            self.kill()


# Bulat: изображения для составления поля
tile_images = {'.': load_image('tileGrass1.png'),
               ',': load_image('tileGrass_roadEast.png'),
               '@': load_image('tileGrass_roadCornerUL.png'),
               '!': load_image('tileGrass_roadCornerUR.png'),
               '>': load_image('tileGrass_roadCornerLR.png'),
               '(': load_image('tileGrass_roadSplitS.png'),
               ')': load_image('tileGrass_roadSplitN.png'),
               '^': load_image('tileGrass_roadNorth.png'),
               '/': load_image('tileSand1.png'),
               '*': load_image('tileGrass_roadTransitionE_dirt.png'),
               '-': load_image('tileGrass_transitionE.png'),
               '#': load_image('tileSand_roadEast.png'),
               '|': load_image('tileSand_roadCornerLL.png'),
               '<': load_image('tileSand_roadCornerLR.png'),
               '&': load_image('tileSand_roadCornerUL.png'),
               '$': load_image('tileSand_roadNorth.png'),
               '=': load_image('tileSand_roadSplitS.png'),
               '+': load_image('tileSand_roadSplitN.png')
               }

# Bulat: все группы спрайтов
tiles = pygame.sprite.Group()
players = pygame.sprite.Group()
particles = pygame.sprite.Group()
bullets = pygame.sprite.Group()
objects = pygame.sprite.Group()
ui = pygame.sprite.Group()

# Bulat: создание объектов
create_objects()

# Bulat: построение уровня
level_blueprint = [i.strip() for i in list(open('level.txt', 'r'))]
for y in range(10):
    for x in range(12):
        tile = level_blueprint[y][x]
        sprite = Tile(tile_images[tile], x * 64, y * 64)
        tiles.add(sprite)

# Bulat: создание интерфейса и игроков
ui.add(UI(load_image('HPBar.jpg'), 0, 576, 'HPBarOut', None))
ui.add(UI(load_image('HPBar.jpg'), 388, 576, 'HPBarOut', None))

player_green = Player(load_image('tank_green.png'), 138, 16, 'green')
ui.add(UI(load_image('HPBarIn.png', -1), 2, 577, 'HPBar', player_green))
ui.add(UI(pygame.transform.scale(load_image('ArmorBar.png'), (377, 14)), 2, 560, 'ArmorBar', player_green))

player_sand = Player(load_image('tank_sand.png'), 720, 394, 'sand')
ui.add(UI(load_image('HPBarIn.png', -1), 390, 577, 'HPBar', player_sand))
ui.add(UI(pygame.transform.scale(load_image('ArmorBar.png'), (377, 14)), 390, 560, 'ArmorBar', player_sand))
player_sand.rotation(-90)
player_sand.direction = east

players.add(player_green, player_sand)

# Bulat: главный цикл игры
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Bulat: вверх
            if event.key == pygame.K_w:
                player_green.moving_down = False
                player_green.moving_left = False
                player_green.moving_right = False

                player_green.rotation(player_green.direction - north)
                player_green.direction = north
                player_green.moving_top = True

            # Bulat: вниз
            if event.key == pygame.K_s:
                player_green.moving_up = False
                player_green.moving_left = False
                player_green.moving_right = False

                player_green.rotation(player_green.direction - south)
                player_green.direction = south
                player_green.moving_down = True

            # Bulat: вправо
            if event.key == pygame.K_d:
                player_green.moving_down = False
                player_green.moving_left = False
                player_green.moving_top = False

                player_green.rotation(player_green.direction - west)
                player_green.direction = west
                player_green.moving_right = True

            # Bulat: влево
            if event.key == pygame.K_a:

                player_green.moving_down = False
                player_green.moving_top = False
                player_green.moving_right = False

                player_green.rotation(player_green.direction - east)
                player_green.direction = east
                player_green.moving_left = True

            # Bulat: выстрел
            elif event.key == pygame.K_SPACE and player_green.can_shoot:
                # Bulat: изображения для эффекта
                images = [load_image('Flash_A_01.png', -1), load_image('Flash_A_02.png', -1),
                          load_image('Flash_A_03.png', -1),
                          load_image('Flash_A_04.png', -1), load_image('Flash_A_05.png', -1)]
                if player_green.direction == south:
                    green_b = Bullet(load_image('bulletGreen3_outline.png', -1), player_green.rect.x + 18,
                                     player_green.rect.y + 46)
                    img = pygame.transform.scale(load_image('Flash_A_01.png', -1), (50, 50))
                    shot = Particle(img, player_green.rect.x - 3, player_green.rect.y + 34,
                                    player_green, 'shot')
                    shot.images = images
                    particles.add(shot)

                elif player_green.direction == north:
                    green_b = Bullet(load_image('bulletGreen3_outline.png', -1), player_green.rect.x + 18,
                                     player_green.rect.y - 23)
                    img = pygame.transform.scale(load_image('Flash_A_01.png', -1), (50, 50))
                    shot = Particle(img, player_green.rect.x - 4, player_green.rect.y - 40,
                                    player_green, 'shot')
                    shot.images = images
                    particles.add(shot)

                elif player_green.direction == east:
                    green_b = Bullet(load_image('bulletGreen3_outline.png', -1), player_green.rect.x - 23,
                                     player_green.rect.y + 18)
                    green_b.rotation(-90)
                    img = pygame.transform.scale(load_image('Flash_A_01.png', -1), (50, 50))
                    shot = Particle(img, player_green.rect.x - 38, player_green.rect.y,
                                    player_green, 'shot')
                    shot.images = images
                    particles.add(shot)

                elif player_green.direction == west:
                    green_b = Bullet(load_image('bulletGreen3_outline.png', -1), player_green.rect.x + 42,
                                     player_green.rect.y + 18)
                    green_b.rotation(90)
                    img = pygame.transform.scale(load_image('Flash_A_01.png', -1), (50, 50))
                    shot = Particle(img, player_green.rect.x + 42, player_green.rect.y + 18,
                                    player_green, 'shot')
                    shot.images = images
                    particles.add(shot)
                player_green.can_shoot = False
                player_green.reloading = True
                green_b.direction = player_green.direction
                bullets.add(green_b)

            # второй игрок

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player_sand.moving_down = False
                    player_sand.moving_left = False
                    player_sand.moving_right = False

                    player_sand.rotation(player_sand.direction - north)
                    player_sand.direction = north
                    player_sand.moving_top = True

                if event.key == pygame.K_DOWN:
                    player_sand.moving_up = False
                    player_sand.moving_left = False
                    player_sand.moving_right = False

                    player_sand.rotation(player_sand.direction - south)
                    player_sand.direction = south
                    player_sand.moving_down = True

                if event.key == pygame.K_RIGHT:
                    player_sand.moving_down = False
                    player_sand.moving_left = False
                    player_sand.moving_top = False

                    player_sand.rotation(player_sand.direction - west)
                    player_sand.direction = west
                    player_sand.moving_right = True

                if event.key == pygame.K_LEFT:

                    player_sand.moving_down = False
                    player_sand.moving_top = False
                    player_sand.moving_right = False

                    player_sand.rotation(player_sand.direction - east)
                    player_sand.direction = east
                    player_sand.moving_left = True

                elif event.key == pygame.K_RCTRL and player_sand.can_shoot:
                    images = [load_image('Flash_A_01.png', -1), load_image('Flash_A_02.png', -1),
                              load_image('Flash_A_03.png', -1),
                              load_image('Flash_A_04.png', -1), load_image('Flash_A_05.png', -1)]
                    if player_sand.direction == south:
                        sand_b = Bullet(load_image('bulletSand3_outline.png', -1), player_sand.rect.x + 18,
                                        player_sand.rect.y + 46)

                        img = pygame.transform.scale(load_image('Flash_A_01.png', -1), (50, 50))
                        shot = Particle(img, player_sand.rect.x - 3, player_sand.rect.y + 34,
                                        player_sand, 'shot')
                        shot.images = images
                        particles.add(shot)

                    elif player_sand.direction == north:
                        sand_b = Bullet(load_image('bulletSand3_outline.png', -1), player_sand.rect.x + 18,
                                        player_sand.rect.y - 23)
                        img = pygame.transform.scale(load_image('Flash_A_01.png', -1), (50, 50))
                        shot = Particle(img, player_sand.rect.x - 4, player_sand.rect.y - 40,
                                        player_sand, 'shot')
                        shot.images = images
                        particles.add(shot)

                    elif player_sand.direction == east:
                        sand_b = Bullet(load_image('bulletSand3_outline.png', -1), player_sand.rect.x - 23,
                                        player_sand.rect.y + 18)
                        sand_b.rotation(-90)
                        img = pygame.transform.scale(load_image('Flash_A_01.png', -1), (50, 50))
                        shot = Particle(img, player_sand.rect.x - 38, player_sand.rect.y,
                                        player_sand, 'shot')
                        shot.images = images
                        particles.add(shot)

                    elif player_sand.direction == west:
                        sand_b = Bullet(load_image('bulletSand3_outline.png', -1), player_sand.rect.x + 42,
                                        player_sand.rect.y + 18)
                        sand_b.rotation(90)
                        img = pygame.transform.scale(load_image('Flash_A_01.png', -1), (50, 50))
                        shot = Particle(img, player_sand.rect.x + 42, player_sand.rect.y + 18,
                                        player_sand, 'shot')
                        shot.images = images
                        particles.add(shot)

                    player_sand.can_shoot = False
                    player_sand.reloading = True
                    sand_b.direction = player_sand.direction
                    bullets.add(sand_b)

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                player_green.moving_top = False

            elif event.key == pygame.K_s:
                player_green.moving_down = False

            elif event.key == pygame.K_d:
                player_green.moving_right = False

            elif event.key == pygame.K_a:
                player_green.moving_left = False

            # игрок 2

            if event.key == pygame.K_UP:
                player_sand.moving_top = False

            elif event.key == pygame.K_DOWN:
                player_sand.moving_down = False

            elif event.key == pygame.K_RIGHT:
                player_sand.moving_right = False

            elif event.key == pygame.K_LEFT:
                player_sand.moving_left = False

    # Bulat: отрисовка всех групп спрайтов
    tiles.draw(screen)
    tiles.update()
    players.draw(screen)
    players.update()
    objects.draw(screen)
    objects.update()
    bullets.draw(screen)
    bullets.update()
    particles.draw(screen)
    particles.update()
    ui.draw(screen)
    ui.update()

    # Bulat:  возрождение уничтоженного игрока/игроков
    if destroyed_player:
        if 'green' in destroyed_player:
            respawn_green_tick += 1
            if respawn_green_tick == 120:
                player_green = Player(load_image('tank_green.png'), 138, 16, 'green')
                players.add(player_green)
                destroyed_player.remove('green')
                respawn_green_tick = 0
                ui.add(UI(load_image('HPBarIn.png', -1), 2, 577, 'HPBar', player_green))
                ui.add(UI(pygame.transform.scale(load_image('ArmorBar.png'), (377, 14)), 2, 560,
                          'ArmorBar', player_green))

        if 'sand' in destroyed_player:
            respawn_sand_tick += 1
            if respawn_sand_tick == 120:
                player_sand = Player(load_image('tank_sand.png'), 720, 394, 'sand')
                player_sand.rotation(-90)
                player_sand.direction = east
                players.add(player_sand)
                destroyed_player.remove('sand')
                respawn_sand_tick = 0
                ui.add(UI(load_image('HPBarIn.png', -1), 390, 577, 'HPBar', player_sand))
                ui.add(UI(pygame.transform.scale(load_image('ArmorBar.png'), (377, 14)), 390, 560,
                          'ArmorBar', player_green))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
