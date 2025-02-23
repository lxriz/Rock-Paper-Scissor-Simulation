import pyglet
from entities import Entity
from entities import Species
import random as r
import matplotlib.pyplot as plt

WIDTH = 1200
HEIGHT = 800

GRID_SIZE = 400

X_GRID = WIDTH//GRID_SIZE+1
Y_GRID = HEIGHT//GRID_SIZE+1

ENTITY_NUMB = 60
ENTITY_SIZE = 55

LABELS = []
RESOURCES = []
ENTITIES = []
RULES = [[0,1,0],
         [1,1,2],
         [0,2,2]]

GRID = []

DATA = []


def load_image(name, path, color):
    species_image = Species(name, path, ENTITY_SIZE, color)
    RESOURCES.append(species_image)


def floating_average(data, size):
    i = 0

    counter = 0
    sums = 0

    y = []
    x = []

    while i < len(data):
        if counter == size:
            counter = 0
            sums = sums // size
            x.append(i)
            y.append(sums)
            sums = 0

        sums += data[i]
        i += 1
        counter += 1

    return x, y


def load_labels():
    offset = (len(LABELS)-1) * 45
    label = pyglet.text.Label(font_size=30, font_name="DIN Alternate", color=(60, 60, 60, 255), x=10, y=10 + offset)
    LABELS.append(label)


update_time = 0


def update(dt):
    global update_time

    if update_time == 60:
        update_time = 0
        i = 0
        for entry in DATA:
            entry.append(RESOURCES[i].number)
            i += 1
    else:
        update_time += 1

    if check_end():
        pyglet.clock.unschedule(update)
        LABELS[0].draw()
        if update_time != 0:
            i = 0
            for entry in DATA:
                entry.append(RESOURCES[i].number)
                i += 1

        for index in range(0, len(DATA)):
            x = range(0, len(DATA[index]))
            y = DATA[index]
            plt.plot(x, y, color=RESOURCES[index].color, linewidth=3, label=RESOURCES[index].name)

        floating_size = 5
        for index in range(0, len(DATA)):
            x, y = floating_average(DATA[index], floating_size)
            plt.plot(x, y, "--", color=RESOURCES[index].color, label=f"{RESOURCES[index].name} floating average", )

        plt.xlabel("Turn")
        plt.ylabel("Number of elements")
        plt.legend()
        plt.show()

    # Entry of every entity in grid
    for entity in ENTITIES:
        row = int(entity.body.x // GRID_SIZE)
        column = int(entity.body.y // GRID_SIZE)
        GRID[column][row].append(entity)

    # Calculation of collision
    for column in range(0, Y_GRID):
        for row in range(0, X_GRID):
            amount_in_list = len(GRID[column][row])
            while amount_in_list > 0:
                entity = GRID[column][row][0]
                i = 0

                for index in range(1,amount_in_list):
                    collider = GRID[column][row][index]

                    # Collision occurred
                    if entity.check_collision(collider):
                        species_entity = entity.species
                        species_collider = collider.species

                        rule_entity = RULES[species_entity][species_collider]
                        rule_collider = RULES[species_collider][species_entity]

                        #print(species_entity, "->",rule_entity," | " , species_collider, "->", rule_collider)

                        if rule_entity != species_entity:
                            RESOURCES[species_entity].entity_killed()
                            RESOURCES[rule_entity].entity_born()
                            entity.change_species(species=rule_entity,
                                                  size=ENTITY_SIZE,
                                                  scale=RESOURCES[rule_entity].scale,
                                                  image=RESOURCES[rule_entity].image)

                        if rule_collider != species_collider:
                            RESOURCES[species_collider].entity_killed()
                            RESOURCES[rule_collider].entity_born()
                            collider.change_species(species=rule_entity,
                                                  size=ENTITY_SIZE,
                                                  scale=RESOURCES[rule_collider].scale,
                                                  image=RESOURCES[rule_collider].image)

                        GRID[column][row].pop(index)
                        amount_in_list -= 1
                        break
                    i += 1
                GRID[column][row].pop(0)
                amount_in_list -= 1

    # Move of every entity
    for entity in ENTITIES:
        entity.move(dt, width=WIDTH, height=HEIGHT)

    for index in range(1, len(LABELS)):
        LABELS[index].text = f"{RESOURCES[index-1].name}: {RESOURCES[index-1].number}"


def new_grid():
    for _ in range(0, Y_GRID):
        row = []
        for _ in range(0, X_GRID):
            row.append([])
        GRID.append(row)


def check_end():
    i = 0
    for species in RESOURCES:
        if species.number == ENTITY_NUMB:
            LABELS[0].text = f"{RESOURCES[i].name} has won !"
            LABELS[0].draw()
            return True
        i += 1

    return False


def start():
    window = pyglet.window.Window(width=WIDTH, height=HEIGHT, caption="GAME OF DEATH")
    pyglet.gl.glClearColor(0.1, 0.1, 0.1, 0.1)

    load_image(name="Scissors", path="scissors.png", color="blue")
    load_image(name="Rock", path="rock.png", color="gray")
    load_image(name="Paper", path="paper.png", color="brown")



    LABELS.append(pyglet.text.Label(x=10, y=HEIGHT-80, font_size=40, color=(255, 3, 83, 255)))
    for _ in RESOURCES:
        load_labels()

    new_grid()

    for _ in RESOURCES:
        DATA.append([])

    for id in range(0, ENTITY_NUMB):
        species = r.randint(0, len(RESOURCES)-1)
        RESOURCES[species].entity_born()
        scale = RESOURCES[species].scale
        image = RESOURCES[species].image
        entity = Entity(species=species, size=ENTITY_SIZE, scale=scale, image=image, id=id)
        entity.set_random_position(height=HEIGHT, width=WIDTH)
        entity.set_random_vector()
        ENTITIES.append(entity)

    @window.event()
    def on_draw():
        window.clear()
        for label in LABELS:
            label.draw()

        for entity in ENTITIES:
            entity.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()


start()
