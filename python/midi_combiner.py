from mido import MidiFile, Message
import sys

original_track_names = sorted(sys.argv[2:])
new_track_name = sys.argv[1]

original_files = map(lambda tn: MidiFile(tn), original_track_names)

new_file = MidiFile()
new_file.ticks_per_beat = original_files[0].ticks_per_beat

for n, original_file in enumerate(original_files):
    track = original_file.tracks[0]
    for message in track:
        try:
            message.channel = n
        except AttributeError:
            pass

    new_file.tracks.append([Message('program_change', program=12, time=0)] + track)

new_file.save(new_track_name)

piano = [1, 2, 3, 4, 5, 6, 7, 8]
chromatic_percussion = [9, 10, 11, 12, 13, 14, 15, 16]
organ = [17, 18, 19, 20, 21, 22, 23, 24]
guitar = [25, 26, 27, 28, 29, 30, 31, 32]
bass = [33, 34, 35, 36, 37, 38, 39, 40]
strings = [41, 42, 43, 44, 45, 46, 47, 48]
ensemble = [49, 50, 51, 52, 53, 54, 55, 56]
brass = [57, 58, 59, 60, 61, 62, 63, 64]
reed = [65, 66, 67, 68, 69, 70, 71, 72]
pipe = [73, 74, 75, 76, 77, 78, 79, 80]
synth_lead = [81, 82, 83, 84, 85, 86, 87, 88]
synth_pad = [89, 90, 91, 92, 93, 94, 95, 96]
synth_effects = [97, 98, 99, 100, 101, 102, 103, 104]
ethnic = [105, 106, 107, 108, 109, 110, 111, 112]
percussive = [113, 114, 115, 116, 117, 118, 119, 120]
sound_effects = [121, 122, 123, 124, 125, 126, 127, 128]
instrument_map = {1: "acoustic_grand_piano", 2: "bright_acoustic_piano", 3: "electric_grand_piano",
                  4: "honky_tonk_piano",
                  5: "electric_piano_1", 6: "electric_piano_2", 7: "harpsichord", 8: "clavinet", 9: "celesta",
                  10: "glockenspiel",
                  11: "music_box", 12: "vibraphone", 13: "marimba", 14: "xylophone", 15: "tubular_bells",
                  16: "dulcimer",
                  17: "drawbar_organ", 18: "percussive_organ", 19: "rock_organ", 20: "church_organ", 21: "reed_organ",
                  22: "accordion",
                  23: "harmonica", 24: "tango_accordion", 25: "acoustic_guitar_nylon", 26: "acoustic_guitar_steel",
                  27: "electric_guitar_jazz", 28: "electric_guitar_clean", 29: "electric_guitar_muted",
                  30: "overdriven_guitar",
                  31: "distortion_guitar", 32: "guitar_harmonics", 33: "acoustic_bass", 34: "electric_bass_finger",
                  35: "electric_bass_pick", 36: "fretless_bass", 37: "slap_bass_1", 38: "slap_bass_2",
                  39: "synth_bass_1",
                  40: "synth_bass_2", 41: "violin", 42: "viola", 43: "cello", 44: "contrabass", 45: "tremolo_strings",
                  46: "pizzicato_strings", 47: "orchestral_harp", 48: "timpani", 49: "string_ensemble_1",
                  50: "string_ensemble_2",
                  51: "synth_strings_1", 52: "synth_strings_2", 53: "choir_aahs", 54: "voice_oohs", 55: "synth_choir",
                  56: "orchestra_hit", 57: "trumpet", 58: "trombone", 59: "tuba", 60: "muted_trumpet",
                  61: "french_horn",
                  62: "brass_section", 63: "synth_brass_1", 64: "synth_brass_2", 65: "soprano_sax", 66: "alto_sax",
                  67: "tenor_sax",
                  68: "baritone_sax", 69: "oboe", 70: "english_horn", 71: "bassoon", 72: "clarinet", 73: "piccolo",
                  74: "flute",
                  75: "recorder", 76: "pan_flute", 77: "blown_bottle", 78: "shakuhachi", 79: "whistle", 80: "ocarina",
                  81: "lead_1_square", 82: "lead_2_sawtooth", 83: "lead_3_calliope", 84: "lead_4_chiff",
                  85: "lead_5_charang",
                  86: "lead_6_voice", 87: "lead_7_fifths", 88: "lead_8_bass_lead", 89: "pad_1_new_age",
                  90: "pad_2_warm",
                  91: "pad_3_polysynth", 92: "pad_4_choir", 93: "pad_5_bowed", 94: "pad_6_metallic", 95: "pad_7_halo",
                  96: "pad_8_sweep",
                  97: "fx_1_rain", 98: "fx_2_soundtrack", 99: "fx_3_crystal", 100: "fx_4_atmosphere",
                  101: "fx_5_brightness",
                  102: "fx_6_goblins", 103: "fx_7_echoes", 104: "fx_8_sci_fi", 105: "sitar", 106: "banjo",
                  107: "shamisen", 108: "koto",
                  109: "kalimba", 110: "bagpipe", 111: "fiddle", 112: "shanai", 113: "tinkle_bell", 114: "agogo",
                  115: "steel_drums",
                  116: "woodblock", 117: "taiko_drum", 118: "melodic_tom", 119: "synth_drum", 120: "reverse_cymbal",
                  121: "gwuitar_fret_noise", 122: "breath_noise", 123: "seashore", 124: "bird_tweet",
                  125: "telephone_ring",
                  126: "helicopter", 127: "applause", 128: "gunshot"}
