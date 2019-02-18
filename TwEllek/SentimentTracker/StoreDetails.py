import pickle
import os.path
import dill

def load_dill(file_name):
    if os.path.isfile(file_name): # file exists
        print(file_name, 'exists')
        try:
            print("loading pickle: ", file_name)
            program_path = os.path.dirname(os.path.realpath("__file__")) + '/'
            file = open(program_path + file_name, "rb")
            unpickler = pickle.Unpickler(file)
            t = unpickler.load()
            return t
        except Exception as error:
            print('Error opening file:', error)
            return False
    else:
        print(file_name, 'does not exist')
        return False


def save_dill(obj, file_name):
    program_path = os.path.dirname(os.path.realpath("__file__"))
    # print('saving: ' + file_name + ' at path: ' + str(program_path))
    file = open(program_path + '/' + file_name, "wb")
    dill.dump(obj, file)
