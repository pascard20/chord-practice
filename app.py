from functions import open_icon, generate_progressions, construct_scale, init_CTkFrame, draw_progression
from variables import *
from settings import *
import customtkinter as ctk
import time
import random
from datetime import datetime


class Root(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.wm_attributes('-alpha', 0)
        self.title(APP_TITLE)
        self.iconbitmap(PATH_ICON)

        # App
        self.app = App(self)

        # Binds
        self.bind('<Map>', self.deiconify_app)
        self.bind('<Unmap>', self.iconify_app)
        self.bind('<FocusIn>', self.self_focus)

        # Run
        self.mainloop()

    def deiconify_app(self, event=None):
        self.app.deiconify()

    def iconify_app(self, event=None):
        self.app.withdraw()

    def self_focus(self, event=None):
        self.app.tkraise()


class App(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master, fg_color=COLOR_APP['fg'])
        self.master = master

        # Window
        self.overrideredirect(True)
        self.width, self.height = WINDOW_SIZE[0], WINDOW_SIZE[1]
        x, y = (self.winfo_screenwidth() - self.width) // 2, (self.winfo_screenheight() - self.height) // 3
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Layout
        self.title_bar = TitleBar(self, self.close_app, self.minimise_app)
        self.app_layout = AppLayout(self)

        self.title_bar.pack(fill='x')
        self.app_layout.pack(expand=True, fill='both')

        # Binds
        self.bind('<Button-1>', self.click)

    def close_app(self):
        with open('defaults.txt', 'w') as file:
            file.write(f"Key: {self.app_layout.var_scale_selected.get()}\n")
            file.write(f"Random key: {self.app_layout.var_random_scale_check.get()}\n")
            file.write(f"Turns: {self.app_layout.var_turns.get()}\n")
        self.master.destroy()

    def minimise_app(self):
        self.master.state('iconic')

    def click(self, event=None):
        if str(event.widget.winfo_parent()) != str(self.app_layout.ent_turns):
            self.focus()
            if not self.app_layout.var_turns.get():
                self.app_layout.var_turns.set('1')


class TitleBar(ctk.CTkFrame):
    def __init__(self, master, close_func, minimise_func):
        super().__init__(master, fg_color='transparent', corner_radius=0)
        self.master = master
        self.drag_data = {'x': 0, 'y': 0}

        # Layout
        self.title_frame = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)
        self.title_frame.pack(side='left', fill='y', padx=(PADDING_TITLEBAR, 0))

        self.icon = ctk.CTkLabel(
            self.title_frame,
            text='',
            image=open_icon(PATH_TITLE_ICON, ICON_SIZE_TITLE),
            width=ICON_SIZE_TITLE[0],
            height=ICON_SIZE_TITLE[1],
        )
        self.title = ctk.CTkLabel(
            self.title_frame,
            text=APP_TITLE,
            text_color=COLOR_APP['text'],
            font=(FONT, FONT_SIZE_S)
        )
        self.icon.pack(side='left', fill='y', ipadx=PADDING_TITLEBAR)
        self.title.pack(side='left', fill='y')

        # Buttons
        self.close = TitleBarButton(self, close_func, PATH_CLOSE)
        self.minimise = TitleBarButton(self, minimise_func, PATH_MINIMISE)

        self.close.pack(side='right', ipadx=ICON_SIZE_BUTTON[0], ipady=ICON_SIZE_BUTTON[1]//2)
        self.minimise.pack(side='right', ipadx=ICON_SIZE_BUTTON[0], ipady=ICON_SIZE_BUTTON[1]//2)

        # Binds
        for m in [self] + self.title_frame.winfo_children():
            m.bind('<Enter>', lambda event: self.configure(fg_color=COLOR_APP['hover']))
            m.bind('<Leave>', lambda event: self.configure(fg_color='transparent'))
            m.bind('<Button-1>', lambda event: self.start_drag(self, event))
            m.bind('<B1-Motion>', self.drag_window)
        
    def start_drag(self, main_widget, event):
        self.drag_data = {
            'x': event.x - main_widget.winfo_rootx() + event.widget.winfo_rootx(),
            'y': event.y - main_widget.winfo_rooty() + event.widget.winfo_rooty()
        }
        
    def drag_window(self, event):
        x = event.x_root - self.drag_data['x']
        y = event.y_root - self.drag_data['y']
        self.master.geometry(f"+{x}+{y}")
        self.configure(fg_color=COLOR_APP['hover'])


class CustomButton(ctk.CTkButton):
    def __init__(
            self,
            master,
            command,
            width=0,
            height=0,
            ico_path=None,
            text=None,
            font=None,
            fg_color='#000000',
            text_color='#000000',
            click_color='#000000',
            hover_color='#000000',
            border_color='#000000',
            border_width=1
    ):
        super().__init__(
            master,
            text=text,
            font=font,
            image=open_icon(ico_path, ICON_SIZE_BUTTON) if ico_path else ico_path,
            fg_color=fg_color,
            text_color=text_color,
            width=width,
            height=height,
            corner_radius=0,
            hover=False,
            border_color=border_color,
            border_width=border_width
        )

        self.hover, self.clicked = False, False
        self.fg_color = fg_color
        self.border_color = border_color
        self.click_color = click_color
        self.hover_color = hover_color
        self.command = command
        self.text = text
        self.border_width = border_width
        self.width, self.height = width, height

        # Binds
        self.bind('<Enter>', self.enter)
        self.bind('<Leave>', self.leave)
        self.bind('<Button-1>', self.click)
        self.bind('<ButtonRelease-1>', self.release)
        self.bind('<Map>', self.update_size)

    def reposition_label(self):
        if self.text:
            for m in self.winfo_children():
                if str(m.winfo_name()) == '!label':
                    m.grid_forget()
                    m.place(
                        x=self.border_width,
                        y=self.border_width,
                        width=self.width - (self.border_width * 2 + 1),
                        height=self.height - (self.border_width * 2),
                    )

    def update_size(self, event=None):
        self.width, self.height = self.winfo_width(), self.winfo_height()
        self.reposition_label()

    def enter(self, event=None):
        self.hover = True
        self.configure(fg_color=self.click_color if self.clicked else self.hover_color)

    def leave(self, event=None):
        self.hover, self.clicked = False, False
        self.configure(fg_color = self.fg_color, border_color=self.border_color)

    def click(self, event=None):
        self.clicked = True
        self.configure(fg_color = self.click_color, border_color= self.click_color)

    def release(self, event=None):
        if self.hover and self.clicked:
            self.command()
        self.configure(
            fg_color=self.hover_color if self.hover else self.fg_color,
            border_color=self.hover_color if self.hover else self.border_color
        )
        self.clicked = False


class TitleBarButton(CustomButton):
    def __init__(self, master, command, ico_path):
        super().__init__(
            master,
            command,
            width=ICON_SIZE_BUTTON[0],
            height=ICON_SIZE_BUTTON[1],
            ico_path=ico_path,
            fg_color='transparent',
            border_width=0,
            click_color=COLOR_APP['click'],
            hover_color=COLOR_APP['hover']
        )


class AppButton(CustomButton):
    def __init__(self, master, command, text, hover_color=None, click_color=None):
        self.hover_color = hover_color if hover_color else COLOR_APP['hover']
        self.click_color = click_color if click_color else COLOR_APP['click']

        super().__init__(
            master,
            command,
            text=text,
            font=(FONT, FONT_SIZE_M),
            fg_color='transparent',
            text_color=COLOR_APP['text'],
            border_color=COLOR_APP['hover'],
            hover_color=self.hover_color,
            click_color=self.click_color,
            width=165,
            height=50
        )

        self.border_color = COLOR_APP['hover']

        if hover_color:
            self.bind(
                '<Enter>', lambda event: self.configure(fg_color=self.hover_color, border_color=self.hover_color)
            )
            self.bind(
                '<Leave>', lambda event: self.configure(fg_color='transparent', border_color=self.border_color)
            )


class AppLayout(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color='transparent', corner_radius=0)
        self.master = master

        # Variables
        try:
            with open(f"defaults.txt", 'r') as file:
                self.defaults = {
                    line.split(': ')[0]: line.rstrip('\n').split(': ')[1]
                    for line in file if ': ' in line
                }
        except FileNotFoundError:
            self.defaults = {}

        defaults_keys = self.defaults.keys()
        self.notes_list = ['/'.join(m) for m in NOTES]
        self.var_scale_selected = ctk.StringVar(value=self.defaults['Key'] if 'Key' in defaults_keys and self.defaults['Key'] in self.notes_list else str(self.notes_list[SCALE_ROOT]))
        self.var_random_scale_check = ctk.StringVar(value=self.defaults['Random key'] if 'Random key' in defaults_keys else 'off')
        self.var_turns = ctk.StringVar(value=self.defaults['Turns'] if 'Turns' in defaults_keys else NUM_TURNS)

        if int(self.var_turns.get()) > MAX_TURNS:
            self.var_turns.set(str(MAX_TURNS))
        self.var_turns.trace('w', self.check_entry)

        self.progressions, self.progressions_selected, self.progressions_discarded = None, None, None
        self.var_question, self.var_scale_name, self.var_question_number, self.var_answer = ctk.StringVar(), ctk.StringVar(), ctk.StringVar(), ctk.StringVar()
        self.var_time, self.var_wrong_answers, self.var_correct_answers = ctk.StringVar(), ctk.StringVar(), ctk.StringVar()

        self.question_count, self.num_digits, self.start_time, self.final_time = 0, 0, 0, 0
        self.current_progression, self.constructed_scale = [], []

        # Tracing
        self.var_random_scale_check.trace('w', self.handle_random_scale_checkbox)

        """ ------------------------------- MENU ------------------------------- """

        self.frm_menu = init_CTkFrame(self)
        self.frm_menu.pack(expand=True, fill='both')

        self.lbl_app_title = ctk.CTkLabel(
            self.frm_menu,
            text="Chord Practice",
            font=(FONT, FONT_SIZE_TITLE),
            text_color=COLOR_APP['text']
        )
        self.lbl_app_title.pack(pady=(50, 20))

        self.frm_settings_border = ctk.CTkFrame(
            self.frm_menu,
            fg_color=COLOR_APP['fg'],
            corner_radius=0,
            border_color=COLOR_APP['hover'],
            border_width=1
        )
        self.frm_settings = init_CTkFrame(self.frm_settings_border)
        self.frm_settings_border.pack(padx=(20, 20), pady=(20, 20), ipadx=30, ipady=15)
        self.frm_settings.pack(padx=(20, 20), pady=(20, 20), fill='both', expand=True)

        # Scale settings
        self.frm_settings_scale = init_CTkFrame(self.frm_settings)
        self.frm_settings_scale.pack(side='left', fill='y', expand=True, padx=(0, 10), pady=(5, 0))

        self.lbl_scale_title = TitleLabel(self.frm_settings_scale, 'Key')

        self.opt_scale_options = ctk.CTkComboBox(
            self.frm_settings_scale,
            values=['/'.join(m) for m in NOTES],
            variable=self.var_scale_selected,
            width=ENTRY_WIDTH + ENTRY_BUTTON_WIDTH * 2,
            corner_radius=0,
            fg_color=COLOR_APP['fg'],
            font=(FONT, FONT_SIZE_M),
            button_color=COLOR_BUTTON['fg'],
            button_hover_color=COLOR_BUTTON['hover'],
            border_color=COLOR_BUTTON['fg'],
            dropdown_hover_color=COLOR_APP['light_hover'],
            dropdown_font=(FONT, FONT_SIZE_S),
            dropdown_text_color=COLOR_APP['fg'],
            dropdown_fg_color=COLOR_APP['text'],
            text_color=COLOR_APP['text'],
            text_color_disabled=COLOR_APP['text_transparent'],
            border_width=1,
            justify='center',
            state='readonly',
            height=ENTRY_HEIGHT
        )

        self.chk_random_scale = ctk.CTkCheckBox(
            self.frm_settings_scale,
            text='Random',
            text_color=COLOR_APP['text'],
            font=(FONT, FONT_SIZE_S),
            variable=self.var_random_scale_check,
            onvalue='on',
            offvalue='off',
            corner_radius=0,
            checkbox_width=18,
            checkbox_height=18,
            border_width=1,
            border_color=COLOR_BUTTON['fg'],
            fg_color=COLOR_BUTTON['fg'],
            hover_color=COLOR_BUTTON['fg']
        )

        self.lbl_scale_title.pack(pady=(0, 25))
        self.opt_scale_options.pack()
        self.chk_random_scale.pack(pady=(15, 0), padx=(15, 0))
        self.handle_random_scale_checkbox() # Check if random scale option is checked by default

        # Number of turns settings
        self.frm_settings_turns = init_CTkFrame(self.frm_settings)
        self.frm_settings_turns.pack(fill='y', expand=True, side='left', pady=(5, 0))

        self.lbl_turns_title = TitleLabel(self.frm_settings_turns, 'Turns')
        self.frm_settings_turns_entry = init_CTkFrame(self.frm_settings_turns)

        self.lbl_turns_title.pack(pady=(0, 25))
        self.frm_settings_turns_entry.pack()

        self.ent_turns = ctk.CTkEntry(
            self.frm_settings_turns_entry,
            fg_color=COLOR_APP['fg'],
            textvariable=self.var_turns,
            border_color=COLOR_BUTTON['fg'],
            corner_radius=0,
            width=ENTRY_WIDTH,
            font=(FONT, FONT_SIZE_M),
            text_color=COLOR_APP['text'],
            height=ENTRY_HEIGHT,
            border_width=1,
            justify='center'
        )

        self.btn_add_turn = TurnButton(self.frm_settings_turns_entry, '+', self.add_turn)
        self.btn_substract_turn = TurnButton(self.frm_settings_turns_entry, '-', self.substract_turn)

        self.btn_substract_turn.pack(side='left')
        self.ent_turns.pack(side='left')
        self.btn_add_turn.pack(side='left')

        self.btn_start = AppButton(
            self.frm_menu,
            self.start_exercise,
            'Start',
        )

        self.lbl_credits = ctk.CTkLabel(
            self.frm_menu,
            text='created by Łukasz Pasternak | 2024',
            font=(FONT, FONT_SIZE_S+1),
            text_color=COLOR_APP['text_credits']
        )

        self.lbl_credits.pack(side='bottom', pady=(0, 10))
        self.btn_start.pack(side='bottom', pady=(0, 85))

        """ ----------------------------- QUESTION ----------------------------- """

        self.frm_question_space = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)

        self.lbl_scale_name = ctk.CTkLabel(
            self.frm_question_space,
            textvariable=self.var_scale_name,
            text_color=COLOR_APP['text_transparent'],
            font=(FONT, FONT_SIZE_L+2)
        )
        self.lbl_question_number = ctk.CTkLabel(
            self.frm_question_space,
            textvariable=self.var_question_number,
            text_color=COLOR_APP['text_transparent'],
            font=(FONT_NUMBERS, FONT_SIZE_L)
        )
        self.lbl_question = ctk.CTkLabel(
            self.frm_question_space,
            textvariable=self.var_question,
            text_color=COLOR_APP['text'],
            font=(FONT, FONT_SIZE_XXL)
        )
        self.lbl_answer = ctk.CTkLabel(
            self.frm_question_space,
            textvariable=self.var_answer,
            text_color=COLOR_APP['text_gentle'],
            font=(FONT, FONT_SIZE_XL)
        )
        self.lbl_scale_name.place(relx=0.505, y=15, anchor='n')
        self.lbl_question_number.place(relx=0.5, y=42, anchor='n')
        self.lbl_question.place(relx=0.5, rely=0.46, anchor='center')
        self.lbl_answer.place(relx=0.5, rely=0.57, anchor='center')

        # Buttons
        self.frm_buttons_top = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)
        self.frm_buttons_bottom = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)

        self.btn_reveal = AppButton(
            self.frm_buttons_top,
            self.reveal_progression,
            'Reveal'
        )
        self.btn_correct = AppButton(
            self.frm_buttons_bottom,
            self.answer,
            'Correct',
            COLOR_APP['hover_correct'],
            COLOR_APP['click_correct'],
        )
        self.btn_wrong = AppButton(
            self.frm_buttons_bottom,
            lambda: self.answer('wrong'),
            'Wrong',
            COLOR_APP['hover_wrong'],
            COLOR_APP['click_wrong'],
        )

        self.btn_reveal.pack(fill='x', padx=(10, 10), pady=(10, 0))
        self.btn_wrong.pack(side='left', padx=(10, 5), fill='x', expand=True)
        self.btn_correct.pack(side='left', padx=(5, 10), fill='x', expand=True)

        """ ---------------------------- END SCREEN ---------------------------- """

        self.frm_end = init_CTkFrame(self)

        self.lbl_end_scale_name = ctk.CTkLabel(
            self.frm_end,
            textvariable=self.var_scale_name,
            text_color=COLOR_APP['text'],
            font=(FONT, FONT_SIZE_TITLE)
        )
        self.lbl_end_scale_name.pack(pady=(50, 0))

        self.frm_summary = init_CTkFrame(self.frm_end)
        self.frm_summary.pack(pady=(40, 0))

        self.frm_summary.columnconfigure(0, weight='2')
        self.frm_summary.columnconfigure(1, weight='1')
        self.frm_summary.rowconfigure(0, weight='1')
        self.frm_summary.rowconfigure(1, weight='1')
        self.frm_summary.rowconfigure(2, weight='1')

        self.lbl_summary_list = [
            EndLabel(self.frm_summary, 'Correct answers:'),
            EndLabel(self.frm_summary, textvariable=self.var_correct_answers),
            EndLabel(self.frm_summary, 'Wrong answers:'),
            EndLabel(self.frm_summary, textvariable=self.var_wrong_answers),
            EndLabel(self.frm_summary, 'Time:'),
            EndLabel(self.frm_summary, textvariable=self.var_time),
        ]

        for idx, label in enumerate(self.lbl_summary_list):
            label.grid(
                column=idx % 2,
                row=idx // 2,
                sticky='w' if idx % 2 == 0 else 'e',
                padx=(0, 20) if idx % 2 == 0 else (20, 0),
                pady=(0, 4)
            )

        self.frm_end_buttons = init_CTkFrame(self.frm_end)
        self.frm_end_buttons.pack(pady=(75, 0))

        self.btn_end_list = [
            AppButton(self.frm_end_buttons, lambda: self.handle_restart('menu'), 'Return to menu'),
            AppButton(self.frm_end_buttons, lambda: self.handle_restart('restart'), 'Restart'),
            AppButton(self.frm_end_buttons, self.master.close_app, 'Quit')
        ]
        for button in self.btn_end_list:
            button.pack(pady=(0, 20))

    """ ---------------------- OPERATIONAL FUNCTIONS ----------------------- """

    def update_time_output(self):
        self.var_time.set(
            f"{
            str(self.final_time // 60) + ' min ' if self.final_time >= 60 else ''
            }{
            str(self.final_time % 60) + ' sec' if self.final_time % 60 != 0 else '0 sec' if self.final_time == 0 else ''
            }"
        )

    def check_entry(self, *args):
        new_string = []
        for char in self.var_turns.get():
            if char and not (char == '0' and not new_string):
                if char.isdigit():
                    new_string.append(char)
        output = ''.join(new_string)
        if output and int(output) > MAX_TURNS:
            output = str(MAX_TURNS)
        self.var_turns.set(output)

    def add_turn(self):
        if not self.var_turns.get():
            self.var_turns.set('1')
        elif int(self.var_turns.get()) < MAX_TURNS:
            self.var_turns.set(str(int(self.var_turns.get()) + 1))

    def substract_turn(self):
        turns = self.var_turns.get()
        if not turns or int(turns) <= 1:
            self.var_turns.set('1')
        else:
            self.var_turns.set(str(int(turns) - 1))

    def handle_random_scale_checkbox(self, *args):
        if self.var_random_scale_check.get() == 'on':
            self.opt_scale_options.configure(state='disabled', border_color=COLOR_BUTTON['disabled'], button_color=COLOR_BUTTON['disabled'])
        else:
            self.opt_scale_options.configure(state='normal', border_color=COLOR_BUTTON['fg'], button_color=COLOR_BUTTON['fg'])

    def print_progression(self):
        self.current_progression = self.progressions_selected[self.question_count]
        progression_output = '-'.join([chord[0] for chord in self.current_progression])
        self.update_question_number()
        self.var_question.set(f"{progression_output}")

    def update_question_number(self):
        additional_zeroes = (self.num_digits - len(str(self.question_count + 1))) * '0'
        self.var_question_number.set(f"{additional_zeroes}{self.question_count + 1}/{len(self.progressions_selected)}")

    def update_digits(self):
        self.num_digits = len(str(len(self.progressions_selected)))

    def reveal_progression(self):
        progression_names = [
            self.constructed_scale[CHORDS_ROMAN.index(chord[0].lower().rstrip('°'))] \
            + (chord[1] if chord[1] != 'M' else '')
            for chord in self.current_progression
        ]
        self.var_answer.set(f"{', '.join(progression_names)}")

    def hide_widgets(self, layout_type, widgets):
        layouts = {
            'pack': 'pack_forget',
            'place': 'place_forget',
            'grid': 'grid_forget'
        }
        for widget in widgets:
            getattr(widget, layouts[layout_type])()

    """ ---------------------------- EXERCISE FUNCTIONS ---------------------------- """

    def start_exercise(self):
        self.var_wrong_answers.set('0')
        self.var_correct_answers.set('0')
        self.progressions, self.progressions_selected, self.progressions_discarded = generate_progressions(int(self.var_turns.get()))
        self.frm_menu.pack_forget()
        self.frm_question_space.pack(expand=True, fill='both')
        self.frm_buttons_bottom.pack(side='bottom', pady=(10, 10), fill='x')
        self.frm_buttons_top.pack(side='bottom', fill='x')
        self.update_digits()
        scale_root = ['/'.join(m) for m in NOTES].index(self.var_scale_selected.get())
        if self.var_random_scale_check.get() == 'on':
            scale_root = random.choice([m for m in range(len(NOTES)) if m != scale_root])
            self.var_scale_selected.set('/'.join(NOTES[scale_root]))
        self.constructed_scale = construct_scale(SCALE_TYPE, scale_root, SCALE_MODE)
        self.var_scale_name.set(f"{self.constructed_scale[0]} {MODES[SCALE_MODE]}")
        self.print_progression()
        self.start_time = time.time()

    def answer(self, answer_type='correct'):
        if answer_type == 'wrong':
            draw_progression(self.progressions, self.progressions_selected, self.progressions_discarded)
            self.update_digits()
            self.update_question_number()
            self.var_wrong_answers.set(str(int(self.var_wrong_answers.get()) + 1))
        else:
            self.var_correct_answers.set(str(int(self.var_correct_answers.get()) + 1))
        if self.question_count >= len(self.progressions_selected) - 1:
            self.hide_widgets('pack', [self.frm_question_space, self.frm_buttons_top, self.frm_buttons_bottom])
            self.final_time = round(time.time() - self.start_time)
            self.frm_end.pack()
            self.update_time_output()

            try:
                with open('log.txt', 'r') as file:
                    lines = file.readlines()
            except FileNotFoundError:
                lines = []

            with open('log.txt', 'a') as file:
                if lines:
                    file.write('\n\n\n')

                file.write(f"{self.var_scale_name.get()}\n")
                file.write(f"{datetime.now().strftime("%d.%m.%Y %H:%M")}\n")
                file.write(f"{'='*16}\n")
                file.write(f"Correct answers: {self.var_correct_answers.get()}\n")
                file.write(f"Wrong answers: {self.var_wrong_answers.get()}\n")
                file.write(f"Time: {self.var_time.get()}")
        else:
            self.question_count += 1
            self.print_progression()
        self.var_answer.set('')

    def handle_restart(self, action_type):
        self.frm_end.pack_forget()
        self.question_count = 0
        if action_type == 'menu':
            self.frm_menu.pack(expand=True, fill='both')
        elif action_type == 'restart':
            self.start_exercise()


class TurnButton(ctk.CTkButton):
    def __init__(self, master, text, command):
        super().__init__(
            master,
            text=text,
            command=command,
            width=ENTRY_BUTTON_WIDTH+1,
            fg_color=COLOR_BUTTON['fg'],
            hover_color=COLOR_BUTTON['hover'],
            corner_radius=0,
            font=(FONT_BOLD, FONT_SIZE_L),
            height=ENTRY_HEIGHT,
        )


class TitleLabel(ctk.CTkLabel):
    def __init__(self, master, text):
        super().__init__(
            master,
            text=text,
            text_color=COLOR_APP['text'],
            font=(FONT_LIGHT, FONT_SIZE_L)
        )


class EndLabel(ctk.CTkLabel):
    def __init__(self, master, text=None, textvariable=None):
        super().__init__(
            master,
            text=text,
            text_color=COLOR_APP['text'],
            font=(FONT_LIGHT, FONT_SIZE_L),
            textvariable=textvariable
        )


if __name__ == '__main__':
    Root()