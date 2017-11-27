#truerandom v1.0 beta
#sergio@infosegura.net
#www.infosegura.net

#True random numbers are obtained from http://www.random.org/
#If the module fails to obtain the random list it will return -1

#-----------IMPORTS----------------#
from urllib.request import urlopen
import urllib.request
from urllib.error import URLError, HTTPError


#-----------CLASSES--------------#
class myURLopener(urllib.request.FancyURLopener):

    def http_error_401(self, url, fp, errcode, errmsg, headers, data=None):
        print("Warning: cannot open, site requires authentication")
        return None

#-----------FUNCTIONS--------------#
def getnum(min,max,amount):
    global randlist
##    try:
      if True:
        url_opener = myURLopener()
        data = url_opener.open("http://www.random.org/integers/?num="+str(amount)+"&min="+str(min)+"&max="+str(max)+"&col=1&base=10&format=plain&rnd=new")
        print("helloo")
        randlist=data.read()
        print("helloo2")
        data.close()
        randlist[:] = [line.rstrip('\n') for line in randlist]
        
        for n in range(len(randlist)):
            randlist[n]=int(randlist[n])

        return randlist
##    except HTTPError as e:
##        # do something
##        print('Error code: ', e.code)
##    except URLError as e:
##        # do something (set req to blank)
##        print('Reason: ', e.reason)
##    except:
##        randlist=[]
##        randlist.append(-1)
##        return randlist

print(getnum(0,5,3))
