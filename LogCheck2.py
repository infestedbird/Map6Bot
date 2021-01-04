
import re
import csv
import io, sys
import os.path
import smtplib
import datazap_log_uploader
import datetime

from myconfig import *
""" Load Passwords and user list from file""" 

#print("teset")
current_time = datetime.datetime.today()

allmaps = set()

def checktiming(mythrottle,mypedal,myign1,myign2,myign3,myign4,myign5,myign6,myrpm,mytimestamp,mytrigger):
    "Verifying if timing is right"
    output = io.StringIO()
    myigndev = myign2 + myign3 + myign4 + myign5 + myign6
   # if myigndev > 50:
    if mythrottle > 95 and mypedal > 96:
        "Throttle Pressed Mode"
        #print("throttlemode")
        if myigndev > 4.2 and myigndev < ((myign1 - 4) *6) :
            print("Timing Deviation Detected at Timestamp",mytimestamp," RPM:",myrpm ," Correction: ", myigndev , file=output)
            print("IGN1:",myign1,"IGN2:",myign2,"IGN3:",myign3,"IGN4",myign4,"IGN5:",myign5,"IGN6:",myign6, file=output)
            #mytrigger = mytrigger + 1
    return output.getvalue()

def checktrims(mythrottle,mypedal,myrpm,mytimestamp,mytrims,mytrims2,myafr1,myafr2):
    "detect high fuel trims"
    output = io.StringIO()
    myspread = mytrims2 - mytrims
    if mythrottle > 95 and myspread > 10 :
        print("Fuel Trim seperation detected rpm:",myrpm,"trim1:",mytrims , "trim2",mytrims2, "TS:",mytimestamp,myspread , "afr1:", myafr1 ,"afr2:", myafr2, file=output)
    if mythrottle > 95 and mytrims > 50 :
        print("High Fuel Trim Detected",mytrims , mytrims2 ,"RPM:",myrpm, file=output)
    if mythrottle > 95 and mytrims < 7  :
        print("Low Fuel Trim Detectecd watch for frozens trims",mytrims, file=output)
    return output.getvalue()

def checkhpfp(mythrottle,mypedal,myrpm,mytimestamp,myfp_h):
    "Check for HPFP Issues"
    output = io.StringIO()
    if mythrottle > 95 and mypedal >90:
        if myfp_h < 10 :
            print("HPFP Issues Detected at Timestamp",mytimestamp,"RPM:",myrpm,myfp_h, file=output)
    return output.getvalue()

def checkthrottleclose(mythrottle,mypedal,myrpm,myboost,myboost2 , mytimestamp):
    "CheckThrottleCode"
    output = io.StringIO()
    #print(mypedal , mythrottle)
    if mypedal > 95 and myrpm >4000 :
        if mythrottle < 95 :
            print("Throttle Close Detected at TS:",mytimestamp,"RPM:",myrpm,"Throttle",mythrottle,"Pedal",mypedal, file=output)
            if (myboost - myboost2) > 1:
                    print("Large boost drop Detected at rpm:",myrpm,"boost1",myboost,"boost2",myboost2, file=output)
    return output.getvalue()

def checkmethflow(mythrottle,mypedal,myrpm,myboost,mytimestamp,mymeth,mytriggercount):
    "Check Methanol Flow"
    output = io.StringIO()
    if mymeth == 0 :
        #print("")
        return output.getvalue()
    if mypedal > 95 and mymeth < 90 and mytriggercount > 1 and myboost > 10  :
        print("Meth Flow issue Detected TS:",mytimestamp,"RPM:",myrpm,"Boost:",myboost,"Meth Flow:",mymeth, file=output)
    return str(output.getvalue())

def checkboostdeviation(mythrottle,mypedal,myboost,myboost2,mytimestamp):
    "Detect Deviations in boost1 and boost"
    output = io.StringIO()
    if mythrottle > 95 and (myboost - myboost2) > 1.9 :
        print("Boost1 and Boost2 To far apart B1:" , myboost , "B2" , myboost2 , (myboost - myboost2) , "TS:" , mytimestamp, file=output )
    return output.getvalue()

def checkvin(myvin):
    "Check for paying clients"
    output = io.StringIO()
    #my_clients = {"5LC9K6054505" : "Will Hatzer" , "peter@yancoappraisal.com" : "Pizza"  }
    if myvin in my_clients :
        print("Thank you",my_clients[myvin], "for being a paying supporter! Your Gratituty is appreicated!" , file=output)
        #print(my_clients[myvin])
    else:
        print("I provide my services free of charge, Please consider donating to help support my ongoing efforts!" , file=output)
    return output.getvalue()

def checkemail(myemail):
""" Checking For Supporters"""

    reemail = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", myemail)
    email = reemail[0]
    print(email)
    output = io.StringIO()
   # my_clients = { "bill.hatzer@gmail.com"  : "Will Hatzer" , }
                
    print(my_clients)
    if email in my_clients :
        print("Thank you", my_clients[email], "for being a paying support!!! Your Gratuity is appreciated!!!" , file=output )
    else:
        print("I will not reach out for follow-ups for every log. If you want follow-up regarding your data, please contact me on messenger. While this is a free tool, and while I do not charge for in-depth assistance in the traditional sense, I will prioritize paying supporters. I do my best to get to everyone, but the volume of users of this free tool dictates that timely assistance to everyone is unlikely." , file=output)
    return output.getvalue()


def checkboost(myboostlimit,cyl):
    "Check Boost Limit"
    output = io.StringIO()
    if myboostlimit > 25.1 and cyl > 4 :
        print("Please Conisder Lowering your Boost Limit", file=output)
        print("Current Limit",myboostlimit,"Consider dropping below 25psi", file=output)
    if myboostlimit > 26 and cyl == 4 :
        print("Please Consider lowering your boost liimt", file=output)
        print("Current Limit", myboostlimit, "Consider dropping below 26psi", file=output)
    return output.getvalue()

def checkiat(myrpm,mythrottle,mypedal,myiat):
    "Detect Heat Soak"
    output = io.StringIO()
    if myrpm > 2500 and mythrottle > 95 and myiat > 118 :
        print("Heat Soak Detected! RPM:",myrpm,"IAT:",myiat, file=output)
    return output.getvalue()

def checkfirmware(firmwareversion):
    "Note firmware upgrades"
    output = io.StringIO()
    if firmwareversion < 19:
        print("Please consider upgrading to the latest stable firmware or Ask Will about Latest Beta" , file=output)
    return output.getvalue()


def Lap3Parse(mysender,mylog):
    print("lap3 stubs")
    datazap_link = datazap_log_uploader.upload_log(mylog, mysender , str(current_time), datazap_user , datazap_password )

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
    except:
        print('Something went wrong...')

    sent_from = gmail_user
    to = ['bill.hatzer@gmail.com', mysender ]
    subject = "Data Log Report for ", mysender
    body = """ 
Lap3 supoprt is ALPHA, Once I've gathered enough logs to add more detections I will. Please reach out if you have examples of bad Lap3 Logs.  HPFP Crash , Timing Devitations , Meth Failure and more

Starting Report:
 %s """ % ( datazap_link )

    email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject , body)

    print(email_text)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print('Email Sent!!!')
    except:
        print("Something Broke")



class LogCheck:


    def __init__(self, logFile, sender):
        self.logFile = logFile
        self.sender = sender



    def MyLog(self):
        with open(self.logFile) as csvfile:
            mycsv = csv.reader(csvfile, delimiter=',')
            row1 = next(mycsv)
#            print(row1)
#            print(row1[0], "Var1" )
#            print(row1[1])
        if "Module::" in  row1[0] :
            print("Lap3 Mode")
        if "Firmware" in row1[0] : 
            print("Jb4 mode")
            #Lap3Parse()
            print("pizza")
            exit()
            print("test")

        
    def ParseLog(self):
        loopcount = 0
        triggercount = 4

        iatOut = '\nIAT\n-------------------\n'
        timingOut = '\nTiming\n----------------\n'
        hpfpOut = '\nHPFP Report\n--------------------\n'
        throttlecloseOut = "\nThrottle Report\n-----------------\n"
        methflowOut = "\nMethFlowReport\n-----------------\n"
        boostdevOut = "\nBoost Deviations\n--------------------\n"
        trimsOut = "\nFuel Trims\n-------------------------\n"
        boostOut = "\nBoost Warning\n-----------------------\n"
        firmwarecheck ="\nFirmware Check\n----------------------\n"
        boostOut = "\nBoost Safety Check\n---------------------------\n"

        if not os.path.exists(self.logFile) or not os.path.isfile(self.logFile):
            #logging.error("file {0} does not exist".format(self.logFile))
            print("file {0} does not exist.".format(self.logFile))
            sys.exit(1)

        with open(self.logFile) as csvfile:
            mycsv = csv.reader(csvfile, delimiter=',')
            row1 = next(mycsv)
            row2 = next(mycsv)
            row3 = next(mycsv)
            row4 = next(mycsv)
            row5 = next(mycsv)
            emailOut = checkemail(self.sender)
            tunedata = row4
            if "Module::" in row1[0] :
                Lap3Parse(self.sender,self.logFile)
                exit()
            print(tunedata)
            firmware = row2[0]
            safety = row4[11]
            if safety == 1:
                safety = '1, Boost over safety'
            elif safety == 2:
                safety = '2, AFR Lean'
            elif safety == 3:
                safety = '3, Fuel Pressure Low'
            elif safety == 4:
                safety = '4, Meth Flow Low'
            else:
                safety = '5, Fuel Trim Variance'
           # datazap_notes = ("Time:" + str(current_time) + "Firmware" + firmware + "Safety" + safety)
            boostlimit = float(row4[0])
            vin = row2[12]
        #    print(vin)
            firmwarever = int(firmware.split('/')[1])
            firmwarecheck += checkfirmware(firmwarever)

            vinOut = checkvin(vin)
            #emailOut = checkemail(self.sender)
            boostOut += checkboost(boostlimit, 6)
            #
            if "Module::" in row1[0] :
                print("Lap3Mode")
                Lap3Parse(self.sender,self.logFile)
                exit()
            #exit()
            for row in mycsv:
        #            print(row)
        #            print(float(row[0])
        #            print(float(row[0],float(row[1],float(row[2])
                    loopcount = loopcount +1
                    timestamp=float(row[0])
                    rpm=float(row[1])
                    ecu_psi=float(row[2])
                    target=float(row[3])
                    boost=float(row[4])
                    pedal=float(row[5])
                    iat=float(row[6])
                    fuelen=float(row[7])
                    wgdc=float(row[8])
                    throttle=float(row[9])
                    fp_h=float(row[10])
                    ign_1=float(row[11])
                    avg_ign=float(row[12])
                    calc_torque=float(row[13])
                    trims=float(row[14])
                    dme_bt=float(row[15])
                    meth=float(row[16])
                    fp_l=float(row[17])
                    afr=float(row[18])
                    gear=float(row[19])
                    ff=float(row[20])
                    load=float(row[21])
                    clock=float(row[22])
                    #global map
                    map=float(row[23])
                    afr2=float(row[24])
                    ign_2=float(row[25])
                    ign_3=float(row[26])
                    ign_4=float(row[27])
                    ign_5=float(row[28])
                    ign_6=float(row[29])
                    oilf=float(row[30])
                    waterf=float(row[31])
                    transf=float(row[32])
                    e85=float(row[33])
                    boost2=float(row[34])
                    trims2=float(row[35])
                    mph=float(row[36])
                    allmaps.add(int(map))
                    #print(allmaps)
                    datazap_notes = ("Time:" + "" + str(current_time) + " ][ " + "Firmware:" + "" + firmware + " ][ " +  "Safety:" + "" + safety + " ][ " + "Map: " + "" + str(allmaps))



                    iatOut += checkiat(rpm,throttle,pedal,iat)
                    timingOut += checktiming(throttle,pedal,ign_1,ign_2,ign_3,ign_4,ign_5,ign_6,rpm,timestamp,triggercount)
                    hpfpOut += checkhpfp(throttle,pedal,rpm,timestamp,fp_h)
                    throttlecloseOut += checkthrottleclose(throttle,pedal,rpm,boost,boost2,timestamp)
                    methflowOut += checkmethflow(throttle,pedal,rpm,boost,timestamp,meth,triggercount)
                    boostdevOut += checkboostdeviation(throttle,pedal,boost,boost2,timestamp)
                    trimsOut += checktrims(throttle,pedal,rpm,timestamp,trims,trims2,afr,afr2)

        print("Notes Box for Datazap.me")
        print("datazap url for viewing logs")
        print(vinOut)
        print(firmwarecheck)


        print('REPORT BELOW')
        print(boostOut)
        #print(timingOut)
        print(iatOut)
        print(hpfpOut)
        print(throttlecloseOut)
        print(methflowOut)
        print(boostdevOut)
        print(trimsOut)

            #print(mph
            #print(rpm)

        print(self.sender)
        datazap_link = datazap_log_uploader.upload_log(self.logFile, self.sender , datazap_notes , datazap_user , datazap_password )
        part_url = '?log=0&data=1-3-4-5-9-11-14-18-23-25-26-27-28-29'
        new_url = datazap_link + part_url
       


        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
        except:
            print('Something went wrong...')

        sent_from = gmail_user
        to = ['bill.hatzer@gmail.com', self.sender ]
        subject = "Data Log Report for ", self.sender
        body = """%s 


This tool is a beta and I'm still fixing bugs. If you only have a single report for a section in many cases its 
A False positive. The tool also Doesn't always detect things properly on 2.0t and 1.6t cars. 
Starting Report:
 %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s """ % (emailOut, new_url , "", "", "","", "", "", "", "", "", "","", "", "", "", "", "", "", "", "" , "", "", "", "",  datazap_link,firmwarecheck,boostOut,iatOut,hpfpOut,throttlecloseOut,methflowOut,boostdevOut,trimsOut,timingOut)

        email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject , body)

        print(email_text)
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail(sent_from, to, email_text)
            server.close()

            print('Email Sent!!!')
        except:
            print('something went wrong sending email')
