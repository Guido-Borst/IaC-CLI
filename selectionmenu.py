# Copyright 2024 Guido Borst. All Rights Reserved.

import curses

def draw_menu(stdscr, current_index, options, counters, menu_text, bool_input):
    stdscr.clear()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    stdscr.addstr(0, 0, menu_text)

    for i, option in enumerate(options):
        if bool_input:
            counter_str = '(*)' if counters[i] > 0 else '( )'
        else:
            counter_str = str(counters[i])
        if i == current_index:
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(i+2, 0, f'{counter_str} {option}')
            stdscr.attroff(curses.color_pair(2))
        else:
            stdscr.addstr(i+2, 0, f'{counter_str} {option}')

    stdscr.addstr(i+4, 0, 'Press Enter to confirm your selection or Q to quit')

    stdscr.refresh()

def main(stdscr, options, counters=None, menu_text='Select options using cursor keys:', bool_input=False):
    if counters is None:
        counters = [0]*len(options)
    curses.cbreak()
    stdscr.keypad(True)
    current_index = 0
    draw_menu(stdscr, current_index, options, counters, menu_text, bool_input)

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_index = max(0, current_index - 1)
        elif key == curses.KEY_DOWN:
            current_index = min(len(options) - 1, current_index + 1)
        elif key == curses.KEY_RIGHT and not bool_input:
            counters[current_index] += 1
        elif key == curses.KEY_LEFT and not bool_input:
            counters[current_index] = max(0, counters[current_index] - 1)
        elif key == ord(' ') and bool_input:
            counters[current_index] = 1 if counters[current_index] == 0 else 0
        elif key == ord('Q') or key == ord('q'):
            break
        elif (key == curses.KEY_ENTER or key in [10, 13]) and any(counters):
            break

        draw_menu(stdscr, current_index, options, counters, menu_text, bool_input)

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

    return counters

def make_menu_selection(options, counters=None, menu_text='Select options:', print_results=False, bool_input=False):
    counters = curses.wrapper(main, options, counters, menu_text, bool_input)
    if print_results:
        for i, option in enumerate(options):
            print(f'{option}: {counters[i]}')
    return counters
    

if __name__ == "__main__":
    options = ['Option A', 'Option B', 'Option C', 'Option D']
    counters = make_menu_selection(options, print_results=True, bool_input=True)

