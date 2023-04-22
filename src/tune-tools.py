#!/usr/bin/env python3
"""
Author : Kai Blumberg
Date   : 2023-03-16
Purpose: Help to create and practice music

run:
python3 tune-tools.py -i input/notes/1.txt -w -m 'create_chord_chart' -k b -n
python3 tune-tools.py -i input/chords/1.txt -w -m 'get_chord_notes' -k b
python3 tune-tools.py -i input/chords/1.txt -w -m 'suggest_scales' -k b
python3 tune-tools.py -i input/chords/2.txt -m 'print_chord_fingerboard' -ins 'guitar' -k b
python3 tune-tools.py -i input/scales/1.txt -m 'print_scale_fingerboard' -ins 'guitar' -k b
"""

import os
import argparse
import sys
import csv
import random
import re
import itertools


# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-i',
        '--input',
        help='Input txt file or string where each line is a space delimited list of notes to generate chords with, '
             'or chord name and symbol to get the notes of',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-k',
        '--keys',
        help='Choice of sharp (#) or flat (b) to write note and chord labels with',
        metavar='str',
        type=str,
        default='b')

    parser.add_argument(
        '-w', '--weights', help='A boolean flag for using chord weights to less randomly select chords', action='store_true')

    parser.add_argument(
        '-n', '--notes_gen_chord', help='A boolean flag for whether to print the notes of chords created with '
                                        'create_chord_chart', action='store_true')
    parser.add_argument(
        '-ins',
        '--instrument',
        help="Type of instrument to print fingerboard of options: 'guitar', 'bass', 'ukulele', 'violin', 'mandolin'",
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-m',
        '--main',
        help='main function to 1) generate a chord chart from notes -m "create_chord_chart", 2) Get note from a chord '
             '-m "get_chord_notes", 3) Suggest scales to play over chords "suggest_scales", 4) Print a chord to an '
             'instrument fingerboard "print_chord_fingerboard", 5) Print a scale to an '
             'instrument fingerboard "print_scale_fingerboard"',
        metavar='str',
        type=str,
        default='create_chord_chart')

    return parser.parse_args()


# --------------------------------------------------
def warn(msg):
    """Print a message to STDERR"""
    print(msg, file=sys.stderr)


# --------------------------------------------------
def die(msg='Something bad happened'):
    """warn() and exit with error"""
    warn(msg)
    sys.exit(1)


# --------------------------------------------------
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# --------------------------------------------------
def get_chrom_number(chro_num_list, note_str):
    """Get the chromatic number associated with a note name string"""
    for c in chro_num_list:
        if c['note_string_flat'] == note_str or c['note_string_sharp'] == note_str:
            return int(c['chromatic_number'])
    eprint(f'{note_str} is not an existing note string label')
    die(msg=f'{note_str} is not an existing note string label')


# --------------------------------------------------
def get_chrom_note(chro_num_list, chrom_number, key_arg):
    """Get the note name string associated with a chromatic number"""
    for c in chro_num_list:
        if c['chromatic_number'] == str(chrom_number):
            if key_arg == 'b':
                return c['note_string_flat']
            else:
                return c['note_string_sharp']
    die(msg=f'{chrom_number} is not an existing chromatic note index')


# --------------------------------------------------
def get_chrom_from_chord_num(notation_str, chro_num_list):
    """Get the chromatic number from the chord notation string"""
    # input notation_str e.g. b3
    # output chromatic number 4
    for c in chro_num_list:
        chord_numbers = c['chord_number_string'].split("|")
        if notation_str in chord_numbers:
            return c['chromatic_number']
        elif notation_str == 'NA':
            raise Exception("The notation_str is NA")
    die(msg=f'{notation_str} is not an existing chord notaton string')


# --------------------------------------------------
def get_chord_chrom_list(chord_name, chords_list, chro_num_list):
    note_list = []
    for m in chords_list:
        if m['name'] == chord_name:
            note_list.append(get_chrom_from_chord_num(notation_str=m['one'], chro_num_list=chro_num_list))
            try:
                note_list.append(get_chrom_from_chord_num(notation_str=m['three'], chro_num_list=chro_num_list))
            except:
                pass
            try:
                note_list.append(get_chrom_from_chord_num(notation_str=m['five'], chro_num_list=chro_num_list))
            except:
                pass
            try:
                note_list.append(get_chrom_from_chord_num(notation_str=m['seven'], chro_num_list=chro_num_list))
            except:
                pass
            try:
                note_list.append(get_chrom_from_chord_num(notation_str=m['nine'], chro_num_list=chro_num_list))
            except:
                pass
            try:
                note_list.append(get_chrom_from_chord_num(notation_str=m['eleven'], chro_num_list=chro_num_list))
            except:
                pass
            try:
                note_list.append(get_chrom_from_chord_num(notation_str=m['thirteen'], chro_num_list=chro_num_list))
            except:
                pass
            return note_list


# --------------------------------------------------
def transpose(chrom_number, transp_int):
    chrom_number = int(chrom_number)
    """Transpose a chromatic number"""
    # input a chromatic number and a transposition integer range(0-11) inclusive
    # print(chrom_number, transp_int)
    if transp_int not in range(0, 12):
        die(msg='Invalid transposition integer range')
    else:
        # print(chrom_number, transp_int)
        result = chrom_number + transp_int
        if result > 12:
            result -= 12
            return result
        else:
            return result


# --------------------------------------------------
def get_chord_label_notes(chord_name, transp_int, chords_list, chro_num_list, key_arg):
    """
    Takes a chord name and transposition integer and returns a dict with a
    note list and the chord label
    """
    chrom_list = get_chord_chrom_list(chord_name=chord_name, chords_list=chords_list, chro_num_list=chro_num_list)
    transpose_list = [transpose(chrom_number=t, transp_int=transp_int) for t in chrom_list]
    note_list = [get_chrom_note(chro_num_list=chro_num_list, chrom_number=t, key_arg=key_arg) for t in transpose_list]
    label = f'{note_list[0]}' + chord_name
    d = {'label': label, 'note_list': note_list}
    return d


# --------------------------------------------------
def get_chord_label_chrom_notes(chord_name, transp_int, chords_list, chro_num_list, key_arg):
    """
    Takes a chord name and transposition integer and returns a dict with a
    chromatic note list and the chord label
    """
    chrom_list = get_chord_chrom_list(chord_name=chord_name, chords_list=chords_list, chro_num_list=chro_num_list)
    transpose_list = [transpose(chrom_number=t, transp_int=transp_int) for t in chrom_list]
    chord_key = get_chrom_note(chro_num_list=chro_num_list, chrom_number=transpose_list[0], key_arg=key_arg)
    match = re.search(r"/root[+](\d)", chord_name)
    if match:
        increment = match.group(1)
        new_num = transpose(chrom_number=transpose_list[0], transp_int=int(increment))
        new_note_lab = get_chrom_note(chro_num_list=chro_num_list, chrom_number=new_num, key_arg=key_arg)
        label = f'{new_note_lab}/{chord_key}'
    else:
        label = f'{chord_key}' + chord_name
    d = {'label': label, 'chrom_note_list': transpose_list}
    return d


# --------------------------------------------------
def generate_random_chord(chords_list, chro_num_list, key_arg, weights_arg):
    """
    Takes the chords_list (list of chords) and uses it to randomly choose a chord and a key based on a randomly
    generated transposition int
    returns a chord label and chromatic note list
    """
    # Generate number for a random chord
    if weights_arg == False:
        random_chord = random.randint(0, (len(chords_list) - 1))
        chord = chords_list[int(random_chord)]
        chord_name = chord['name']
    else:
        weighted_list = []
        for m in chords_list:
            weighted_list.extend([m['name'] for i in range(int(m['weight']))])
        random_number = random.randint(0, (len(weighted_list) - 1))
        chord_name = weighted_list[int(random_number)]
    # Generate random number for transposition int
    transp_int = random.randint(0, 11)
    result = get_chord_label_chrom_notes(chord_name=chord_name, transp_int=transp_int, chords_list=chords_list,
                                         chro_num_list=chro_num_list, key_arg=key_arg)
    return result


# --------------------------------------------------
def is_sublist(A, B):
    """ Test if A is sublist of B
    https://www.geeksforgeeks.org/python-check-if-a-list-is-contained-in-another-list/"""
    if not A:
        return True
    if not B:
        return False
    if A[0] == B[0]:
        return is_sublist(A[1:], B[1:])
    return is_sublist(A, B[1:])


# # --------------------------------------------------
# # original
# def get_chord_for_target_notes(target_list, chords_list, chro_num_list, key_arg, weights_arg):
#     """ Input list of chomatic note integers """
#     chord = generate_random_chord(chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg,
#                                   weights_arg=weights_arg, transp_int=False)
#     chrom_note_list = chord['chrom_note_list']
#     # if is_sublist(target_list.sort(), chrom_note_list.sort()):
#
#     # if set(target_list) <= set(chrom_note_list):
#     if all(x in chrom_note_list for x in target_list):
#         print('target_list', target_list)
#         print('chrom_note_list', chrom_note_list)
#         print(chord['label'])
#         return chord
#         # d = {'label': chord['label'], 'chrom_note_list': chrom_note_list}
#         # return d
#     else:
#         get_chord_for_target_notes(target_list=target_list, chords_list=chords_list, chro_num_list=chro_num_list,
#                                    key_arg=key_arg, weights_arg=weights_arg)
# --------------------------------------------------
# Working for loop version
def get_chord_for_target_notes(target_list, chords_list, chro_num_list, key_arg, weights_arg, number):
    """ Input list of chomatic note integers """
    for n in range(0, number):
        chord = generate_random_chord(chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg,
                                      weights_arg=weights_arg)
        chrom_note_list = chord['chrom_note_list']
        if all(x in chrom_note_list for x in target_list):
            # print(n)
            return chord
    for n in range(0, number):
        chord = generate_random_chord(chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg,
                                      weights_arg=weights_arg)
        chrom_note_list = chord['chrom_note_list']
        if all(x in chrom_note_list for x in target_list[:-1]):
            # print(n)
            return chord
    for n in range(0, number):
        chord = generate_random_chord(chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg,
                                      weights_arg=weights_arg)
        chrom_note_list = chord['chrom_note_list']
        if all(x in chrom_note_list for x in target_list[:-2]):
            # print(n)
            return chord
    for n in range(0, number):
        chord = generate_random_chord(chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg,
                                      weights_arg=weights_arg)
        chrom_note_list = chord['chrom_note_list']
        if all(x in chrom_note_list for x in target_list[0:3]):
            # print(n)
            return chord
    for n in range(0, number):
        chord = generate_random_chord(chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg,
                                      weights_arg=weights_arg)
        chrom_note_list = chord['chrom_note_list']
        if all(x in chrom_note_list for x in target_list[0:2]):
            return chord
    for n in range(0, number):
        chord = generate_random_chord(chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg,
                                      weights_arg=weights_arg)
        chrom_note_list = chord['chrom_note_list']
        if all(x in chrom_note_list for x in target_list[0:1]):
            return chord


# --------------------------------------------------
def create_chord_chart(input_list, chro_num_list, chords_list, key_arg, weights_arg, notes_for_gen_chord_bool_arg):
    """Main function 1: print out chart of chords generated from each line of the input note list file"""
    print_list = []
    for i in input_list:
        target_list = i.split(" ")
        target_list = [get_chrom_number(chro_num_list=chro_num_list, note_str=t) for t in target_list]

        chord = get_chord_for_target_notes(target_list=target_list, chords_list=chords_list,
                                           chro_num_list=chro_num_list,
                                           key_arg=key_arg, weights_arg=weights_arg, number=1000)
        print_list.append(chord['label'])
    chord_list = print_list
    print_list = [''] + print_list + ['']
    print_string = ' | '.join(print_list)
    print(print_string[1:])
    if notes_for_gen_chord_bool_arg:
        print('\n')
        print('Chord notes:')
        get_chord_notes(input_list=chord_list, chro_num_list=chro_num_list, chords_list=chords_list, key_arg=key_arg)


# --------------------------------------------------
def parse_printed_chord(input_chord, chro_num_list):
    """
    Helper function for Main function 2 and 3: Parse an input chord from written version with note and symbol
    Return chord_name, chrom_note and bass_note
    """
    input_chord.strip()
    bass_note = ''
    match = re.search(
        r"(C#|Cb|C|Db|D#|D|Eb|E|F#|F|Gb|G#|G|Ab|A#|A|Bb|B)/(C#|Cb|C|Db|D#|D|Eb|E|F#|F|Gb|G#|G|Ab|A#|A|Bb|B)",
        input_chord)
    if match:
        note_str = match.group(1)
        chord_name = ''
        bass_note = match.group(2)
    else:
        try:
            match2 = re.search(r"(C#|Cb|C|Db|D#|D|Eb|E|F#|F|Gb|G#|G|Ab|A#|A|Bb|B)(.*)", input_chord)
            note_str = match2.group(1)
            chord_name = match2.group(2)
        except:
            die(msg=f'{input_chord} is not a valid input chord')
    if chord_name == '':
        chord_name = ' '
    chrom_note = get_chrom_number(chro_num_list=chro_num_list, note_str=note_str)
    d = {'chord_name': chord_name, 'chrom_note': int(chrom_note), 'bass_note': bass_note}
    return d


# --------------------------------------------------
def get_chord_notes(input_list, chro_num_list, chords_list, key_arg):
    """Main function 2: Gets a list of notes for each chord in the input file"""
    for i in input_list:
        chord = parse_printed_chord(input_chord=i, chro_num_list=chro_num_list)
        try:
            res = get_chord_label_notes(chord_name=chord['chord_name'], transp_int=(int(chord['chrom_note']) - 1),
                                        chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg)
        except:
            die(msg=f'{i} is not a valid input chord')
        notes_string = ', '.join(res['note_list'])
        if chord['bass_note'] != '':
            notes_string = chord['bass_note'] + ', ' + notes_string
        print(f"{i}: {notes_string}")


# --------------------------------------------------
def get_chord_chrom_notes(input_list, chro_num_list, chords_list, key_arg, scales_list, action, fingerboard_list,
                          instrument):
    """
    Gets a list of chromatic notes for each chord in an input file use list in:
    Main function 3 to suggest scales to play over the input chord
    Main function 4 to print the input chord notes on an instrument fingerboard diagram
    """
    for i in input_list:
        chord = parse_printed_chord(input_chord=i, chro_num_list=chro_num_list)
        try:
            res = get_chord_label_chrom_notes(chord_name=chord['chord_name'], transp_int=(int(chord['chrom_note']) - 1),
                                              chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg)
        except:
            die(msg=f'{i} is not a valid input chord')
        if chord['bass_note'] != '':
            res['label'] = res['label'].strip() + '/' + chord['bass_note']
            bass_chrom_num = get_chrom_number(chro_num_list=chro_num_list, note_str=chord['bass_note'])
            res['chrom_note_list'] = [bass_chrom_num] + res['chrom_note_list']
        if action == 'suggest_scales':
            suggest_scales(scales_list=scales_list, input_chord=res, chro_num_list=chro_num_list, key_arg=key_arg)
        else:
            print_fingerboard(input_dict=res, chro_num_list=chro_num_list, key_arg=key_arg,
                              fingerboard_list=fingerboard_list, instrument=instrument)


# --------------------------------------------------
def suggest_scales(scales_list, input_chord, chro_num_list, key_arg):
    """Helper for Main function 3: Suggest scales that work over an input chords"""
    target_list = input_chord['chrom_note_list']
    # need to transpose target_list to C
    input_chord_label = input_chord['label']
    dist_to_c = target_list[0] - 1
    inv_dist = 12 - dist_to_c
    if inv_dist >= 12:
        inv_dist -= 12
    transposed_target_list = [transpose(chrom_number=t, transp_int=inv_dist) for t in target_list]
    consonant_scale_list = []
    other_scale_list = []
    for s in scales_list:
        scale_chrom_num_list = s['chromatic_numbers'].split("|")
        scale_chrom_num_list = list(map(int, scale_chrom_num_list))
        for x in range(0, 12):
            transpose_list = [transpose(chrom_number=t, transp_int=x) for t in scale_chrom_num_list]
            sort_list = sorted(transpose_list, key=abs)
            if is_sublist(transposed_target_list, sort_list):
                c_number = transpose_list[0] - inv_dist
                if c_number <= 0:
                    c_number += 12
                note_lab = get_chrom_note(chro_num_list=chro_num_list, chrom_number=c_number, key_arg=key_arg)
                consonant_scale_list.append(f"{note_lab} {s['name']}")
            combos_list = [list(e) for e in
                           itertools.combinations(transposed_target_list, (len(transposed_target_list) - 1))]
            # Do subset combinations of target_list for more possibilities
            for c in combos_list:
                if is_sublist(c, sort_list):
                    c_number = transpose_list[0] - inv_dist
                    if c_number <= 0:
                        c_number += 12
                    note_lab = get_chrom_note(chro_num_list=chro_num_list, chrom_number=c_number,
                                              key_arg=key_arg)
                    other_scale_list.append(f"{note_lab} {s['name']}")
    [consonant_scale_list.append(x) for x in consonant_scale_list if x not in consonant_scale_list]
    [other_scale_list.append(x) for x in other_scale_list if x not in other_scale_list]
    # Remove duplicative scales
    consonant_scale_list = clean_suggested_scale_list(scale_list=consonant_scale_list, key_arg=key_arg)
    other_scale_list = clean_suggested_scale_list(scale_list=other_scale_list, key_arg=key_arg)
    # # Remove duplication between lists
    other_scale_list = [i for i in other_scale_list if i not in consonant_scale_list]
    final_other_list = []
    [final_other_list.append(x) for x in other_scale_list if x not in final_other_list]
    consonant_scales_string = '\n'.join(consonant_scale_list)
    other_scales_string = '\n'.join(final_other_list)
    print(
        f"{input_chord_label.strip()}:\nScale(s) with all chord notes\n{consonant_scales_string}\n\nOther scale(s)\n{other_scales_string}\n")


# --------------------------------------------------
def clean_suggested_scale_list(scale_list, key_arg):
    """Helper function for Main function 3 to clean up the lists of suggested scales"""
    dim1 = ['Db whole half diminished', 'E whole half diminished', 'G whole half diminished',
            'Bb whole half diminished']
    dim2 = ['C# whole half diminished', 'E whole half diminished', 'G whole half diminished',
            'A# whole half diminished']
    dim3 = ['D whole half diminished', 'F whole half diminished', 'Ab whole half diminished',
            'B whole half diminished']
    dim4 = ['D whole half diminished', 'F whole half diminished', 'G# whole half diminished',
            'B whole half diminished']
    dim5 = ['C whole half diminished', 'Eb whole half diminished', 'Gb whole half diminished',
            'A whole half diminished']
    dim6 = ['C whole half diminished', 'D# whole half diminished', 'F# whole half diminished',
            'A whole half diminished']

    wholetone1 = ['C whole tone scale', 'D whole tone scale', 'E whole tone scale', 'Gb whole tone scale',
                  'Ab whole tone scale', 'Bb whole tone scale']
    wholetone2 = ['C whole tone scale', 'D whole tone scale', 'E whole tone scale', 'F# whole tone scale',
                  'G# whole tone scale', 'A# whole tone scale']
    wholetone3 = ['B whole tone scale', 'Db whole tone scale', 'Eb whole tone scale', 'F whole tone scale',
                  'G whole tone scale', 'A whole tone scale']
    wholetone4 = ['B whole tone scale', 'C# whole tone scale', 'D# whole tone scale', 'F whole tone scale',
                  'G whole tone scale', 'A whole tone scale']

    if set(dim5).issubset(scale_list) or set(dim6).issubset(scale_list):
        if key_arg == 'b':
            scale_list = [i for i in scale_list if i not in dim5]
            scale_list.append('whole half diminished C, Eb, Gb, A')
        else:
            scale_list = [i for i in scale_list if i not in dim6]
            scale_list.append('whole half diminished C, D#, F#, A')
    if set(dim1).issubset(scale_list) or set(dim2).issubset(scale_list):
        if key_arg == 'b':
            scale_list = [i for i in scale_list if i not in dim1]
            scale_list.append('whole half diminished Db, E, G, Bb')
        else:
            scale_list = [i for i in scale_list if i not in dim2]
            scale_list.append('whole half diminished C#, E, G, A#')
    if set(dim3).issubset(scale_list) or set(dim4).issubset(scale_list):
        if key_arg == 'b':
            scale_list = [i for i in scale_list if i not in dim3]
            scale_list.append('whole half diminished D, F, Ab, B')
        else:
            scale_list = [i for i in scale_list if i not in dim4]
            scale_list.append('whole half diminished D, F, G#, B')
    if set(wholetone1).issubset(scale_list) or set(wholetone2).issubset(scale_list):
        if key_arg == 'b':
            scale_list = [i for i in scale_list if i not in wholetone1]
            scale_list.append('whole tone scale C, D, E, Gb, Ab, Bb')
        else:
            scale_list = [i for i in scale_list if i not in wholetone2]
            scale_list.append('whole tone scale C, D, E, F#, G#, A#')
    if set(wholetone3).issubset(scale_list) or set(wholetone4).issubset(scale_list):
        if key_arg == 'b':
            scale_list = [i for i in scale_list if i not in wholetone3]
            scale_list.append('whole tone scale B, Db, Eb, F, G, A')
        else:
            scale_list = [i for i in scale_list if i not in wholetone4]
            scale_list.append('whole tone scale B, C#, D#, F, G, A')
    return scale_list


# --------------------------------------------------
def print_fingerboard(input_dict, chro_num_list, key_arg, fingerboard_list, instrument):
    """Helper for Main function 4 and 5: print the notes of an input chord or scale to an instrument fingerboard"""
    chrom_note_list = input_dict['chrom_note_list']
    edge_str = ''
    string_1 = ''
    string_2 = ''
    string_3 = ''
    string_4 = ''
    string_5 = ''
    dots_str = ''
    for f in fingerboard_list:
        edge_str += ''.join(f['edge'])
        string_1 += ''.join(
            f['node'][0][:2] + format_fingerboard_note_str(chrom_number=int(f['string_1']),
                                                           chrom_note_list=chrom_note_list,
                                                           chro_num_list=chro_num_list, key_arg=key_arg) + f['node'][
                                                                                                           1:3])
        string_2 += ''.join(
            f['node'][0][:2] + format_fingerboard_note_str(chrom_number=int(f['string_2']),
                                                           chrom_note_list=chrom_note_list,
                                                           chro_num_list=chro_num_list, key_arg=key_arg) + f['node'][
                                                                                                           1:3])
        string_3 += ''.join(
            f['node'][0][:2] + format_fingerboard_note_str(chrom_number=int(f['string_3']),
                                                           chrom_note_list=chrom_note_list,
                                                           chro_num_list=chro_num_list, key_arg=key_arg) + f['node'][
                                                                                                           1:3])
        string_4 += ''.join(
            f['node'][0][:2] + format_fingerboard_note_str(chrom_number=int(f['string_4']),
                                                           chrom_note_list=chrom_note_list,
                                                           chro_num_list=chro_num_list, key_arg=key_arg) + f['node'][
                                                                                                           1:3])
        try:
            f['string_5']
            string_5 += ''.join(
                f['node'][0][:2] + format_fingerboard_note_str(chrom_number=int(f['string_5']),
                                                               chrom_note_list=chrom_note_list,
                                                               chro_num_list=chro_num_list, key_arg=key_arg) + f[
                                                                                                                   'node'][
                                                                                                               1:3])
        except:
            pass
        try:
            dots_str += ''.join(f['inlay_dots'])
        except:
            pass
    label = f"{input_dict['label'].strip()} on {instrument}"
    # print diagram
    if instrument == 'guitar':
        print(
            f"{label}\n{edge_str}\n{string_1}\n{edge_str}\n{string_2}\n{edge_str}\n{string_3}\n{edge_str}\n{string_4}\n{edge_str}\n{string_5}\n{edge_str}\n{string_1}\n{edge_str}\n{dots_str}\n")
    if instrument == 'bass':
        print(
            f"{label}\n{edge_str}\n{string_3}\n{edge_str}\n{string_4}\n{edge_str}\n{string_5}\n{edge_str}\n{string_1}\n{edge_str}\n{dots_str}\n")
    if instrument == 'ukulele' or instrument == 'mandolin':
        print(
            f"{label}\n{edge_str}\n{string_1}\n{edge_str}\n{string_2}\n{edge_str}\n{string_3}\n{edge_str}\n{string_4}\n{edge_str}\n{dots_str}\n")
    if instrument == 'violin':
        print(
            f"{label}\n{edge_str}\n{string_1}\n{edge_str}\n{string_2}\n{edge_str}\n{string_3}\n{edge_str}\n{string_4}\n{edge_str}\n")


# --------------------------------------------------
def format_fingerboard_note_str(chrom_number, chrom_note_list, chro_num_list, key_arg):
    """
    Helper for function 4
    returns a note string formatted to print to an instrument fingerboard diagram
    """
    note_str = get_chrom_note(chro_num_list=chro_num_list, chrom_number=chrom_number, key_arg=key_arg)
    if chrom_number in chrom_note_list:
        if len(note_str) == 1:
            note_str += ' '
    else:
        note_str = '  '
    return note_str


# --------------------------------------------------
def print_scale_fingerboard(input_list, scales_list, chro_num_list, key_arg, fingerboard_list, instrument):
    """Main function 5: prints the notes from an input scale to an instrument fingerboard diagram"""
    # parsing steps
    regex_string_scales_list = []
    for s in scales_list:
        regex_string_scales_list.append(s['name'])
    regex_string_scales = '|'.join(regex_string_scales_list)
    regex_string = f'(C#|Cb|C|Db|D#|D|Eb|E|F#|F|Gb|G#|G|Ab|A#|A|Bb|B)\s({regex_string_scales})'

    for i in input_list:
        note_str = ''
        scale_str = ''
        match = re.search(regex_string, i)
        if match:
            note_str = match.group(1)
            scale_str = match.group(2)
        else:
            die(msg=f'{i} is not a valid scale name')
        # end parsing steps returns note_str scale_str if helper?

        chrom_num = get_chrom_number(chro_num_list=chro_num_list, note_str=note_str)
        scale_chrom_num_list = []
        for s in scales_list:
            if s['name'] == scale_str:
                scale_chrom_num_list = s['chromatic_numbers'].split("|")
                scale_chrom_num_list = list(map(int, scale_chrom_num_list))
        # Need to transpose target_list to C to check against chromatic numbers of the scales list
        dist_to_c = chrom_num - 1
        inv_dist = 12 - dist_to_c
        if inv_dist >= 12:
            inv_dist -= 12
        transposed_target_list = [transpose(chrom_number=t, transp_int=inv_dist) for t in scale_chrom_num_list]
        # Transpose back to original key
        c_number = chrom_num - inv_dist
        if c_number <= 0:
            c_number += 12
        re_transposed_target_list = [transpose(chrom_number=t, transp_int=(c_number - 1)) for t in
                                     transposed_target_list]
        # print(note_str, scale_str, re_transposed_target_list)
        res = {'label': f'{note_str} {scale_str}', 'chrom_note_list': re_transposed_target_list}
        # print(res)
        print_fingerboard(input_dict=res, chro_num_list=chro_num_list, key_arg=key_arg,
                          fingerboard_list=fingerboard_list, instrument=instrument)


# --------------------------------------------------
def main():
    """Make a jazz noise here"""
    args = get_args()
    main_arg = args.main
    key_arg = args.keys
    input_arg = args.input
    weights_arg = args.weights
    notes_for_gen_chord_bool_arg = args.notes_gen_chord
    instrument_arg = args.instrument
    # Resources
    dirname = os.path.dirname(os.path.abspath(__file__))
    chords_arg = os.path.join(dirname, "resources/chords.tsv")
    scales_arg = os.path.join(dirname, "resources/scales.tsv")
    chrom_num_file = os.path.join(dirname, "resources/chromatic_numbers.tsv")
    guitar_file = os.path.join(dirname, "resources/guitar.tsv")
    ukulele_file = os.path.join(dirname, "resources/ukulele.tsv")
    violin_file = os.path.join(dirname, "resources/violin.tsv")

    if key_arg not in ['b', '#']:
        die(msg='Incorrect Keys argument should be # or b')

    if main_arg == 'print_chord' and instrument_arg == '':
        die(msg="Invalid instrument flag should be one of: 'guitar', 'bass', 'ukulele', 'violin', 'mandolin'")

    chro_num_list = []
    # open and save chromatic_numbers file as list of OrderedDict
    # List of chromatic notes C to B with their numbered from 1-12
    with open(chrom_num_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            chro_num_list.append(row)

    chords_list = []
    # open and save chords file as list of OrderedDict
    with open(chords_arg, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            chords_list.append(row)

    input_list = []
    if os.path.exists(os.path.dirname(input_arg)):
        # open and save input file
        with open(input_arg) as file:
            input_list = [line.strip() for line in file]
    else:
        input_list = input_arg.splitlines()
    input_list = [i.strip() for i in input_list]

    scales_list = []
    # open and save scales file as list of OrderedDict
    with open(scales_arg, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            scales_list.append(row)

    guitar_fingerboard_list = []
    # open and save guitar_file as list of OrderedDict
    # Input table of data for a guitar fingerboard with chromatic_numbers and print strings
    with open(guitar_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            guitar_fingerboard_list.append(row)

    ukulele_fingerboard_list = []
    # open and save ukulele_file as list of OrderedDict
    # Input table of data for a guitar fingerboard with chromatic_numbers and print strings
    with open(ukulele_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            ukulele_fingerboard_list.append(row)

    violin_fingerboard_list = []
    # open and save violin_file as list of OrderedDict
    # Input table of data for a guitar fingerboard with chromatic_numbers and print strings
    with open(violin_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            violin_fingerboard_list.append(row)

    if instrument_arg == "guitar":
        fingerboard_list = guitar_fingerboard_list
    if instrument_arg == "bass":
        fingerboard_list = guitar_fingerboard_list
    if instrument_arg == "ukulele":
        fingerboard_list = ukulele_fingerboard_list
    if instrument_arg == "violin":
        fingerboard_list = violin_fingerboard_list
    if instrument_arg == "mandolin":
        fingerboard_list = violin_fingerboard_list

    # import sys
    # sys.setrecursionlimit(100000)
    # print(sys.getrecursionlimit())

    ## Testing individual functions:
    # a = get_chrom_note(chro_num_list=chro_num_list, chrom_number=2, key_arg=key_arg)
    # b = get_chrom_number(chro_num_list=chro_num_list, note_str='A')
    # c = get_chrom_from_chord_num(notation_str='b3', chro_num_list=chro_num_list)
    # d = get_chord_chrom_list(chord_name='7susb9', chords_list=chords_list, chro_num_list=chro_num_list)
    # e = get_chord_label_notes(chord_name='7susb9', transp_int=10, chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg)
    # f = get_chord_label_chrom_notes(chord_name='/root+1', transp_int=0, chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg)
    # g = generate_random_chord(chords_list=chords_list, chro_num_list=chro_num_list, key_arg=key_arg, weights_arg=weights_arg)
    # h = parse_printed_chord(input_chord='Dm', chro_num_list=chro_num_list)

    if main_arg == 'create_chord_chart':
        """Main function 1: print out chart of chords generated from each line of the input note list file"""
        create_chord_chart(input_list=input_list, chro_num_list=chro_num_list, chords_list=chords_list, key_arg=key_arg,
                           weights_arg=weights_arg, notes_for_gen_chord_bool_arg=notes_for_gen_chord_bool_arg)
    elif main_arg == 'get_chord_notes':
        """Main function 2: Gets a list of notes for each chord in the input file"""
        get_chord_notes(input_list=input_list, chro_num_list=chro_num_list, chords_list=chords_list, key_arg=key_arg)

    elif main_arg == 'suggest_scales':
        """Main function 3: Suggest scales that work over an input list of chords"""
        get_chord_chrom_notes(input_list=input_list, chro_num_list=chro_num_list, chords_list=chords_list,
                              key_arg=key_arg, scales_list=scales_list, action='suggest_scales', fingerboard_list='',
                              instrument='')

    elif main_arg == 'print_chord_fingerboard':
        """Main function 4: prints the notes from an input chord to an instrument fingerboard diagram"""
        get_chord_chrom_notes(input_list=input_list, chro_num_list=chro_num_list, chords_list=chords_list,
                              key_arg=key_arg, scales_list=scales_list, action='print_chord',
                              fingerboard_list=fingerboard_list, instrument=instrument_arg)

    elif main_arg == 'print_scale_fingerboard':
        """Main function 5: prints the notes from an input scale to an instrument fingerboard diagram"""
        print_scale_fingerboard(input_list=input_list, scales_list=scales_list, chro_num_list=chro_num_list,
                                key_arg=key_arg, fingerboard_list=fingerboard_list, instrument=instrument_arg)
    else:
        die(msg=f'{main_arg} is not a valid feature select "create_chord_chart" or "get_chord_notes" instead')


# --------------------------------------------------
if __name__ == '__main__':
    main()
