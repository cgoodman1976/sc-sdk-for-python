#!/usr/bin/env python
#***********************************************************************************#
# ver0.97 => Add -f option force purge local data                                   #
# ver0.97 => Enhance extend disk feature to reduce manual operation                 # 
# ver0.96.5 => a) Fix SCSI Bus issue that found at G-Cloud SUSE Enterprise          #
# ver0.96 => b) Add update inventory option -i                                      #
# ver0.96 => c) Fix RemoveAllDisk issue at linux platform                           #
# ver0.95 => Add extend disk feature for windows only                               #
# ver0.94 => a) Fix format issue at Python ver2.4                                   #
# ver0.94 => b) Set logger level to "DEBUG" to support Python ver2.4                #
# ver0.93 => a) Add purge feature to delete activation data from local              #
# ver0.93 => b) Chang mount point detection mechanism instead of hardcode sleep     #
# ver0.92 => Fix input args with "&" issue                                          #
# ver0.91 => Fix admin privilege checking issue in windows platform                 #
# ver0.9 => Win8 & Win 2012 Server Support                                          #
# ver0.8 => Add Distributoer information on Lunix environment                       #
# ver0.7 => Add HTTP connection checking                                            #
# ver0.6 => Add how to usage the python,version info and debugging log              #
# ver0.0 => Complete all fetuares                                                   #
# Created by => Alex Chnag                                                          #
#***********************************************************************************#

import socket, sys, os, platform, time, subprocess, re
import datetime, getopt, logging ,pwd

def diskopt(getdisk,servicename,stopsvr,passphrase,appfile):
    getdisk = []
    returndisk = []
    cmd1 = None
    rdisk = None
    index1 = 0    
    subprocess.call(servicename,shell=True) #start SCAgent to mount all encrypted volume
    #auto-scandisk from wmic
    cmd1 = 'wmic logicaldisk get name'
    result_disk = subprocess.Popen(cmd1,bufsize=1024,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    while 1:
            rdisk = result_disk.readline()
            if not rdisk:
                break
            else :
                if (rdisk == '\n'):
                    continue
                elif (rdisk[:4] == 'Name'):
                    continue
                elif (rdisk[:1] == '\r'):
                    continue
                else:
                    getdisk.insert(index1,rdisk[:1])
                    index1 +=1
    logging.info('Scan disk output : %s' % getdisk)
    x = None
    dc = 0
    targetvolume = 0
    notextend = 0
    #start to extend disk
    for x in getdisk :       
        cmd = None
        result = None
        if ((x == 'A') or (x == 'C') or (x == 'D')):
            logging.info('Unable to extend volume : %s' % x)
            continue        
        else :            
            logging.info('==> Start to extend disk : %s' % x)
            # create extend.txt file
            extendfile = None
            extendfile = 'extend_'+x+'.txt'        
            FILE = open(".\\%s" % extendfile,"w")	
            os.access(extendfile,os.R_OK)
            FILE.write("Rescan\n")
            FILE.write("select volume "+str(targetvolume)+"\n")
            FILE.write("extend\n")
            FILE.write("exit\n")            
            FILE.close()
            # execute the diskpart command   
            cmd = "diskpart.exe /s "+extendfile+">> result.log"
            logging.info("Execute command : %s" %cmd)
            if (subprocess.call(cmd,shell=True) != True):
                logging.info("Extend not available")
                notextend +=1
            else :
                logging.info("Extend successful")                
                targetvolume += 1            
                returndisk.insert(dc,x)
                time.sleep(15) #Microsoft recommend set sleep 15 seconds before next batch
        dc +=1        
    logging.info('<== Complete %s disk extensions' %dc)
    logging.info('Extend disk : %s' %targetvolume)
    logging.info('Not extend disk : %s' %notextend)
    subprocess.call(stopsvr,shell=True)
    update_inventory(passphrase,appfile)
    if (targetvolume >= 1):
        return (True,returndisk)
    else :
        return (False,returndisk)
                
def remove_without_reboot(scsi_2,mountpoint,passphrase,appfile,scpath,servicename):
    ret1 = None
    ret2 = None
    newpoint = None
    if (platform.system() == "Linux"):        
        time.sleep(1)
        ret1 = get_local_disk_linux(scsi_2,'delscsiid')
        time.sleep(1)
        ret2 = get_local_disk_linux(scsi_2,'init')
        logging.info('Re-initial SCSI disk scan result : %s' %ret2[0])                        
        update_inventory(passphrase,appfile)
        if (ret2[0] == True):                            
            logging.info('First SCSI disk :%s' % ret2[1][0])            
            newpoint = mountpoint.strip("1")+ret2[1][0][11] #got right scsi_id                            
            startagent(scpath,servicename,newpoint)                        
    if (platform.system() == "Windows"):        
        ret1 = get_c9_local_disk_win(scsi_2)
        logging.info('Re-initial SCSI disk scan result : %s' %ret1[0])
        update_inventory(passphrase,appfile)
        if (ret1[0] == True):                                                      
            newpoint = chr(ord(mountpoint.strip(":\\"))+int(ret1[1][0][8])-1)+":\\" #got right scsi_id 
            startagent(scpath,servicename,newpoint)  
    return (True)
    
def update_inventory(passphrase,appfile):
    logging.info("==> Option : Start Inventory list update process...")
    result_str = None
    cmd =(appfile+" "+
          "--passphrase="+'"'+passphrase+'"'+" "+          
          "--publish-inventory "+
          "--get-device-list "+
          "--quiet ")
    logging.info("Command: %s" %cmd)
    if(platform.system() == 'Linux'):
          cmd1 = subprocess.Popen(cmd,bufsize=1024,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True).stdout                
    if(platform.system() == 'Windows'):
          cmd1 = subprocess.Popen(cmd,bufsize=1024,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    result_str = cmd1.read()
    logging.info("<== Option : Update Inventory list to KMS successful...")
    return (True)
    
def purgeall(scpath):
    try :
        import xml.etree.ElementTree as et
    except:
        import cElementTree as et
    #delet all data
    cmd = None
    delcmd = None
    configxml = None
    message = None
    if (platform.system() == 'Windows'):
        #delcmd = [('del *.old'),('del *.bin'),('del kms_public_key.pem'),('del device.conf')]
        delcmd = [('del *.old'),('del device.conf'),('del extend*.txt'),('del result.log')]
        for cmd in delcmd:
            logging.info('Purge command: %s' % cmd)
            subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
        configxml = scpath+'\\config.xml'
    if (platform.system() == 'Linux'):
        #delcmd =[('rm -rf *.old'),('rm -rf *.bin'),('rm -rf kms_public_key.pem'),('rm -rf device.conf')]
        delcmd =[('rm -rf *.old'),('rm -rf device.conf')]
        for cmd in delcmd:
            logging.info('Purge command: %s' % cmd)
            subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True).stdout
        configxml = scpath+'/config.xml'
    # modify config.xml to remove device,key and server data
    logging.info('Path of Config XML file : %s' % configxml)
    tree = et.parse(configxml)
    root = tree.getroot()
    last = 0
    x = 0
    for e in root.findall("./agent/devices/device"): # verify how many devices be created
        last += 1
    logging.info('How many device info found : %s' %str(last))
    if (last == 0):
        message = '===> No acitvation data found from config.xml file and skip this modification action <==='
        logging.error("%s" % message)
        return (False)
    else : 
        #csp = None
        #csp = root.findall("./csp")
        #csp[0].set('id','')
        #logging.info('Reset CSP date successful...')
        #for node in root:
        #    if (node.tag == 'server'):
        #        del root[root.getchildren().index(node)]
        #        logging.info('First level target node %s remove successful...' % node)
        #    for subnode in node:
        #        if (subnode.tag == 'key'):
        #            del node[node.getchildren().index(subnode)]
        #            logging.info('Second level target node %s remove successful...' % subnode)
        for node in root:
            for subnode in node:
                for x in range(int(last)):
                    for qnode in subnode:
                        if (qnode.tag == 'device'):
                            del subnode[subnode.getchildren().index(qnode)]
                            logging.info('3rd level target node %s remove successful...' % qnode)
                        else:
                            continue
                    x +=1
        tree.write(configxml)
        message = '==> Purge local data successful and try activation again <==='
        logging.info("%s" % message)
        return (True)
def chk_con(kms):    
    #Parse kms
    hostname = None
    port = None
    result = None
    ip = None
    ipaddr = None 
    hostname = re.search('https://(.*?):',kms,flags=0).group(1)
    logging.info('KMS FQDN : %s' %hostname)
    port = re.search('https://.*:(.*)/',kms,flags=0).group(1)
    logging.info ('KMS WebAPI Port : %s' %port)
    #DNS resolve
    try:
        socket.gethostbyname(hostname)
    except :
        logging.error('DNS resolve problem for this KMS server FQDN : %s' %hostname)
        print '!!! DNS resolve issue for FQDN : %s!!!' %hostname
        return (False)
    else :
        result = socket.gethostbyaddr(hostname)
        ip = result[2]        
        ipaddr = ip[0]
        logging.info('KMS IP address : %s' %ipaddr)
    #TCP connect
    socket.timeout(10)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ipaddr,int(port)))        
    except Exception, e:
        logging.exception('TCP connection error with %s:%d. Exception type is %s' % (ipaddr, int(port), `e`))
        print 'TCP connection error with KMS server %s port %d. Error type %s'% (ipaddr, int(port), `e`)
        return (False)
    else :
        s.shutdown(1)
        s.close()
        return(True)
def get_hostname():
    host1 = socket.gethostname() #Hontname only
    host2 = socket.getfqdn(host1) #FQDN name
    logging.info("Hostname : %s" % host1)
    logging.info("FQDN     : %s" % host2)
    return (True)

def get_osinfo():
    osname1 = platform.platform(aliased=0,terse=0)
    osname2 = os.name
    logging.info("Platform name    : %s" %osname1)    
    logging.info("OS name          : %s" %osname2)
    logging.info("Python version   : %s" %str(sys.version_info[:3]))
    if (platform.system() == 'Linux'):
        cmd = 'lsb_release -a'
        result = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True).stdout
        while 1:
                info = result.readline()
                if not info :
                         break
                else :
                        if info != '\n':    
                            logging.info("%s" % info.strip())
    return (True)

def get_adminrole(kms):   
    if (chk_con(kms) == False):
        return (False)    
    if (platform.system() == 'Windows'):
        import ctypes
        # is_admin = os.listdir(os.sep.join([os.environ.get('SystemRoot','C:\windows'),'temp']))
        if (ctypes.windll.shell32.IsUserAnAdmin() == 1):
            logging.info("User name :%s has been grant admin privilege" %os.environ['USERNAME'])            
            logging.info("<==Step 0: Checking user privilege")
            return (True)
        else:
            logging.error("User name :%s without admin privilege !!!" %os.environ['USERNAME'])
            print 'Permission issue, try using Run as administraor to execute this scripti'
            return (False)        
    if (platform.system() == 'Linux'):
        if (os.getgid() == 0):
            username = pwd.getpwuid(os.getuid())[0]
            logging.info("User name :%s has been grant admin privilege" %username)
            logging.info("<==Step 0: Checking user privilege")
            return (True)
        else:
            logging.error("User name :%s without admin privilege !!!" %os.getlogin())
            print 'Permission issue'
            return (False)
                    
def is_filelocked(filepath):
        locked = None
        file_object = None
        buffer_size = 0
	if os.path.exists(filepath):
		try:
                	#print "Trying to open %s." % filepath
	                buffer_size = 8
	                file_object = open(filepath, 'a',buffer_size)
        	        if file_object:
	        	        #print "%s is not locked." % filepath
				locked = False
		except IOError, message:
	                    logging.error("File is locked(unable to open in append mode).%s" % message)
        	            locked = True        
        else:
            logging.error("$s not found." % filepath)
        return locked

def gendevicefile(mountpoint,filesystem,scpath,devicefile,backupfile):
        # check Agent installed and file exist or not
        if (os.path.exists(scpath) == False):
            logging.error("Alert - SecureCloud Runtime Agent does not install yet !!!")
            return (False)		
        else:
            if (os.path.isfile(devicefile) == True)and(is_filelocked(devicefile) == False):
                os.rename(devicefile,backupfile)
                if (c_conf(devicefile,mountpoint,filesystem) == True): 
                    logging.info("Device file Re-create successful")
                    logging.info("<== Step 1: Start to create device file...")
                    return (True)
                else :
                    return (False)
            if (os.path.isfile(devicefile) == False):
                if (c_conf(devicefile,mountpoint,filesystem) == True):
                    logging.info("Device file Create successful")
                    logging.info("<== Step 1: Start to create device file...")        
                    return (True)
                else:
                    return (False)

def c_conf(devicefile,mountpoint,filesystem):
	identity = None
	scsi = None
	scsi_2 = []
	diskresult = None
	FILE = open(devicefile,"w")	
        os.access(devicefile,os.R_OK)
        identity = socket.getfqdn(socket.gethostname())
	if (platform.system() == 'Windows'):
                diskresult = get_c9_local_disk_win(scsi_2)
	if (platform.system() == 'Linux'):                
		diskresult = get_local_disk_linux(scsi_2,'init')
        if ((diskresult[0] != True) or (diskresult[2] == 0)):
		FILE.close()
		logging.error("Device emulator failure --- Check extra Data volume is attached propriety or not !!!")
		return (False)		
	else:
		devicecounter = 1 #for linux and device config file
		devicecounter1 = 0 #for windows only
		#print diskresult[1]
		for scsi in diskresult[1]:			
                        FILE.write("[device"+str(devicecounter)+"]\n")				
                        FILE.write("id="+identity+scsi+"\n")
			if(platform.system() == 'Linux'):
                            FILE.write("mountpoint="+ mountpoint.strip("1")+str(devicecounter)+"\n")
			if(platform.system() == 'Windows'):
                            FILE.write("mountpoint="+ chr(ord(mountpoint.strip(":\\"))+devicecounter1)+"\n")
                        FILE.write("filesystem="+ filesystem +"\n")
			FILE.write("access=readWrite\n")
			FILE.write("os="+str.lower(platform.system())+"\n")
			FILE.write("Keysize=256\n")
			devicecounter += 1
			devicecounter1 +=1
                logging.info("Device emulator...Successful")
                FILE.close()
                return (True)

def get_c9_local_disk_win(scsi_2):
    import _libc9utilities
    buffer = '\0' * 1024 * 4
    lines = None
    line = None
    aa=0
    scsi_2= []
    result =_libc9utilities.listScsiDevices(buffer,1024*4)
    #print buffer
    if (result == 0):
        value = buffer[0:buffer.find('\0')] #format buffer data1
        lines = value.split("\n") #format buffer data2
        result =[]
        #print lines
        for line in lines:
            idName = line.split("|") #split data to 2 part by |
            if (len(idName) == 2): 
                diskInfo = dict() #define the diskInfo data type to dictionary            
                diskInfo["id"] = "scsi"+idName[0]
                device = idName[1].split("\\")
                diskInfo["device_name"] = device[2]
                if (device[2] != 'Harddisk0'): #filter the System volume out since sc3.0 doesn't support system volume encryption
                    logging.info("Diskinfo : __scsi%s" %idName[0])
                    scsi_2.insert(aa,"__scsi"+idName[0])
                    aa +=1                    
        if (aa > 0):
            logging.info("Success to emulate the SCSI ID from C9 library")
            return (True,scsi_2,aa)
        else:
            logging.error("Extra SCSI Disk not found")
            return (False,scsi_2,aa)
    else:
        logging.error("Failed to emulate the SCSI ID from C9 library")
        return (False,scsi_2,aa)        
def get_local_disk_linux(scsi_2,option):
        cmd1 = 'echo "- - -"'+' > '+'/sys/class/scsi_host/'
        cmd2 = '/scan'
        pp = 0
        kk = 0
        scsi_2 = []
        # Re-scan SCSI devices
        result1 = None
        line1 = None
        pre_scan = 'ls /sys/class/scsi_host/'
        result1 = subprocess.Popen(pre_scan,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True).stdout        
        while 1:
                line1 = result1.readline(5)                
                if not line1:
                    break                    
                else :
                    if line1 != '\n':                        
                        scan = cmd1+line1.strip('\n')+cmd2
                        logging.info("Scan command : %s" %scan)
                        os.system(scan)
                        kk +=1        
        if (kk == 0):
            logging.error("SCSI HOST not found")
            return (False,scsi_2,kk)
        else :
            filterdisk = "__scsi"+str(kk-1)+"__0.0.0"
            logging.info("Filter scsi_disk : %s" %filterdisk)
        # Get SCSI Disk ID
        checkdisk = 'ls /sys/class/scsi_disk/'
        result2 = None
        line2 = None
        result2 = subprocess.Popen(checkdisk,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True).stdout
        # Delete SCSI Disk ID without rebooting
        if (option == 'delscsiid'):
            cmd3 = 'echo 1'+' > '+'/sys/bus/scsi/drivers/sd/'
            cmd4 = '/delete'
            result3 = None        
        while 1:
                line2 = result2.readline()                
                if not line2 :
                    break                
                elif line2 != '\n':
                    diskinfo="__scsi"+line2[0]+"__"+line2[2]+"."+line2[4]+"."+line2[6]
                    scsiid = line2[0]+":"+line2[2]+":"+line2[4]+":"+line2[6]
                    if (int(line2[0]) != (kk-1)):
                        logging.info("Special case and change default filterdisk")
                        filterdisk = "__scsi"+line2[0]+"__0.0.0"
                    #filter the system volume out
                    if (diskinfo != filterdisk):
                        logging.info("Diskinfo :%s" % diskinfo)
                        scsi_2.insert(pp,diskinfo)
                        pp +=1
                        if (option == 'delscsiid'):
                            delcmd = cmd3+scsiid+cmd4
                            logging.info('Delete Command : %s' %delcmd)
                            result3 = subprocess.Popen(delcmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True).stdout
                        else:
                            continue
        if ((pp == 0) and (option == 'init')):
            logging.error("Extra SCSI Disk not found")
            return (False,scsi_2,pp)
        else :
            return (True,scsi_2,pp)
    
def executesc(accountID,passphrase,appfile,scpath,kms1):        
	result_str = None
	cmd =(appfile+" "+
		"--csp-id=Native "+
		"--guid="+accountID+" "+
		"--ignore-ssl-error "+
		"--timeout=10 "+
		"--url="+kms1+" "+
		"--passphrase="+'"'+passphrase+'"'+" "+
		"--register "+
		"--get-device-list "+
		"--with-provisioning "+
		"--publish-inventory "+
		"--quiet "+
		"--devices=device.conf")
	logging.info("Command: %s" %cmd)
	os.chdir(scpath)
	if(platform.system() == 'Linux'):
            cmd1 = subprocess.Popen(cmd,bufsize=1024,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True).stdout                
	if(platform.system() == 'Windows'):
            cmd1 = subprocess.Popen(cmd,bufsize=1024,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
	result_str = cmd1.read()
	#Execute Result:%s" % result_str
	logging.info("<== Step 2: Start to execute Activation process...")
	return (True)   

def startagent(scpath,servicename,mountpoint):
	os.chdir(scpath)
	try:
		subprocess.call(servicename,shell=True)
	except StandardError,message:
		logging.error("Start SC Runtime Agent error : %s" % message)
		return (False)
	else:
                logging.info("Start SC Runtime agent and waitting for encrypted volume : %s" % mountpoint)                
                waitting = 1
                trycount = 0
                #Waitting loop
                while waitting: 
                    try :
                           os.chdir(mountpoint)
                           if (trycount >= 600):
                               return (False)
                    except IOError,message:
                            logging.info("!!!%s" %message)
                            time.sleep(1)
                            trycount += 1
                            continue
                    except StandardError,message:
                            logging.info("***%s" %message)
                            time.sleep(1)
                            trycount += 1
                            continue
                    else :
                        logging.info(" Mount target volume successful...")
                        waitting = 0                                        
		logging.info("Current working path :%s" %os.getcwd())
		F1 = open('testfile.txt',"w")
		i = 0
		for i in range(100):
			F1.write("Add text "+str(i)+" into testfile\n")
			i +=1
		F1.close()
		try:
			(os.access('testfile.txt',os.R_OK) == True) and (os.remove('testfile.txt') == True)
		except IOError, message:
			logging.error("I/O error message :%s" % message)
			logging.error("File name testfile.txt or Path :%s" %os.getcwd())
			return (False)
		else:
                    logging.info("<== Step 3: Verify SC Runtim Agent and Mountpoint successful...")
                    return(True)
def main(argv):
        logger = logging.basicConfig(filename='activate.log',level=logging.DEBUG,format='%(asctime)s %(levelname)s : %(message)s -- @(%(lineno)d)')
        sver = "0.97.1"        
        t1 = datetime.datetime.now()
        try:
            options, args = getopt.getopt(sys.argv[1:],"hvuifea:p:",["para1=","para2="])
        except getopt.GetoptError:
            print 'Usage: activate.py -a AccountID -p Passphrase'
            sys.exit(2)        
        para1 = None
        para2 = None
        para3 = None
        accountID = None
        passphrase = None
        option = None
        extenddisk = 0
        getdisk = []
        purge = 0
        updateive = 0
        forcedeactive = 0
        scsi_2 = []
        for opt, arg in options:
            if opt == '-h':
                print 'Usage for Activation on Windows : activate.py -a AccountID -p "Passphrase"'
                print 'Usage for Activation on Linux   : python activate.py -a AccountID -p "Passphrase"'
                print 'Usage for Extenddisk : activate.py -p "Passphrase" -e'
                print 'Usage for Remove alld isk : activate.py -p "Passphrase" -u'
                print 'Usage for Inventory update : activate.py -p "Passphrase" -i'
                print 'Usage for Purge local data : activate.py -p "Passphrase" -f' 
                print '-a, option input AccountID,Example: 51B4AB97-2B6B-48CF-A198-CFA80E24D275' 
                print '-p, option input Passphrase,Example: KEtMwfM+Emi0'
                print '-e, option to extend disk size for windows only'
                print '-u, option to remove encryption disk after detached from hypervisor'
                print '-i, option to update inventory list to KMS server'
                print '-f, option to force purge all data for testing purpose'
                sys.exit()            
            if opt == '-v':                
                print 'Version:'+sver+' Author by: Trend Micro'                
                sys.exit()
            elif opt in ("-u"):
                purge = 1
            elif opt in ("-a","--para1"):
                accountID = arg
            elif opt in ("-p","--para2"):
                passphrase = arg            
            elif opt in ("-e"):
                extenddisk = 1                
            elif opt in ("-i"):
                updateive = 1
            elif opt in ("-f"):
                forcedeactive = 1
            else:
                return(False, "unhandled option")
        if (sys.version_info < (2,4,0)):
            print 'You need python 2.6 or later to run this script\n'
            return (False)
        logging.info('****** Start activation Process by script version %s ******' % sver)
        #market out the ID/Passphrase output
	#logging.info('AccID = %s, Passphrase = %s' %(accountID,passphrase))
        get_hostname()
        get_osinfo()
        #check platform and prepre default value
	if(platform.system() == "Windows"):
		mountpoint = "E:\\" #Define default mount point start from E drive for Windows
	        filesystem = "ntfs"
        	scpath = os.environ['PROGRAMFILES']+"\\Trend Micro\\SecureCloud\\Agent"
	        devicefile = os.environ['PROGRAMFILES']+"\\Trend Micro\\SecureCloud\\Agent\\device.conf"
        	appfile = "scconfig.exe"
	        backupfile = os.environ['PROGRAMFILES']+"\\Trend Micro\\SecureCloud\\Agent\\"+time.strftime("%H"+"%M"+"%S",time.localtime())+"_device.old"
        	servicename = "net start C9AgentSvc"
		stopsvr = "net stop C9AgentSvc"
	elif (platform.system() == "Linux"):
        	mountpoint = "/secure_disk1" #Define default mount point start from /secure_disk1 volume for Linux
	        filesystem = "ext3"
	        scpath = "/var/lib/securecloud"
	        devicefile = "/var/lib/securecloud/device.conf"
	        appfile = "./scconfig.sh"
        	backupfile = "/var/lib/securecloud/"+time.strftime("%H"+"%M"+"%S",time.localtime())+"_device.old"
	        servicename = "service scagentd start"
		stopsvr = "service scagentd stop"
	else:                
        	logging.error('The target OS = %s does not support !!!' %platform.system())
        	print 'OS not support yet'
	        return (False)        
        kms1 = "https://vm-sc3.twsme.qa.com:8443/"
	logging.info("==> Step 0: Checking Connection and permission...")
	if (get_adminrole(kms1) == True):		
                #Extend disksize for Windows platform only
                optresult = None
                if (extenddisk == 1):                    
                    if (platform.system() != "Windows"):
                        logging.error("Extend disksize support Windows platform only")
                        print 'The feature does not support %s platform' %platform.system()
                        return (False)
                    else :
                        optresult = diskopt(getdisk,servicename,stopsvr,passphrase,appfile)
                        if (optresult[0] == False):
                            print 'Exception!!! Some of Disk space extensios not available pleaes check result.log for more detail'                          
                        mountpoint = optresult[1][0]+":\\"                            
                        startagent(scpath,servicename,mountpoint)
                        t2= datetime.datetime.now()
			logging.info("Total process time :%s" %str(t2-t1))
			logging.info('====== Complete Extend disk process ======')
			print 'Extend disk process complete'
			return (True) 		    	
                subprocess.call(stopsvr,shell=True)
                #Remove encryption disk without rebooting process
                if (purge == 1):
                    if (remove_without_reboot(scsi_2,mountpoint,passphrase,appfile,scpath,servicename) == True):
                        t2 = datetime.datetime.now()
                        logging.info("Total process time :%s" %str(t2-t1))
                        logging.info('====== Complete Purge process ======')
                        print 'Remove encryption volume successful'
                        return (True)
                    else :
                        print 'Remove encryption volume failure!!!'
                        retrun (False)
                #Update inventory list to KMS server, no error handle yet
                if (updateive == 1):
                    update_inventory(passphrase,appfile)
                    subprocess.call(servicename,shell=True)
                    t2 = datetime.datetime.now()
		    logging.info("Total process time :%s" %str(t2-t1))
		    logging.info('====== Complete Inventory update process ======')
		    print 'Update inventory list successful'
		    return (True)
		#Force deactivate all encrypted volume
                if (forcedeactive == 1):
                    purgeall(scpath)                    
                    t2 = datetime.datetime.now()
		    logging.info("Total process time :%s" %str(t2-t1))
		    logging.info('====== Complete Deactive process ======')
		    print 'Force deactive all encryted devices successful'
		    return (True)
		#Normal Activation process start here
		logging.info("==> Step 1: Start to create device file...")
		if (gendevicefile(mountpoint,filesystem,scpath,devicefile,backupfile) == True):
			logging.info("==> Step 2: Start to execute Activation process...")
			if (executesc(accountID,passphrase,appfile,scpath,kms1) == True):
				logging.info("==> Step 3: Verify the SC Runtim Agent and mountpoint...")
				if (startagent(scpath,servicename,mountpoint) == True):
					t2 = datetime.datetime.now()
					logging.info("Total process time :%s" %str(t2-t1))
					logging.info('====== Complete Activation process ======')
					print 'Activation successful'
					return (True)
				else:
					logging.error("!!!Failed at Setp 3 Verification!!!")
 		    			subprocess.call(stopsvr,shell=True)
 		    			print 'Fail to start SC Runtime Agent!!!'
					return (False)
			else:
				logging.error("!!!Failed at Setp 2 Activation process!!!")
				print 'Faile to execute the activation command!!!'
				return (False)
		else:
                        logging.error("!!!Failed at Step 1 Create device file!!!")
                        print 'Faile to create device file!!!'
                        return (False)
	else:
        	logging.error("!!!Failed at Step 0 Connection or Permission issue!!!")
        	print 'Failed at pre-checking process!!!'
	        return (False)
if __name__ == '__main__':
    main(sys.argv[1:])  
