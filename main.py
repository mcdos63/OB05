import pygame
import sys
from collections import deque
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
CELL_SIZE = 30  # Размер ячейки
MAZE_WIDTH, MAZE_HEIGHT = 30, 20  # Размеры матрицы
WIDTH, HEIGHT = MAZE_WIDTH * CELL_SIZE, MAZE_HEIGHT * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Evolution")

# Цвета
color0 = (100, 100, 100)
color1 = (10, 50, 50)
color2 = (10, 70, 70)
color3 = (10, 90, 90)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)  # Преграда 1 - оранжевая

# Загрузка спрайтов
pacman_sprite = pygame.image.load("pacman.png")  # Спрайт персонажа (30x30)
monster_sprite = pygame.image.load("monster.png")  # Спрайт монстра (30x30)
pacman_sprite = pygame.transform.scale(pacman_sprite, (CELL_SIZE, CELL_SIZE))
monster_sprite = pygame.transform.scale(monster_sprite, (CELL_SIZE, CELL_SIZE))

# Матрица игрового поля в виде строки
maze_string = (
    "333333333333333333333333333333"
    "300000000000000300000030000003"
    "302001020002000300300030000003"
    "300001000001000300200000320003"
    "323233300001000000200000300003"
    "300001033333333333322332330003"
    "300001000000000000000000000003"
    "300001000033333333333333333333"
    "302222100030000000000000000003"
    "300000000030000300000000000003"
    "300001000000000300000000333333"
    "300001000000000300000000000003"
    "300001000000000300000000000003"
    "300001222233330333333333000003"
    "300003300000000300000000000333"
    "300003000000000300033333333333"
    "300000000000000000220000000003"
    "300033333333333333300000000003"
    "300000000000000000000000000043"
    "333333333333333333333333333333"
)

# Преобразование строки в матрицу
maze = [list(map(int, maze_string[i:i + MAZE_WIDTH])) for i in range(0, len(maze_string), MAZE_WIDTH)]

# Первоначальные позиции
pacman_x, pacman_y = 1, 1  # Начальная позиция персонажа
monster_x, monster_y = 27, 18  # Начальная позиция монстра

# Класс для создания частиц
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 8)
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(-2, -0.5)  # Частицы движутся вверх

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.size -= 0.1  # Уменьшение размера частицы со временем
        if self.size <= 0:
            particles.remove(self)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

# Список для хранения частиц
particles = []

# Счетчики
monster_attempts = {}  # Словарь для подсчета попыток преодоления преград 2
monster_move_counter = 0  # Счетчик ходов для монстра (для замедления)

# Волновой алгоритм для поиска пути
def find_path(start_x, start_y, target_x, target_y):
    queue = deque([(start_x, start_y)])
    visited = [[False] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]
    prev = [[None] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]
    visited[start_y][start_x] = True

    while queue:
        x, y = queue.popleft()
        if (x, y) == (target_x, target_y):
            break

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and
                not visited[ny][nx] and maze[ny][nx] in [0, 1]
            ):
                queue.append((nx, ny))
                visited[ny][nx] = True
                prev[ny][nx] = (x, y)

    # Восстановление пути
    path = []
    current = (target_x, target_y)
    while current and current != (start_x, start_y):
        path.append(current)
        current = prev[current[1]][current[0]]
    path.reverse()
    return path

# Функция отрисовки лабиринта
def draw_maze():
    for row_index, row in enumerate(maze):
        for col_index, cell in enumerate(row):
            color = None
            if cell == 0:
                color = color0
            elif cell == 1:
                color = color1
            elif cell == 2:
                color = color2
            elif cell == 3:
                color = color3
            elif cell == 4:
                color = BLUE

            if color:
                pygame.draw.rect(
                    screen,
                    color,
                    (col_index * CELL_SIZE, row_index * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )

# Основной игровой цикл
clock = pygame.time.Clock()
running = True
player_moved = False  # Флаг, указывающий, что игрок сделал ход
victory = False  # Флаг, указывающий, что игрок выиграл

while running:
    screen.fill(BLACK)

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if not player_moved:  # Ход игрока
        new_pacman_x, new_pacman_y = pacman_x, pacman_y

        if keys[pygame.K_UP]:
            new_pacman_y -= 1
        elif keys[pygame.K_DOWN]:
            new_pacman_y += 1
        elif keys[pygame.K_LEFT]:
            new_pacman_x -= 1
        elif keys[pygame.K_RIGHT]:
            new_pacman_x += 1

        # Проверка столкновений персонажа с лабиринтом
        if maze[new_pacman_y][new_pacman_x] in [0, 4]:  # Персонаж может двигаться только по 0 или 4
            pacman_x, pacman_y = new_pacman_x, new_pacman_y
            player_moved = True  # Игрок сделал ход

        # Проверка победы
        if maze[pacman_y][pacman_x] == 4:
            print("Вы выиграли!")
            victory = True
            running = False

    elif player_moved:  # Ход монстра
        # Увеличиваем счетчик ходов монстра
        monster_move_counter += 1

        # Монстр делает ход только на каждом втором шаге
        if monster_move_counter % 2 == 0:
            # Движение монстра по волновому алгоритму
            path = find_path(monster_x, monster_y, pacman_x, pacman_y)
            if path:
                next_x, next_y = path[0]

                # Проверка на преграду 2
                if maze[next_y][next_x] == 2:
                    # Увеличиваем счетчик попыток для этой преграды
                    key = (next_x, next_y)
                    if key not in monster_attempts:
                        monster_attempts[key] = 0
                    monster_attempts[key] += 1

                    # Если попыток >= 2, преобразуем преграду 2 в 0
                    if monster_attempts[key] >= 2:
                        maze[next_y][next_x] = 0
                        del monster_attempts[key]

                        # Преобразуем случайную соседнюю ячейку 0 в 2
                        neighbors = [
                            (nx, ny) for nx, ny in [(next_x + dx, next_y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]]
                            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and maze[ny][nx] == 0
                        ]
                        if neighbors:
                            x, y = random.choice(neighbors)
                            maze[y][x] = 2

                elif maze[next_y][next_x] in [0, 1]:
                    monster_x, monster_y = next_x, next_y

        player_moved = False  # Переход хода к игроку

    # Проверка столкновения персонажа и монстра
    if (pacman_x, pacman_y) == (monster_x, monster_y):
        print("Вы проиграли!")
        running = False

    # Отрисовка лабиринта
    draw_maze()

    # Отрисовка персонажа и монстра
    screen.blit(pacman_sprite, (pacman_x * CELL_SIZE, pacman_y * CELL_SIZE))
    screen.blit(monster_sprite, (monster_x * CELL_SIZE, monster_y * CELL_SIZE))

    # Создание частиц при победе
    if victory:
        for _ in range(10):
            particles.append(Particle(pacman_x * CELL_SIZE, pacman_y * CELL_SIZE, BLUE))

    # Обновление и отрисовка частиц
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.size <= 0:
            particles.remove(particle)

    # Обновление экрана
    pygame.display.flip()

    # Ограничение FPS
    clock.tick(10)

# Завершение Pygame
pygame.quit()
sys.exit()