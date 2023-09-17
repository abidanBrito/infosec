import os
import os.path
import filecmp

def check_challenge(fname):
    if os.path.isfile(fname+'_solution'):
        p_one = " "
        if(fname == "highcard"):
            p_one = " partially "
        if (not os.path.isfile(fname)) or (not filecmp.cmp(fname, fname+'_solution')):
            print('Challenge' + p_one + 'failed!')
        else:
            print('Challenge' + p_one + 'solved!')