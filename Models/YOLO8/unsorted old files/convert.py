
import os

import pandas as pd
import shutil

# create a folder

# os.makedirs("stuff", exist_ok=True)

'''
filename	 Fog_High	 Fog_Low	 Lens_Obstruction_1	 Lens_Obstruction_2	 Lens_Obstruction_3	 Light_Reflection_High	 Light_Reflection_Low	 Sea_Roughness_1	 Sea_Roughness_2	 Sea_Roughness_3	 Sea_Roughness_4	 Visibility_Restricted
masonboro_inlet-2024-01-09-n63_jpg.rf.0b94724cac864db23e946cddf0325b02.jpg	1	0	0	0	1	0	0	0	0	1	0	0
masonboro_inlet-2024-01-09-n52_jpg.rf.07f4ae18c4ad9093e57119b52523a10d.jpg	1	0	0	0	1	0	0	0	0	1	0	0
masonboro_inlet-2024-01-09-n29_jpg.rf.0293238870899170dfb561b8f711073a.jpg	1	0	0	0	1	0	0	0	0	1	0	1
masonboro_inlet-2023-12-17-n37_jpg.rf.0cb4d1f3a876051672697e6f39137616.jpg	1	0	0	0	1	0	0	0	0	1	0	1
'''

# open a csv, it will have a structure such as the one above. calculate the number of classes each image has for each row

# train
# test
# valid


CSV = pd.read_csv(
    r"C:\Users\death\Documents\Github\WebCoos-Camera-Features\Models\YOLO8 Classification\data\valid\_classes.csv")


# create a folder for each column head in the "stuff" folder

# for column in CSV.columns[1:]:
#     className = column.replace(" ", "")
#     os.makedirs(f"stuff/{className}", exist_ok=True)


# # iterate through the rows
for index, row in CSV.iterrows():

    # iterate through the columns
    for column in CSV.columns[1:]:
        # if the column has a 1, create a file inside the folder
        # removed whitespace from column

        if row[column] == 1:
            className = column.replace(" ", "")
            # print(f"stuff/{className}/{row['filename']}.txt")
            if os.path.exists(f"C:/Users/death/Documents/Github/WebCoos-Camera-Features/Models/YOLO8 Classification/data/valid/{row['filename']}"):
                # copy jpg file to the folder
                source = f"C:/Users/death/Documents/Github/WebCoos-Camera-Features/Models/YOLO8 Classification/data/valid/{row['filename']}"
                destination = f"stuff/{className}/{row['filename']}"
                shutil.copy2(source, destination)
