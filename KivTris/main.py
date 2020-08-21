from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

import random

# I know it is an ugly global variable.
player_score = 0


class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)


# Startscreen
class Menu1(Screen):
    @staticmethod
    def quit_the_game():
        exit()


# Credits
class Menu3(Screen):
    scrollingText = ListProperty([])
    offsetList = NumericProperty(0)
    stdFontSize = NumericProperty(12)
    stdFontColor = (1, 1, 1, 1)
    scrollingTextPaused = BooleanProperty(False)
    _clock = None
    creditText = [" ",
                  ("KivTris", 8, (.2, .2, 1, 1)),
                  " ",
                  ("Author", 8, (.2, .2, 1, 1)),
                  "Github: Johdal12",
                  " ",
                  "https://de.depositphotos.com/56794337/stock-illustration-dark-tetris-background.html",
                  ("Buttons from:", 4, (.2, 1, .2, 1)),
                  "https://dlpng.com/png/6408014",
                  " ",
                  ("Code", 8, (.2, .2, 1, 1)),
                  ("ScreenManager from:", 4, (.2, 1, .2, 1)),
                  "https://stackoverflow.com/questions/46716017/kivy-python-screenmanager",
                  ("Keyboardcontrol from:", 4, (.2, 1, .2, 1)),
                  "https://stackoverflow.com/questions/17280341/how-do-you-check-for-keyboard-events-with-kivy",
                  " ",
                  ("Music", 8, (.2, .2, 1, 1)),
                  ("mp3 from:", 4, (.2, 1, .2, 1)),
                  "http://gamethemesongs.com/Tetris_-_GameBoy_-_Type_A.html",
                  " ",
                  ]

    def __init__(self, **kwargs):
        # first fill the scrolling text list with enough spaces/lines
        self.scrollingText = []
        for i in range(1, 32 + len(self.creditText)):
            self.scrollingText.append(" ")
            self.scrollingText.append(0)
            self.scrollingText.append(self.stdFontColor)

        # fill the scrolling text list with the credits text
        for i in range(1, len(self.creditText) + 1):
            element = self.creditText[i - 1]
            if isinstance(element, tuple):
                self.scrollingText[i * 3 + 45] = element[0]
                self.scrollingText[i * 3 + 46] = element[1]
                self.scrollingText[i * 3 + 47] = element[2]
            else:
                self.scrollingText[i * 3 + 45] = element
                self.scrollingText[i * 3 + 46] = 0
                self.scrollingText[i * 3 + 47] = self.stdFontColor

        # and finally the super init :-)
        super(Menu3, self).__init__(**kwargs)

    def on_pre_leave(self, *args):
        # stop the clock...
        if self._clock:
            self._clock.cancel()

    def on_pre_enter(self, *args):
        self.offsetList = 0
        self.stdFontSize = 12
        self.scrollingTextPaused = False
        self.start_the_clock()

    def start_the_clock(self):
        self._clock = Clock.schedule_interval(self.change_offsetlist, .75)

    def change_offsetlist(self, interval):
        # pause button was pressed then don't change the offset
        if self.scrollingTextPaused:
            return interval
        if (self.offsetList + 15) * 3 < len(self.scrollingText):
            self.offsetList += 1
        else:
            # restart with credits
            self.offsetList = 0

    def reduce_std_font_size(self):
        if self.stdFontSize > 2:
            self.stdFontSize = self.stdFontSize - 1

    def raise_std_font_size(self):
        if self.stdFontSize < 32:
            self.stdFontSize += 1

    def pause_scrolling_text(self):
        if self.scrollingTextPaused:
            self.scrollingTextPaused = False
            self.start_the_clock()
        else:
            if self._clock:
                self._clock.cancel()
            self.scrollingTextPaused = True


# Game
class Menu4(Screen):
    game_paused = BooleanProperty(False)
    music_off = BooleanProperty(False)
    brick_field = ListProperty([])
    next_brick = ListProperty([])
    score = NumericProperty(0)
    level = NumericProperty(1)
    lines = NumericProperty(0)
    falling_brick = []
    falling_brick_x = 4
    falling_brick_y = -2
    _brick_timer = None
    _drop_speed = 1.0
    _full_lines = []
    _keyboard = None
    _music = None
    _music_timer = None
    empty_brick_line = "W" + 10 * "_" + "W"

    def __init__(self, **kwargs):
        for i in range(0, 4):
            self.next_brick.append("____")
        # first fill the brickfield with enough lines
        for i in range(0, 21):
            self.brick_field.append(self.empty_brick_line)
        self.brick_field.append(12*"W")
        self.full_lines = []
        self._drop_speed = 1.0
        self.level = 1
        self.score = 0
        self.lines = 0
        self._music = SoundLoader.load("Tetris - GameBoy - Type A.mp3")
        # finally the super init
        super(Menu4, self).__init__(**kwargs)

    def clear_brick_field(self):
        for i in range(0, 21):
            self.brick_field[i] = self.empty_brick_line

    def _keyboard_closed(self):
        if not self._keyboard:
            return
        # Clear Keyboard bindings
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'a' or keycode[1] == 'left':
            self.brick_moves_left()
        elif keycode[1] == 'd' or keycode[1] == 'right':
            self.brick_moves_right()
        elif keycode[1] == 's' or keycode[1] == 'down':
            self.brick_moves_down(1)
        elif keycode[1] == 'w' or keycode[1] == 'up':
            self.brick_rotates()
        elif keycode[1] == 'p':
            self.pause_the_game()
        elif keycode[1] == "dummy":
            print(keyboard, text, modifiers)
        return True

    def on_pre_enter(self, *args):
        self.clear_brick_field()
        self.falling_brick = self.get_a_brick()
        self.next_brick = self.get_a_brick()
        self.falling_brick_x = 4
        self.falling_brick_y = -2
        self._drop_speed = 1.0
        self.level = 1
        self.score = 0
        self.lines = 0
        self.game_paused = False
        self.play_the_music()

        self.calculate_drop_speed()
        self.draw_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
        self._start_the_game()

    def on_pre_leave(self, *args):
        self._stop_the_game()
        self.stop_the_music()

    def play_the_music(self, interval=0):
        if self._music:
            self._music.play()
            self._music_timer = Clock.schedule_once(self.play_the_music, self._music.length+4)
        return interval

    def stop_the_music(self):
        if self._music:
            self._music.stop()
            if self._music_timer:
                self._music_timer.cancel()

    def music_on_off(self):
        if self.music_off:
            self.music_off = False
            self.play_the_music()
        else:
            self.music_off = True
            self.stop_the_music()

    def pause_the_game(self):
        if self.game_paused:
            self.game_paused = False
            self._start_the_game()
        else:
            self.game_paused = True
            self._stop_the_game()

    def _start_the_game(self):
        self._brick_timer = Clock.schedule_interval(self.brick_timer_drop, self._drop_speed)
        # initialize the Keyboard for Computer Use
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def brick_timer_drop(self, interval):
        self.brick_moves_down(0)
        return interval

    def _stop_the_game(self):
        # stop the clock...
        if self._brick_timer:
            self._brick_timer.cancel()
        # stop the keyboard...
        if self._keyboard:
            self._keyboard_closed()

    def draw_brick_at_location(self, brick, brick_x, brick_y):
        if not self.check_if_brick(brick):
            return
        # lets draw it
        for row in range(0, 4):
            if 0 <= brick_y+row < len(self.brick_field):
                row_from_field = list(self.brick_field[brick_y+row])
            else:
                row_from_field = []

            for col in range(0, 4):
                if 0 <= brick_x+col < len(row_from_field):
                    if brick[row][col] != "_":
                        row_from_field[brick_x+col] = brick[row][col]

            if 0 <= brick_y+row < len(self.brick_field):
                self.brick_field[brick_y+row] = ''.join(row_from_field)

    # Check if brick is a legal brick?
    @staticmethod
    def check_if_brick(brick):
        if len(brick) != 4:
            return False
        else:
            for row in brick:
                if len(row) != 4:
                    return False
        return True

    def collision_brick_at_location(self, brick, brick_x, brick_y):
        if not self.check_if_brick(brick):
            return False
        # lets check for collisions
        for row in range(0, 4):
            if 0 <= brick_y+row < len(self.brick_field):
                row_from_field = list(self.brick_field[brick_y+row])
            else:
                row_from_field = []

            for col in range(0, 4):
                if 0 <= brick_x+col < len(row_from_field):
                    if brick[row][col] != "_" and row_from_field[brick_x+col] != "_":
                        # print("collision @ ", brick_x, col, brick_y, row)
                        return True
        return False

    def remove_brick_at_location(self, brick, brick_x, brick_y):
        if not self.check_if_brick(brick):
            return
        # lets remove it
        for row in range(0, 4):
            if 0 <= brick_y+row < len(self.brick_field):
                row_from_field = list(self.brick_field[brick_y+row])
            else:
                row_from_field = []

            for col in range(0, 4):
                if 0 <= brick_x+col < len(row_from_field):
                    if brick[row][col] != "_":
                        row_from_field[brick_x+col] = "_"

            if 0 <= brick_y+row < len(self.brick_field):
                self.brick_field[brick_y+row] = ''.join(row_from_field)

    def brick_moves_down(self, score_plus=0):
        if self.game_paused:
            return
        self.remove_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
        # if not collides -> remove old and moves to the new row
        # else -> stays in old row and brick change
        if not self.collision_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y+1):
            self.falling_brick_y += 1
            self.draw_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
            # If brick moves down because of interaction from user: score +1; automatic movement score +0.
            self.score += score_plus
        else:
            self.draw_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
            # Check for and remove full lines!
            self.check_for_and_remove_full_lines()

            self.falling_brick_x = 4
            self.falling_brick_y = -2
            self.falling_brick = self.next_brick[:]
            self.next_brick = self.get_a_brick()

            # There is no place for a new brick.
            if self.collision_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y):
                self.game_over()

    def check_for_and_remove_full_lines(self):
        self.full_lines = []
        for row in range(0, 4):
            bricks_in_line = 0
            for col in range(1, 11):
                if 0 <= row+self.falling_brick_y < len(self.brick_field)-1:
                    if self.brick_field[row + self.falling_brick_y][col] != "_":
                        bricks_in_line += 1
            if bricks_in_line == 10:
                self.full_lines.append(row+self.falling_brick_y)
                # Lets make the full line a different color.
                self.brick_field[row + self.falling_brick_y] = "W" + "B"*10 + "W"

        # We have no full lines. Just return.
        if len(self.full_lines) == 0:
            return

        # First stop the game
        self._stop_the_game()
        # Dont forget to calculate the new Score!
        self.calculate_new_score()
        # We have to wait few moments to show the changed full lines.
        Clock.schedule_once(self.step_for_step_remove_the_lines, .5)

    def calculate_new_score(self):
        self.lines += len(self.full_lines)
        factor = [40, 100, 300, 1200]
        self.score += factor[len(self.full_lines)-1] * self.level
        if self.lines > self.level * 10:
            self.level += 1
            self.calculate_drop_speed()

    def calculate_drop_speed(self):
        self._drop_speed = (0.8 - ((self.level - 1) * 0.007)) ** ((self.level + 1) / 2 - 1.0)

    def step_for_step_remove_the_lines(self, interval):
        if len(self.full_lines) == 0:
            # Restart the game
            self._start_the_game()
            return interval
        else:
            # Then remove one full line after the other from top down
            # and move the lines above one row down.
            self.move_lines_down_to_row(self.full_lines[0])
            # We have to wait few moments to show the changed lines.
            self.full_lines = self.full_lines[1:]
            Clock.schedule_once(self.step_for_step_remove_the_lines, .5)

    def move_lines_down_to_row(self, target_row):
        # The Value of target_row is
        if 0 > target_row or target_row >= len(self.brick_field):
            return

        for i in range(target_row, 0, -1):
            self.brick_field[i] = self.brick_field[i-1]
        self.brick_field[0] = "W" + 10*"_" + "W"

    def brick_moves_left(self):
        if self.game_paused:
            return
        # falling_brick_x - 1
        self.remove_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
        # if collides -> stays in old col
        # else -> remove old and moves to the new col
        if self.collision_brick_at_location(self.falling_brick, self.falling_brick_x-1, self.falling_brick_y):
            self.draw_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
        else:
            self.falling_brick_x -= 1
            self.draw_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)

    def brick_moves_right(self):
        if self.game_paused:
            return
        # falling_brick_x + 1
        self.remove_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
        # if collides -> stays in old col
        # else -> remove old and moves to the new col
        if self.collision_brick_at_location(self.falling_brick, self.falling_brick_x+1, self.falling_brick_y):
            self.draw_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
        else:
            self.falling_brick_x += 1
            self.draw_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)

    def brick_rotates(self):
        if self.game_paused:
            return
        backup_brick = self.falling_brick[:]
        self.remove_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
        # rotates + 90degree
        self.falling_brick = self.brick_rotate_90degree(self.falling_brick)
        # if collides -> return to old orientation
        # else ->  new orientation it is
        if self.collision_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y):
            self.falling_brick = backup_brick[:]
            self.draw_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)
        else:
            self.draw_brick_at_location(self.falling_brick, self.falling_brick_x, self.falling_brick_y)

    def brick_rotate_90degree(self, brick):
        if not self.check_if_brick(brick):
            return self.get_a_brick()
        new_brick_str = ''.join(brick)
        new_brick_str = new_brick_str[::-1]
        new_brick = []
        for i in range(0, 4):
            new_brick.append(new_brick_str[3-i::4])
        return new_brick

    @staticmethod
    def get_a_brick(brick_wish=-1):
        # 1-7 are the numbers for a possible brick
        brick_number = random.randrange(1, 8, 1)
        # We have a brick_wish :-)
        if 1 <= brick_wish < 8:
            brick_number = brick_wish
        # the bricks
        # Brick number 1 == I
        if brick_number == 1:
            new_brick = ["____",
                         "1111",
                         "____",
                         "____"]
        # Brick number 2 == J
        elif brick_number == 2:
            new_brick = ["____",
                         "_2__",
                         "_222",
                         "____"]
        # Brick number 3 == L
        elif brick_number == 3:
            new_brick = ["____",
                         "___3",
                         "_333",
                         "____"]
        # Brick number 4 == o
        elif brick_number == 4:
            new_brick = ["____",
                         "_44_",
                         "_44_",
                         "____"]
        # Brick number 5 == S
        elif brick_number == 5:
            new_brick = ["____",
                         "__55",
                         "_55_",
                         "____"]
        # Brick number 6 == T
        elif brick_number == 6:
            new_brick = ["____",
                         "__6_",
                         "_666",
                         "____"]
        # Brick number 7 == Z
        else:
            new_brick = ["____",
                         "_77_",
                         "__77",
                         "____"]

        # we have a newbrick
        return new_brick

    def game_over(self):
        global player_score
        self._stop_the_game()
        player_score = self.score
        self.manager.current = "Highscore"


# Highscore
class Menu5(Screen):
    highscoreText = ListProperty([])
    enterNewHighscore = BooleanProperty(False)
    _highscoreFilename = "score.txt"

    def __init__(self, **kwargs):
        # first fill the highscore with enough spaces/lines
        self.highscoreText = []
        for i in range(1, 16):
            self.highscoreText.append(" ")

        # and finally the super init :-)
        super(Menu5, self).__init__(**kwargs)

    def on_pre_leave(self, *args):
        global player_score
        # reset the score, when leaving this screen
        player_score = 0
        # write the score
        self.save_highscore()

    def on_pre_enter(self, *args):
        global player_score
        if player_score > 0:
            if self.get_minimum_highscore() < player_score:
                self.enterNewHighscore = True
            else:
                self.enterNewHighscore = False
                player_score = 0

        # read the score
        self.read_highscore()

    # namegenerator
    @staticmethod
    def get_random_name():
        randomNamesForHighscore = ["Chuck", "Arnold", "Bruce", "Alexej", "Anton", "Kivy", "Bob", "Cathryn",
                                   "Alyssa", "Beatrice", "Hero", "Charlie", "Peanut", "Udo", "Klaus", "Maria",
                                   "Stefan", "Abraham", "Ben", "Chris", "Lara", "Jenny", "Chrissy", "Hubert",
                                   "Normen", "Steffen", "Eva", "Max", "Melissa", "Tristan", "Carsten", "Anita",
                                   "Ute", "Moni", "Nele", "Michael", "Jacob", "Claudia", "Charlotte", "Hanna",
                                   "Henry", "Henning", "Dave", "Ida", "Bjoern", "Jonathan", "Johan", "George",
                                   "Cindy", "Kevin", "Sylvester", "Kobe", "Jet", "Angel", "Jason", "Caprice",
                                   "Mickey", "Anetta", "Dolph", "Tia", "Randy", "Jamie", "Giselle", "Gary",
                                   "Nessa", "Terry", "Ariana", "Steve", "Tiffany", "Nancy"]
        return random.choice(randomNamesForHighscore)

    # generate new highscore = reset highscore
    def generate_new_highscore(self):
        for i in range(1, len(self.highscoreText) + 1):
            self.highscoreText[-i] = self.define_highscore_line(self.get_random_name(), i * 1000)

        # backup before rage quit...
        self.save_highscore()

    @staticmethod
    def define_highscore_line(newname, newscore):
        score = str(newscore)
        filler = (40 - len(score) - len(newname)) * "."
        return newname + filler + score

    def save_highscore(self):
        openedFile = open(self._highscoreFilename, "w")
        for i in range(0, len(self.highscoreText)):
            openedFile.write(self.highscoreText[i] + "\n")
        openedFile.close()

    def read_highscore(self):
        openedFile = open(self._highscoreFilename, "r")
        readingData = openedFile.readlines()
        index = 0
        while index < len(self.highscoreText) and index < len(readingData):
            self.highscoreText[index] = readingData[index].strip()
            index += 1
        # readlines to few
        if index < len(self.highscoreText):
            for i in range(index, len(self.highscoreText)):
                self.highscoreText[i] = self.define_highscore_line("Unknown", 0)
        openedFile.close()

    def get_minimum_highscore(self):
        return self.get_score_from_position(len(self.highscoreText) - 1)

    @staticmethod
    def get_score_from_line(scoreline):
        #
        if str.find(scoreline[::-1], ".") == -1:
            return 0
        # string reduced to score (right side of string)
        scoreline = scoreline[len(scoreline) - str.find(scoreline[::-1], "."):]

        # convertable?
        if scoreline.isnumeric():
            scoreline = int(scoreline)
        else:
            scoreline = 0
        # return the value
        return scoreline

    def insert_new_highscore(self, newname, newscore):
        # its to low? go
        if newscore < self.get_minimum_highscore():
            return
        # where to place?
        newPosition = len(self.highscoreText)
        for i in range(0, len(self.highscoreText)):
            if self.get_score_from_position(i) < newscore:
                newPosition = i
                break
        # move from lines from new position 1 step down
        for i in range(len(self.highscoreText) - 1, newPosition, -1):
            self.highscoreText[i] = self.highscoreText[i - 1]

        # new position = newName & newScore
        self.highscoreText[newPosition] = self.define_highscore_line(newname, newscore)

    def get_score_from_position(self, scoreindex=0):
        # check for out of range
        if scoreindex < 0:
            return 0
        if scoreindex >= len(self.highscoreText):
            return 0
        # score from line
        return self.get_score_from_line(self.highscoreText[scoreindex])

    @staticmethod
    def get_name_from_line(scoreline):
        if str.find(scoreline, "...") == -1:
            return "Unknown"
        # string reduced to score (right side of string)
        scoreline = scoreline[0:str.find(scoreline, "...")]

        # convertable?
        if len(scoreline) == 0:
            return "Unknown"
        else:
            return scoreline

    def name_entered(self, new_name):
        global player_score
        # do we really are allowed enter the highscore now?
        if not self.enterNewHighscore:
            return
        # check the input for to long or to short input-string
        if len(new_name) == 0:
            new_name = "Unknown"
        elif len(new_name) > 30:
            new_name = new_name[:31]

        self.insert_new_highscore(new_name, player_score)
        self.enterNewHighscore = False
        self.ids.highscoreinput.text = "Insert_your_name"
        player_score = 0
        self.save_highscore()


Builder.load_file("KivTris.kv")


class KivTris(App):
    def __init__(self, **kwargs):
        super(KivTris, self).__init__(**kwargs)

    def build(self):
        Window.clearcolor = (0, 0, 0, 1)

        # avoid error multiple screens detected, when using screenmanager inside .kv file
        sm = MyScreenManager()
        sm.add_widget(Menu1(name="Startscreen"))
        sm.add_widget(Menu3(name="Credits"))
        sm.add_widget(Menu4(name="Game"))
        sm.add_widget(Menu5(name="Highscore"))

        return sm


#
# start the fun
#
if __name__ == '__main__':
    KivTris().run()
