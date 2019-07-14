import csv

line_id_list = []
with open('C:/Users/Lampros Yfantis/Desktop/VC_Network_Data_Fran/Rail_Network_Data/Train_route_platform.csv', 'r') as trp:
    Train_route_platforms = csv.DictReader(trp)
    for row in Train_route_platforms:
        if row['line_id'] not in line_id_list:
            line_id_list.append(row['line_id'])

print(line_id_list)

line_seq_num_dict = {}
for line in line_id_list:
    line_seq_num_dict.update({line: []})
    with open('C:/Users/Lampros Yfantis/Desktop/VC_Network_Data_Fran/Rail_Network_Data/Train_route_platform.csv', 'r') as trp:
        Train_route_platforms = csv.DictReader(trp)
        for row in Train_route_platforms:
            if row['line_id'] == line:
                line_seq_num_dict[line].append(int(row['sequence_no']))
print(line_seq_num_dict)
