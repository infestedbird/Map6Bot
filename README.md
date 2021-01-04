####About Map6bot
 wrote Map6bot to help people with reviewing their data logs from the Kia Stinger and Hyungdai G70, The tool should work with other JB4 based logs as well as other Lap3 based logs. It would be trivial to add support for other platforms. 

## Future Of Map6Bot
We want to continue to dev on this project, including a rewrite that allows us to make errors clickable and they would be highlighted in the logs , Better 4cyl detection  ( We've got a solution just needs written) , Externlize the Sensitivity of the application,  Add Min Trigger counts.


### How was it built? 
map6bot has been designed to work with selenium webdriver. Our instructions will outline how to setup map6bot
to run from a raspberry pi 3 or 4.  You will need a couple of things. 



#1  a imap box to pull emails from (Defaults are setup for gmail imap)
#2  A raspberry pi to run this from or the ability to change the selenium webdriver to a windows or mac based one (Does work!)
#3  A data zap account.
#4 Install the Required Modules Below


mydriver.py:  Tool for kicking for a log review from a command line and doesn't require a imap email account

logcheck2.py: Primary code for reviewing logs

dotheemail.py: This is the primary script for processing an imap email account and getting CSV files to be processed

myconfig.py: This file contains all of the primary configs this includes login and password as well as paying clients for special message payloads.

datazapupload.py: This code expects /home/pi/map6 and you may need to tweak

map6bot.sh: Basic Loop I use for running the bot on my Pi


#### Install Notes

pip3 install selenium
pip3 install webdriver_manager

apt-get install chromium-chromedriver




#Config notes
All of the config is stored in myconfig.py, We have included example values for you to start from.



#Tweaking the Sensntivity 
Coming Soon we will be adding some teaking to the external variables

written by Josh and Will Hatzer with support from Steven Briggs and Stinger Community
bill.hatzer@gmail.com (Will)
joshhatzer@gmail.com (Josh)
