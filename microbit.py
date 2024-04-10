from microbit import *
from random import randint as rand
import music


def melody(notes, wait=False):
    base = ['D4', '']
    aigu = ['A', '', 'D', '', 'B', '']
    grave = ['A', '', 'D', '', 'G', '']
    descente = ['C5', '', 'A4', '', 'F', '']

    pause = [''] * 4

    musics: dict = {
        'pause_on': [''] * 1 + ['A4:1', 'F3'],
        'pause_off': ['F3:1', 'A4'] + pause,
        'lose': pause + ['B4:2', 'B4', 'A4', 'F3:4'],
        'play': ['D4:2', 'D', 'F', 'A5:1', 'G5:2'] + pause,
        'background': (base*3 + aigu + base*2 + grave)*2 + base*2 + descente
    }

    cycle = False

    if notes == 'background':
        cycle = True

    music.set_tempo(bpm=240)
    music.play(musics[notes], wait=wait, loop=cycle)



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
        'pause': [[0, 0, 0, 0, 0], [0, 1, 0, 1, 0], [0, 1, 0, 1, 0], [0, 1, 0, 1, 0], [0, 0, 0, 0, 0]],
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

    if player == 5:
        player = 0
    elif player == -1:
        player = 4

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
def main_runner() -> None:
    melody('play', wait=True)
    melody('background')
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
        movement = handle_movement(player)

        if movement == -1:
            if playing:
                melody('pause_on')
                playing = False
            else:
                melody('pause_off', wait=True)
                melody('background')
                playing = True
        elif playing:
            player = movement

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
    melody('lose')

    sleep(1000)

    display.clear()
    if score < 10:
        display.show(str(score))
        sleep(1000)
    else:
        display.scroll(str(score))

    button_a.was_pressed()
    button_b.was_pressed()


def main(game: int) -> None:
    if game == 0:
        main_runner()


draw('play')
game = 0

while True:
    sleep(100)

    a_pressed: bool = button_a.was_pressed()
    b_pressed: bool = button_b.was_pressed()

    if a_pressed and b_pressed:
        main(game)
        draw('play')

    if a_pressed and not b_pressed:
        game -= 1
    elif b_pressed and not a_pressed:
        game += 1
