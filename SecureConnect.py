# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Robust Connect of Tinkerforge IMU and GPS and Write to File

# <markdowncell>

# Based on [Tinkerforge Tutorial](http://www.tinkerforge.com/de/doc/Tutorials/Tutorial_Rugged/Tutorial.html#tutorial-rugged-approach)

# <codecell>

from tinkerforge.ip_connection import IPConnection
from tinkerforge.brick_imu import IMU
from tinkerforge.bricklet_gps import GPS

# <codecell>

HOST = "localhost"
PORT = 4223

# <codecell>

ipcon = IPConnection()

# <codecell>

def cb_enumerate(uid, connected_uid, position, hardware_version, 
                 firmware_version, device_identifier, enumeration_type):
    
    if connected_uid == '0':
        print 'Master Brick UID: \t%s' % (uid)
    
    #print 'UID: %s' % uid
    #print 'connected_uid: %s' % connected_uid
    #print 'position: %s' % position
    #print 'hardware_version: %i.%i.%i' % hardware_version
    #print 'firmware_version: %i.%i.%i' % firmware_version
    #print 'device_identifier: %d' % device_identifier
    #print 'enumeration_type: %d' % enumeration_type
    
    
    if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or \
       enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
        
        # Enumeration is for IMU Brick
        if device_identifier == IMU.DEVICE_IDENTIFIER:
            
            print 'IMU Brick UID: \t\t%s' % (uid)
            
            # Create imu device object
            imu = IMU(uid, ipcon) 
            imu.set_all_data_period(100)
            imu.register_callback(imu.CALLBACK_ALL_DATA, cb_imudynamic)
            
            
        # Enumeration is for GPS Bricklet
        if device_identifier == GPS.DEVICE_IDENTIFIER:
            
            print 'GPS Bricklet UID: \t%s' % (uid)
            
            # Create imu device object
            gps = GPS(uid, ipcon) 
            gps.set_coordinates_callback_period(100)
            gps.register_callback(gps.CALLBACK_COORDINATES, cb_coordinates)

# <codecell>

# Callback handles reconnection of IP Connection
def cb_connected(connected_reason):
    # Enumerate devices again. If we reconnected, the Bricks/Bricklets
    # may have been offline and the configuration may be lost.
    # In this case we don't care for the reason of the connection
    ipcon.enumerate()

# <codecell>

def cb_imudynamic(acc_x, acc_y, acc_z, mag_x, mag_y, mag_z, ang_x, ang_y, ang_z, temp):
    '''
    Gibt die kalibrierten Beschleunigungen des Beschleunigungsmessers für die X, Y und Z-Achse in mG zurück (G/1000, 1G = 9.80605m/s²).
    '''
    ax = acc_x*9.80605/1000.0
    ay = acc_y*9.80605/1000.0
    az = acc_z*9.80605/1000.0

    '''
    Gibt die kalibrierten Winkelgeschwindigkeiten des Gyroskops für die X, Y und Z-Achse in °/14,375s zurück. (Um den Wert in °/s zu erhalten ist es notwendig durch 14,375 zu teilen)
    '''
    rollrate = ang_x/14.375
    pitchrate= ang_y/14.375
    yawrate =  ang_z/14.375

    temp = temp/100.0
    
    with open('IMUdump.csv', 'a+b') as f:
        f.write('%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.1f\n' % (ax, ay, az, rollrate, pitchrate, yawrate, temp))

# <codecell>

def cb_coordinates(latitude, ns, longitude, ew, pdop, hdop, vdop, epe):
    '''
    Gibt die GPS Koordinaten zurück. Breitengrad und Längengrad werden im Format DD.dddddd° angegeben, der Wert 57123468 bedeutet 57,123468°. Die Parameter ns und ew sind Himmelsrichtungen für Breiten- und Längengrad. Mögliche Werte für ns und ew sind 'N', 'S', 'E' und 'W' (Nord, Süd, Ost, West).
    PDOP, HDOP und VDOP sind die "Dilution Of Precision" (DOP) Werte. Sie spezifizieren die zusätzlichen multiplikativen Effekte von der GPS Satellitengeometrie auf die GPS-Präzision. hier gibt es mehr Informationen dazu. Die Werte werden in Hundertstel gegeben.
    EPE ist der "Estimated Position Error". Der EPE wird in cm gegeben. Dies ist nicht der absolut maximale Fehler, es ist der Fehler mit einer spezifischen Konfidenz. Siehe hier für mehr Informationen.
    '''    
    lat = latitude/1000000.0
    lon = longitude/1000000.0
    pdop = pdop/100.0
    hdop = hdop/100.0
    vdop = vdop/100.0
    epe = epe/100.0
    
    with open('GPSdump.csv', 'a+b') as f:
        f.write('%.6f,%.6f,%.2f,%.2f,%.2f,%.2f\n' % (lat, lon, pdop, hdop, vdop, epe))

# <codecell>

ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, cb_enumerate)
ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, cb_connected)

# <codecell>

ipcon.connect(HOST, PORT)

# <codecell>

raw_input('>>> Logging Data to file(s)... (Press key to exit)\n')

