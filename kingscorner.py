''' King's corner made in Python with pygame '''

from random import shuffle
import pygame as pg

pg.font.init()
font = pg.font.SysFont('Comic Sans MS', 48)


def draw(win, board, deck, top, draw_outline=True):

    bg = pg.image.load('images/background.png')
    win.blit(bg, bg.get_rect())

    board.draw(win, draw_outline)
    if deck:
        card_down = pg.image.load('images/cardDown.png')
        card_down.set_colorkey((150, 150, 150))
        card_rect = card_down.get_rect()
        card_rect.x = 660
        card_rect.y = 200
        win.blit(card_down, card_rect)

    top.draw(win)

    pg.display.flip()


def get_card_image(suite, value):
    ''' Returns the image of a card with the given suite and value '''

    image = pg.image.load('images/cardUp.png')

    if value.isalpha():
        value_img = pg.image.load(f'images/{value}.png')
        value_img.set_colorkey((150, 150, 150))
        value_rect = value_img.get_rect()
    else:
        value_img = font.render(str(value), True, (0, 0, 0))
        value_rect = value_img.get_rect()
        value_rect.topleft = (65, 55)

    image.blit(value_img, value_rect)

    suite_img = pg.image.load(f'images/{suite}.png')
    suite_img.set_colorkey((150, 150, 150))
    suite_rect = suite_img.get_rect()

    image.blit(suite_img, suite_rect)
    image.set_colorkey((150, 150, 150))
    return image


class Events:
    ''' A static class that keeps track of events '''

    mouse = False
    d = False

    @classmethod
    def update(cls):

        for e in pg.event.get():

            if e.type == pg.QUIT:
                cls.stop()

            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_q:
                    cls.stop()
                elif e.key == pg.K_d:
                    cls.d = True
            
            elif e.type == pg.MOUSEBUTTONDOWN:
                cls.mouse = True
            elif e.type == pg.MOUSEBUTTONUP:
                cls.mouse = False
    
    @classmethod
    def stop(cls):

        pg.quit()
        raise SystemExit(0)


class Card:

    def __init__(self, suite, value):

        self.suite = suite
        self.value = value
        self.image = get_card_image(suite, value)
        self.rect = self.image.get_rect()
        self.facing = 'up'
        self.selected = False

    def draw(self, win):

        if self.facing == 'up':
            img = self.image
        else:
            img = pg.image.load('images/cardDown.png')

        img.set_colorkey((150, 150, 150))
        rect = img.get_rect()
        rect.center = self.rect.center
        win.blit(img, rect)

        if self.selected:
            outline = pg.image.load('images/selected.png')
            outline.set_colorkey((150, 150, 150))
            win.blit(outline, self.rect)


class Board:
    ''' A static class for the 4*4 board you play on '''

    matrix = list([None] * 4 for _ in range(4))

    @classmethod
    def create_places(cls):
        ''' Create the rects for where the cards go '''

        cls.places = []

        for y in range(4):
            cls.places.append([])

            for x in range(4):
                rect = pg.Rect((0, 0), (120, 180))
                rect.x = 10
                rect.y = 10
                rect.x += 130 * x
                rect.y += 190 * y
                cls.places[y].append(rect)

    @classmethod
    def draw(cls, win, draw_outline):

        # Draw the cards
        for my, py in zip(cls.matrix, cls.places):
            for mx, px in zip(my, py):
                if mx is not None:
                    mx.rect = px
                    mx.draw(win)

        # If the mouse is hovering over a rect in cls.places, make an outline (if its ok to)
        if draw_outline:
            mouse_x, mouse_y = pg.mouse.get_pos()
            for y in cls.places:
                for x in y:
                    if x.collidepoint(mouse_x, mouse_y):
                        img = pg.image.load('images/select.png')
                        img.set_colorkey((150, 150, 150))
                        rect = img.get_rect()
                        rect.topleft = x.topleft
                        win.blit(img, rect)


win = pg.display.set_mode((790, 770))
pg.display.set_caption("King's Corner")

# First we'll make the deck of cards
deck = []
for suite in 'schd':
    for value in [str(x) for x in range(2, 11)] + ['j', 'q', 'k', 'a']:
        deck.append(Card(suite, value))
shuffle(deck)

# Now we'll get the board ready
Board.create_places()

# The top card of the deck
top_card = deck.pop()
top_card.rect.x = 660
top_card.rect.y = 200

playing = True
while playing:

    Events.update()

    # Find out how many spaces need to be filled
    empty = 0
    for y in Board.matrix:
        for x in y:
            if x is None:
                empty += 1

    # Fill up the board
    for _ in range(empty):

        # Bring the top card of the deck over
        top_card.rect.x -= 130

        placing = True
        while placing:

            Events.update()
            if Events.mouse:

                for yi, y in enumerate(Board.places):
                    for xi, x in enumerate(y):
                        if x.collidepoint(pg.mouse.get_pos()):
                            if Board.matrix[yi][xi] is None:

                                valid = True
                                if top_card.value == 'k':
                                    if (xi not in (0, 3)) or (yi not in (0, 3)):
                                        valid = False
                                if top_card.value in 'qj':
                                    if ((xi in (0, 3)) and (yi in (0, 3))) or ((xi in (1, 2)) and (yi in (1, 2))):
                                        valid = False
                                if valid:
                                    Board.matrix[yi][xi] = top_card
                                    placing = False

                Events.mouse = False

            draw(win, Board, deck, top_card)

        if deck:
            top_card = deck.pop()
            top_card.rect.x = 660
            top_card.rect.y = 200
        else:
            while True:
                Events.update()

    top_card.facing = 'down'
    Events.mouse = False

    # Empty the board
    selected = None
    while True:

        Events.update()
        if Events.mouse:

            for yi, y in enumerate(Board.places):
                for xi, x in enumerate(y):
                    if x.collidepoint(pg.mouse.get_pos()):

                        if Board.matrix[yi][xi] is None:
                            continue
                        if Board.matrix[yi][xi].value in 'kqj':
                            if selected is not None:
                                Board.matrix[selected[0]][selected[1]].selected = False
                                selected = None
                            continue

                        if selected is None:
                            if Board.matrix[yi][xi].value == '10':
                                Board.matrix[yi][xi] = None
                            else:
                                Board.matrix[yi][xi].selected = True
                                selected = [yi, xi]
                        else:
                            if [yi, xi] == selected:
                                selected = None
                                continue

                            selected_value = (1 if Board.matrix[selected[0]][selected[1]].value == 'a'
                                              else int(Board.matrix[selected[0]][selected[1]].value))
                            card_value = 1 if Board.matrix[yi][xi].value == 'a' else int(Board.matrix[yi][xi].value)

                            card_sum = selected_value + card_value
                            if card_sum == 10:
                                Board.matrix[selected[0]][selected[1]] = None
                                Board.matrix[yi][xi] = None
                                selected = None
                            else:
                                Board.matrix[selected[0]][selected[1]].selected = False
                                selected = None
            Events.mouse = False

        if Events.d:
            Events.d = False
            break

        draw(win, Board, deck, top_card)
    
    top_card.facing = 'up'
