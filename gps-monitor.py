#!/usr/bin/python2
import serial
import sys, os
import time
import config


from time import gmtime, strftime
timestr = strftime("%Y%m%d-%H%M", gmtime())
LOG_FILE = "/run/shm/gps-monitor/gps-monitor-" + timestr + ".log"
#LOG_FILE = "/run/shm/gps-monitor/gps-monitor-20141006-060001.log"

# use different logfile is passed as command line argument
if len(sys.argv) > 1:
  LOG_FILE = sys.argv[1]
print "LOG_FILE=" + LOG_FILE

# save current process ID - to kill it on the next launch
import os
# print "os.getpid=", os.getpid()
open("./monitor.pid", 'w').write(str(os.getpid()))

GPS_PORT = config.GPS_PORT

avg_latitude = config.avg_latitude
avg_longitude = config.avg_longitude
avg_altitude = config.avg_altitude

#$GPTXT,01,01,02,u-blox ag - www.u-blox.com*50
#$GPTXT,01,01,02,HW  UBX-G60xx  00040007 FF7FFFFFp*53
#$GPTXT,01,01,02,ROM CORE 7.03 (45969) Mar 17 2011 16:18:34*59
#$GPTXT,01,01,02,ANTSUPERV=AC SD PDoS SR*20
#$GPTXT,01,01,02,ANTSTATUS=DONTKNOW*33

# http://us.cactii.net/~bb/gps.py
def gps_DegreeConvert(degrees):
  deg_min, dmin = degrees.split('.')
  degrees = int(deg_min[:-2])
  minutes = float('%s.%s' % (deg_min[-2:], dmin))
  decimal = degrees + (minutes/60)
  return decimal
  

# function to send commands to the GPS 
def gps_sendUBX(MSG, length):
  GPS = serial.Serial(GPS_PORT, 9600, timeout=1)
  GPS.flush()
  time.sleep(0.05)
  
  # mylog("Sending UBX Command: ")
  ubxcmds = ""
  for i in range(0, length):
    GPS.write(chr(MSG[i])) #write each byte of ubx cmd to serial port
    ubxcmds = ubxcmds + str(MSG[i]) + " " # build up sent message debug output string
  GPS.write("\r\n") #send newline to ublox
  # mylog(ubxcmds) #print debug message
  # mylog("UBX Command Sent...")
  
  GPS.flush()
  time.sleep(0.05)
  
  n = GPS.inWaiting()
  # print "gps_sendUBX:", n
  if n:
    GPS.read(n)
  
  GPS.close()

# function to send commands to the GPS 
def gps_sendNMEA(MSG):
  GPS = serial.Serial(GPS_PORT, 9600, timeout=1)
  GPS.flush()
  time.sleep(0.05)
  
  GPS.write(MSG + "\r\n")
  
  GPS.flush()
  time.sleep(0.05)
  
  n = GPS.inWaiting()
  # print "gps_sendNMEA:", n
  if n:
    GPS.read(n)
  
  GPS.close()



def gps_setup():
  print("Setting up GPS..")
  
  # turn off unneeded NMEA sentences
  # setNMEAoff = bytearray.fromhex("B5 62 06 00 14 00 01 00 00 00 D0 08 00 00 80 25 00 00 07 00 01 00 00 00 00 00 A0 A9")
  # gps_sendUBX(setNMEAoff, len(setNMEAoff))
  setNMEAoff = "$PUBX,40,GLL,0,0,0,0*5C"
  gps_sendNMEA(setNMEAoff)
  setNMEAoff = "$PUBX,40,ZDA,0,0,0,0*44"
  gps_sendNMEA(setNMEAoff)
  setNMEAoff = "$PUBX,40,VTG,0,0,0,0*5E"
  gps_sendNMEA(setNMEAoff)
  setNMEAoff = "$PUBX,40,GSV,0,0,0,0*59"
  gps_sendNMEA(setNMEAoff)
  setNMEAoff = "$PUBX,40,GSA,0,0,0,0*4E"
  gps_sendNMEA(setNMEAoff)
  # setNMEAoff = "$PUBX,40,GGA,0,0,0,0*5A"
  # gps_sendNMEA(setNMEAoff)
  # setNMEAoff = "$PUBX,40,RMC,0,0,0,0*47"
  # gps_sendNMEA(setNMEAoff)
  
  # UBX-CFG-RST - reset, warmstart
  UBXcmd = bytearray.fromhex("B5 62 06 04 04 00 01 00 04 00 13 70")
  # UBX-CFG-RST - forced reset, warmstart
  UBXcmd = bytearray.fromhex("B5 62 06 04 04 00 01 00 00 00 0F 68")
  # UBX-CFG-RST - forced reset, coldstart
  #UBXcmd = bytearray.fromhex("B5 62 06 04 04 00 01 00 04 00 13 70")
  #gps_sendUBX(UBXcmd, len(UBXcmd))
  
  # airborne <1G
  # setNavmode = bytearray.fromhex("B5 62 06 24 24 00 FF FF 06 03 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 16 DC")
  # gps_sendUBX(setNavmode, len(setNavmode))
  
  # 0.1 Hz
  UBXcmd = bytearray.fromhex("B5 62 06 08 06 00 10 27 0A 00 01 00 56 01")
  # 1 Hz
  UBXcmd = bytearray.fromhex("B5 62 06 08 06 00 E8 03 01 00 01 00 01 39")
  # 5 Hz
  #UBXcmd = bytearray.fromhex("B5 62 06 08 06 00 C8 00 01 00 01 00 DE 6A")
  gps_sendUBX(UBXcmd, len(UBXcmd))
  
  
  # read all responses
  GPS = serial.Serial(GPS_PORT, 9600, timeout=1)
  n = GPS.inWaiting()
  if n:
    GPS.read(n)
  GPS.close()
  
  print("GPS setup done")


from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    m = 6367 * c * 1000
    return m

# ------------------------------------------------------------------------




total_lat = total_lon = total_alt = 0
total_sats = 0
max_dev_pos = max_dev_alt = 0

time_prev = ""
gps_buffer = ""
nmeatype = ""
i = 1

try:

  gpsdata = {
    'date': 0,
    'time': 0,
    'latitude': 0,
    'longitude': 0,
    'altitude': 0,
    'speed': 0,
    'course': 0,
    'fixq': 0,
    'satellites': 0,
  }
  
  print "Opening serial port.."
  gps_setup()
  GPS = serial.Serial(GPS_PORT, 9600, timeout=1)
  print "Port opened"

  while True:
    try:
      data_line = GPS.readline().strip()
      if (data_line.__len__() > 0):
          
        nmeastr = data_line
        #print nmeastr
        if nmeastr[:3] == '$GP' and "*" in nmeastr: #and nmeastr[len(nmeastr)-2:] == '\r\n':
          nmeatype = nmeastr[3:6]
          # print nmeatype
          if nmeatype == 'RMC' or nmeatype == 'GGA' or nmeatype == 'GSA':
            tmp = nmeastr.split(',')
            # print tmp
            if nmeatype == 'RMC':
              tmp_time = tmp[1]
              # tmp_time = float(tmp_time)
              tmp_t = tmp_time.split(".")
              tmp_time = float(tmp_t[0])
              tmp_time_10th = float("0." + tmp_t[1])
              # string = "%06f" % tmp_time
              string = "%06i" % tmp_time
              string_10th = "%02f" % tmp_time_10th 
              hours = string[0:2]
              minutes = string[2:4]
              seconds = string[4:6]
              milliseconds = string_10th[2:3]
              tmp_time = hours + ':' + minutes + ':' + seconds + '.' + milliseconds
              gpsdata["time"] = tmp_time

              tmp_date = tmp[9]
              tmp_date = int(tmp_date)
              string = "%06i" % tmp_date
              day = string[0:2]
              month = string[2:4]
              year = 2000 + int(string[4:6])
              tmp_date = str(year) + '-' + month + '-' + day
              if year >= 2014:
                gpsdata["date"] = tmp_date

              if tmp[3] != "":
                lat = gps_DegreeConvert(tmp[3])
                if tmp[4] == "S": lat *= -1
                gpsdata["latitude"] = round(lat, 7)
                lon = gps_DegreeConvert(tmp[5])
                if tmp[6] == "W": lon *= -1
                gpsdata["longitude"] = round(lon, 7)

              if tmp[7] != "":
                gpsdata['speed'] = round(float(tmp[7]) * 1.852)
              if tmp[8] != "":
                gpsdata['course'] = round(float(tmp[8]))

            if nmeatype == 'GGA':
              tmp_time = tmp[1]
              # tmp_time = float(tmp_time)
              tmp_t = tmp_time.split(".")
              tmp_time = float(tmp_t[0])
              tmp_time_10th = float("0." + tmp_t[1])
              # string = "%06f" % tmp_time
              string = "%06i" % tmp_time
              string_10th = "%02f" % tmp_time_10th 
              hours = string[0:2]
              minutes = string[2:4]
              seconds = string[4:6]
              milliseconds = string_10th[2:3]
              tmp_time = hours + ':' + minutes + ':' + seconds + '.' + milliseconds
              gpsdata["time"] = tmp_time

              if tmp[2] != "":
                lat = gps_DegreeConvert(tmp[2])
                if tmp[3] == "S": lat *= -1
                gpsdata["latitude"] = round(lat, 7)
                lon = gps_DegreeConvert(tmp[4])
                if tmp[5] == "W": lon *= -1
                gpsdata["longitude"] = round(lon, 7)

              gpsdata['satellites'] = int(tmp[7])
              if tmp[9] != "":
                gpsdata['altitude'] = float(tmp[9])

            if nmeatype == 'GSA':
              gpsdata['fixq'] = int(tmp[2])


        if nmeatype == 'RMC':
          # write packet
          # 2014-10-03 10:43:31.6,57.123,24.123,123.6,5,0.000007,-0.000005,-9.3,0.783

          if gpsdata['satellites'] > 4 and gpsdata['time'] != time_prev:
            
            gpsstr = ""
            gpsstr += str(gpsdata['date']) + " " + str(gpsdata['time'])
            gpsstr += "," + str(gpsdata['latitude']) + "," + str(gpsdata['longitude'])
            gpsstr += "," + str(gpsdata['altitude'])
            gpsstr += "," + str(gpsdata['satellites'])
            
            gpsstr += "," + str('{0:f}'.format(gpsdata['latitude'] - avg_latitude))
            gpsstr += "," + str('{0:f}'.format(gpsdata['longitude'] - avg_longitude))

            dev_alt = round(gpsdata['altitude'] - avg_altitude, 1)
            dev_pos = round(haversine(gpsdata['longitude'], gpsdata['latitude'], avg_longitude, avg_latitude), 2)

            gpsstr += "," + str(dev_alt)
            gpsstr += "," + str(dev_pos)
            
            #print gpsdata
            # print i, gpsstr
            
            time_prev = gpsdata['time']
            total_lat += gpsdata['latitude']
            total_lon += gpsdata['longitude']
            total_alt += gpsdata['altitude']
            total_sats += gpsdata['satellites']
            if abs(dev_alt) > max_dev_alt:
              max_dev_alt = abs(dev_alt)
            if dev_pos > max_dev_pos:
              max_dev_pos = dev_pos
                          
            gps_buffer += gpsstr + "\n"
            if i % 5 == 0:
              open(LOG_FILE, 'a').write(gps_buffer)
              gps_buffer = ""

            i += 1

          
    except Exception, e:
      print(data_line)
      print e
      print "------------"
      continue

except KeyboardInterrupt:
  print " Quitting.."
  open("./monitor.pid", 'w').write("")

  # read all responses
  GPS = serial.Serial(GPS_PORT, 9600, timeout=1)
  n = GPS.inWaiting()
  if n:
    GPS.read(n)
  GPS.close()

  stats = ""
  stats += "started: " + timestr + "\n"
  stats += "readings: " + str(i) + "\n"
  stats += "avg_latitude: " + str(total_lat/i) + "\n"
  stats += "avg_longitude: " + str(total_lon/i) + "\n"
  stats += "avg_altitude: " + str(total_alt/i) + "\n"
  stats += "avg_satellites: " + str(round(float(total_sats)/i, 2)) + "\n"
  stats += "max position deviation: " + str(max_dev_pos) + "\n"
  stats += "max altitude deviation: " + str(max_dev_alt) + "\n"
  stats += "total lat: " + str(total_lat) + "\n"
  stats += "total lon: " + str(total_lon) + "\n"
  stats += "total alt: " + str(total_alt) + "\n"
  if max_dev_pos > 20:
    print stats
  stats += "-------\n"
  open("./stats.txt", 'a').write(stats)
  
  sys.exit()
