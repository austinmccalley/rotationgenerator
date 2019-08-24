#!/usr/bin/env python


import sys
import getopt
from datetime import datetime
from tqdm import tqdm
import uuid
import math
# from nltk.tokenize  import sent_tokenize, word_tokenize

# ALL IN MINUTES
ROTATION_PERIOD = 20
BREAK_START_PERIOD = 120
BREAK_END_PERIOD = 180


overall_rotation = []
breaks = {}


def parse_schedule(schedule_file):
    guards = []
    string = ""

    f = open(schedule_file, 'r')
    f1 = f.readlines()

    for line in tqdm(f1):
        if line is not None or not string:
            line_split = line.split(',')
            if line_split[0] != "name":
                if len(line_split) == 4:
                    guard = {
                        "name": line_split[0],
                        "in": line_split[1],
                        "out": line_split[2],
                        "age": line_split[3],
                        "id": str(uuid.uuid4())
                    }
                else:
                    guard = {
                        "name": line_split[0],
                        "in": line_split[1],
                        "out": line_split[2],
                        "age": line_split[3],
                        "id": line_split[4].strip('\n')
                    }
                guards.append(guard)
    print('Parsed {} guards out of the schedule file.'.format(len(guards)))
    return guards


def save_schedule(schedule, breaks):
    with open('out/%s.out' % uuid.uuid4(), 'w') as out:
        out.writelines("%s\n" % rotation for rotation in schedule)
        out.write(str(breaks))


def parse_on_off(on_positions, off_positions, schedule, amount_guards):
    # Find total length of shift
    today_init = datetime.now()
    earliest_time = today_init.replace(
        hour=23, minute=59, second=59, microsecond=0)
    latest_time = today_init.replace(
        hour=0, minute=0, second=0, microsecond=0)

    for guard in schedule:

        # In time calculations
        in_time = guard["in"].split(":")
        in_hour = int(in_time[0])
        in_minute = int(in_time[1])
        in_time = today_init.replace(
            hour=in_hour, minute=in_minute,
            second=0, microsecond=0)

        if in_time < earliest_time:
            earliest_time = in_time

        # Out time calculations
        out_time = guard["out"].split(":")
        out_hour = int(out_time[0])
        out_minute = int(out_time[1])
        out_time = today_init.replace(
            hour=out_hour, minute=out_minute,
            second=0, microsecond=0)

        if out_time > latest_time:
            latest_time = out_time

    shift_length = (latest_time-earliest_time).seconds
    shift_length = (shift_length/60)

    total_rotations = math.floor(shift_length/ROTATION_PERIOD)

    print('Our shift length is %s minutes long. With %s total rotations' %
          (shift_length, total_rotations))

    break_taken = []
    for i in range(1, int(total_rotations+1)):
        if i == 1:
            current_rotation = []
            for guard in schedule:
                current_rotation.append(guard['id'])
            overall_rotation.append(current_rotation)
        else:

            past_rotation = overall_rotation[i-2]
            current_rotation = rotate(past_rotation, -1)
            overall_rotation.append(current_rotation)

            current_rotation_time = i * ROTATION_PERIOD

            if current_rotation_time >= BREAK_START_PERIOD:
                curr_break_taken = []
                # Itterate through the current guarding spots
                for j in range(1, len(current_rotation)+1):
                    # If the guarding spot is off
                    if j in set(off_positions) and not (len(off_positions)-1) == len(curr_break_taken):

                        guardID = current_rotation[j-1]
                        if guardID not in set(break_taken):
                            # Guard is on their break
                            break_taken.append(guardID)
                            breaks[guardID] = current_rotation_time
                            curr_break_taken.append(current_rotation_time)

                            break_taken.append(guardID)

    save_schedule(overall_rotation, breaks)


def rotate(l, n):
    return l[n:] + l[:n]


def main(argv):
    """ Main program """

    guards = 0
    positions = 0
    try:
        outputfile, inputfile
    except NameError:
        outputfile = None
        inputfile = None

    """ Initialze arguments """
    try:
        opts, args = getopt.getopt(argv, "hvg:o:i:p:", ['guards=', 'ofile='])
    except getopt.GetoptError as e:
        print('main.py -i <input.schedule> -o',
              '<output.rotation> -p <amount of positions>')
        sys.exit(2)

    """ Parse arguments """
    for opt, arg in opts:
        if opt == '-h':
            print(
                'main.py -i <input.schedule> -o',
                ' <output.rotation> -p <amount of positions>')
            sys.exit()
        elif opt in ('-g', "--guards"):
            guards = arg
        elif opt in ('-o', "--output", "-ofile"):
            outputfile = arg
        elif opt in ('-i', '--input', 'ifile'):
            inputfile = arg
        elif opt in ('-p', '--positions'):
            positions = int(arg)

    schedule = parse_schedule(inputfile)
    amount_guards = len(schedule)

    if positions >= amount_guards:
        print('ERROR: More guards needed')
        sys.exit()

    print('Making a %s guard rotation with %s spots on.' %
          (amount_guards, positions))

    if ((float(amount_guards)/float(positions)) == 2):
        # Even amount of positions for guards

        # Check to make sure we have enough guards
        if int(amount_guards) > int(positions):
            # print('Have enough guards')

            if positions*2 == amount_guards:
                # Simple on off rotation
                # print('On and then off')

                on_positions = []
                off_positions = []

                for x in range(1, (amount_guards + 1)):
                    if (int(x) % 2) == 0:
                        off_positions.append(x)
                    else:
                        on_positions.append(x)

                parse_on_off(on_positions, off_positions,
                             schedule, amount_guards)

            else:
                print('We do not have enough guards in that schedule! We need %s positions' % (
                    positions))
    else:

        if (float(amount_guards)/positions) > 2:
            on_positions = [1]
            off_positions = []
            past_pos = 1
            for x in range(1, positions):
                next_pos = math.floor(
                    (float(amount_guards - x) / 2) + past_pos)
                on_positions.append(int(next_pos))
                past_pos = next_pos

            for i in range(1, amount_guards):
                if i not in set(on_positions):
                    off_positions.append(i)
            parse_on_off(on_positions, off_positions, schedule, amount_guards)


if __name__ == "__main__":
    main(sys.argv[1:])
