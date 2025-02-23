import pyglet
import random as r
import math


class Species:

    def __init__(self, name, path, target_size, color):
        self.image = pyglet.image.load(path)
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.name = name
        self.scale = target_size / self.image.width
        self.number = 0
        self.color = color

    def entity_killed(self):
        self.number -= 1

    def entity_born(self):
        self.number += 1


class Entity:

    max_speed = 100
    last_collision = -1

    def __init__(self, id, species, size, scale, image):
        self.species = species
        self.body = pyglet.sprite.Sprite(img=image)
        self.body.scale = scale
        self.radius = size // 2

        self.x_vector = 0
        self.y_vector = 0

        self.id = id

    def set_random_position(self, height, width):
        self.body.x = r.randint(self.radius, width - self.radius)
        self.body.y = r.randint(self.radius, height - self.radius)

    def calc_rotation(self):
        length = math.sqrt(self.x_vector**2 + self.y_vector**2)
        degree = self.x_vector / (length + 1)
        degree = math.acos(degree) * 180 / 3.14

        if self.y_vector > 0:
            self.body.rotation = -degree
        else:
            self.body.rotation = degree

    def set_random_vector(self):
        self.x_vector = r.randint(0, self.max_speed * 2) - self.max_speed
        self.y_vector = r.randint(0, self.max_speed * 2) - self.max_speed
        self.calc_rotation()

    def border_collision(self, width, height):
        collided = False

        if self.body.x <= self.radius:
            self.body.x = self.radius
            self.x_vector *= -1
            collided = True

        if self.body.y <= self.radius:
            self.body.y = self.radius
            self.y_vector *= -1
            collided = True

        if self.body.x >= width - self.radius:
            self.body.x = width - self.radius
            self.x_vector *= -1
            collided = True

        if self.body.y >= height - self.radius:
            self.body.y = height - self.radius
            self.y_vector *= -1
            collided = True

        if collided:
            self.calc_rotation()
            self.last_collision = -1


    def move(self,dt , width, height):
        self.border_collision(width=width, height=height)
        self.body.x += self.x_vector * dt
        self.body.y += self.y_vector * dt

    def check_collision(self, collider):
        if self.last_collision == collider.id:
            return False

        dx = collider.body.x - self.body.x
        dy = collider.body.y - self.body.y

        distance = math.sqrt(dx**2 + dy**2)

        if distance <= self.radius + collider.radius:
            temp_x_vec = self.x_vector
            temp_y_vec = self.y_vector
            self.change_vector(collider.x_vector, collider.y_vector)
            collider.change_vector(temp_x_vec, temp_y_vec)

            self.last_collision = collider.id
            collider.last_collision = self.id
            return True
        else:
            return False

    def change_species(self, species, size, scale, image):
        self.species = species
        self.radius = size // 2
        self.body.scale = scale
        self.body.image = image

    def change_vector(self, x, y):
        self.x_vector = x
        self.y_vector = y
        self.calc_rotation()

    def draw(self):
        self.body.draw()
