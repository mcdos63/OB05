import pygame
import sys
from collections import deque
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
CELL_SIZE = 40  # Размер ячейки
MAZE_WIDTH, MAZE_HEIGHT = 30, 20  # Размеры матрицы
WIDTH, HEIGHT = MAZE_WIDTH * CELL_SIZE, MAZE_HEIGHT * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Evolution")

# Цвета
color0 = pygame.Color(100, 100, 100, 0)  # Прозрачный цвет (альфа = 0)
color1 = (10, 50, 50)
color2 = (10, 70, 70)
color3 = (10, 90, 90)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (200, 200, 0)
ORANGE = (255, 165, 0)

# Загрузка спрайтов
pacman_sprite = pygame.image.load("pacman1.png")  # Спрайт персонажа
monster_sprite = pygame.image.load("monster1.png")  # Спрайт монстра
pacman_sprite = pygame.transform.scale(pacman_sprite, (CELL_SIZE, CELL_SIZE))
monster_sprite = pygame.transform.scale(monster_sprite, (CELL_SIZE, CELL_SIZE))

# Загрузка изображения фона
background_image = pygame.image.load("background.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Масштабируем под размер экрана

# Матрица игрового поля в виде строки
maze_string = (
    "333333333333333333333333333333"
    "300000000000000300000030000003"
    "302221020002000300300030000003"
    "300021000001000300200000320003"
    "320233300001000000200000300003"
    "300000003333333333322332330003"
    "300321000000000000000000000003"
    "300200000033333333333333333333"
    "302222100030000000000000000003"
    "300000000030000300000000000003"
    "303301220000022300000000333333"
    "300021000000000300000000000003"
    "320001000000000300000000000003"
    "300001222233330333333333000003"
    "322100330000000030000000000333"
    "300003000000200300033333330333"
    "322000002000200002200030000003"
    "300030322323333303300030022333"
    "300000000000000000003000000043"
    "333333333333333333333333333333"
)

# Преобразование строки в матрицу
maze = [list(map(int, maze_string[i:i + MAZE_WIDTH])) for i in range(0, len(maze_string), MAZE_WIDTH)]

# Количество зерен
KS = 100
# Радиус зерен
SEED_RADIUS = 8

# Функция для размещения зерен на поле
def place_seeds(maze, ks):
    empty_cells = [(x, y) for y, row in enumerate(maze) for x, cell in enumerate(row) if cell == 0]
    random.shuffle(empty_cells)  # Перемешиваем пустые клетки
    for i in range(min(ks, len(empty_cells))):
        x, y = empty_cells[i]
        maze[y][x] = 5  # Размещаем зерно

# Размещение зерен
place_seeds(maze, KS)

# Счетчик собранных зерен
collected_seeds = 0

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
                not visited[ny][nx] and maze[ny][nx] in [0, 1, 5]  # Учитываем зерна как проходимые
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
                color = color0  # Прозрачный цвет
            elif cell == 1:
                color = color1
            elif cell == 2:
                color = color2
            elif cell == 3:
                color = color3
            elif cell == 4:
                color = (monster_move_counter % 2*255,monster_move_counter % 2*255, 255)
            elif cell == 5:  # Зерна
                color = YELLOW

            if color and cell != 5:  # Отдельно обрабатываем зерна
                rect = pygame.Surface((CELL_SIZE - 1, CELL_SIZE - 1),
                                      pygame.SRCALPHA)  # Создаем поверхность с альфа-каналом
                rect.fill(color)  # Заполняем поверхность цветом
                screen.blit(rect, (col_index * CELL_SIZE + 1, row_index * CELL_SIZE + 1))

                # Отрисовка зерен
            if cell == 5:
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (
                        col_index * CELL_SIZE + CELL_SIZE // 2,  # Центр по X
                        row_index * CELL_SIZE + CELL_SIZE // 2  # Центр по Y
                    ),
                    SEED_RADIUS
                )


# Отрисовка счетчика зерен
def draw_seed_counter(screen, collected_seeds, total_seeds):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"SEEDS: {collected_seeds:03}/{total_seeds}", True, WHITE)
    screen.blit(text, (WIDTH - text.get_width() - 10, HEIGHT - text.get_height() - 10))

# Основной игровой цикл
clock = pygame.time.Clock()
running = True
player_moved = False  # Флаг, указывающий, что игрок сделал ход
victory = False  # Флаг, указывающий, что игрок выиграл

while running:
    # Отрисовка фона
    screen.blit(background_image, (0, 0))

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
        if maze[new_pacman_y][new_pacman_x] in [0, 4, 5]:  # Персонаж может двигаться по 0, 4 или 5
            pacman_x, pacman_y = new_pacman_x, new_pacman_y
            player_moved = True  # Игрок сделал ход

            # Проверка на сбор зерна
            if maze[pacman_y][pacman_x] == 5:
                collected_seeds += 1  # Увеличиваем счетчик зерен
                maze[pacman_y][pacman_x] = 0  # Убираем зерно

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

                elif maze[next_y][next_x] in [0, 1, 5]:  # Монстр может проходить через зерна
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

    # Отрисовка счетчика зерен
    draw_seed_counter(screen, collected_seeds, KS)

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
    clock.tick(15)

# Завершение Pygame
pygame.quit()
input("Press Enter to continue...")
sys.exit()