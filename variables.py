class Scale:
    def __init__(self, intervals, chord_types):
        self.intervals = intervals
        self.chord_types = chord_types


NOTES = [
    ['A'],          # 0
    ['A#', 'Bb'],   # 1
    ['B'],          # 2
    ['C'],          # 3
    ['C#', 'Db'],   # 4
    ['D'],          # 5
    ['D#', 'Eb'],   # 6
    ['E'],          # 7
    ['F'],          # 8
    ['F#', 'Gb'],   # 9
    ['G'],          # 10
    ['G#', 'Ab'],   # 11
]

SHARP_KEYS = [0, 2, 3, 5, 7, 10]
FLAT_KEYS = [1, 4, 6, 8, 9, 11]
CHORDS_ROMAN = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii']

SCALES = {
    'regular': Scale([2, 2, 1, 2, 2, 2, 1], ['M', 'min', 'min', 'M', 'M', 'min', 'dim']),
    # 'major pentatonic': Scale([2, 2, 3, 2, 3]),
    # 'minor pentatonic': Scale([3, 2, 2, 3, 2]),
    # 'blues': Scale([3, 2, 1, 1, 3, 2])
}

MODES = {
    0: 'major',     # ionian
    1: 'dorian',
    2: 'phrygian',
    3: 'lydian',
    4: 'mixolydian',
    5: 'minor',     # aeolian
    6: 'locrian'
}
