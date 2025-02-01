import pygame
import random
import time

# Inicialización de Pygame
pygame.init()

# Configuración del bucle del juego
running = True

# Dimensiones de la ventana
width, height = 400, 400
square_size = width // 4

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (150, 150, 150)

# Crear la ventana
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Juego de damas 4x4 Julián López")

# Representación del tablero
def reset_board():
    return [
        [0, -1, 0, -1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 0, 1, 0]
    ]

board = reset_board()

# Inicializar la tabla Q
Q = {}
learning_rate = 0.1
discount_factor = 0.9
exploration_rate = 1.0
exploration_decay = 0.99

# Función para dibujar el tablero
def draw_board():
    for row in range(4):
        for col in range(4):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

# Función para dibujar las fichas
def draw_pieces():
    for row in range(4):
        for col in range(4):
            if board[row][col] == 1:
                pygame.draw.circle(screen, BLUE, (col * square_size + square_size // 2, row * square_size + square_size // 2), square_size // 4)
            elif board[row][col] == -1:
                pygame.draw.circle(screen, RED, (col * square_size + square_size // 2, row * square_size + square_size // 2), square_size // 4)

# Función para obtener todos los movimientos posibles
def get_possible_moves(board, player):
    moves = []
    for row in range(4):
        for col in range(4):
            if board[row][col] == player:
                directions = [(-1, 1), (-1, -1), (1, 1), (1, -1)]
                for dr, dc in directions:
                    new_row = row + dr
                    new_col = col + dc
                    if 0 <= new_row < 4 and 0 <= new_col < 4:
                        if board[new_row][new_col] == 0:
                            moves.append((row, col, new_row, new_col))
                        elif board[new_row][new_col] == -player:
                            new_row += dr
                            new_col += dc
                            if 0 <= new_row < 4 and 0 <= new_col < 4 and board[new_row][new_col] == 0:
                                moves.append((row, col, new_row, new_col))
    return moves

# Función para realizar un movimiento
def make_move(board, move):
    start_row, start_col, end_row, end_col = move
    new_board = [row.copy() for row in board]  # Crear una copia del tablero
    new_board[end_row][end_col] = new_board[start_row][start_col]
    new_board[start_row][start_col] = 0

    # Verificar si hay una captura y eliminar la ficha capturada
    if abs(end_row - start_row) == 2:
        capture_row = (start_row + end_row) // 2
        capture_col = (start_col + end_col) // 2
        new_board[capture_row][capture_col] = 0

    return new_board

# Función para verificar si el juego ha terminado
def game_over(board):
    return not any(get_possible_moves(board, player) for player in [1, -1]) or only_one_type_of_piece(board)

# Función para obtener la representación del estado del tablero
def get_state(board):
    return str(board)

# Función para elegir la acción de la IA usando Q-learning
def choose_action(state, possible_moves):
    if random.uniform(0, 1) < exploration_rate:
        return random.choice(possible_moves)  # Exploración
    else:
        # Explotación: elegir la acción con el valor Q más alto
        q_values = [Q.get((state, str(move)), 0) for move in possible_moves]
        max_q = max(q_values)
        best_moves = [move for move, q in zip(possible_moves, q_values) if q == max_q]
        return random.choice(best_moves)

# Función para actualizar la tabla Q
def update_q(state, action, reward, next_state):
    best_next_q = max(Q.get((next_state, str(a)), 0) for a in get_possible_moves(board, -1))
    current_q = Q.get((state, str(action)), 0)
    new_q = current_q + learning_rate * (reward + discount_factor * best_next_q - current_q)
    Q[(state, str(action))] = new_q

# Definir jugador
player = 1  
selected_piece = None

# Función para dibujar el botón de reinicio
def draw_reset_button():
    button_rect = pygame.Rect(10, 10, 120, 50)  # Aumentar el tamaño del botón
    mouse_pos = pygame.mouse.get_pos()

    # Efecto de relieve
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect, border_radius=10)  # Color más oscuro al pasar el mouse
        pygame.draw.rect(screen, WHITE, button_rect.move(2, 2), border_radius=10)  # Sombra
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect, border_radius=10)  # Color normal
        pygame.draw.rect(screen, WHITE, button_rect.move(2, 2), border_radius=10)  # Sombra

    # Dibuja el borde del botón
    pygame.draw.rect(screen, BLACK, button_rect, 2, border_radius=10)

    # Texto
    font = pygame.font.Font(None, 36)  # Aumentar el tamaño de la fuente
    text = font.render("Reiniciar", True, BLACK)  # Color de texto negro
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)  # Centrar el texto en el botón
    return button_rect  # Devolver el rectángulo del botón para la detección de clics

# Función para verificar si solo hay un tipo de ficha en el tablero
def only_one_type_of_piece(board):
    blue_count = sum(row.count(1) for row in board)
    red_count = sum(row.count(-1) for row in board)
    return blue_count == 0 or red_count == 0

# Función para mostrar el mensaje de fin de juego
def draw_game_over_message(winner):
    font = pygame.font.Font(None, 48)
    if winner == 1:
        text = font.render("Ganó el jugador!", True, BLUE)
    elif winner == -1:
        text = font.render("Ganó la IA!", True, RED)
    else:
        text = font.render("Empate!", True, BLACK)

    # Crear un fondo semitransparente
    overlay = pygame.Surface((width, height))  # Crear una superficie del tamaño de la ventana
    overlay.fill((255, 255, 255))  # Color blanco
    overlay.set_alpha(128)  # Establecer la transparencia (0-255, donde 0 es completamente transparente y 255 es completamente opaco)
    screen.blit(overlay, (0, 0))  # Dibujar el fondo semitransparente

    # Dibuja el texto
    text_rect = text.get_rect(center=(width // 2, height // 2))
    screen.blit(text, text_rect)

# Función para calcular la recompensa
def calculate_reward(new_board, player):
    if game_over(new_board):
        return 10 if player == 1 else -10  # Recompensa por ganar
    elif any(row.count(-player) for row in new_board):
        return 1  # Recompensa por capturar una pieza
    return 0  # Sin recompensa

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            col, row = event.pos[0] // square_size, event.pos[1] // square_size
            if event.button == 1:  # Haga clic izquierdo para seleccionar
                if selected_piece is None:
                    if board[row][col] == player:  # Solo permitir seleccionar piezas azules
                        selected_piece = (row, col)
                else:
                    move = (selected_piece[0], selected_piece[1], row, col)
                    if move in get_possible_moves(board, player):
                        # Realizar el movimiento
                        new_board = make_move(board, move)
                        reward = calculate_reward(new_board, player)  # Calcular recompensa
                        state = get_state(board)
                        next_state = get_state(new_board)
                        update_q(state, move, reward, next_state)  # Actualizar la tabla Q
                        board = new_board
                        selected_piece = None
                        if not game_over(board):
                            player = -player
                            possible_moves = get_possible_moves(board, player)
                            if possible_moves:  # Solo si hay movimientos posibles
                                action = choose_action(get_state(board), possible_moves)
                                board = make_move(board, action)
                                player = -player
                                time.sleep(1)  # Esperar 1 segundo para que el jugador vea el movimiento de la IA
            elif event.button == 3:  # Haga clic derecho para deseleccionar
                selected_piece = None
            
            # Verificar si se hizo clic en el botón de reinicio
            button_rect = draw_reset_button()
            if button_rect.collidepoint(event.pos):
                board = reset_board()  # Reiniciar el tablero
                Q.clear()  # Limpiar la tabla Q
                exploration_rate = 1.0  # Reiniciar la tasa de exploración
                player = 1  # Asegurarse de que el jugador sea azul al reiniciar
                selected_piece = None  # Reiniciar la selección de piezas

    # Dibuja el tablero y las piezas
    draw_board()
    draw_pieces()
    
    # Resaltar la pieza seleccionada 
    if selected_piece:
        pygame.draw.circle(screen, GREEN, (selected_piece[1] * square_size + square_size // 2, selected_piece[0] * square_size + square_size // 2), square_size // 3)

    # Dibuja el botón de reinicio solo si hay un solo tipo de ficha
    if only_one_type_of_piece(board):
        draw_reset_button()

    # Mostrar mensaje de fin de juego si corresponde
    if game_over(board):
        winner = 1 if sum(row.count(1) for row in board) > 0 else -1 if sum(row.count(-1) for row in board) > 0 else 0
        draw_game_over_message(winner)

    pygame.display.update()

    # Reducir la tasa de exploración
    exploration_rate *= exploration_decay

pygame.quit()