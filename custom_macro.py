# Modifications to Creality K1 Custom Macros
# by Flint Million (flint.million@mnsu.edu)

# This file is modified from GPL code and hence is distributed
# under the terms of the GPL v3 or later.

import time

class CUSTOM_MACRO:

    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.pheaters = None
        self.heater_hot = None
        self.extruder_temp=None
        self.bed_temp=None
        self.prtouch = None

        # Registers the Creality custom macros as GCODE commands
        # Updated by fmillion-mnsu - You can now add new commands by simply
        # adding a function to the class called cmd_WHATEVER, setting a docstring
        # on that fucntion, and adding WHATEVER to this list.
        # TODO: add self-discovery by looking for commands as functions starting with cmd_
        custom_macro_list = [
            "CX_PRINT_LEVELING_CALIBRATION",
            "CX_CLEAN_CALIBRATION_FLAGS",
            "CX_PRINT_DRAW_ONE_LINE",
            "CX_ROUGH_G28",
            "CX_NOZZLE_CLEAR",
            "SET_QMODE_FLAG"
        ]
        for cm in custom_macro_list:
            self.gcode.register_command(cm, getattr(self, f"cmd_{cm}"), desc=getattr(self, f"cmd_{cm}").__doc__)
        
        # Set values on self
        self.default_extruder_temp = config.getfloat("default_extruder_temp", default=220.0)
        self.default_bed_temp = config.getfloat("default_bed_temp", default=50.0)
        self.g28_ext_temp = config.getfloat("g28_ext_temp", default=200.0)
        self.nozzle_clear = config.getboolean('nozzle_clear', True)
        self.calibration = config.getint('calibration', default=0)
        self.leveling_calibration = 0
        self.qmode_flag = 0
        
    def get_status(self, eventtime):
        return {
            'leveling_calibration': self.leveling_calibration,
            'default_extruder_temp': self.default_extruder_temp,
            'default_bed_temp': self.default_bed_temp,
            'g28_ext_temp': self.g28_ext_temp,
            'qmode_flag': self.qmode_flag
        }

    def cmd_CX_PRINT_LEVELING_CALIBRATION(self, gcmd):
        """Start Print function,three parameter:EXTRUDER_TEMP(180-300),BED_TEMP(0-100),CALIBRATION(0 or 1)"""
        self.gcode.run_script_from_command('CHECK_BED_MESH AUTO_G29=1')
        pass

    def cmd_CX_CLEAN_CALIBRATION_FLAGS(self, gcmd):
        """Clean calibration flags"""
        self.leveling_calibration = 0
        pass

    def cmd_CX_PRINT_DRAW_ONE_LINE(self, gcmd):
        """Draw primer line before printing"""
        self.gcode.respond_info("Running macro: CX_PRINT_DRAW_ONE_LINE")

        # If we have NoneType on extruder/bed temps, get them as we do in CX_ROUGH_G28.
        # Workaround to allow you to manually prepare the printer using PRINT_PREPARED.

        if self.extruder_temp is None:
            self.extruder_temp = gcmd.get_float('EXTRUDER_TEMP', default=self.default_extruder_temp, minval=180.0, maxval=320.0)
        if self.bed_temp is None:
            self.bed_temp = gcmd.get_float('BED_TEMP', default=self.default_bed_temp, minval=0.0, maxval=130.0)

        # Move the extruder to the starting position
        self.gcode.run_script_from_command('G28 X Y')
        self.gcode.run_script_from_command('M83')
        self.gcode.run_script_from_command('G1 X10 Y10 Z2 F6000')
        self.gcode.run_script_from_command('G1 Z0.1 F600')
        
        # Wait for printer to reach print temperature
        self.pheaters = self.printer.lookup_object('heaters')
        self.heater_hot = self.printer.lookup_object('extruder').heater
        #self.gcode.respond_info("can_break_flag = %d" % (self.pheaters.can_break_flag))
        self.gcode.run_script_from_command('M104 S%d' % (self.extruder_temp))
        self.gcode.run_script_from_command('M140 S%d' % (self.bed_temp))
        self.gcode.respond_info(f"CX_PRINT_DRAW_ONE_LINE: Waiting for printing temperature... (extruder={self.extruder_temp}, bed={self.bed_temp})")
        self.pheaters.set_temperature(self.heater_hot, self.extruder_temp, True)
        #self.gcode.respond_info("can_break_flag = %d" % (self.pheaters.can_break_flag))
        while self.pheaters.can_break_flag == 1:
            time.sleep(1)
        #self.gcode.respond_info("can_break_flag = %d" % (self.pheaters.can_break_flag))
        if self.pheaters.can_break_flag == 3:
            self.pheaters.can_break_flag = 0
            self.gcode.respond_info("CX_PRINT_DRAW_ONE_LINE: Printing temperature achieved.")
            #self.gcode.respond_info("can_break_flag is 3")
            gcodes = [
                'G21',
                'G1 F2400 E-0.5',
                'SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=5',
                'M204 S12000',
                'SET_VELOCITY_LIMIT ACCEL_TO_DECEL=6000',
                # 'SET_PRESSURE_ADVANCE ADVANCE=0.04',
                # 'SET_PRESSURE_ADVANCE SMOOTH_TIME=0.04',
                'M220 S100',
                'M221 S100',
                'G1 Z2.0 F1200',
                'G1 X0.1 Y20 Z0.3 F6000.0',
                'G1 X0.1 Y180.0 Z0.3 F3000.0 E10.0',
                'G1 X0.4 Y180.0 Z0.3 F3000.0',
                'G1 X0.4 Y20.0 Z0.3 F3000.0 E10.0',
                'G1 Y10.0 F3000.0',
                'G1 Z2.0 F600.0',
                'G1 Z0.3 F600.0',
                'G1 Z2.0 F600.0',
                'G1 F2400 E-0.5', # retract a bit of filament to reduce oozing
                # 'G1 X0.4 Y10.0 Z0.3 F6000.0',
                'M82',
                'G92 E0',
                'G1 F12000',
                'G21',
            ]
            for gc in gcodes:
                self.gcode.run_script_from_command(gc)

        self.gcode.respond_info("Macro FINISHED: CX_PRINT_DRAW_ONE_LINE")

    def cmd_CX_ROUGH_G28(self, gcmd):
        "rough G28"
        self.gcode.respond_info("Running macro: CX_ROUGH_G28")
        self.extruder_temp = gcmd.get_float('EXTRUDER_TEMP', default=self.default_extruder_temp, minval=180.0, maxval=320.0)
        #self.g28_ext_temp = self.extruder_temp - 70
        if self.g28_ext_temp > 200.0:
            self.g28_ext_temp = 200.0

        self.gcode.respond_info(f"CX_ROUGH_G28: g28_ext_temp = {self.g28_ext_temp}")
        try:
            self.prtouch = self.printer.lookup_object('prtouch_v2')
        except:
            self.prtouch = self.printer.lookup_object('prtouch')
            gcmd.respond_info("CX_ROUGH_G28: prtouch (not v2)")
        self.prtouch.change_hot_min_temp(self.g28_ext_temp)
        self.bed_temp = gcmd.get_float('BED_TEMP', default=self.default_bed_temp, minval=0.0, maxval=130.0)
        self.leveling_calibration = gcmd.get_int('LEVELING_CALIBRATION', default=1, minval=0, maxval=1)
        self.gcode.run_script_from_command('M104 S%d' % (self.g28_ext_temp))
        self.gcode.run_script_from_command('M140 S%d' % (self.bed_temp))
        self.gcode.run_script_from_command('M204 S500')
        self.gcode.run_script_from_command('G28')
        # self.gcode.run_script_from_command('NOZZLE_CLEAR HOT_MIN_TEMP=%d HOT_MAX_TEMP=%d BED_MAX_TEMP=%d' % (self.g28_ext_temp, self.extruder_temp - 20, self.bed_temp))

        self.gcode.respond_info("Macro FINISHED: CX_ROUGH_G28")

    def cmd_CX_NOZZLE_CLEAR(self, gcmd):
        "nozzle clear with temperature"
        self.gcode.respond_info("Running macro: CX_NOZZLE_CLEAR")
        self.gcode.run_script_from_command('NOZZLE_CLEAR HOT_MIN_TEMP=%d HOT_MAX_TEMP=%d BED_MAX_TEMP=%d' % (self.g28_ext_temp, self.extruder_temp - 20, self.bed_temp))
        pass

    def cmd_SET_QMODE_FLAG(self, gcmd):
        "set qmode flag"
        self.qmode_flag =  gcmd.get_int('FLAG', default=1, minval=0, maxval=1)
        gcmd.respond_info("SET_QMODE_FLAG: self.qmode_flag={}".format(self.qmode_flag))
        import json, logging
        try:
            print_stats = self.printer.lookup_object('print_stats')
            v_sd = self.printer.lookup_object('virtual_sdcard')
            speed_mode_path = v_sd.speed_mode_path
            if print_stats.state == "printing" and self.qmode_flag == 1:
                result = {}
                result["speed_mode"] = 2
                with open(speed_mode_path, "w") as f:
                    f.write(json.dumps(result))
                    f.flush()
        except Exception as err:
            err_msg = "cmd_SET_QMODE_FLAG err %s" % str(err)
            logging.error(err_msg)
        pass

def load_config(config):
    return CUSTOM_MACRO(config)
