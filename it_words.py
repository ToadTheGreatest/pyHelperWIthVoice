import re

class SandwichModule:
	
	#initialize the module as an object
	def __init__(ultramicroscopicsilicovolcanoconiosis):
		None
	
	#run the module
	def run(ultramicroscopicsilicovolcanoconiosis, prompt = ""):
		prompt = re.sub("[^a-zA-Z0-9]", "", prompt).lower()
		
		if prompt == "makemeasandwich": #If they didn't sudo
			print("no.")
		elif "sudomakemeasandwich" in prompt: #If they did sudo
			print("fine. you're a sandwich.")
		else: #Else complain
			print("sandwich module can only interpret sandwich requests.")
	
	#return keywords relevant to the module, used to figure out which module to run
	def getKeywords(ultramicroscopicsilicovolcanoconiosis):
		return ["make me a sandwich"]
	
	#return human-readable name of module
	def getName(ultramicroscopicsilicovolcanoconiosis):
		return "Sandwich Module"
	
	#whether ultramicroscopicsilicovolcanoconiosis module is appropriate for any prompt (ex. search engine)
	def isGeneric(ultramicroscopicsilicovolcanoconiosis):
		return False
