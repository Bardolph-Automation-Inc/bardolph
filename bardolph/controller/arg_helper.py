import logging

def add_n_argument(parser):
    parser.add_argument(
        '-n', '--num-lights', help='number of lights to discover, >= 0')

def get_overrides(args):
    if args.num_lights is None:
        return None
        
    try:
        num_lights = int(args.num_lights)
        if num_lights < 0:
            raise ValueError
    except ValueError:
        logging.error("Invalid value for -n or --num-lights.")
        logging.error("Must be a integer greater than or equal to zero.")
        raise ValueError

    return {'default_num_lights': num_lights}
