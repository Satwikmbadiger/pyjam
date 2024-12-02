import pygame

class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color, padding=2):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        self.padding = padding
        
        # Set the size of the button dynamically based on the text size and padding
        text_width, text_height = self.text.get_size()
        button_width = text_width + 10 * self.padding
        button_height = text_height + 10 * self.padding

        if self.image is not None:
            # Resize the image dynamically to fit the button size (maintains aspect ratio)
            self.image = pygame.transform.scale(self.image, (button_width, button_height))
            self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        else:
            # Create a rectangle for the button based on the text and padding
            self.rect = pygame.Rect(self.x_pos - button_width // 2, self.y_pos - button_height // 2, button_width, button_height)

        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            # Display the image as the button background
            screen.blit(self.image, self.rect)
        # Display the text on top of the image or background
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)