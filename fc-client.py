from libfptr10 import IFptr
from pathlib import Path
from datetime import datetime
from platform import architecture
import socket, requests, re, logging, sys, os, gzip

logging.basicConfig(level=logging.NOTSET, filename='fc-client-' + datetime.today().strftime("%Y%m%d%H%M%S") + '.log')
logger = logging.getLogger('fc-client')

# Get computer name
computerName = socket.gethostname()

# Set your Fiscalcheck server IP-address
server = 'SERVER_IP'

def exceptionHandler(type, value, tb):
    logger.critical(str(tb.tb_lineno) + " : Uncaught exception: {0}".format(str(value)))
    requests.post(f"http://{server}/api/error", json={"name": computerName, "message": str(tb.tb_lineno) + ' : ' + str(value), "dt": datetime.today().strftime("%Y-%m-%d %H:%M:%S")})

sys.excepthook = exceptionHandler

# Read logs and try to connect
fptr = IFptr()
fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_MODEL, str(IFptr.LIBFPTR_MODEL_ATOL_AUTO))
try:
    with open(str(Path.home()) + '\\AppData\\Roaming\\ATOL\\drivers10\\logs\\fptr10.log', 'r', encoding="utf-8") as log:
        logs = ''.join(log.readlines())
    ip = re.findall('"IPAddress" : \S+', logs)[0].replace('"IPAddress" : ', '').replace('"', '').replace(',', '')
except:
    aged = list(sorted(list(filter(lambda x: x[-3:] == '.gz', os.listdir(str(Path.home()) + '\\AppData\\Roaming\\ATOL\\drivers10\\logs'))), 
                    key=lambda x: os.path.getctime(str(Path.home()) + '\\AppData\\Roaming\\ATOL\\drivers10\\logs\\' + x), reverse=True))
    index = 0
    try:
        with gzip.open(str(Path.home()) + '\\AppData\\Roaming\\ATOL\\drivers10\\logs\\' + aged[index]) as file:
            logs = file.read()
    except:
        index += 1
    finally:
        with gzip.open(str(Path.home()) + '\\AppData\\Roaming\\ATOL\\drivers10\\logs\\' + aged[index]) as file:
            logs = str(file.read())
        try:
            ip = re.findall('"IPAddress" : \S+', logs)[0].replace('"IPAddress" : ', '').replace('"', '').replace(',', '')
        except:
            ip = '192.168.1.10'
            requests.post(f"http://{server}/api/error", json={"name": computerName, "message": 'SET DEFAULT USB', "dt": datetime.today().strftime("%Y-%m-%d %H:%M:%S")})
if ip == '192.168.1.10':
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_USB))
else:
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_TCPIP))
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_IPADDRESS, ip)
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_IPPORT, "5555")
fptr.applySingleSettings()
fptr.open()
if not fptr.isOpened():  # If script can't connect to device, try to reconnect
    while not fptr.isOpened():
        fptr.open()

# Get registration number
fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
fptr.fnQueryData()
regNumber = fptr.getParamString(1037)

# Get serial number
fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_STATUS)
fptr.queryData()
serialNumber = fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER)

# Get address
fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
fptr.fnQueryData()
address = fptr.getParamString(1009)

# Get company name
fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
fptr.fnQueryData()
companyName = fptr.getParamString(1048)

# Get expiration date
fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_VALIDITY)
fptr.fnQueryData()
expirationDate = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME).strftime("%Y-%m-%d")

# Close connection and write information to log-file
fptr.close()

# Send data to server
check = requests.get(f"http://{server}/api/kkm/" + regNumber)
if check.status_code == 404:
    req = requests.post(f"http://{server}/api/kkm", json={"reg": regNumber, "ser": serialNumber, "name": computerName, "exp": expirationDate, "adr": address, "yl": companyName})
elif check.status_code == 200:
    req = requests.put(f"http://{server}/api/kkm/" + regNumber, json={"reg": regNumber, "ser": serialNumber, "name": computerName, "exp": expirationDate, "adr": address, "yl": companyName})