import itertools
import argparse
from ast import literal_eval


parser = argparse.ArgumentParser()
parser.add_argument('script_fn', type=str)
parser.add_argument('--set', nargs='+')
parser.add_argument('--sweep', action='store_true')


def my_literal_eval(value):
    try:
        value = literal_eval(value)
    except ValueError:
        pass
    except SyntaxError:
        pass
    return value


def get_param_dict(sweep_dict, set_dict):
    sweep_attrs = list(sweep_dict.keys())
    sweep_combo = list(itertools.product(*sweep_dict.values()))
    params = []
    for sc in sweep_combo:
        param = {sweep_attrs[i]: sc[i] for i in range(len(sc))}
        param.update(set_dict)
        params.append(param)

    return params


def get_exp(config):
    exp_list = []
    for k, v in config.items():
        exp_list.append(k)
        exp_list.append(str(v))
    return '_'.join(exp_list)


def print_params(script_fn, params):
    for c in params:
        s = f'python {script_fn} --set '
        for k, v in c.items():
            s += k
            s += ' '
            s += str(v)
            s += ' '
        s += 'exp '
        s += get_exp(c)
        print(s)


def parse_sweep_arg(sweep_arg):
    key_str, vals_str = sweep_arg.split(':')
    if '/' in key_str:
        full_key, short_key = key_str.split('/')
    else:
        full_key = key_str
        short_key = key_str
    full_key = full_key.strip()
    short_key = short_key.strip()
    
    vals = [my_literal_eval(v.strip()) for v in vals_str.split(',')]
    
    return full_key, vals


def main(args):
    set_dict = {}
    if args.set is not None:
        set_keys = args.set[0::2]
        set_vals = args.set[1::2]
        set_dict = {set_keys[i]: my_literal_eval(set_vals[i]) for i in range(len(set_keys))}

    params = []
    if args.sweep:
        print('Enter sweep parameters: ')
        sweep_dict = {}	
        while True:
            message = input()
            if message == '':
                break
            else:
                key, vals = parse_sweep_arg(message)
                sweep_dict[key] = vals
        params = get_param_dict(sweep_dict, set_dict)
    else:
        if set_dict != {}:
            params = [set_dict]

    print_params(args.script_fn, params)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
