import pygame, sys, time, random
from enum import Enum
from typing import Deque, Tuple
from collections import deque
from copy import deepcopy


class Difficulty(Enum):
    """
    Қиындық параметрлері
    Оңай      ->  10
    Орташа    ->  25
    Қиын      ->  40
    Өте қиын  ->  60
    """

    EASY = 10
    MEDIUM = 25
    HARD = 40
    SUPER_HARD = 60


class Direction(Enum):
    LEFT = "Сол"
    RIGHT = "Оң"
    UP = "Жоғары"
    DOWN = "Төмен"


class Block:
    BLOCK_SIZE = 10

    def __init__(self, x: int, y: int) -> None:
        self.x: int = Block.convert_to_block_pos(x)
        self.y: int = Block.convert_to_block_pos(y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, value: "Block") -> bool:
        return self.x == value.x and self.y == value.y

    @staticmethod
    def convert_to_block_pos(x: int) -> int:
        return x // Block.BLOCK_SIZE * Block.BLOCK_SIZE

    @staticmethod
    def create_random_block(max_x: int, max_y: int) -> "Block":
        return Block(
            Block.convert_to_block_pos(random.randrange(1, max_x)),
            Block.convert_to_block_pos(random.randrange(1, max_y)),
        )

    def move_up(self) -> None:
        self.y -= self.BLOCK_SIZE

    def move_down(self) -> None:
        self.y += self.BLOCK_SIZE

    def move_left(self) -> None:
        self.x -= self.BLOCK_SIZE

    def move_right(self) -> None:
        self.x += self.BLOCK_SIZE


# Ойын терезесінің (экранынің) параметрлері
class Window:
    def __init__(self, frame_size_x: int, frame_size_y: int) -> None:
        # Терезе ені
        self.frame_size_x = frame_size_x
        # Терезе биіктігі
        self.frame_size_y = frame_size_y

    # Шектен шығу анықтайтын метод
    def is_in_bound(self, block: Block) -> bool:
        if block.x < 0 or block.x >= self.frame_size_x:
            return False
        if block.y < 0 or block.y >= self.frame_size_y:
            return False
        return True

    def get_top_location(self) -> Tuple[int, int]:
        return (self.frame_size_x  / 2, self.frame_size_y / 4)

    def get_top_left_location(self) -> Tuple[int, int]:
        return (self.frame_size_x  / 10, self.frame_size_y / 10)
    
    def get_bottom_location(self) -> Tuple[int, int]:
        return (self.frame_size_x  / 2, self.frame_size_y / 1.25)

class Snake:
    def __init__(self, head_x_pos: int, head_y_pos: int, snake_length: int = 3) -> None:
        self.snake_body: Deque[Block] = deque()

        for i in range(snake_length):
            self.snake_body.append(Block(head_x_pos - i * Block.BLOCK_SIZE, head_y_pos))

        self.direction = Direction.RIGHT

    def get_head_pos(self) -> Block:
        return deepcopy(self.snake_body[0])

    def change_direction(self, new_direciton: Direction) -> None:
        # Жыланның бірден қарама-қарсы бағытта қозғала алмайтыды
        if new_direciton == Direction.UP and self.direction != Direction.DOWN:
            self.direction = Direction.UP
        if new_direciton == Direction.DOWN and self.direction != Direction.UP:
            self.direction = Direction.DOWN
        if new_direciton == Direction.LEFT and self.direction != Direction.RIGHT:
            self.direction = Direction.LEFT
        if new_direciton == Direction.RIGHT and self.direction != Direction.LEFT:
            self.direction = Direction.RIGHT

    def move(self, grow = False) -> None:
        # Жыланды жылжыту
        next_head_pos = self.get_head_pos()
        if self.direction == Direction.UP:
            next_head_pos.move_up()
        if self.direction == Direction.DOWN:
            next_head_pos.move_down()
        if self.direction == Direction.LEFT:
            next_head_pos.move_left()
        if self.direction == Direction.RIGHT:
            next_head_pos.move_right()
        if not grow:
            self.snake_body.pop()
        self.snake_body.appendleft(next_head_pos)

    # Жыланның денесіне қол тигізу
    def is_touching_itself(self) -> bool:
        match_count = 0
        for pos in self.snake_body:
            if self.get_head_pos() == pos:
                match_count += 1
        return match_count != 1


class Game:
    # Жылан басының координаталары
    SNAKE_X_POS = 100
    SNAKE_Y_POS = 50
    # Ойын терезесінің енімен биіктігі
    WINDOW_WIDTH = 720
    WINDOW_HEIGHT = 480
    # Жылан ұзындығы
    SNAKE_LENGTH = 3

    def __init__(self, difficulty: Difficulty) -> None:
        self.difficulty = difficulty
        self.snake = Snake(self.SNAKE_X_POS, self.SNAKE_Y_POS, self.SNAKE_LENGTH)

        # FPS - 1 секундтағы кадрлар сандарының контроллері
        self.fps_controller = pygame.time.Clock()

        self.window_frame = Window(Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT)

        #  Түс объекттері. Color класстың конструкторына берілетін 3 сан - қызыл, жасыл, көк (RGB color model) түстерінің кодтары. Осылайша түстерді анықтай аламыз.
        self.black = pygame.Color(0, 0, 0)
        self.white = pygame.Color(255, 255, 255)
        self.red = pygame.Color(255, 0, 0)
        self.green = pygame.Color(0, 255, 0)
        self.blue = pygame.Color(0, 0, 255)

        self.game_window = pygame.display.set_mode(
            (self.window_frame.frame_size_x, self.window_frame.frame_size_y)
        )

        # Жылан тамағының координаталары
        self.food_pos = Block.create_random_block(
            self.window_frame.frame_size_x,
            self.window_frame.frame_size_y,
        )

        self.score = 0
        # Тағамның координаталары өзгерді ме
        self.food_spawn = False

    def show_score(self, active: bool, color: pygame.Color, size: int) -> None:
        score_font = pygame.font.SysFont("times new roman", size)
        score_surface = score_font.render("Ұпай " + str(self.score), True, color)
        score_rect = score_surface.get_rect()
        if active == 1:
            score_rect.midtop = self.window_frame.get_top_left_location()
        else:
            score_rect.midtop = self.window_frame.get_bottom_location()
        self.game_window.blit(score_surface, score_rect)

    # Ойын Аяқталды
    def game_over(self) -> None:
        my_font = pygame.font.SysFont("times new roman", 90)  # шрифт
        game_over_surface = my_font.render(
            "Ойын Аяқталды", True, self.red
        )  # Ойын Аяқталды текст анықтауы
        # ойын аяқталу текісттің локация төртбұрышы
        game_over_rect = game_over_surface.get_rect()  
        game_over_rect.midtop = self.window_frame.get_top_location()
        # түсін анықтау
        self.game_window.fill(self.black)  
        self.game_window.blit(game_over_surface, game_over_rect)
        # ойынның счетің суретін салу
        self.show_score(False, self.red, 20)
        pygame.display.flip()
        # 3 секун күту
        time.sleep(3)
        # ойын терезесін жабу
        pygame.quit()
        # питон скриптті тоқтатады
        sys.exit()

    def paint_snake(self) -> None:
        for pos in self.snake.snake_body:
            # Жылан денесі
            # .draw.rect(ойын_беті, түс, xy-координаталары)
            # xy-координаталары -> .Rect(x, y, x_өлшемі, y_өлшемі)
            pygame.draw.rect(
                self.game_window,
                self.green,
                pygame.Rect(pos.x, pos.y, Block.BLOCK_SIZE, Block.BLOCK_SIZE),
            )

    def paint_apple(self) -> None:
        # Жылан тағамы
        pygame.draw.rect(
            self.game_window,
            self.white,
            pygame.Rect(
                self.food_pos.x, self.food_pos.y, Block.BLOCK_SIZE, Block.BLOCK_SIZE
            ),
        )

    def handle_key_press(self, event: pygame.event.Event) -> None:
        # W -> Жоғары; S -> Төмен; A -> Сол; D -> Оң
        if event.key == pygame.K_UP or event.key == ord("w"):
            self.snake.change_direction(Direction.UP)
        if event.key == pygame.K_DOWN or event.key == ord("s"):
            self.snake.change_direction(Direction.DOWN)
        if event.key == pygame.K_LEFT or event.key == ord("a"):
            self.snake.change_direction(Direction.LEFT)
        if event.key == pygame.K_RIGHT or event.key == ord("d"):
            self.snake.change_direction(Direction.RIGHT)
        # Esc -> Ойыннан шығу
        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def start(self) -> None:
        # Негізгі логика
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Перне басылған сайын
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_press(event)

            # Жылан алма жеу ережесі
            if self.snake.get_head_pos() == self.food_pos:
                self.score += 1
                self.food_spawn = True
                self.snake.move(True)
            else:
                self.snake.move(False)

            # Экранда жаңа тағамның пайда болуы
            if self.food_spawn:
                self.food_pos = Block.create_random_block(
                    self.window_frame.frame_size_x,
                    self.window_frame.frame_size_y,
                )
                self.food_spawn = False

            self.game_window.fill(self.black)
            self.paint_snake()
            self.paint_apple()

            print(self.snake.get_head_pos())

            # Ойынның аяқталу шарттары
            if not self.window_frame.is_in_bound(self.snake.get_head_pos()) or self.snake.is_touching_itself():
                self.game_over()

            self.show_score(True, self.white, 20)
            # Ойын экранын жаңарту
            pygame.display.update()
            # Жаңарту жылдамдығы
            self.fps_controller.tick(self.difficulty.value)


def main() -> None:
    # Ойынды инициализациялау, қателердің бар-жоғын тексеру
    check_errors = pygame.init()
    # pygame.init() мысал шығаруы -> (6, 0)
    # tuple-дағы екінші сан - қателердің саны
    if check_errors[1] > 0:
        print(
            f"[!] Ойынды инициализациалау кезінде {check_errors[1]} қате табылды, тоқтату..."
        )
        sys.exit(-1)
    else:
        print("[+] Ойын сәтті инициализацияланды")

    # Ойын терезесіне ат қою
    pygame.display.set_caption("Жылан")

    print("Ойын қыйншылығын танданыз")
    print("Қиындық тандау үшін 1-4 сан тандаңыз")
    print("Оңай      ->  1")
    print("Орташа    ->  2")
    print("Қиын      ->  3")
    print("Өте қиын  ->  4")

    difficulty = input()
    while not difficulty in ["1", "2", "3", "4"]:
        print("1 мен 5 арасындағы санды тандаңыз")
        difficulty = input()

    if difficulty == "1":
        difficulty = Difficulty.EASY
    if difficulty == "2":
        difficulty = Difficulty.MEDIUM
    if difficulty == "3":
        difficulty = Difficulty.HARD
    if difficulty == "4":
        difficulty = Difficulty.SUPER_HARD

    game = Game(difficulty)

    game.start()


if __name__ == "__main__":
    main()
