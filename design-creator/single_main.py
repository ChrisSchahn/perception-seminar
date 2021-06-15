import random
import numpy as np
import csv
from pathlib import Path


def get_name_list(name, filters, intensities, file_type):
    name_list = []
    for filt in filters:
        if filt == "OG":
            name_list.append([name + "_" + filt + file_type, filt, "0"])
            continue

        for intensity in intensities:
            name_list.append([name + "_" + filt + "_" + intensity + file_type, filt, intensity])

    return name_list


def get_design_for_picture(name_list):
    design_list = []

    for l_idx in range(len(name_list)):
        # for r_idx in range(l_idx, len(name_list)):
        # if name_list[l_idx][0] != name_list[r_idx][0]:
        design_list.append([name_list[l_idx][0],
                            name_list[l_idx][1],
                            name_list[l_idx][2]])

    return design_list


def shuffle_left_right_pic(pairs):
    for i in range(len(pairs)):
        if bool(random.getrandbits(1)):
            # swap position
            pairs[i][0], pairs[i][1], pairs[i][2], pairs[i][3], pairs[i][4], pairs[i][5] = pairs[i][1], pairs[i][0], \
                                                                                           pairs[i][3], pairs[i][2], \
                                                                                           pairs[i][5], pairs[i][4]
    return pairs


def write_to_csv(design):
    filename = "design_single_experiment_1.csv"

    file = Path(filename)
    index = 2

    while file.is_file():
        filename = "design_single_experiment_" + str(index) + ".csv"
        file = Path(filename)
        index += 1

    fields = ['image_a', 'filter_a', 'intensity_a']

    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(design)


def main():
    filters = ["OG", "Clarendon", "Lark", "Juno"]
    intensities = ["25", "50", "75", "100"]

    girl_one_pics = get_name_list("Girl1", filters, intensities, ".jpg")
    girl_two_pics = get_name_list("Girl2", filters, intensities, ".jpg")
    lake_pics = get_name_list("Lake", filters, intensities, ".jpg")
    #mountains_pics = get_name_list("Mountains", filters, intensities, ".jpg")
    ocean_pics = get_name_list("Ocean", filters, intensities, ".jpg")
    temple_pics = get_name_list("Temple", filters, intensities, ".jpg")

    girl_one_design = get_design_for_picture(girl_one_pics)
    girl_two_design = get_design_for_picture(girl_two_pics)
    lake_design = get_design_for_picture(lake_pics)
    #mountains_design = get_design_for_picture(mountains_pics)
    ocean_design = get_design_for_picture(ocean_pics)
    temple_design = get_design_for_picture(temple_pics)

    design = girl_one_design + girl_two_design + lake_design + ocean_design + temple_design
    #design = shuffle_left_right_pic(design)

    npdesign = np.asarray(design)
    np.random.shuffle(npdesign)
    write_to_csv(npdesign)


if __name__ == "__main__":
    main()
