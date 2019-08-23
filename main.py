
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, getopt
from datetime import datetime
from tqdm import tqdm
import uuid
# from nltk.tokenize  import sent_tokenize, word_tokenize

ROTATION_PERIOD = 20

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

def save_schedule(schedule):
    with open('out/%s.out'%uuid.uuid4(), 'w') as out:
        out.writelines("%s\n" % rotation for rotation in schedule)


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
        opts, args = getopt.getopt(argv, "hvg:o:i:p:", ['guards=','ofile='])
    except getopt.GetoptError as e:
        print('main.py -i <input.schedule> -o <output.rotation> -p <amount of positions>')
        sys.exit(2)
    

    """ Parse arguments """
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -i <input.schedule> -o <output.rotation> -p <amount of positions>')
            sys.exit()
        elif opt in ('-g', "--guards"):
            guards = arg
        elif opt in ('-o', "--output", "-ofile"):
            outputfile = arg
        elif opt in ('-i', '--input', 'ifile'):
            inputfile = arg
        elif opt in ('-p', '--positions'):
            positions = int(arg)

    """ 
    TODO: Make a way where if basic requirements are not met return error message.
  
        if outputfile or inputfile is None:
            print('Please define both an input and output file')
            print('main.py -i <input.schedule> -o <output.rotation>')
            sys.exit() 
    """


    schedule = parse_schedule(inputfile)
    amount_guards = len(schedule)

    print('Making a %s guard rotation with %s spots on.' % (amount_guards, positions))

    if (int(positions) % 2) == 0:
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

                print('On Postions %s' % on_positions)
                print('Off Postions %s' % off_positions)

                # Find total length of shift
                today_init = datetime.now()
                earliest_time = today_init.replace(hour=23, minute=59, second=59,microsecond=0)
                latest_time = today_init.replace(hour=0, minute=0, second=0,microsecond=0)

                for guard in schedule:
                    
                    # In time calculations
                    in_time = guard["in"].split(":")
                    in_hour = int(in_time[0])
                    in_minute = int(in_time[1])
                    in_time = today_init.replace(hour=in_hour, minute=in_minute, second=0, microsecond=0)

                    if in_time < earliest_time:
                        earliest_time = in_time
                
                    
                    # Out time calculations
                    out_time = guard["out"].split(":")
                    out_hour = int(out_time[0])
                    out_minute = int(out_time[1])
                    out_time = today_init.replace(hour=out_hour, minute=out_minute, second=0, microsecond=0)

                    if out_time > latest_time:
                        latest_time = out_time
                

                shift_length = (latest_time-earliest_time).seconds
                shift_length = (shift_length/60)

                total_rotations = shift_length/ROTATION_PERIOD

                print('Our shift length is %s minutes long. With %s total rotations' % (shift_length, total_rotations))

                for i in range(1, total_rotations+1):
                    if i == 1:
                        current_rotation = []
                        for guard in schedule:
                            current_rotation.append(guard['id'])
                        overall_rotation.append(current_rotation)
                    else:
                        '''
                        i -1 is the index of the last rotation
                        Rotate overall_rotation[i-1] to the right by one
                        '''

                        past_rotation = overall_rotation[i-2]
                        current_rotation = rotate(past_rotation, -1)
                        overall_rotation.append(current_rotation)
                
                # print(overall_rotation)
                save_schedule(overall_rotation)
            else:
                print('We do not have enough guards in that schedule! We need %s positions' % (positions))
    else:
        print('Odd positions')
    


if __name__ == "__main__":
    main(sys.argv[1:])