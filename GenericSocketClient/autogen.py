import json

obj_type_convertor = {
	"UINT" : "NSUInteger",
	"FLOAT" : "CGFloat",
}

obj_type_nsnum_convertor = {
	"UINT" : "intValue",
	"FLOAT" : "floatValue",
}


class CodeGenerator(object):

	def __init__(self, json_file):
		self._json_data  = open(json_file)
		self._all_data   = json.load(self._json_data)
		self._event_data = self._all_data["events"]
		
		return

	def generateEventStructures(self):

		return_str = "\n\n"
		
		for event in self._event_data:

			return_str += "@interface %sEvent : NSObject\n\n" % event["name"]

			for param in event["params"]:

				return_str += "@property %s %s;\n" % (obj_type_convertor[event["params"][param]], param)

			return_str += "\n@end\n\n"
			return_str += "\n@implementation %sEvent\n\n" % event["name"]

			for param in event["params"]:

				return_str += "@synthesize %s;\n" % (param)

			return_str += "@end\n\n"



		return return_str

	def generateMessageSeparators(self):
		return """
#define kMessageSeparator @"%s"
#define kParamSeperator @"%s"
		""" % (self._all_data["message_seperator"], self._all_data["param_separator"])		

	def generateEventLoadingCode(self, event):
		
		return_str = ""

		param_count = 1

		for param in event["params"]:
			return_str += "event.%s = [[components objectAtIndex:%d] %s];\n\t" % (param, param_count, obj_type_nsnum_convertor[event["params"][param]])
			param_count += 1

		return return_str

	def generateTransportReceiver(self):

		return_str = "\n\n"

		for event in self._event_data:

			return_str += """

if([cmd isEqualToString:@"%s"])
{
	%sEvent *event = [[%sEvent alloc] init];

	%s
	[[NSNotificationCenter defaultCenter] postNotificationName:%s object:event];

}

""" % (event["short_name"], event["name"], event["name"], self.generateEventLoadingCode(event), "k%sNotification" % event["name"])
		
		return return_str

	def generateNotificationDefines(self):

		return_str = ""

		for event in self._event_data:
			return_str += "#define k%sNotification @\"%s\"\n" % (event["name"], event["name"])

		return return_str