import cv2
import mediapipe as mp
import numpy as np
import pygame
from pygame import mixer
import time

# Inicializar pygame para sonidos
pygame.init()
mixer.init()

# Configuración de sonido
try:
    key_sound = mixer.Sound("key_press.wav")
    print("Sonido 'key_press.wav' cargado exitosamente.")
except (pygame.error, FileNotFoundError):
    print("Advertencia: No se encontró 'key_press.wav'. Se usará un sonido sintético.")
    sample_rate = 55000
    duration = 0.05
    frequency = 880
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * t * 2 * np.pi) * 0.3
    tone = np.column_stack((tone, tone))  # Estéreo
    key_sound = pygame.sndarray.make_sound((tone * 32767).astype(np.int16))
    key_sound.set_volume(0.2)

# Configuración de MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8)
mp_drawing = mp.solutions.drawing_utils

# Configuración de cámara
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# --- DISEÑO DEL TECLADO COMPACTO ---
keyboard = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ñ'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '<-'],
    ['MAYUS', 'ESPACIO', 'BORRAR']  # Botón BORRAR más pequeño
]

# Tamaños compactos
key_size = 60
key_margin = 8
keyboard_width = (key_size + key_margin) * 10 - key_margin
keyboard_height = 5 * (key_size + key_margin) - key_margin

# Centrar el teclado
start_x = (1280 - keyboard_width) // 2
start_y = (720 - keyboard_height - 150) // 2  # Dejar espacio para área de texto y botón EXIT

# Variables de estado
selected_key_info = None
typed_text = ""
caps_lock = False
cursor_counter = 0
last_click_time = 0
click_cooldown = 0.5
exit_program = False

# --- FUNCIONES ---
def get_key_from_pos(x, y):
    """Obtiene la tecla en la posición (x, y) del cursor."""
    for i, row in enumerate(keyboard):
        current_x = start_x
        for j, key in enumerate(row):
            if key == 'ESPACIO':
                key_w = key_size * 5 + key_margin * 4
            elif key == 'MAYUS':
                key_w = key_size * 3 + key_margin * 2
            elif key == 'BORRAR':  # Botón BORRAR más pequeño
                key_w = key_size * 2 + key_margin * 1
            else:
                key_w = key_size
            
            key_x = current_x
            key_y = start_y + i * (key_size + key_margin)
            
            if key_x <= x <= key_x + key_w and key_y <= y <= key_y + key_size:
                return (i, j, key, 'keyboard')
            
            current_x += key_w + key_margin
    
    # Verificar si se hizo clic en el botón EXIT
    exit_btn_x = (1280 - key_size * 3) // 2
    exit_btn_y = start_y + keyboard_height + 30
    exit_btn_w = key_size * 3
    exit_btn_h = key_size
    
    if exit_btn_x <= x <= exit_btn_x + exit_btn_w and exit_btn_y <= y <= exit_btn_y + exit_btn_h:
        return (0, 0, 'EXIT', 'exit_button')
    
    return None

def is_click(hand_landmarks):
    """Detecta gesto de clic (pulgar e índice juntos)."""
    thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    distance = ((thumb.x - index.x)**2 + (thumb.y - index.y)**2)**0.5
    return distance < 0.04

def process_key(key_info):
    """Procesa la tecla presionada."""
    global typed_text, caps_lock, exit_program
    if not key_info: return
    
    _, _, key, area = key_info
    
    key_sound.play()
    
    if area == 'exit_button' and key == 'EXIT':
        exit_program = True
        return
    
    if key == '<-':
        typed_text = typed_text[:-1]
    elif key == 'ESPACIO':
        typed_text += ' '
    elif key == 'MAYUS':
        caps_lock = not caps_lock
    elif key == 'BORRAR':
        typed_text = ""
    else:
        typed_text += key.upper() if caps_lock else key.lower()

def draw_keyboard(img):
    """Dibuja el teclado compacto centrado con área de texto."""
    global selected_key_info
    
    # Área de texto (centrada arriba del teclado)
    text_area_height = 100
    text_area_y = start_y - text_area_height - 20
    text_area_x = start_x
    text_area_w = keyboard_width
    
    # Fondo semitransparente para el área de texto
    overlay = img.copy()
    cv2.rectangle(overlay, (text_area_x, text_area_y), 
                 (text_area_x + text_area_w, text_area_y + text_area_height), 
                 (40, 40, 40), -1)
    alpha = 0.7
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    # Borde del área de texto
    cv2.rectangle(img, (text_area_x, text_area_y), 
                 (text_area_x + text_area_w, text_area_y + text_area_height), 
                 (100, 100, 100), 2)
    
    # Texto escrito con soporte para múltiples líneas
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_color = (255, 255, 255)
    
    # Dividir el texto en líneas
    max_width = text_area_w - 30
    lines = []
    current_line = ""
    
    for word in typed_text.split(' '):
        test_line = current_line + word + ' '
        width = cv2.getTextSize(test_line, font, 0.8, 1)[0][0]
        if width < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    
    if current_line:
        lines.append(current_line)
    
    # Mostrar las líneas (últimas 2)
    display_lines = lines[-2:] if len(lines) > 2 else lines
    for i, line in enumerate(display_lines):
        y_pos = text_area_y + 40 + i * 30
        cv2.putText(img, line, (text_area_x + 15, y_pos), font, 0.8, text_color, 1)
    
    # Cursor parpadeante
    if cursor_counter < 20 and lines:
        last_line = lines[-1]
        cursor_x_pos = text_area_x + 15 + cv2.getTextSize(last_line, font, 0.8, 1)[0][0]
        cursor_y_pos = text_area_y + 40 + (len(display_lines)-1)*30
        cv2.line(img, (cursor_x_pos, cursor_y_pos - 20), 
                (cursor_x_pos, cursor_y_pos + 5), 
                text_color, 2)

    # Dibujar teclas (centradas)
    for i, row in enumerate(keyboard):
        current_x = start_x
        for j, key in enumerate(row):
            if key == 'ESPACIO':
                key_w = key_size * 5 + key_margin * 4
            elif key == 'MAYUS':
                key_w = key_size * 3 + key_margin * 2
            elif key == 'BORRAR':  # Botón BORRAR más pequeño
                key_w = key_size * 2 + key_margin * 1
            else:
                key_w = key_size
            
            x = current_x
            y = start_y + i * (key_size + key_margin)

            # Color de la tecla
            color = (60, 60, 60)
            if selected_key_info and selected_key_info[0] == i and selected_key_info[1] == j and selected_key_info[3] == 'keyboard':
                color = (100, 100, 100)
            elif key == 'MAYUS' and caps_lock:
                color = (40, 40, 40)
            elif key == 'BORRAR':
                color = (80, 40, 40)

            # Dibujar tecla
            cv2.rectangle(img, (x, y), (x + key_w, y + key_size), color, -1)
            cv2.rectangle(img, (x, y), (x + key_w, y + key_size), (100, 100, 100), 1)
            
            # Texto de la tecla
            display_text = key.upper() if caps_lock and len(key) == 1 else key
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(display_text, font, 0.6, 1)[0]
            text_x = x + (key_w - text_size[0]) // 2
            text_y = y + (key_size + text_size[1]) // 2
            cv2.putText(img, display_text, (text_x, text_y), font, 0.6, (255, 255, 255), 1)

            current_x += key_w + key_margin
    
    # Dibujar botón EXIT centrado en la parte inferior
    exit_btn_x = (1280 - key_size * 3) // 2
    exit_btn_y = start_y + keyboard_height + 30
    exit_btn_w = key_size * 3
    exit_btn_h = key_size
    
    exit_color = (40, 40, 80)
    if selected_key_info and selected_key_info[2] == 'EXIT' and selected_key_info[3] == 'exit_button':
        exit_color = (60, 60, 120)
    
    cv2.rectangle(img, (exit_btn_x, exit_btn_y), 
                 (exit_btn_x + exit_btn_w, exit_btn_y + exit_btn_h), 
                 exit_color, -1)
    cv2.rectangle(img, (exit_btn_x, exit_btn_y), 
                 (exit_btn_x + exit_btn_w, exit_btn_y + exit_btn_h), 
                 (100, 100, 150), 2)
    
    exit_text_size = cv2.getTextSize("EXIT", cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    exit_text_x = exit_btn_x + (exit_btn_w - exit_text_size[0]) // 2
    exit_text_y = exit_btn_y + (exit_btn_h + exit_text_size[1]) // 2
    cv2.putText(img, "EXIT", (exit_text_x, exit_text_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# --- BUCLE PRINCIPAL ---
while cap.isOpened() and not exit_program:
    success, frame = cap.read()
    if not success:
        print("Ignorando fotograma vacío de la cámara.")
        continue
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    
    selected_key_info = None
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            cursor_x, cursor_y = int(index_tip.x * w), int(index_tip.y * h)
            
            # Cursor
            cv2.circle(frame, (cursor_x, cursor_y), 10, (0, 255, 255), -1)
            cv2.circle(frame, (cursor_x, cursor_y), 12, (255, 255, 255), 2)
            
            key_info = get_key_from_pos(cursor_x, cursor_y)
            if key_info:
                selected_key_info = key_info
                
                if is_click(hand_landmarks):
                    current_time = time.time()
                    if current_time - last_click_time > click_cooldown:
                        process_key(key_info)
                        last_click_time = current_time
                        cv2.circle(frame, (cursor_x, cursor_y), 15, (0, 0, 255), 2)

    draw_keyboard(frame)
    cursor_counter = (cursor_counter + 1) % 40
    
    cv2.imshow('Teclado Virtual Centrado', frame)
    
    if cv2.waitKey(5) & 0xFF == 27 or exit_program:
        break

# Liberar recursos
hands.close()
cap.release()
cv2.destroyAllWindows()
mixer.quit()
pygame.quit()
