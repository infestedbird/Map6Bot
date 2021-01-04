import LogCheck2
import sys
print('to run this file you will need to include a filename')
length =len( sys.argv)
if length == 2:
    file_name = str(sys.argv[1])
    gmail_user = 'joshhatzer@gmail.com'
elif length == 3:
    file_name = str(sys.argv[1])
    gmail_user = str(sys.argv[2])
elif length == 1:
    print('you have forgot the filename')
    exit()









logchk = LogCheck2.LogCheck(file_name, gmail_user)
#logchk = log_testy.LogCheck('./lap3.csv', user_gmail )
logchk.ParseLog()
