class PythonRunner:
	
	#initialize the module as an object
	def __init__(self):
		self.text = "Hello World!"
	
	#run the module
	def run(self, prompt = ""):
		if prompt[:7] == "python ":
			try:
				exec(prompt[7:])
			except Exception as e:
				print(f"Error: {e}")
		else: #else complain
			print("Illegal Prompt")
	
	#return keywords relevant to the module, used to figure out which module to run
	def getKeywords(self):
		return ["python"]
	
	#return human-readable name of module
	def getName(self):
		return "Python Runner"
	
	#whether self module is appropriate for any prompt (ex. search engine)
	def isGeneric(self):
		return False
