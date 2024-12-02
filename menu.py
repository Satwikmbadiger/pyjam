import pygame
import sys
from button import Button

pygame.init()

pygame.mixer.init()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")

BG = pygame.image.load('resources\\images\\Background.png')
BG = pygame.transform.scale(BG, (1280, 720))

volume = 0.5

pygame.mixer.music.load('resources\\audio\\bg_music.mp3')
pygame.mixer.music.set_volume(volume)
pygame.mixer.music.play(-1)

def get_font(size):
    return pygame.font.Font('resources\\font\\font.ttf', size)

def play():
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        PLAY_TEXT = get_font(45).render("This is the PLAY screen.", True, "#b68f40")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        PLAY_BACK = Button(image=None, pos=(640, 460), 
                            text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

        pygame.display.update()
    
def options():
    global volume
    slider_x = 400
    slider_width = 480
    slider_height = 20
    handle_width = 20
    bg_slider_height = 40  # Height of the slider background box

    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.blit(BG, (0, 0))

        OPTIONS_TEXT = get_font(100).render("OPTIONS", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_VOLUME = get_font(75).render("VOLUME", True, "Black")
        OPTIONS_RECT = OPTIONS_VOLUME.get_rect(center=(640, 200))
        SCREEN.blit(OPTIONS_VOLUME, OPTIONS_RECT)

        # Draw the volume slider background
        pygame.draw.rect(SCREEN, (100, 100, 100), (slider_x - 10, 350 - 10, slider_width + 20, bg_slider_height), border_radius=5)
        # Draw the volume slider
        pygame.draw.rect(SCREEN, "Black", (slider_x, 350, slider_width, slider_height))
        handle_x = slider_x + int(volume * slider_width)
        pygame.draw.rect(SCREEN, "Green", (handle_x - (handle_width // 2), 350, handle_width, slider_height))

        OPTIONS_BACK = Button(image=None, pos=(640, 600), text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

            if event.type == pygame.MOUSEMOTION:
                if slider_x <= OPTIONS_MOUSE_POS[0] <= slider_x + slider_width and 350 <= OPTIONS_MOUSE_POS[1] <= 350 + slider_height:
                    volume = (OPTIONS_MOUSE_POS[0] - slider_x) / slider_width
                    volume = max(0, min(1, volume))
                    pygame.mixer.music.set_volume(volume)

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("PYGAME", True, "White")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load('resources\\images\\Play Rect.png'), pos=(640, 250), 
                            text_input="PLAY", font=get_font(55), base_color="White", hovering_color="#b68f40")
        OPTIONS_BUTTON = Button(image=pygame.image.load('resources\\images\\Options Rect.png'), pos=(640, 400), 
                            text_input="OPTIONS", font=get_font(55), base_color="White", hovering_color="#b68f40")
        QUIT_BUTTON = Button(image=pygame.image.load('resources\\images\\Quit Rect.png'), pos=(640, 550), 
                            text_input="QUIT", font=get_font(55), base_color="White", hovering_color="#b68f40")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()