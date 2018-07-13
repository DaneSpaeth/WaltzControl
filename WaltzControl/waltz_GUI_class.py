from tkinter import Tk, Menu, Label, LabelFrame, Button, Checkbutton, Radiobutton, Entry, messagebox, IntVar, StringVar,  Frame, END, W, E
import time
import datetime
import locale
import pathlib

import lx200commands as lx

class WaltzGUI(lx.Lx200Commands):
    def __init__(self, master):
        """Class builds GUI to control Waltz Telescope.
           Uses Tkinter for GUI functionality.
           Inherits from lx200commands.Lx200Commands class.
           This class provides functionality to talk to serial connection 
           using the lx200 protocol.
        """
        
        super().__init__()
        
        self.master = master
        master.title("Waltz Control Panel")
       
        #Store CET and UCT
        self.CET = ''
        self.UTC = ''
        
        #Store if telescope is waiting for slew to finish
        self.waiting=True
        
        ## Building up GUI Widgets ##
        
        #Menubars
        menubar=Menu(self.master)
        
        #Connection menu
        connectionmenu = Menu(menubar, tearoff=0)
        connectionmenu.add_command(label="Open Connection", command=self.open_connection_buttonclick)
        connectionmenu.add_command(label="Close Connection", command=self.close_connection_buttonclick)
        menubar.add_cascade(label="Connection", menu=connectionmenu)
        
        #settings_menu
        settings_menu=Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Enable buttons",command=self.stop_waiting)
        settings_menu.add_command(label="Toggle Precision",command=super().toggle_precision)
        menubar.add_cascade(label="Settings",menu=settings_menu)
        
        
        
        #Pointing_stars_menu
        pointing_stars_menu=Menu(menubar, tearoff=0)
        pointing_stars_menu.add_command(label="Save as Pointing Star", command=self.save_pointing_star)
        menubar.add_cascade(label="Pointing Star", menu= pointing_stars_menu)
        
        #Special_positions_menu
        special_positions_menu=Menu(menubar, tearoff=0)
        special_positions_menu.add_command(label="Slew to Primary Mirror Position",command=self.primary_mirror_pos_buttonclick)
        special_positions_menu.add_command(label="Slew to Secondary Mirror Position",command=self.secondary_mirror_pos_buttonclick)
        special_positions_menu.add_command(label="Slew to Park Position",command=self.park_telescope_buttonclick)
        menubar.add_cascade(label="Special Positions",menu=special_positions_menu)
        
        
        #Show menubar
        self.master.config(menu=menubar)
        
        #Output frame
        output_frame=Frame(master)
        output_frame.grid(row=0,columnspan=3)

        self.LST_label = Label(output_frame,
                               font=('arial', 15, 'bold'),
                               text="LST")
        self.LST_label.grid(row=0,column=0)
        
        self.LST_display = Label(output_frame,
                                 font=('arial', 20, 'bold'),
                                 bg='light green')
        self.LST_display.grid(row=0, column=1,padx=10, pady=10)
        
        self.local_time_label= Label(output_frame,
                              font=('arial', 15, 'bold'),
                              text='LT')
        self.local_time_label.grid(row=0, column=3)
        
        self.local_time_display = Label(output_frame,
                                 font=('arial', 20, 'bold'),
                                 bg='light green')
        self.local_time_display.grid(row=0, column=4,padx=10,pady=10)
        
        self.UTC_label= Label(output_frame,
                              font=('arial', 15, 'bold'),
                              text='UTC')
        self.UTC_label.grid(row=0, column=5)
        
        self.UTC_display = Label(output_frame,
                                 font=('arial', 20, 'bold'),
                                 bg='light green')
        self.UTC_display.grid(row=0, column=6,padx=10,pady=10)
        
        
        
        self.RA_label= Label(output_frame,
                             font=('arial', 15, 'bold'),
                             text= "RA")
        self.RA_label.grid(row=1, column =0)
        
        self.RA_display= Label(output_frame,
                               font=('arial', 20, 'bold'), 
                               bg='light green')
        self.RA_display.grid(row=1, column =1)
        
        self.DEC_label= Label(output_frame,
                              font=('arial', 15, 'bold'),
                              text= "DEC")
        self.DEC_label.grid(row=1, column =3)
        
        self.DEC_display= Label(output_frame,
                                font=('arial', 20, 'bold'),
                                bg='light green')
        self.DEC_display.grid(row=1, column =4)
        
        self.HA_label= Label(output_frame,
                              font=('arial', 15, 'bold'),
                              text= "HA")
        self.HA_label.grid(row=1, column =5)
        
        self.HA_display= Label(output_frame,
                                    font=('arial', 20, 'bold'),
                                    bg='light green')
        self.HA_display.grid(row=1, column=6)
        
        #Interchange_frame
        #To interchange W<->E buttons and N<->S
        self.interchange_frame=Frame(master)
        self.interchange_frame.grid(row=1, column=0,pady=10)
        #Define Variables
        self.inter_WE=IntVar()
        self.inter_NS=IntVar()
        self.inter_NS_checkbox=Checkbutton(self.interchange_frame,
                                           text='N <> S',
                                           font=('arial', 10, 'bold'),
                                           variable=self.inter_NS,
                                           command=self.interchange_north_south)
        self.inter_NS_checkbox.grid(row=0,column=0,sticky='w',pady=5)
        
        
        self.inter_WE_checkbox=Checkbutton(self.interchange_frame,
                                           text='W <> E',
                                           font=('arial', 10, 'bold'), 
                                           variable=self.inter_WE,
                                           command=self.interchange_west_east)
        self.inter_WE_checkbox.grid(row=1,column=0,sticky='w',pady=5)
        
        
        
        #Control frame
        self.control_frame=Frame(master)
        self.control_frame.grid(row=1,column=1,pady=10)


        self.south_button = Button(self.control_frame,
                                   text="S",
                                   font=('arial', 20, 'bold'),
                                   bg='LightGrey',
                                   height = 1, 
                                   width = 2)
        self.south_button.grid(row=0,column=1)
        
        self.west_button = Button(self.control_frame,
                                  text="W",
                                  font=('arial', 20, 'bold'),
                                  bg='LightGrey',
                                  height = 1,
                                  width = 2)
        self.west_button.grid(row=1,column=0)
        
        self.east_button = Button(self.control_frame,
                                  text="E",
                                  font=('arial', 20, 'bold'),
                                  bg='LightGrey',
                                  height = 1,
                                  width = 2)
        self.east_button.grid(row=1,column=2)
        
        
        self.north_button = Button(self.control_frame,
                                   text="N",
                                   font=('arial', 20, 'bold'),
                                   bg='LightGrey',
                                   height = 1,
                                   width = 2)
        self.north_button.grid(row=2,column=1)
        
        self.stop_button = Button(self.control_frame,
                                  text="STOP",
                                  font=('arial',20, 'bold'),
                                  fg='White',
                                  bg='Red',
                                  activeforeground='Red',
                                  activebackground='White',
                                  command=super().stop_at_current_pos)
        self.stop_button.grid(row=3,column=0, columnspan=3, pady=10)

        #Radiobutton frame
        self.radiobutton_frame=Frame(master)
        self.radiobutton_frame.grid(row=1,column=2,pady=10)
        
        
        radiobutton_parameters=[('Slew',0,self.set_speed_max),
                                ('Find',1, self.set_speed_find),
                                ('Center',2, self.set_speed_center),
                                ('Guide',3, self.set_speed_guide)]
        
        self.speed=StringVar()
        #Initialize speed to guiding speed
        self.speed.set('Guide')
        
        for keyword, position, execute in radiobutton_parameters:
            self.speed_radiobutton= Radiobutton(self.radiobutton_frame,
                                                text=keyword,
                                                variable=self.speed,
                                                value=keyword,
                                                command=execute,
                                                font=('arial', 10, 'bold'))
            self.speed_radiobutton.grid(row=position,column=0,sticky=W)
        
        #Options Frame
        self.options_frame=Frame(master)
        self.options_frame.grid(row=0,column=3,padx=20)
     
        self.sync_button = Button(self.options_frame,
                                       text="Synchronize \n with Target",
                                       font=('arial', 12, 'bold'),
                                       bg='LightGrey',
                                       command=self.sync_yes_no,
                                       state='disabled')
        self.sync_button.grid(row=0,column=0,padx=5)
        
        
        
        
        #Target Frame
        self.target_frame=LabelFrame(master,
                                text='Select Target (apparent position)',
                                font=('arial', 15))
        self.target_frame.grid(row=1,rowspan=1,column=3,padx=20)
        
        self.HIP_label = Label(self.target_frame,
                               font=('arial', 15),
                               text="Hipparcos")
        self.HIP_label.grid(row=0,column=0)
        
        self.HIP_entry= Entry(self.target_frame,
                              font=('arial', 15))
        self.HIP_entry.grid(row=0, column=1,pady=10)
        
        
        self.target_ra_label = Label(self.target_frame,
                                     font=('arial', 15),
                                     text="Target RA")
        self.target_ra_label.grid(row=1,column=0)
        
        self.target_ra_entry= Entry(self.target_frame,
                                    font=('arial', 15))
        self.target_ra_entry.grid(row=1, column=1,pady=10)

        
        self.target_dec_label = Label(self.target_frame,
                                      font=('arial', 15),
                                      text="Target DEC")
        self.target_dec_label.grid(row=2,column=0)
        
        self.target_dec_entry= Entry(self.target_frame,
                                     font=('arial', 15))
        self.target_dec_entry.grid(row=2, column=1,pady=10)
        
        self.slew_target_button = Button(self.target_frame,
                                         text="Slew to Target",
                                         font=('arial', 15),
                                         bg='LightGrey',
                                         state='disabled',
                                         command=self.slew_to_target_buttonclick)
        self.slew_target_button.grid(row=3,columnspan=2)
        
        #At first check if serial connection is open (also contains initial commands)
        self._respond_to_connection_state()
        
        #Message box for Warning
        caution=("CAUTION: THIS IS A FIRST ATTEMPT TO CONTROL THE WALTZ TELESCOPE.\n"+
                 "BAD INPUTS OR CRASHES OF THE PROGRAM COULD BE HARMFUL TO THE TELESCOPE.\n"+
                 "DO NOT USE THIS PROGRAM ALONE AND ALWAYS PREPARE FOR STOPING MOVEMENTS "+ 
                 "OF THE TELESCOPE VIA THE EMERGENCY STOPS IN THE DOME!")
        messagebox.showwarning("Warning",message=caution,parent=master)
    
    
    def close_connection_buttonclick(self):
        """ Closes the connection to serial and responds properly to it
        """
        #First check the connection state
        if self.connected==False:
            print('Connection already closed')
            return 0
        #Close serial connection
        super().close_connection()
        #Check if connection is realy closed
        #this will set self.connected=False
        #Respond to closed connection
        self._respond_to_connection_state()
        
        
    def open_connection_buttonclick(self):
        """ Closes the connection to serial and responds properly to it
        """
        #First check the connection state
        if self.connected==True:
            print('Connection already open')
            return 0
        #Open serial connection
        super().open_connection()
        #Respond to open connection
        self._respond_to_connection_state()
    
    
    def _start_commands(self):
        """ Contains all functions to be executed at start of program.
        """
        
        #Commands to be executed even without connection
        self.refresh_times()
        
        #If connection is not open close program
        if not self.connected:
            return 0
        
        #Commands for initial settings
        self.set_speed_guide()
        #This is the StringVar defining which initial setting the speed Radiobuttons have
        self.speed.set('Guide')
        
        #Commands to be executed all the time (if connection is open)
        self.display_coordinates()
        
        #Check for format of coordinates and toggle automatically
        #We always want format DEC=dd mm ss
        if len(self.dec)==7:
            super().toggle_precision()
    def _respond_to_connection_state(self):
        """ Checks connection to serial port.
            Print Warning if not and closes program.
            Enables and binds all buttons if connection is set.
        """
        #If connection to Waltz is closed
        if not self.connected:
            #Disable all buttons
            self.disable_all_buttons()
            self.stop_button.config(state='disabled')
            #Message box if serial connection is not open
            caution=("Warning: No Connection to Waltz")
            messagebox.showwarning("Warning",message=caution,parent=self.master)
            #Start Commands 
            #(it will take care that only the ones that do not use the serial connection are executed)
            self._start_commands()
        if self.connected:
            #Enable all buttons
            self.enable_all_buttons()
            #Start Commands
            self._start_commands()
                    
    def refresh_times(self):
        """ Refreshs all times (LST, LT, UTC)
        
            Introduced to have only one function call in the background.
            Better to syn clocks
        """
        #Refresh individual times
        self.refresh_LST()
        self.refresh_local_time()
        self.refresh_UTC()
        
        #Also refresh hour_angle synced to times because it will change in the same pace
        super().calculate_hour_angle()
        self.HA_display.config(text=self.ha)
        #Calls itself all 200 ms
        self.master.after(200, self.refresh_times)
    
    def refresh_local_time(self):
        """ Displays the current Central Eruopean Time on CET_display.
            Calls itself all 200ms to refresh time.
        """
        
        # get the current local time from the PC
        local_time_now = time.strftime('%H:%M:%S')
        # if time string has changed, update it
        if local_time_now != self.CET:
            self.local_time = local_time_now
            self.local_time_display.config(text=self.local_time)
    
    def refresh_LST(self):
        """ Displays the current Local Sidereal Time on LST_display.
            Calls itself all 200ms to refresh time.
        """
        super().get_LST()
        self.LST_display.config(text=self.LST)
        
    def refresh_UTC(self):
        """ Displays the current Coordinated Universal Time on UTC_display.
            Calls itself all 200 ms to refresh time.
        """
        #Get current UTC from datetime
        UTC_now= datetime.datetime.utcnow()
        UTC_now=UTC_now.strftime("%H:%M:%S")
        #Check if UTC has changed since last call
        if UTC_now != self.UTC:
            #Save current UTC in self.UTC
            self.UTC = UTC_now
            #Display UTC
            self.UTC_display.config(text=self.UTC)
    
    def display_coordinates(self):
        """ Displays Right ascension and Declination.
            
            Hour angle will be displayed synced to times.
            It should change at the same rate as LST.
            Look at refresh_times()
        """
        
        #If connection is not open close program
        if not self.connected:
            return 0
        
        self.get_coordinates()
        self.RA_display.config(text=self.ra)
        self.DEC_display.config(text=self.dec)
        if not self.connected:
            self._respond_to_connection_state()
        self.master.after(500,self.display_coordinates)
        
    def interchange_west_east(self):
        """Interchanges West and East Buttons.
        """
        #self.inter_WE.get() will return 1 if box is checked and 0 if not
        if self.inter_WE.get():
            #Grid Positions if checkbutton is checked
            self.west_button.grid(row=1,column=2)
            self.east_button.grid(row=1,column=0)  
        if not self.inter_WE.get():
            #Grid Position in default state
            self.west_button.grid(row=1,column=0)
            self.east_button.grid(row=1,column=2)
            
    def interchange_north_south(self):
        """Interchanges North and South Buttons.
        """
        #self.inter_WE.get() will return 1 if box is checked and 0 if not
        if self.inter_NS.get():
            #Grid Positions if checkbutton is checked
            self.south_button.grid(row=2,column=1)
            self.north_button.grid(row=0,column=1)  
        if not self.inter_NS.get():
            #Grid Position in default state
            self.south_button.grid(row=0,column=1)
            self.north_button.grid(row=2,column=1)
            
    def start_move_west_buttonclick(self, event):
        """ Sends move west LX200 command to serial connection
        """
        super().start_move_west()
        
    def stop_move_west_buttonclick(self, event):
        """ Sends stop move west LX200 command to serial connection
        """
        super().stop_move_west()
        
    def start_move_north_buttonclick(self, event):
        super().start_move_north()
        
    def stop_move_north_buttonclick(self, event):
        super().stop_move_north()
        
    def start_move_south_buttonclick(self, event):
        super().start_move_south()
        
    def stop_move_south_buttonclick(self, event):
        super().stop_move_south()
        
    def start_move_east_buttonclick(self, event):
        super().start_move_east()
        
    def stop_move_east_buttonclick(self, event):
        super().stop_move_east()
        
    def slew_to_target_buttonclick(self):
        """Slews to target.
           Target must be set before via set_target_dec_from_string and set_target_ra_from_string
        """
        #Slew to target and wait for slew to finish
        super().slew_to_target()
        self.wait_for_slew_finish()
        
        #After slewing (and if something went wrong):
        #Set all valid_target entries to 0 (controller won't let you slew to
        #the same coordinates twice
        self.valid_target=[0,0]
        self.slew_target_button.config(state='disabled')
    
    #def continue_slew(self,initial_target_ra, initial_target_dec):
        """ Continues slewing after possible initial slew to medium position.
            Performs slewing if no slew to medium position is necessary.
        """
        #Check if slew is finished. Default Value of slew_done=True,
        #so it will also be True if no slew to medium position was necessary.)
        #if self.slew_done:
            #Set the initial target coordinates as normal target coordinates again
            #super().set_target_ra_from_string(initial_target_ra)
            #super().set_target_dec_from_string(initial_target_dec)
            #Slew to target
            #super().slew_to_target()
            #Wait for the slew to finish (disables all buttons etc.)
            #self.wait_for_slew_finish()
        #else:
            #If previous slew is not finished the funcion will call itself every second.
            #self.master.after(1000, self.continue_slew, initial_target_ra, initial_target_dec)
        
    def park_telescope_buttonclick(self,counter=1,park=True):
        """Parks telescope and waits for slew to finish.
           
           counter counts if parking is executed the first or 
           second time.
           park specifies if controller gets a parking command 
           or if the function just waits until first slew has finished.
        """
        #We need to call park telescope twice 
        #because the tracking will change RA while DEC is still adjusting
        #Park telescope for the first time
        if counter==1:
            #If parking is activated
            if park:
                print('Slew to Park Position the first time')
                #Slew telescope to parking position
                super().park_telescope()
            #Start waiting: Call wait_for_slew_finish with call_itself=False
            #So the funtion will just check if slew has finished
            if not self.wait_for_slew_finish(call_itself=False):
                #If slew has not yet finished
                print('Waiting for First Parking to finish')
                #Call the park funtion after 1 sec with counter=1 and slew=False
                #So it will be in counter=1 loop but will not send 
                #a park command to the controller
                self.master.after(1000,self.park_telescope_buttonclick,
                                  1,False)
                return 0
            else:
                #If slewing has finished
                #Disable all buttons (need because it will otherwise wait
                #for one second until it disables again)
                self.disable_all_buttons()
                print('Finished First Parking')
                #Call park function again after 1 second but enter counter=2 loop
                #Also activate parking again with park=True
                #Useful to wait one second as safetiy that slewing has stopped
                self.master.after(1000,self.park_telescope_buttonclick,
                                  2,True)
                return 0
        #Second Parking loop
        if counter==2:
            if park:
                #If parking is activated
                print('Slew to Park Position the second time')
                #Slew telescope to parking position
                super().park_telescope()
                #Wait again as above. But call counter=2 fpr second parking loop
            if not self.wait_for_slew_finish(call_itself=False):
                print('Waiting for Second Parking to finish')
                self.master.after(1000,self.park_telescope_buttonclick,
                                  2,False)
                return 0
            else:
                #When slewing is done
                print('Finished Second Parking')
                #Show message box to tell user to shut off the controller
                message=("Turn off the telescope controller to stop tracking"+
                 " and remain in park position!")
                messagebox.showinfo("Information",message=message,parent=self.master)
                return 0 
        
    def primary_mirror_pos_buttonclick(self):
        """Slew Telescope to Primary Mirror Cover Position.
        
           Uses LX200Commands primary_mirror_pos.
        """
        super().primary_mirror_pos()
        self.wait_for_slew_finish()
        
    def secondary_mirror_pos_buttonclick(self):
        """Slew Telescope to Secondary Mirror Cover Position.
        
           Uses LX200Commands secondary_mirror_pos.
        """
        super().secondary_mirror_pos()
        self.wait_for_slew_finish()
      
      
    def set_hip_target_from_entry(self, event):
        """ Gets a HIP number from the HIP_entry widget and calculates the coordinates.
            Sets these coordinates as target_ra and target_dec 
            and displays them in the corresponding entry widgets.
        """
        hip_nr=self.HIP_entry.get()
        super().set_hip_target(hip_nr)
        self.target_ra_entry.delete(0, END)
        self.target_ra_entry.insert(0, self.target_ra)
        self.target_dec_entry.delete(0, END)
        self.target_dec_entry.insert(0, self.target_dec)
        
        #Check if there are valid coordinates set and enable slew button
        if 0 not in self.valid_target:
            self.slew_target_button.config(state='normal')
            self.sync_button.config(state='normal')
           
    def set_target_ra_from_entry(self, event):
        """ Gets a ra input from the target_ra_entry widget and sets it as target_ra.
            Accepted formats include hh mm ss and hh mm.t.
            Clears text of HIP_entry widget.
        """
        ra_input=self.target_ra_entry.get()
        super().set_target_ra_from_string(ra_input)
        self.target_ra_entry.delete(0, END)
        self.target_ra_entry.insert(0, self.target_ra)
        self.HIP_entry.delete(0, END)
        
        #Check if there are valid coordinates set and enable slew button
        if 0 not in self.valid_target:
            self.slew_target_button.config(state='normal')
        
    def set_target_dec_from_entry(self, event):
        """ Gets a dec input from the target_dec_entry widget and sets it as target_ra.
            Accepted formats include dd mm ss and dd mm.
            Clears text of HIP_entry widget.
        """
        dec_input=self.target_dec_entry.get()
        super().set_target_dec_from_string(dec_input)
        self.target_dec_entry.delete(0, END)
        self.target_dec_entry.insert(0, self.target_dec)
        self.HIP_entry.delete(0, END)
        
        #Check if there are valid coordinates set and enable slew button
        if 0 not in self.valid_target:
            self.slew_target_button.config(state='normal')
        
    def sync_yes_no(self):
        """Displays yes/no message if sync_button is clicked on.
        """
        result=messagebox.askyesno("Synchroniziation", 
                                     "Do you really want to synchronize coordinates with target coordinates?")
        if result:
            self.sync_on_target_buttonclick()
        
    def sync_on_target_buttonclick(self):
        """Gets target coordinates from entries.
           Synchronizes coordinates with target coordinates.
           In Case of Hipparcos target it will recalculate target coordinates
           at time of synchronization.
        """
        hip_nr=self.HIP_entry.get()
        if hip_nr!='':
            super().sync_on_hip(hip_nr)
            self.target_ra_entry.delete(0, END)
            self.target_ra_entry.insert(0, self.target_ra)
            self.target_dec_entry.delete(0, END)
            self.target_dec_entry.insert(0, self.target_dec)
        else:
            #If no Hip target_ get coordinates from entries
            #None refers to no event (such as Return)
            self.set_target_ra_from_entry(None)
            self.set_target_dec_from_entry(None)
            if hip_nr=='' and self.target_ra and self.target_dec:
                super().sync_on_coordinates()
            else:
                print('No valid coordinates set. Synchronisation stopped')
        #After sync (and if something went wrong):
        #Set all valid_target entries to 0 (controller won't let you slew to
        #the same coordinates twice
        self.valid_target=[0,0]
        self.slew_target_button.config(state='disabled')
            
    def wait_for_slew_finish(self,call_itself=True):
        """Waits until coordinates equal target coordinates within tolerance.
           Disables all (except STOP) buttons until target coordinates are reached.
           call_itself determines if funtion will call itself after 1 second.
           This is very useful to set to False if you want to call waiting from
           different function that should pause until waiting is over.
           
           Can be stopped by stop_waiting.
        """
        #Disable all buttons
        self.disable_all_buttons()
        #Check if slew has finished or self.stop_waiting parameter=True
        #Enable buttons if so.
        #self.stop_waiting parameter can be set by button in menubar
        #Then break the loop
        if super().slew_finished():
            #Enable all buttons again
            self.enable_all_buttons()
            return True
        else:
            #If variable call_itself is true
            #Calls itself after 1 second.
            #After call is asigned to global variable waiting 
            #to stop it via stop_waiting.
            if call_itself:
                global waiting
                waiting=self.master.after(1000,self.wait_for_slew_finish)
            return False
    
    def stop_waiting(self):
        """Stops Waiting for slew to finish and enables all buttons.
        
           Can be called in the menu.
        """
        #First disable all buttons to avoid binding events more than once.
        self.disable_all_buttons()
        #Enable all buttons 
        self.enable_all_buttons()
        #And try to stop waiting if waiting is going on.
        try:
            self.master.after_cancel(waiting)
        except NameError:
            return 0
        
    def delete_entries(self,event):
        """ Deletes entries of target_ra and target_dec.
        
            Used when entering new Hipparcos Number.
        """
        self.target_ra_entry.delete(0,END)
        self.target_dec_entry.delete(0,END)
            
        
    def disable_all_buttons(self):
        """ Disables all buttons and unbinds all bindings.
            Except of Stop Button
        """
        #Disable all buttons 
        #We also need to unbind the buttons which are called by events instead of commands
        for child in self.control_frame.winfo_children():
            child.config(state='disabled')
            child.unbind("<ButtonPress-1>")
            child.unbind("<ButtonRelease-1>")
        #Enable Stop Button again. It should always be enabled.
        self.stop_button.config(state='normal')
        
        #Disable and unbind entry widgets in target_frame
        for child in self.target_frame.winfo_children():
            child.config(state='disabled')
            child.unbind("<Return>")
            child.unbind("<Tab>")
        
        
        self.sync_button.config(state='disabled')
        
        #Radiobuttons
        for child in self.radiobutton_frame.winfo_children():
            child.config(state='disabled')
        
    def enable_all_buttons(self):
        """ Enables all buttons and binds all bindings.
            Except of Stop Button.
            All bindings are defined here, except of commands of buttons.
        """
        #Disable all buttons 
        #We also need to bind the buttons which are called by events instead of commands
        for child in self.control_frame.winfo_children():
            child.config(state='normal')
        #Add the bindings manually
        self.north_button.bind("<ButtonPress-1>",self.start_move_north_buttonclick)
        self.north_button.bind("<ButtonRelease-1>",self.stop_move_north_buttonclick)
        self.west_button.bind("<ButtonPress-1>",self.start_move_west_buttonclick)
        self.west_button.bind("<ButtonRelease-1>",self.stop_move_west_buttonclick)
        self.south_button.bind("<ButtonPress-1>",self.start_move_south_buttonclick)
        self.south_button.bind("<ButtonRelease-1>",self.stop_move_south_buttonclick)
        self.east_button.bind("<ButtonPress-1>",self.start_move_east_buttonclick)
        self.east_button.bind("<ButtonRelease-1>",self.stop_move_east_buttonclick)
        
        
        self.sync_button.config(state='normal')
        
        #Enable and bind entry widgets in target_frame
        for child in self.target_frame.winfo_children():
            child.config(state='normal')
        #Do not enable slew button
        self.slew_target_button.config(state='disabled')
        #Add the bindings manually
        #When entering any new number or char (also when deleting),
        #the entries of target_ra and target_dec should be deleted
        #Important to bind Return and Tab after this first binding to override this functionality
        #Otherwise it would also just delete the entries
        self.HIP_entry.bind("<Key>",
                            self.delete_entries,add='+')
        self.HIP_entry.bind("<Return>",
                            self.set_hip_target_from_entry, add="+")
        self.HIP_entry.bind("<Tab>",
                            self.set_hip_target_from_entry, add="+")

        
        self.target_ra_entry.bind("<Return>",
                                  self.set_target_ra_from_entry, add="+") 
        self.target_ra_entry.bind("<Tab>",
                                  self.set_target_ra_from_entry,add="+")
        
        
        self.target_dec_entry.bind("<Return>",
                                   self.set_target_dec_from_entry, add="+")
        self.target_dec_entry.bind("<Tab>", 
                                   self.set_target_dec_from_entry, add="+")
        
        
        #Radiobuttons
        for child in self.radiobutton_frame.winfo_children():
            child.config(state='normal')
    
    def save_pointing_star(self):
        """ Saves Pointings Stars Information to file.
            
            Takes Hipparcos Number, RA, DEC LST and Date and saves to file.
            
            Also Saves Hipparcos Number, RA, DEC, HA, 
            target_ra, target_dec, LST, UTC and Date to second file.
            This could lead to potentially new system of pointing_star data.
            This could be easier to handle.
            Not done yet.
        """
        ### Traditional File ###
        try:
            hipparcos=self.HIP_entry.get()
            #Need integer to catch errors and for formatting
            hipparcos=int(hipparcos)
            #Format Hipparcos Number to 000123
            hip_pointing="{:06d}".format(hipparcos)
        except ValueError:
            print('Invalid Hiparcos number')
            return 0
        
        #Format RA to hh mm ss
        (RA_hours,h,rest)=self.ra.partition('h')
        (RA_min,m,rest)=rest.partition('m')
        (RA_sec,s,rest)=rest.partition('s')
        RA_pointing="{} {} {}".format(RA_hours, RA_min, RA_sec)
        
        #Format DEC to +dd mm ss
        (DEC_deg,grad,rest)=self.dec.partition('°')
        (DEC_min,m,rest)=rest.partition("'")
        (DEC_sec,s,rest)=rest.partition('"')
        DEC_pointing="{} {} {}".format(DEC_deg, DEC_min, DEC_sec)
        
        #Format LST to hh mm ss
        (LST_hours,h,rest)=self.LST.partition(':')
        (LST_min,m,rest)=rest.partition(':')
        (LST_sec,s,rest)=rest.partition(':')
        LST_pointing="{} {} {}".format(LST_hours, LST_min, LST_sec)
        
        #Get Date in Format dd.mm.yyyy (using locale module)
        today = datetime.date.today()
        Date_pointing=today.strftime('%d.%m.%Y')
        
        line="{}    {}    {}    {}    {}\n".format(hip_pointing,
                                                 RA_pointing,
                                                 DEC_pointing,
                                                 LST_pointing,
                                                 Date_pointing)
        #Filename and path using pathlib module
        #File is in parrent_directory/pointing_stars/pointings_stars.txt
        current_path=pathlib.Path.cwd()
        parrent_path=current_path.parent
        file_path=parrent_path / 'pointing_stars' / 'pointing_stars.txt'
        #With automatically closes the file in the end
        with open(str(file_path), 'a') as ps_file:
            print('Saving pointing star to (old format) file')
            ps_file.write(line)
            
            
        ### New Format File ###
        line=("{}    {}    {}    {}    {}    {}    {}    {}    {}"
            "    {}    {}    {}    {}    {}    {}\n")
        line=line.format(hip_pointing,
                         self.ra,
                         self.ra_float,
                         self.dec,
                         self.dec_float,
                         self.ha,
                         self.ha_float,
                         self.target_ra,
                         self.target_ra_float,
                         self.target_dec,
                         self.target_dec_float,
                         self.target_ha_float,
                         self.LST,
                         self.UTC,
                         Date_pointing)
        
        #Filename and path using pathlib module
        #File is in parrent_directory/pointing_stars/pointings_stars_new_format.txt
        current_path=pathlib.Path.cwd()
        parrent_path=current_path.parent
        file_path=parrent_path / 'pointing_stars' / 'pointing_stars_new_format.txt'
        #With automatically closes the file in the end
        with open(str(file_path), 'a') as ps_file:
            print('Saving pointing star to (new format) file')
            ps_file.write(line)
            
