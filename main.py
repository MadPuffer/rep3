import pygame

pygame.init()
screen = pygame.display.set_mode((768, 576))
clock = pygame.time.Clock()

south = 0
east = 90
north = 180
west = 270


def load_image(name, colorkey=None):
    image = pygame.image.load(f'sprites/{name}').convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Tile(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Particle(pygame.sprite.Sprite):
    def __init__(self, img, x, y, tank, type):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.hitanimcount = 0
        self.shotanimcount = 0
        self.images = []
        self.tank = tank
        self.type = type

    def rotation(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        if self.type == 'hit':
            self.hitanimcount += 1
            self.image = self.images[self.hitanimcount // 6]
            self.image = pygame.transform.scale(self.image, (30, 30))
            if self.tank.direction == north or self.tank.direction == south:
                self.rect.x = self.tank.rect.x + 9
                self.rect.y = self.tank.rect.y + 12
            else:
                self.rect.x = self.tank.rect.x + 12
                self.rect.y = self.tank.rect.y + 9
            if self.hitanimcount == 29:
                self.kill()
        elif self.type == 'shot':
            self.shotanimcount += 1
            if self.shotanimcount == 10:
                self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

        self.health = 120
        self.speed = 1

        self.south = 0
        self.east = 90
        self.north = 180
        self.west = 270
        self.direction = self.south

        self.moving_left = False
        self.moving_right = False
        self.moving_top = False
        self.moving_down = False

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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = img.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.damage = 40
        self.speed = 10
        self.direction = ''

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
        if 768 < self.rect.x < 0 or 576 < self.rect.y < 0:
            self.kill()
        if pygame.sprite.spritecollideany(self, players):
            hit = Particle(pygame.transform.scale(load_image('explosion1.png', -1), (1, 1)), self.x, self.y,
                           pygame.sprite.spritecollideany(self, players), 'hit')
            images = [load_image('smokeOrange0.png', -1), load_image('smokeOrange1.png', -1),
                      load_image('smokeOrange2.png', -1), load_image('smokeOrange3.png', -1),
                      load_image('smokeOrange4.png', -1)]
            hit.images = images
            particles.add(hit)
            self.kill()


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

tiles = pygame.sprite.Group()
players = pygame.sprite.Group()
particles = pygame.sprite.Group()
bullets = pygame.sprite.Group()
objects = pygame.sprite.Group()

level_blueprint = [i.strip() for i in list(open('level.txt', 'r'))]
for y in range(9):
    for x in range(12):
        tile = level_blueprint[y][x]
        sprite = Tile(tile_images[tile], x * 64, y * 64)
        tiles.add(sprite)

player_green = Player(load_image('tank_green.png'), 138, 16)
player_reen = Player(load_image('tank_green.png'), 138, 16)
players.add(player_green, player_reen)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:

                player_green.moving_down = False
                player_green.moving_left = False
                player_green.moving_right = False

                player_green.rotation(player_green.direction - north)
                player_green.direction = north
                player_green.moving_top = True

            if event.key == pygame.K_s:

                player_green.moving_up = False
                player_green.moving_left = False
                player_green.moving_right = False

                player_green.rotation(player_green.direction - south)
                player_green.direction = south
                player_green.moving_down = True

            if event.key == pygame.K_d:

                player_green.moving_down = False
                player_green.moving_left = False
                player_green.moving_top = False

                player_green.rotation(player_green.direction - west)
                player_green.direction = west
                player_green.moving_right = True

            if event.key == pygame.K_a:

                player_green.moving_down = False
                player_green.moving_top = False
                player_green.moving_right = False

                player_green.rotation(player_green.direction - east)
                player_green.direction = east
                player_green.moving_left = True

            elif event.key == pygame.K_SPACE:
                if player_green.direction == south:
                    green_b = Bullet(load_image('bulletGreen3_outline.png', -1), player_green.rect.x + 18,
                                     player_green.rect.y + 46)
                elif player_green.direction == north:
                    green_b = Bullet(load_image('bulletGreen3_outline.png', -1), player_green.rect.x + 18,
                                     player_green.rect.y - 23)
                elif player_green.direction == east:
                    green_b = Bullet(load_image('bulletGreen3_outline.png', -1), player_green.rect.x - 23,
                                     player_green.rect.y + 18)
                    green_b.rotation(-90)
                elif player_green.direction == west:
                    green_b = Bullet(load_image('bulletGreen3_outline.png', -1), player_green.rect.x + 42,
                                     player_green.rect.y + 18)
                    green_b.rotation(90)

                green_b.direction = player_green.direction
                bullets.add(green_b)

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                player_green.moving_top = False

            elif event.key == pygame.K_s:
                player_green.moving_down = False

            elif event.key == pygame.K_d:
                player_green.moving_right = False

            elif event.key == pygame.K_a:
                player_green.moving_left = False

    tiles.draw(screen)
    tiles.update()
    players.draw(screen)
    players.update()
    bullets.draw(screen)
    bullets.update()
    particles.draw(screen)
    particles.update()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
