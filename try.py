import subprocess 

  

GET_IP_CMD ="hostname -I" 

  

def run_cmd(cmd):

    return subprocess.check_output(cmd, shell=True).decode('utf-8') 

  

ip = run_cmd(GET_IP_CMD) 

  

print(ip) 