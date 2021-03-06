#!/usr/bin/python

import glob
import os
import sys
import re

# This script is run from Build/<target>_default.build/$(PX4_BASE)/Firmware/src/systemcmds/topic_listener

# argv[1] must be the full path of the top Firmware dir
# argv[2] (optional) is the full path to the EXTERNAL_MODULES_LOCATION

raw_messages = glob.glob(sys.argv[1]+"/msg/*.msg")
if len(sys.argv) > 2:
	external_raw_messages = glob.glob(sys.argv[2]+"/msg/*.msg")
	raw_messages += external_raw_messages # Append the msgs defined in the EXTERNAL_MODULES_LOCATION to the normal msg list
messages = []
topics = []
message_elements = []


for index,m in enumerate(raw_messages):
	temp_list_floats = []
	temp_list_uint64 = []
	temp_list_bool = []
	if("pwm_input" not in m and "position_setpoint" not in m):
		temp_list = []
		topic_list = []
		f = open(m,'r')
		for line in f.readlines():
			items = re.split('\s+', line.strip())

			if ('float32[' in items[0]):
				num_floats = int(items[0].split("[")[1].split("]")[0])
				temp_list.append(("float_array",items[1],num_floats))
			elif ('float64[' in items[0]):
				num_floats = int(items[0].split("[")[1].split("]")[0])
				temp_list.append(("double_array",items[1],num_floats))
			elif ('uint64[' in items[0]):
				num_floats = int(items[0].split("[")[1].split("]")[0])
				temp_list.append(("uint64_array",items[1],num_floats))
			elif ('uint16[' in items[0]):
				num_floats = int(items[0].split("[")[1].split("]")[0])
				temp_list.append(("uint16_array",items[1],num_floats))
			elif ('int32[' in items[0]):
				num_floats = int(items[0].split("[")[1].split("]")[0])
				temp_list.append(("int32_array",items[1],num_floats))
			elif ('int16[' in items[0]):
				num_floats = int(items[0].split("[")[1].split("]")[0])
				temp_list.append(("int16_array",items[1],num_floats))
			elif(items[0] == "float32"):
				temp_list.append(("float",items[1]))
			elif(items[0] == "float64"):
				temp_list.append(("double",items[1]))
			elif(items[0] == "uint64") and len(line.split('=')) == 1:
				temp_list.append(("uint64",items[1]))
			elif(items[0] == "uint32") and len(line.split('=')) == 1:
				temp_list.append(("uint32",items[1]))
			elif(items[0] == "uint16") and len(line.split('=')) == 1:
				temp_list.append(("uint16",items[1]))
			elif(items[0] == "int64") and len(line.split('=')) == 1:
				temp_list.append(("int64",items[1]))
			elif(items[0] == "int32") and len(line.split('=')) == 1:
				temp_list.append(("int32",items[1]))
			elif(items[0] == "int16") and len(line.split('=')) == 1:
				temp_list.append(("int16",items[1]))
			elif (items[0] == "bool") and len(line.split('=')) == 1:
				temp_list.append(("bool",items[1]))
			elif (items[0] == "uint8") and len(line.split('=')) == 1:
				temp_list.append(("uint8",items[1]))
			elif (items[0] == "int8") and len(line.split('=')) == 1:
				temp_list.append(("int8",items[1]))
			elif '# TOPICS' == ' '.join(items[:2]):
				for topic in items[2:]:
					topic_list.append(topic)

		f.close()

		(m_head, m_tail) = os.path.split(m)
		message = m_tail.split('.')[0]

		if len(topic_list) == 0:		
			topic_list.append(message)

		for topic in topic_list:
			messages.append(message)
			topics.append(topic)
			message_elements.append(temp_list)

num_messages = len(messages);

print("""

/****************************************************************************
 *
 *   Copyright (c) 2015 PX4 Development Team. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 * 3. Neither the name PX4 nor the names of its contributors may be
 *    used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 ****************************************************************************/

/**
 * @file topic_listener.cpp
 *
 * Autogenerated by Tools/generate_listener.py
 *
 * Tool for listening to topics when running flight stack on linux.
 */

#include <drivers/drv_hrt.h>
#include <px4_middleware.h>
#include <px4_app.h>
#include <px4_config.h>
#include <uORB/uORB.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

#ifndef PRIu64
#define PRIu64 "llu"
#endif

#ifndef PRId64
#define PRId64 "lld"
#endif

""")
for m in set(messages):
	print("#include <uORB/topics/%s.h>" % m)

print("""
extern "C" __EXPORT int listener_main(int argc, char *argv[]);

static bool check_timeout(const hrt_abstime& time) {
    if (hrt_elapsed_time(&time) > 2*1000*1000) {
		printf("Waited for 2 seconds without a message. Giving up.\\n");
        return true;
    }
    return false;
}
""")

for index, (m, t) in enumerate(zip(messages, topics)):
	print("void listen_%s(unsigned num_msgs, unsigned topic_instance);" % t)

print ("""
\nint listener_main(int argc, char *argv[]) {
	if(argc < 2) {
		printf("need at least two arguments: topic name. [optional number of messages to print] [optional instance]\\n");
		return 1;
	}
""")
print("\tunsigned num_msgs = (argc > 2) ? atoi(argv[2]) : 1;")
print("\tunsigned topic_instance = (argc > 3) ? atoi(argv[3]) : 0;\n")
for index, (m, t) in enumerate(zip(messages, topics)):
	if index == 0:
		print("\tif (strncmp(argv[1],\"%s\",50) == 0) {" % t)
	else:
		print("\t} else if (strncmp(argv[1],\"%s\",50) == 0) {" % t)
	print("\t\tlisten_%s(num_msgs, topic_instance);" % t)

print("\t} else {")
print("\t\t printf(\" Topic did not match any known topics\\n\");")
print("\t}")
print("\t return 0;")
print("}\n")

for index, (m, t) in enumerate(zip(messages, topics)):
	print("void listen_%s(unsigned num_msgs, unsigned topic_instance) {" % t)
	print("\tint sub = orb_subscribe_multi(ORB_ID(%s), topic_instance);" % t)
	print("\torb_id_t ID = ORB_ID(%s);" % t)
	print("\tstruct %s_s container;" % m)
	print("\tmemset(&container, 0, sizeof(container));")
	print("\tbool updated;")
	print("\tunsigned i = 0;")
	print("\thrt_abstime start_time = hrt_absolute_time();")
	print("\twhile(i < num_msgs) {")
	print("\t\torb_check(sub,&updated);")
	print("\t\tif (i == 0) { updated = true; } else { usleep(500); }")
	print("\t\tif (updated) {")
	print("\t\tstart_time = hrt_absolute_time();")
	print("\t\ti++;")
	print("\t\tprintf(\"\\nTOPIC: %s instance %%d #%%d\\n\", topic_instance, i);" % t)
	print("\t\torb_copy(ID,sub,&container);")
	print("\t\tprintf(\"timestamp: %\" PRIu64 \"\\n\", container.timestamp);")
	for item in message_elements[index]:
		if item[0] == "float":
			print("\t\tprintf(\"%s: %%8.4f\\n\",(double)container.%s);" % (item[1], item[1]))
		elif item[0] == "float_array":
			print("\t\tprintf(\"%s: \");" % item[1])
			print("\t\tfor (int j = 0; j < %d; j++) {" % item[2])
			print("\t\t\tprintf(\"%%8.4f \",(double)container.%s[j]);" % item[1])
			print("\t\t}")
			print("\t\tprintf(\"\\n\");")
		elif item[0] == "double":
			print("\t\tprintf(\"%s: %%8.4f\\n\",(double)container.%s);" % (item[1], item[1]))
		elif item[0] == "double_array":
			print("\t\tprintf(\"%s: \");" % item[1])
			print("\t\tfor (int j = 0; j < %d; j++) {" % item[2])
			print("\t\t\tprintf(\"%%8.4f \",(double)container.%s[j]);" % item[1])
			print("\t\t}")
			print("\t\tprintf(\"\\n\");")
		elif item[0] == "uint64":
			print("\t\tprintf(\"%s: %%\" PRIu64 \"\\n\",container.%s);" % (item[1], item[1]))
		elif item[0] == "uint64_array":
			print("\t\tprintf(\"%s: \");" % item[1])
			print("\t\tfor (int j = 0; j < %d; j++) {" % item[2])
			print("\t\t\tprintf(\"%%\" PRIu64 \" \",container.%s[j]);" % item[1])
			print("\t\t}")
			print("\t\tprintf(\"\\n\");")
		elif item[0] == "uint16_array":
			print("\t\tprintf(\"%s: \");" % item[1])
			print("\t\tfor (int j = 0; j < %d; j++) {" % item[2])
			print("\t\t\tprintf(\"%%u \",container.%s[j]);" % item[1])
			print("\t\t}")
			print("\t\tprintf(\"\\n\");")
		elif item[0] == "int32_array":
			print("\t\tprintf(\"%s: \");" % item[1])
			print("\t\tfor (int j = 0; j < %d; j++) {" % item[2])
			print("\t\t\tprintf(\"%%d \",container.%s[j]);" % item[1])
			print("\t\t}")
			print("\t\tprintf(\"\\n\");")
		elif item[0] == "int16_array":
			print("\t\tprintf(\"%s: \");" % item[1])
			print("\t\tfor (int j = 0; j < %d; j++) {" % item[2])
			print("\t\t\tprintf(\"%%d \",container.%s[j]);" % item[1])
			print("\t\t}")
			print("\t\tprintf(\"\\n\");")
		elif item[0] == "int64":
			print("\t\tprintf(\"%s: %%\" PRId64 \"\\n\",container.%s);" % (item[1], item[1]))
		elif item[0] == "int32":
			print("\t\tprintf(\"%s: %%d\\n\",container.%s);" % (item[1], item[1]))
		elif item[0] == "uint32":
			print("\t\tprintf(\"%s: %%u\\n\",container.%s);" % (item[1], item[1]))
		elif item[0] == "int16":
			print("\t\tprintf(\"%s: %%d\\n\",(int)container.%s);" % (item[1], item[1]))
		elif item[0] == "uint16":
			print("\t\tprintf(\"%s: %%u\\n\",(unsigned)container.%s);" % (item[1], item[1]))
		elif item[0] == "int8":
			print("\t\tprintf(\"%s: %%d\\n\",(int)container.%s);" % (item[1], item[1]))
		elif item[0] == "uint8":
			print("\t\tprintf(\"%s: %%u\\n\",(unsigned)container.%s);" % (item[1], item[1]))
		elif item[0] == "bool":
			print("\t\tprintf(\"%s: %%s\\n\",container.%s ? \"True\" : \"False\");" % (item[1], item[1]))
	print("\t\t} else {")
	print("\t\t\tif (check_timeout(start_time)) {")
	print("\t\t\t\tbreak;")
	print("\t\t\t}")
	print("\t\t}")
	print("\t}")
	print("\torb_unsubscribe(sub);")
	print("}\n")