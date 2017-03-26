import csv

# Processes the results_logger.txt output file

input_file = 'results_logger_best.txt'

fp_we_values = []
nn_we_values = []
hn_values = []
inp_values = []

with open(input_file,'r') as f:
    next(f) # skip headings
    line = csv.reader(f,delimiter='\t')
    for item_id,FP_WE, NN_WE, HN, INP, NN_M1, NN_M2, NN_M3, NN_M4, NN_M5, NN_M6 in line:
        fp_we_values.append(float(FP_WE))
        nn_we_values.append(float(NN_WE))
        hn_values.append(int(HN))
        inp_values.append(int(INP))

average_fp_we = float(sum(fp_we_values)) / len(fp_we_values)
average_nn_we = float(sum(nn_we_values)) / len(nn_we_values)
print("Average FP WE value: {val}".format(val=average_fp_we))
print("Average NN WE value: {val}".format(val=average_nn_we))

num_hn_9_or_11 = [x for x in hn_values if x >= 9]
print("Number of hidden nodes values 9 or 11 is {val} out of total {tot} values".format(val=len(num_hn_9_or_11), tot= len(hn_values)))

num_inp_12_or_above = [x for x in inp_values if x >= 12]
print("Number of input nodes with values 12 or above is {val} out of total {tot} values".format(val=len(num_inp_12_or_above), tot=len(inp_values)))

