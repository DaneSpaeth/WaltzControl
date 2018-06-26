import lx200commands as lx

class CommandLineCommands(lx.Lx200Commands):
    
    def __init__(self):
        super().__init__()
        
        #Commands for initial settings
        self.print_info()
        self.toggle_precision()
        self.set_speed_guide()
        self.get_coordinates()
        
        self.command_dic={
            'move_west':self.move_west,
            'west':self.move_west,
            'w':self.move_west,
            'move_east':self.move_east,
            'east':self.move_east,
            'e':self.move_east,
            'move_north':self.move_north,
            'north':self.move_north,
            'n':self.move_north,
            'move_south':self.move_south,
            'south':self.move_south,
            's':self.move_south,
            'get_coordinates':self.print_coordinates,
            'coordinates':self.print_coordinates,
            'c':self.print_coordinates,
            'set_hip_target':self.set_hip_target,
            'hip_target':self.set_hip_target,
            'hip':self.set_hip_target,
            'set_target_dec':self.set_target_dec_from_string,
            'target_dec':self.set_target_dec_from_string,
            'dec':self.set_target_dec_from_string,
            'set_target_ra':self.set_target_ra_from_string,
            'target_ra':self.set_target_ra_from_string,
            'ra':self.set_target_ra_from_string,
            'print_target_coordinates':self.print_target_coordinates,
            'target_coordinates':self.print_target_coordinates,
            'target':self.print_target_coordinates,
            'slew_to_target':self.slew_to_target,
            'slew':self.slew_to_target,
            'set_speed_max':self.set_speed_max,
            'speed_max':self.set_speed_max,
            'set_speed_find':self.set_speed_find,
            'speed_find':self.set_speed_find,
            'set_speed_center':self.set_speed_center,
            'speed_center':self.set_speed_center,
            'set_speed_guide':self.set_speed_guide,
            'speed_guide':self.set_speed_guide,
            'toggle_precision':self.toggle_precision,
            'precision':self.toggle_precision,
            'print_info':self.print_info,
            'info':self.print_info,
            'help':self.print_info,
            'exit':self.exit_program}
        
    def execute_command_dic(self,func_name,*args):
        """Executes functions corresponding to keywords in the command_dic.
           Those Keywords are User inputs.
        """
        self.command_dic[func_name](*args)
        
    def print_target_coordinates(self):
        if self.target_ra and self.target_dec:
            print('Target Coordinates: Ra='+self.target_ra+'  Dec='+self.target_dec)
        else:
            print('No valid target coordinates set!')
            return 0
        
    def set_hip_target(self, hip_nr):
        super().set_hip_target(hip_nr)
        self.print_target_coordinates()
        
    def print_coordinates(self):
        self.get_coordinates()
        print('RA=',self.ra, ' DEC=',self.dec) 

    def print_info(self):
        userinfo=('Possible (LX200) Commands'+'\r\n'+'\r\n'+
                  'get_coordinates /coordinates /c  Print Telescope RA and DEC'+'\r\n'+
                  'move_west:duration or west:duration or w:duration  Move telescope in the west direction for chosen duration (default=0.1s) '+'\r\n'+
                  'move_west or west or w  Move telescope in the west direction for default duration =0.1s '+'\r\n'+
                  'Other directions respectively (east, north, south)'+'\r\n'+'\r\n'+
                  'set_target_dec:+dd mm ss (/+dd mm)  or target_dec or dec  Set target Declination'+'\r\n'+
                  'set_target_ra:hh mm ss (/hh mm.t)  or target_ra or ra  Set target Right Ascension'+'\r\n'+
                  'set_hip_target:"hip_nr" or hip_target:"hip_nr" or hip:"hip_nr"  Set Hipparcos star as target' +'\r\n'+
                  'print_target_coordinates or target_coordinates or target  Print current target coordinates'+'\r\n'+
                  'slew_to_target or slew  Slew to target (target needs to be set before)'+'\r\n'+'\r\n'+
                  'set_speed_max or speed_max  Set speed to max rate (fastest)'+'\r\n'+
                  'set_speed_find or speed_find  Set speed to find rate (second fastest)'+'\r\n'+
                  'set_speed_center or speed_center  Set speed to centering rate (second slowest)'+'\r\n'+
                  'set_speed_guide or speed_guide  Set speed to guiding rate (slowest)'+'\r\n'+'\r\n'+
                  'toggle_precision or precision  Toggle between high and low precision mode' +'\r\n'+'\r\n'+
                  'Enter your commands below.'+'\r\n'+
                  'Insert "exit" to leave the application.'+'\r\n'+'\r\n')
        print(userinfo)