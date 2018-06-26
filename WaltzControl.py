import time

import command_line_class 
# open serial connection
waltz=command_line_class.CommandLineCommands()

print()
print('CAUTION: THIS IS A FIRST ATTEMPT TO CONTROL THE WALTZ TELESCOPE. \n'
      'BAD INPUTS OR CRASHES OF THE PROGRAM COULD BE HARMFUL TO THE TELESCOPE. \n'
      'DO NOT USE THIS PROGRAM ALONE AND ALWAYS PREPARE FOR STOPING MOVEMENTS' 
      ' OF THE TELESCOPE VIA THE EMERGENCY STOPS IN THE DOME!')
def main():
    while 1 :
        # get keyboard input
        # Python 3 users
        inp = input(">> ")
        
        #Look for optional duration parameter. These are separated by a ':'
        command=inp.partition(':')[0]
        parameter=inp.partition(':')[2]
        try:
            parameter=float(parameter)
            if command in waltz.command_dic and parameter>0:
                waltz.execute_command_dic(command, parameter)
        except:
            if command in waltz.command_dic and parameter!='':
                waltz.execute_command_dic(command,parameter)
            elif command in waltz.command_dic:
                waltz.execute_command_dic(command)
            else:
                waltz.write(command.encode('utf-8'))
                time.sleep(0.1)
                out = waltz.get_response()
                print(">>" + out)

main()
            
             
