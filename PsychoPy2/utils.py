import csv, os

def from_csv(path, file):
    '''
    Construct array of dicts, with keys from the csv header and each following row as an aray.
    File must reside in the `resources` folder.
    :param file: 
    :return: 
    '''

    file = path + file
    ret = {}
    header = []

    with open(file, 'r') as f:
        reader = csv.reader(f)
        rownr = 0

        for row in reader:
            id = row[0]
            # row = row[1:]
            if rownr == 0:
                header = row
            else:
                r = dict(zip(header, row))
                ret[id] = r

            rownr = rownr + 1

    return ret

class Screen:
    def display(self):
        return