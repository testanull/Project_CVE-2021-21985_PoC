# Project_CVE-2021-21985_PoC

# JNI Compile

gcc -fPIC -I"$JAVA_HOME/include" -I"$JAVA_HOME/include/linux" -shared -o libhello.so HelloJNI.c