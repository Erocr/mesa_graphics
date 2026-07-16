from mesa import Model
from mesa.visualization import SpaceRenderer

from .Component import Component
from .UIElement import *
from .components import create_space_component
import mesa.visualization.user_param as mesa_user_param
from .Model import RESET_MODEL, NOT_RESETTING

"""
This file contains the logic for drawing.
It is divided in three classes: 
View is the front class, and it is the one that handles all through the other classes.
UserParamView handles only the left column bar, and what is inside. 
ComponentsView handles the page system, and the components.



The important functions:
- View._create_ui  (called in View.__init__, describes where are placed each UIElement)
- ComponentsView.create_ui
- UserParamView.create_ui
- View.add_UIElement
- View.draw  (called once per frame)
- ComponentsView.draw  (called by View.draw)
"""


class View:
    SCROLL_SENSIBILITY = 30

    def __init__(self, model, renderer=None, components=None, play_interval=100, render_interval=1, model_params=None,
                 custom_method_call=None, name=None):
        """ View class.
        /!\\ The user must not use this class, use MesaGraphics instead /!\\

        This class provides all the logic for the graphics. It handles the screen and draws on it.
        The class is divided in two other classes, for a better subdivision. The UserParamView class handles the logic
        for drawing the control bar. The ComponentsView handles the drawing of components.

        :param model: A Model instance that will be visualized. It is the MesaGraphic's Model, and not
        the user's on
        :param renderer: (SpaceRenderer) A SpaceRenderer instance to render the model's space.
        :param components: List of tuples (component, page).
        Component is a function that takes a model instance and returns a pygame Surface representing it.
        You can create them with the matplotlib_components's utility functions, or you can create custom ones.
        The page is an integer describing in which page it must be drawn.
        :param model_params: Parameters for re-instantiating a model.
        Can include user-adjustable parameters and fixed parameters. Defaults to None.
        :param name: Name of the visualization. Defaults to the model's class name.
        """
        self.fonts = {}
        self.init_fonts()
        self.min_window_size = pg.Vector2(500, 300)
        self.screen_size = pg.Vector2(1280, 740)
        self.screen = pg.display.set_mode(self.screen_size, pg.RESIZABLE)
        self.model = model
        self.renderer = renderer
        self.componentsView = ComponentsView(self, components, renderer)
        self.userParamView = UserParamView(self)
        self.ratio = pg.Vector2(1, 1)

        self.ui_elements = []  # List of UI
        self.buttons = {}  # Provide fast and easy access to buttons
        self.ui_completely_focused = None  # UI element completely focused, the other are not interactive while one is
        # completely focused
        # Only the user parameter sliders, and the scrolling slider can be completely focused.
        self.ui_with_secondary_draw = []  # The UI elements that have things to draw after each UI element
        self.reset_start_step_buttons = []
        self.up_bar = None

        if name is None:
            name = type(self.model).__name__
        self._create_ui(name, model_params, custom_method_call, play_interval, render_interval)

    def render(self):
        """
        Renders all the component images according to the model state. It stores the images in the components
        themselves. Note that these operations are really heavy.
        """
        if self.model.reset == RESET_MODEL:
            if self.renderer is not None:
                self.renderer = self.copy_renderer(self.renderer, self.model.mesa_model)
                self.componentsView.modify_renderer(self.renderer)
        self.model.reset = NOT_RESETTING
        self.componentsView.render()

    def draw(self):
        """
        Main function. It is called once per frame by MesaGraphics, in the main thread.
        It refreshes the screen and draws all onto it.
        """
        self.screen.fill(WHITE)
        self.componentsView.draw()  # Draw the components

        # Draw the visible UI Elements
        for ui in self.ui_elements:
            if ui.visible:
                ui.draw(self.screen)

        # Apply the secondary draw of the ui that wants to.
        # Some UI elements need to draw specific things after all the other UI elements if they are focused.
        for ui_elem in self.ui_with_secondary_draw:
            ui_elem.secondary_draw(self.screen)

        # Draw the debug message (if debug is enabled)
        if self.model.debug: self.draw_debug()

        pg.display.flip()  # Refresh the screen with the modifications

    def add_UIElement(self, typ: type, *args, **kwargs):
        """ This function instantiates a new UIElement.

        :param typ: The type of the object we want to create.
        :param args: The parameters to pass in the class that we want to instantiate.
        :param kwargs: The parameters to pass in the class that we want to instantiate.
        :return: The object instantiated

        For example, if you want to instantiate a Button, call add_UIElement(Button, ...).
        """
        to_add = typ(*args, **kwargs)
        self.ui_elements.append(to_add)
        if isinstance(to_add, Button):
            self.buttons[to_add.name] = to_add
        if isinstance(to_add, UserParam):
            if to_add.model_param:
                self.userParamView.userTweakableModelParams[to_add.name] = to_add
            else:
                self.userParamView.userTweakableEntries[to_add.name] = to_add
        return to_add

    def init_fonts(self):
        """
        Called in the __init__ of View.
        It initializes the pygame.font module, and creates some fonts
        """
        default_path = pg.font.get_default_font()
        self.fonts["basic15"] = pg.font.Font(default_path, 15)
        self.fonts["basic20"] = pg.font.Font(default_path, 20)

    def quit(self):
        """ End the visualization """
        pg.quit()

    def resize(self, new_size: pg.Vector2):
        """ Called every time the user changes the window size. """

        # If the new screen size is too small, we modify it to be larger
        new_size_clamped = pg.Vector2(
            max(new_size.x, self.min_window_size.x),
            max(new_size.y, self.min_window_size.y))
        if new_size_clamped.x != new_size.x or new_size_clamped.y != new_size.y:
            self.screen = pg.display.set_mode(new_size_clamped, pg.RESIZABLE)
        new_size = new_size_clamped

        ratio = pg.Vector2(new_size.x / self.screen_size.x,
                           new_size.y / self.screen_size.y)  # ratio is the relative ratio
        self.ratio = mul(ratio, self.ratio)  # self.ratio is the global ratio
        self.screen_size = new_size

        self.componentsView.resize()
        self.update_reset_start_step_buttons()
        self.userParamView.resize()

        self.up_bar.size.x = new_size.x

    def _create_ui(self, name: str, model_params, custom_method_call, play_interval: int, render_interval: int) -> None:
        """
        Instantiates the UI.
        This function creates all the UIElements. This function describes where each element is placed.
        Moreover, the order of creation describes which element is above. The drawer draws them in the order of creation.
        So the last UIElement is the one above the others, and the first one is the one beyond the others.
        """
        self.userParamView.create_ui(model_params, custom_method_call, play_interval, render_interval)
        self._create_up_bar(name)
        self.componentsView.create_ui()

    def _create_up_bar(self, name: str) -> None:
        """ Creates the blue bar on top of the screen, and write the name into it. """
        self.up_bar = self.add_UIElement(Rectangle, pg.Vector2(0, 0), pg.Vector2(1280, 37), color=BLUE)
        text = self.add_UIElement(Text, pg.Vector2(0, 0), name, self.fonts["basic15"], color=WHITE)
        text.set_pos(pg.Vector2(40, 20 - text.image.get_height() / 2))  # noqa
        self._create_remove_controls_button()
        self._create_reset_start_step_buttons()

    def _create_remove_controls_button(self) -> None:
        """ Creates the button that toggles or un-toggles the control bar. """

        def custom_draw(button, screen):
            """ The drawing function that will call the button, instead of the default one. """
            # Background
            bg_color = LIGHT2_BLUE if button.hover else BLUE
            pg.draw.rect(screen, bg_color, pg.Rect(button.pos, button.size), border_radius=10)

            # The screen with a column symbol
            offset = pg.Vector2(5, 5)
            pg.draw.rect(screen, WHITE, pg.Rect(button.pos + offset, button.size - 2 * offset),
                         border_radius=5, width=3)
            pg.draw.line(screen, WHITE, button.pos + offset + pg.Vector2(8, 0),
                         button.pos + offset + pg.Vector2(8, button.size.y - 2 * offset.y - 3), width=3)

        button = self.add_UIElement(Button, pos=pg.Vector2(0, 0), text="",
                                    font=self.fonts["basic15"], name="remove control bar",
                                    custom_draw=custom_draw)

        # Set manually the size of the button
        button.size = pg.Vector2(33, 33)
        button.set_pos(pg.Vector2(2, 2))

    def _create_reset_start_step_buttons(self):
        """ Creates the three buttons in the up bar : RESET, START/STOP and STEP """
        x = 1280 - 190
        texts = ("RESET", "START", "STEP")
        names = ("RESET", "START/STOP", "STEP")

        def custom_draw(b, screen):
            """ The drawing function used to draw the buttons, instead of the default one """

            # Manually sets the size of the button. We set it at each frame because we sometime modify it in another
            # function
            b.size = pg.Vector2(60, 31)

            # Background
            bg_color = LIGHT1_BLUE if b.hover else BLUE
            pg.draw.rect(screen, bg_color, pg.Rect(b.pos, b.size), border_radius=5)

            # Text
            b.text.pos = b.pos + b.size / 2 - pg.Vector2(*b.text.image.get_size()) / 2
            b.text.draw(screen)

        for i in range(3):
            button = self.add_UIElement(Button, pg.Vector2(x, 3), texts[i], self.fonts["basic15"], name=names[i],
                                        custom_draw=custom_draw, font_color=(255, 255, 255))
            self.reset_start_step_buttons.append(button)
            x += 65

    def update_reset_start_step_buttons(self):
        """ Update the position of the RESET/START/STEP buttons according to the size of the screen """
        x = self.screen_size.x - 190
        for button in self.reset_start_step_buttons:
            button.set_pos(pg.Vector2(x, button.pos.y))
            x += 65

    def copy_renderer(self, renderer: SpaceRenderer, model: Model):
        """
        Create a new renderer instance with the same configuration as the original.
        I copy-pasted the function from mesa.
        """
        new_renderer = type(renderer)(model=model, backend=renderer.backend)

        attributes_to_copy = [
            "agent_portrayal",
            "propertylayer_portrayal",
            "space_kwargs",
            "agent_kwargs",
            "space_mesh",
            "agent_mesh",
            "propertylayer_mesh",
            "post_process_func",
        ]

        for attr in attributes_to_copy:
            if getattr(renderer, attr, None) is not None:
                value_to_copy = getattr(renderer, attr)
                setattr(new_renderer, attr, value_to_copy)

        return new_renderer

    def draw_debug(self):
        """
        This function draws debug information to help the programmer, or maybe the user.
        This function is called only if you enter the debug mode by pressing "d".
        """

        # Compute the texts to draw
        texts = []
        for info in self.model.debug_infos:
            texts.append(info + ": " + str(self.model.debug_infos[info]))

        # Render and draw the texts
        y = 0
        for text in texts:
            image = self.fonts["basic15"].render(text, False, (255, 255, 255), (0, 0, 0, 125))
            self.screen.blit(image, pg.Vector2(0, y))
            y += image.get_height()

    def switch_page(self, new_page: int):
        """
        Switch to another page and update page-selection buttons.

        Resets the page scrolling position.
        """
        self.componentsView.switch_page(new_page)

    def scroll_page(self, amount: pg.Vector2):
        """
        Scroll through the components if there are to many components.
        :param amount: How much the user is scrolling.
        """
        self.componentsView.scroll(amount)


class ComponentsView:
    def __init__(self, view: View, components, renderer=None):
        """
        This class handles the components view. It handles the rendering of components and the pages.
        :param view: The View class is useful because only the View class can create new UI elements.
        :param components: The components sent by the user. They are tuples (component, page), or only the component.
        A component is a function that takes the model and returns a pygame.Surface.
        :param renderer: The renderer is optional. It is a SpaceRenderer from mesa.visualization.
        """
        self.view = view
        self.page = 0  # Showed page
        self.min_page = self.max_page = 0  # The minimal page and maximal page existing
        self.components = {0: []}
        if components is not None:
            self._store_components(components)
        if renderer is not None:
            self.components[0].insert(0, Component(self.view.model, create_space_component(renderer)))
        self.switch_page_buttons = []  # Provide fast and easy access to buttons for switching pages
        self.full_switch_page_button_width = 0  # The width of a switch page button, when it has the full name
        self.buttons_full = True  # If the switch page buttons have the full name

        self.scrollingSliderY: ScrollingSlider = None  # noqa
        self.max_page_scrolling_y = self.page_scrolling_y = 0

        self.scrollingSliderX: ScrollingSlider = None  # noqa
        self.max_page_scrolling_x = self.page_scrolling_x = 0

    def modify_renderer(self, renderer):
        """ Change the current space renderer with a new one. """
        self.components[0][0] = Component(self.view.model, create_space_component(renderer))

    def create_ui(self) -> None:
        """ Initialize the UI elements """

        # Scrolling sliders. They are always created. If the screen contains all the elements, the scrollingSliders are
        # not visible
        self.scrollingSliderY = self.view.add_UIElement(ScrollingSlider, pg.Vector2(1270, 37), True, 740 - 37,
                                                        self.max_page_scrolling_y)
        self.scrollingSliderX = self.view.add_UIElement(ScrollingSlider, pg.Vector2(300, 730), False, 1280 - 300,
                                                        self.max_page_scrolling_x)

        self.create_switch_page_buttons()

    def draw(self):
        """
        This function draws all the components in the current page.
        """
        y = (37 - self.page_scrolling_y * self.view.ratio.y)
        gap_y = 10  # The gap between the components
        next_y = y - gap_y

        # default_x is the x coordinate at the left, right after the userParam bar
        default_x = 300 if self.view.userParamView.show_control_bar else 0
        default_x -= self.page_scrolling_x * self.view.ratio.x
        x = default_x

        max_x = default_x  # used to know the width of the component area

        # draws the components
        for component in self.components[self.page]:
            image = component.image
            if image is None:
                continue
            size = image.get_size()

            # If it goes off the page, it is drawn under the previous one
            if size[0] + x > self.view.screen_size.x:
                y = next_y + gap_y
                next_y = y
                x = default_x

            # Compute the new max_x
            if size[0] + x > max_x:
                max_x = size[0] + x

            # Draw
            self.view.screen.blit(image, (x, y))

            # Compute positions for the next loop
            next_y = max(next_y, y + size[1])
            x += size[0] + 10

        next_y -= gap_y  # Remove the final gap

        # Modify the scrolling parameters
        #
        # next_y = initial_y + size_of_components
        #        = 37 - self.page_scrolling_y * self.view.ratio.y + size_of_components
        # So,
        # max_page_scrolling_y = next_y - self.view.screen_size.y + 27*self.view.ratio.y + self.page_scrolling_y * self.view.ratio.y
        #     = -self.screen_size.y + 37 + self.page_scrolling_y * self.view.ratio.y - self.page_scrolling_y * self.view.ratio.y + size_of_components
        #     = (-self.screen_size.y + 37) + 27*self.view.ratio.y + size_of_components
        # (-self.screen_size.y + 37) is the size of the screen without the up bar
        # 27 * self.view.ratio.y is an empirical value, found after some tests
        max_page_scrolling_y = next_y - self.view.screen_size.y + 27*self.view.ratio.y + self.page_scrolling_y * self.view.ratio.y
        self.max_page_scrolling_y = max(max_page_scrolling_y, 0)
        self.scrollingSliderY.update_max_scrolling(self.max_page_scrolling_y / self.view.ratio.y)

        # Same idea for the X axis
        # max_x = default_x + components_width - self.page_scrolling_x * self.view.ratio.x
        # (self.view.screen_size.x - 10 - default_x) is the width of the component part (-10 to remove the Y slider scroller)
        # So,
        # max_x - self.view.screen_size.x + 10 + self.page_scrolling_x * self.view.ratio.x
        # = -self.view.screen_size.x + 10 + default_x + components_width - self.page_scrolling_x * self.view.ratio.x + self.page_scrolling_x * self.view.ratio.x
        # = -component_part_width + components_width
        max_page_scrolling_x = max_x - self.view.screen_size.x + 10 + self.page_scrolling_x * self.view.ratio.x
        self.max_page_scrolling_x = max(max_page_scrolling_x, 0)
        self.scrollingSliderX.update_max_scrolling(self.max_page_scrolling_x / self.view.ratio.x)

        # Clamp the scrolling values with the new max found.
        self._page_scroll_clamp()

    def resize(self):
        """ Called every time the window is resized. It updates the elements according to the new_size. """
        # Change the switch page buttons so that they are centered
        self.update_switch_buttons()

        # Change the position and the size of the sliders
        self.scrollingSliderY.pos = pg.Vector2(self.view.screen_size.x - 10, 37)
        self.scrollingSliderY.resize(self.view.screen_size.y - 37)
        default_x = 300 if self.view.userParamView.show_control_bar else 0
        self.scrollingSliderX.pos = pg.Vector2(default_x, self.view.screen_size.y - 10)
        self.scrollingSliderX.resize(self.view.screen_size.x - default_x - 10 - 3)

    def toggle_untoggle_control_bar(self, toggled):
        """
        If the control bar is toggled, this function un-toggles.
        Else, this function toggles it.
        The control bar is the column on the left part of the screen with the user parameters
        """
        default_x = 300 if toggled else 0
        self.scrollingSliderX.pos = pg.Vector2(default_x, self.view.screen_size.y - 10)
        self.scrollingSliderX.resize(self.view.screen_size.x - default_x)

    def _store_components(self, components: list[tuple[Callable, int] | Callable]):
        """
        Store the components in a more suitable way, so it will be easier to access.
        It associates to each page the list of components that are in this page.

        :param components: A list of components.
        Each component can be a tuple (component, page), or only a component.

        For each element of components. If it is only a component, it will be by default placed at page 0.
        Moreover, if not all the pages are used, it will create empty pages automatically. For example, if you have
        page 0 and 3 used, it will create automatically pages 1 and 2 blank.
        """
        for comp_page in components:
            if isinstance(comp_page, tuple):
                comp, page = comp_page
            else:
                comp, page = comp_page, 0
            if page not in self.components:
                self.components[page] = []
            self.components[page].append(Component(self.view.model, comp))
        self._fill_missing_pages()

    def _fill_missing_pages(self):
        """
        Create as many blank pages as needed.
        If the user puts something in the 0-th page and the second page, this function creates a blank
        page for page 1.
        """
        # Find the minimum page, and the maximum page set by the user
        self.min_page = 0  # 0 is the default page, it exists necessary
        self.max_page = 0
        for page in self.components:
            if page < self.min_page: self.min_page = page
            if page > self.max_page: self.max_page = page

        # Add the pages from min_page to max_page
        for i in range(self.min_page + 1, self.max_page):
            if i not in self.components:
                self.components[i] = []

    def create_switch_page_buttons(self) -> None:
        """
        This function creates the buttons on top of the screen, which allows changing the page.
        They are aligned. If there are too many pages, they will be smaller.
        """

        def custom_page_draw(button, screen):
            """ The function that draws the switch page buttons. It is called instead of the default one. """
            if button.locked:
                # The square, the up-left and up-right corners are rounded
                pg.draw.rect(screen, WHITE, pg.Rect(button.pos, button.size),
                             border_top_left_radius=10, border_top_right_radius=10)

                # Two white quarters of circle at the bottom of the button
                # Start by drawing little white rectangles
                pg.draw.rect(screen, WHITE, pg.Rect(button.pos + pg.Vector2(-10, button.size.y - 10),
                                                    pg.Vector2(10, 10)))
                pg.draw.rect(screen, WHITE,
                             pg.Rect(button.pos + pg.Vector2(button.size.x, button.size.y - 10), pg.Vector2(10, 10)))
                # Then remove a quarter of circle from the rectangles
                pg.draw.circle(screen, BLUE, button.pos + pg.Vector2(-10, button.size.y - 10), 10,
                               draw_bottom_right=True)
                pg.draw.circle(screen, BLUE,
                               button.pos + pg.Vector2(button.size.x + 10, button.size.y - 10), 10,
                               draw_bottom_left=True)
            elif button.hover:
                # The light background with rounded edges when the mouse is on the button
                pg.draw.rect(screen, LIGHT2_BLUE,
                             pg.Rect(button.pos + pg.Vector2(5, 5),
                                     button.size - pg.Vector2(10, 12)),
                             border_radius=10)

            button.text.draw(screen)

        # Chose a minimum size for the window, so that each button can be visible, without stretching the buttons too
        # much
        self.view.min_window_size.x = min(1280, 500 + (self.max_page - self.min_page + 1) * 30)

        # Instantiate the buttons
        for i in range(self.min_page, self.max_page + 1):
            self.switch_page_buttons.append(
                self.view.add_UIElement(Button, pg.Vector2(0, 0), f"PAGE {i}", self.view.fonts["basic15"],
                                        custom_draw=custom_page_draw, font_color=WHITE))
        # Store the switch page button width without stretching
        self.full_switch_page_button_width = self.switch_page_buttons[0].size.x

        # Set the position of the buttons and set the first button locked
        self.update_switch_buttons()
        self.switch_page(self.page)

    def update_switch_buttons(self):
        """
        This function updates the positions of the switch buttons according to the screen size.
        Moreover, if the screen size is too small, it will stretch the buttons.
        """
        # Size that would take the buttons if they are not stretched
        size_x_full = self.full_switch_page_button_width * (self.max_page - self.min_page + 1)

        # The left-most disponible position, and the right-most
        right_pos = self.view.screen_size.x - 190
        left_pos = 300 if self.view.userParamView.show_control_bar else 0
        disponible_size = right_pos - left_pos

        # If stretching is needed
        if size_x_full < disponible_size:
            if not self.buttons_full:  # If the text is stretched, we make it full
                # Change the text of each button
                for i in range(len(self.switch_page_buttons)):
                    button = self.switch_page_buttons[i]
                    page = i + self.min_page
                    col = BLACK if button.locked else WHITE
                    button.modify_text(f"PAGE {page}", color=col)
                self.buttons_full = True

            # The x position of the left-most button
            x = (right_pos + left_pos) // 2 - size_x_full // 2
            for button in self.switch_page_buttons:
                button.set_pos(pg.Vector2(x, 0))
                button.size.y = 37  # The height of the button is always identical to the height of the up-bar
                x += button.size.x
        else:
            if self.buttons_full:  # If the text is full, we stretch it
                for i in range(len(self.switch_page_buttons)):
                    # Change the text of each button
                    button = self.switch_page_buttons[i]
                    page = i + self.min_page
                    col = BLACK if button.locked else WHITE
                    button.modify_text(f"{page}", color=col)
                self.buttons_full = False

            x = left_pos
            button_width = disponible_size // len(self.switch_page_buttons)
            # Set the new position and the new size to each button
            for button in self.switch_page_buttons:
                button.set_pos(pg.Vector2(x, 0))
                button.size = pg.Vector2(button_width, 37)
                button.text.pos = button.pos + button.size // 2 - pg.Vector2(button.text.image.get_size()) // 2
                x += button_width

    def switch_page(self, new_page):
        """ Change the current page """

        # The page1 is the page that was visualized by the user, but is no more
        text1 = f"PAGE {self.page}" if self.buttons_full else str(self.page)
        button1 = self.view.buttons[f"PAGE {self.page}"]
        size1 = button1.size.copy()
        button1.unlock()  # Now possible to click on it
        button1.modify_text(text1, color=WHITE)
        # Changing the text change the size too, we have to re-modify it manually
        button1.size = size1
        button1.text.pos = button1.pos + button1.size // 2 - pg.Vector2(button1.text.image.get_size()) // 2

        self.page = new_page

        # The page2 is the new page that the user is visualizing
        text2 = f"PAGE {self.page}" if self.buttons_full else str(self.page)
        button2 = self.view.buttons[f"PAGE {self.page}"]
        size2 = button2.size.copy()
        button2.lock()  # Now possible to click on it
        button2.modify_text(text2, color=BLACK)
        # Changing the text change the size too, we have to re-modify it manually
        button2.size = size2
        button2.text.pos = button2.pos + button2.size // 2 - pg.Vector2(button2.text.image.get_size()) // 2
        # Changing the text change the size too, we have to re-modify it manually

        # Reset the scrolling value
        # In fact we don't store the maximum scroll for each page, so we don't know here how to clamp the page_scroll
        self.set_page_scroll(pg.Vector2(0))

    def set_page_scroll(self, page_scroll: pg.Vector2):
        """ Modify the page_scrolling values, and the values in the scrollingSliders """
        self.page_scrolling_x = page_scroll.x
        self.scrollingSliderX.value = page_scroll.x
        self.page_scrolling_y = page_scroll.y
        self.scrollingSliderY.value = page_scroll.y

    def _page_scroll_clamp(self):
        """
        Clamp the scrolling, the x value and the y value between 0 and the max computed while drawing the components
        """
        if self.page_scrolling_y <= 0:
            self.page_scrolling_y = 0
        elif self.page_scrolling_y >= self.max_page_scrolling_y / self.view.ratio.y:
            self.page_scrolling_y = self.max_page_scrolling_y / self.view.ratio.y

        if self.page_scrolling_x <= 0:
            self.page_scrolling_x = 0
        elif self.page_scrolling_x >= self.max_page_scrolling_x / self.view.ratio.x:
            self.page_scrolling_x = self.max_page_scrolling_x / self.view.ratio.x

    def render(self):
        """
        Renders all the component images according to the model state. It stores the images in the components
        themselves. Note that these operations are really heavy.
        """
        for component in self.components[self.page]:
            component.render()

    def scroll(self, amount: pg.Vector2):
        diffY = self.scrollingSliderY.value - self.page_scrolling_y + amount.y * self.view.SCROLL_SENSIBILITY
        self.page_scrolling_y += diffY

        diffX = self.scrollingSliderX.value - self.page_scrolling_x + amount.x * self.view.SCROLL_SENSIBILITY
        self.page_scrolling_x += diffX

        self._page_scroll_clamp()
        self.scrollingSliderY.value = self.page_scrolling_y
        self.scrollingSliderX.value = self.page_scrolling_x


class UserParamView:
    def __init__(self, view):
        self.view = view
        self.max_param_scrolling_y = self.param_scrolling_y = 0
        self.scrollable_elements = []  # There are all the elements that you can move scrolling through the parameter window
        self.hideable_elements = []  # List of the UI elements that should be hided when you untoggle the control bar.
        self.userTweakableModelParams = {}  # Provide fast and easy access to user's Model parameters
        self.userTweakableEntries = {}  # Provide fast and easy access to all the tweakable entries (UserParam)
        self.show_control_bar = True
        self.scrollingSlider = None
        self.rect = None
        self.shadow = None

    def resize(self):
        """
        Called every time the user resizes the screen.
        It modifies the scrolling slider, and modify the size of the background rectangle.
        """
        self.scrollingSlider.resize(self.view.screen_size.y - 37)
        self.rect.size.y = self.view.screen_size.y - 37
        self.shadow.p2.y = self.view.screen_size.y

    def create_ui(self, model_params, custom_method_call, play_interval: int, render_interval: int) -> None:
        """
        This function creates the gray column in the left part of the screen, and fills it with the user parameters.
        It creates also the three buttons RESET, START/STOP, and STEP
        """
        # The background gray rectangle
        self.rect = self.view.add_UIElement(Rectangle, pg.Vector2(0, 37), pg.Vector2(300, 703), color=LIGHT2_GRAY)
        self.hideable_elements.append(self.rect)

        # The shadow casts by the rectangle
        width = 5
        self.shadow = self.view.add_UIElement(Shadow, pg.Vector2(300 - width, 37), pg.Vector2(300 - width, 740),
                                              pg.Vector2(1, 0), width)
        self.hideable_elements.append(self.shadow)

        # Create the sliders "play interval" and "render interval"
        self._create_flow_control_entries(play_interval, render_interval)

        # Create the other userParams
        y = 260
        self.max_param_scrolling_y = y - 700
        # Create the userParams for the re-instantiation of the model
        if model_params is not None:
            y = self._create_model_params_entries(model_params) + 50

        # Create the userParams for the custom method calls
        if custom_method_call is not None:
            self._create_custom_method_call_entries(custom_method_call, y)

        # The scrolling slider
        self.scrollingSlider = self.view.add_UIElement(ScrollingSlider, pg.Vector2(285, 37), True, 740 - 37,
                                                       self.max_param_scrolling_y)
        self.hideable_elements.append(self.scrollingSlider)

    def toggle_untoggle_control_bar(self):
        """ Removes the control bar, or makes it visible if it is un-toggled. """
        self.show_control_bar = not self.show_control_bar
        # Toggle/un-toggle all the hideable elements
        for elt in self.hideable_elements:
            elt.visible = self.show_control_bar
        self.view.componentsView.toggle_untoggle_control_bar(self.show_control_bar)

    def scroll_params(self, amount: int):
        """
        Scroll through the parameters.
        Moreover, if the user scrolled touching the scrolling slider, it is taken into account in this function.
        :param amount: How much the user is scrolling.
        """
        # diff takes into account the movement mad with the scrolling slider
        # (self.scrollingSlider.value - self.param_scrolling_y) describes how much the value has been changed using the
        # slider
        # (amount * self.view.SCROLL_SENSIBILITY) is how much the user is scrolling with his mouse (or touchpad)
        diff = self.scrollingSlider.value - self.param_scrolling_y + amount * self.view.SCROLL_SENSIBILITY
        prev_param_scrolling_y = self.param_scrolling_y
        self.param_scrolling_y += diff
        self._param_scroll_clamp()
        amount = self.param_scrolling_y - prev_param_scrolling_y

        # Change the position of each scrollable element
        for element in self.scrollable_elements:
            element.set_pos(element.pos - pg.Vector2(0, amount))
        # updates the scrollingSlider too
        self.scrollingSlider.value = self.param_scrolling_y

    def _param_scroll_clamp(self):
        max_scroll = self.compute_max_param_scroll()
        if self.param_scrolling_y <= 0:
            self.param_scrolling_y = 0
        elif 0 < max_scroll <= self.param_scrolling_y:
            self.param_scrolling_y = max_scroll
        elif max_scroll <= 0:
            self.param_scrolling_y = 0

    def compute_max_param_scroll(self):
        """ Returns the max_param_scrolling_y, according to the size of the screen """

        # Let y_screen : the original screen height
        # Let y_scroll : the max_param_scrolling_y
        # Let r : the ratio for the height of the screen
        # Let size = y_screen + y_scroll : the size of the scrollable part (constant)
        #      ____
        #     |    |<-- y_screen
        #     |____|
        #     |    |
        #     |    |<--- y_scroll
        #     |____|
        #
        # When r != 0, we have size = y_screen * r + y_screen * (1 - r) + y_scroll
        # By identification, we get that max_param_scroll is y_screen * (1 - r) + y_scroll

        y_screen = 740 - 37  # We remove the up_bar
        r = self.view.ratio.y
        y_scroll = self.max_param_scrolling_y
        return y_scroll + y_screen * (1 - r)

    def _add_model_param_label(self, label: str, y: int) -> tuple[int | float, int | float, Text]:
        """
        Helper function that creates the label as Text for a model parameter.

        :return: (next_x, center_y, text_element)
        """
        # Start by splitting the label in multimple lines (if it is too long)
        labels = self._split_label(label)

        if len(labels) == 0: labels = [label]
        text: Text = None  # Contains the last text object created   # noqa
        # Create a text object for each line
        for label in labels:
            if text is not None: y += text.image.get_height()
            text = self.view.add_UIElement(Text, pg.Vector2(10, y), label, self.view.fonts["basic20"], color=BLACK)
            self.hideable_elements.append(text)
            self.scrollable_elements.append(text)
        return text.image.get_width() + 20, y + text.image.get_height() / 2, text  # noqa

    def _split_label(self, label: str):
        """ Split the labels so that only max_number_chars characters are in any line. """
        max_number_chars = 26  # Chose empirically
        res = []
        # Split the label in words
        words = label.split(" ")
        i = -1
        last_chosen_i = 0
        current_size = 0
        while i + 1 < len(words):
            i += 1
            current_size += len(words[i]) + 1  # +1 for the space character

            # If it becomes too long
            if current_size > max_number_chars:

                # If it is made of multiple words
                if i > last_chosen_i:
                    r = ""
                    # Reconstruct the line, stopping right before it becomes too long
                    for j in range(last_chosen_i, i):
                        r += words[j] + " "
                    res.append(r[:-1])
                    last_chosen_i = i
                    i -= 1

                # If it is made of only one long word
                else:
                    # Split the word in multiple lines of 26 characters each
                    while len(words[i]) >= max_number_chars:
                        res.append(words[i][:max_number_chars])
                        words[i] = words[i][max_number_chars:]
                    current_size = len(words[i])
                    last_chosen_i = i
        r = ""
        # Reconstruct the final word
        for j in range(last_chosen_i, i + 1):
            r += words[j] + " "
        res.append(r[:-1])
        return res

    def _create_model_params_entries(self, model_params) -> int:
        """
        Create the tweakable user parameters in the left column, which describe how to re-instantiate the model using
        the RESET button.
        Returns the y position at the bottom of the model param entries.
        """
        starting_y = y = 260

        # The background card for all the model parameters
        card = self.view.add_UIElement(ShadowedCard, pg.Vector2(5, y - 10), pg.Vector2(265, 10), WHITE, 3,
                                       border_radius=10)
        self.scrollable_elements.append(card)
        self.hideable_elements.append(card)
        # Pay attention, we change the size of the card at the end of the function

        # Instantiate the model parameters entries
        for param_name in model_params:
            y = self._create_user_param(param_name, model_params[param_name], y)
        y += 15  # The offset with the next elements

        card.set_size(pg.Vector2(275, y - starting_y))

        # The screen without resizing is 740 pixels height, without the up bar it becomes 703
        self.max_param_scrolling_y = y - 703
        return y

    def _create_custom_method_call_entries(self, custom_method_call, starting_y: int) -> None:
        """
        Instantiate the UserParams, the labels, the buttons, and the background cards for the custom method calls.

        :param custom_method_call: The dictionary given by the user that contains the methods, and the parameters to
        call these methods.
        His format is dict[method_name : dict[parameter_name : parameter]]
        Where parameter can be the value, a Slider (from mesa), or a dictionary (as for the model params)
        :param starting_y: The starting y position, where we will start to put the UIElements.
        """
        y = starting_y

        # Instantiate the labels, buttons, UserParams, and background cards for each method
        for method_name in custom_method_call:
            # Instantiate the background shadowed card
            card_starting_y = y
            card = self.view.add_UIElement(ShadowedCard, pg.Vector2(5, y - 10), pg.Vector2(275, 10), WHITE, 3,
                                           border_radius=10)
            self.hideable_elements.append(card)
            self.scrollable_elements.append(card)
            # Pay attention, we change the size of the card at the end of the function

            # Instantiation of the button
            button = self.view.add_UIElement(Button, pg.Vector2(15, y), method_name, self.view.fonts["basic15"],
                                             name=f"method_call-{method_name}")
            self.hideable_elements.append(button)
            self.scrollable_elements.append(button)

            y += button.size.y + 5  # Add a little gap

            # Instantiate the userParameters and the labels
            params = custom_method_call[method_name]
            for param_name in params:
                params[param_name]["model_param"] = False  # It's value should not be given to re-instantiate the model
                params[param_name]["associated_method"] = method_name
                y = self._create_user_param(param_name, params[param_name], y)
            y += 15

            # Resize the card, according to the size taken by all the elements in it
            card.set_size(pg.Vector2(275, y - card_starting_y))
            y += 50

        y -= 50  # Remove the last gap

        # The screen without resizing is 740 pixels height, without the up bar it becomes 703
        self.max_param_scrolling_y = y - 703

    def _create_user_param(self, param_name: str, model_param, y: int) -> int:
        """
        Create a user parameter (UserParam). A user parameter is something that the user can tweak.
        :param param_name: The name of the user parameter. It is used as an ID to recognize the user parameter.
        If this name already exists, we will automatically add numbers at the end of the name.
        :param model_param: A boolean, set to true if the value of the user parameter is used as a parameter for the
        next instantiation of the user's model.
        :param y: The vertical position at which the user parameter widget should be placed.
        :return: The next available vertical position. This value can be used to place later UI elements without
        overlapping this widget.
        """
        # Extract the arguments
        p = self._user_input_params_extraction(model_param, param_name)
        if p is not None:
            type, param = p
            label = param_name
            if "label" in param:
                label = param.pop("label")

            # Instantiates the labels
            x, y, lastUiElement = self._add_model_param_label(label, y)

            # Repositioning
            x = 15  # x was returned by _add_model_param_label for a previous version. Now it is no more useful
            y += lastUiElement.image.get_height()

            # Instantiate the userParam
            args = self._compute_args_for_user_params_creation(type, x, y)
            elem = self.view.add_UIElement(type, *args, **param)
            self.hideable_elements.append(elem)
            self.scrollable_elements.append(elem)

            y += 30

        return y

    def _create_flow_control_entries(self, play_interval: int, render_interval: int) -> None:
        """
        Create the flow control user parameters. Thus are the two sliders "play interval" and "render interval".
        :param play_interval: The starting value of the play_interval's slider.
        :param render_interval: The starting value of the render_interval's slider.
        """
        starting_y = y = 90
        card = self.view.add_UIElement(ShadowedCard, pg.Vector2(5, y - 10), pg.Vector2(275, 10), WHITE, 3,
                                       border_radius=10)
        # Pay attention, we change the size of the card at the end of the function

        # Instantiate the play interval slider and label
        self.scrollable_elements.append(card)
        self.hideable_elements.append(card)
        play_interval_params = {
            "type": "SliderInt",
            "min": 0,
            "max": 2000,
            "step": 10,
            "value": play_interval,
            "param_name": "play_interval",
            "label": "Play interval (ms):",
            "model_param": False
        }
        y = self._create_user_param("play_interval", play_interval_params, y)

        # Instantiate the render interval slider and label
        render_interval_params = {
            "type": "SliderInt",
            "min": 1,
            "max": 50,
            "step": 1,
            "value": render_interval,
            "param_name": "render_interval",
            "label": "Render interval (steps): ",
            "model_param": False
        }
        y = self._create_user_param("render_interval", render_interval_params, y)

        card.set_size(pg.Vector2(275, y - starting_y))

    def _user_input_params_extraction(self, param, param_name: str) -> tuple[type[UserParam], dict]:
        """
        The user can describe a param with a dictionary, but can also describe it with a mesa_user_param.Slider.

        This functions see how the user describes his userParam, and transform this description in a dictionary
        description.

        :return: Tuple (UIElementClass, parameter_dict) if the parameter definition is recognized, raise an error.
        """
        if isinstance(param, dict):
            param["param_name"] = param_name
            t = param.pop("type")
            param["t"] = t
            if t in ("SliderInt", "SliderFloat"):
                return Slider, param
            elif t == "Checkbox":
                return Checkbox, param
            elif t == "Select":
                return Select, param
            elif t == "InputText":
                return InputText, param
            raise NotImplementedError(f"The type {t} has not been implemented")
        elif isinstance(param, mesa_user_param.Slider):
            res = {
                "param_name": param_name,
                "label": param.label,
                "min": param.min,
                "max": param.max,
                "step": param.step,
                "value": param.value,
                "t": ("SliderInt", "SliderFloat")[param.is_float_slider]
            }
            return Slider, res

    def _compute_args_for_user_params_creation(self, t: type[UserParam], x: int, y: int):
        """
        Build the positional arguments required to instantiate a specific UserParam widget.
        :param t: Widget class to instantiate.
        :return: Tuple of positional arguments compatible with add_UIElement().
        """
        if t == Slider:
            return (pg.Vector2(x, y),)
        elif t == Checkbox:
            return (pg.Vector2(x, y - Checkbox.SIZE.y / 2 * self.view.ratio.y),)
        elif t == Select:
            return (pg.Vector2(x, y),)
        elif t == InputText:
            return (pg.Vector2(x, y),)
