import os, time, sys
# os for listing files in directory, time. for sleep (if needed) and sys for exit
import pandas as pd
# pandas is used for manipulating CSVs 
from collections import Counter

all_apps2 = ()
fullElems = dict()
count = 0

try:
    for filename in os.listdir('.'):        # this will allow to read all current directory, 
                                            # check if it is .csv and if not move back to for loop
        if not filename.endswith('.csv'):    
            continue
            # sends back to begining of for loop
        all_apps1 = ()
        data = pd.read_csv(filename)
        byte = data['Bytes']
        packet = data['Packets']
        app = data['Application']
        data_size = len(data.index)
        #print(app)
        #time.sleep(1)

        #for i in range(data_size):
            #all_apps1 = app[i]
            #print(all_apps1)
        #all_apps2 = all_apps1


        dictOfElems = dict(Counter(app))
        #print(dictOfElems)
    fullElems.update(dictOfElems)
    fullElems = { key:value for key, value in dictOfElems.items() if value > 0}
 
    for key, value in fullElems.items():
        print('Application = ' , key , ' :: Repeated Count = ', value)  
        count+=value
    print(count)


#        for i in range(data_size):
#            #print('app ', i)
#            if packet[i] > 3:
#                try:
#                    #print('try ', i)
#                    packet_size.append(int(byte[i])/int(packet[i]))
#                    tran_size.append(int(byte[i]))
#                except ZeroDivisionError:
#                    packet_size.append(0)
#                apps.append(app[i])
#                #print('packet size total ', i)
#                packet_size_total += packet_size[i]
#                trans_total += tran_size[i]
#                count+=1
#                print('Bytes: ', byte[i], 'Packets: ', packet[i], 'Avg packet size: ', int(packet_size[i]), 'App: ', app[i])
#
#            else:
#                packet_size.append(0)
#                tran_size.append(0)
#                continue
#        total+=packet_size_total
#        total_trans+=trans_total
#        total_count+=count
#    print("\n")
#    print('average for this batch of files is: ', int(total/total_count))
#    print('average transaction size for this batch of files is: ', int(total_trans/total_count))
except KeyboardInterrupt:
#    print("\nProgram stopped. Current avg packet size is ", int(total/total_count), 'B\n')
    sys.exit()
