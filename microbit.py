from microbit import *
from random import randint as rand
import music


# Fonction pour générer un mur avec un seul trou
def generate_layer() -> list[int]:
    clear: int = rand(0, 4)
    return [1]*clear + [0] + [1]*(5-clear-1)


# Fonction pour afficher une grille sur les leds de la carte microbit
def draw_grid(grid: list[list[int]], brightness: int = 9) -> None:
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            display.set_pixel(y, x, grid[x][y]*brightness)


def draw(drawing: str, brightness: int = 9) -> None:
    draws: dict = {
        'play': [[0, 1, 0, 0, 0], [0, 1, 1, 0, 0], [0, 1, 1, 1, 0], [0, 1, 1, 0, 0], [0, 1, 0, 0, 0]],
        'pause': [
            [0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0]
        ],
        'x': [[1, 0, 0, 0, 1], [0, 1, 0, 1, 0], [0, 0, 1, 0, 0], [0, 1, 0, 1, 0], [1, 0, 0, 0, 1]]
    }


    draw_grid(draws[drawing])


# Fonction pour afficher la grille et le joueur sur les leds de la carte microbit
def display_grid(grid: list[list[int]], player: int) -> None:
    draw_grid(grid)
    display.set_pixel(player, 4, 5)


# Fonction pour mettre à jour la grille : descendre les murs
def update_grid(grid: list[list[int]]) -> list[list[int]]:
    for i in range(len(grid)-1, 0, -1):
        grid[i] = grid[i-1]

    if 1 in grid[0]:
        grid[0] = [0]*5
    else:
        grid[0] = generate_layer()

    return grid


# Fonction pour gérer l'appuis des touche de l'utilisateur et bouger en conséquence
def handle_movement(player: int) -> int:
    a_pressed: bool = button_a.was_pressed()
    b_pressed: bool = button_b.was_pressed()

    if a_pressed and b_pressed:
        return -1

    if a_pressed:
        player -= 1
    elif b_pressed:
        player += 1

    while player > 4:
        player -= 5
    while player < 0:
        player += 5

    return player


# Fonction pour vérifier que le joueur touche un mur et meurt ou non
def check_death(grid: list[list[int]], player: int) -> int:
    if grid[4][player] == 1:
        return -1
    elif 1 in grid[4]:
        return 1
    else:
        return 0


# Lancer le jeu
def main() -> None:
    # grille par défaut
    grid: list[list[int]] = [
        [0, 0, 0, 0, 0],
        generate_layer(),
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]

    player: int = 2 # position du joueur
    time_counter: int = 0 # compteur pour faire descendre les murs au bout de plusieurs itérations
    sleep_time: int = 120 # temps d'attente entre deux exécutions de la boucle principale
    pause_time: int = sleep_time*10 # temps d'attente avant que les murs ne décendent
    score: int = 0 # score du joueur (nombre de murs passés)
    playing: bool = True

    # boucle principale
    while True:
        # gérer contrôles
        old_player: int = player
        player = handle_movement(player)

        if player == -1:
            player = old_player

            if playing:
                song: list[str] = ['A4:1', 'F3']
                music.play(song)
                playing = False
            else:
                song: list[str] = ['F3:1', 'A4']
                music.play(song)
                playing = True

        # gestion du temps
        if playing:
            # gestion temps
            time_counter += sleep_time

            # affichage
            display_grid(grid, player)
        else:
            draw('pause')

        score_update: int = check_death(grid, player)

        # gestion de la mort
        if score_update == -1:
            break

        # attente
        sleep(sleep_time)

        # faire descendre les murs au bout d'un certain nombre d'itérations
        if time_counter >= pause_time:
            grid = update_grid(grid)
            time_counter = 0
            pause_time = max(sleep_time*3, pause_time - 10)

            # incrémenter le score
            if score_update > 0:
                score += 1

    draw('x')

    # jouer le son de défaite
    lose_sound: list[str] = ['B4:2', 'B4', 'A4', 'F3:4']
    music.play(lose_sound)

    sleep(1000)

    display.clear()
    display.scroll(str(score))

    button_a.was_pressed()
    button_b.was_pressed()


draw('play')

while True:
    sleep(100)

    if button_a.was_pressed() or button_b.was_pressed():
        main()
        draw('play')
