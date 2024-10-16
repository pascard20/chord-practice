from variables import *
from settings import *
import customtkinter as ctk
from PIL import Image
from itertools import product
from random import randint, choice


def open_icon(path, size):
    ico = Image.open(path).resize(size)
    return ctk.CTkImage(ico, ico, size)


def apply_scale_mode(func_list, func_mode):
    return func_list[func_mode:] + func_list[:func_mode]


def init_CTkFrame(master):
    return ctk.CTkFrame(master, fg_color='transparent', corner_radius=0)


# SCALE_TYPE -> str, root_note -> int, mode -> int
def construct_scale(scale_type, root_note, mode=0):
    scale_output = [NOTES[root_note]]
    intervals_list = SCALES[scale_type].intervals

    # Program ignores mode if SCALE_TYPE is other than regular
    if scale_type == 'regular':
        intervals_list = apply_scale_mode(intervals_list, mode)

    intervals_sum = sum(intervals_list[-mode:])
    corresponding_major_root = root_note - intervals_sum
    if corresponding_major_root < 0:
        corresponding_major_root += len(NOTES)
    use_flats = corresponding_major_root in FLAT_KEYS

    for interval in intervals_list:
        root_note += interval
        if root_note > len(NOTES) - 1:
            root_note -= len(NOTES)
        scale_output.append(NOTES[root_note])

    for idx, note in enumerate(scale_output):
        if len(note) > 1:
            scale_output[idx] = note[int(use_flats)]
        else:
            scale_output[idx] = note[0]
            
    return scale_output


def generate_progressions(num_turns):

    # Apply selected scale's chord pattern to roman numeral chords
    chords_pattern = apply_scale_mode(SCALES[SCALE_TYPE].chord_types, SCALE_MODE)

    chords_processed = [
        [chord.upper(), pattern] if pattern == 'M'
        else [chord + '°', pattern] if pattern == 'dim'
        else [chord, pattern]
        for chord, pattern in zip(CHORDS_ROMAN, chords_pattern)
        if not (SKIP_DIM and pattern == 'dim')
    ]

    # Generate all possible progressions (with no more than two chord repeats)
    progressions = [
        [i, j, k, l]
        for i, j, k, l in product(chords_processed, repeat=4)
        if len(set([tuple(m) for m in [i, j, k, l]])) > 2
    ]

    # Choose a set of progressions
    progressions_selected, progressions_discarded = [], []
    for _ in range(num_turns):
        draw_progression(progressions, progressions_selected, progressions_discarded)

    return progressions, progressions_selected, progressions_discarded


def draw_progression(progressions, progressions_selected, progressions_discarded):
    if not progressions_selected:
        progressions_selected.append(choice(progressions))
        return

    for _ in range(50):
        candidate = progressions[randint(0, len(progressions) - 1)]

        # Ensure no duplicate elements in the same position
        if all(j != progressions_selected[-1][idx] for idx, j in enumerate(candidate)):
            if candidate in progressions_selected:
                progressions_discarded.append(candidate)
            else:
                progressions_selected.append(candidate)
                return
