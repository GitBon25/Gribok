class Button:
    def __init__(self, image, clicked_image, pos, text_input, font, base_color, hovering_color, initial_state=False):
        self.image = image if image is not None else font.render(
            text_input, True, base_color)
        self.clicked_image = clicked_image
        self.x_pos, self.y_pos = pos
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input
        self.text = self.font.render(
            self.text_input, True, self.base_color) if text_input else None
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(
            center=(self.x_pos, self.y_pos)) if self.text else None

        self.is_clicked = initial_state
        self.current_image = self.clicked_image if self.is_clicked else self.image

    def update(self, screen):
        self.current_image = self.clicked_image if self.is_clicked else self.image
        screen.blit(self.current_image, self.rect)
        if self.text:
            screen.blit(self.text, self.text_rect)

    def check_for_input(self, position):
        return self.rect.collidepoint(position)

    def change_color(self, position):
        color = self.hovering_color if self.rect.collidepoint(
            position) else self.base_color
        if self.text:
            self.text = self.font.render(self.text_input, True, color)

    def handle_click(self):
        self.is_clicked = not self.is_clicked
        self.current_image = self.clicked_image if self.is_clicked else self.image
