#!/usr/bin/python

import logging
from struct import pack, unpack

import numpy as np
from src import config

def float_to_bin(f):
    # Pack the float into 4 bytes using IEEE-754 single-precision format
    packed = pack('>f', f)
    # Unpack the bytes as integers
    integers = unpack('>I', packed)
    # Convert the integer to binary representation
    binary = bin(integers[0])[2:].zfill(32)
    return binary

def binary_to_float(binary_str):
    # Determine the sign bit, exponent bits, and mantissa bits
    sign_bit = int(binary_str[0])
    exponent_bits = binary_str[1:9]
    mantissa_bits = binary_str[9:]

    # Convert binary parts to decimal
    exponent = int(exponent_bits, 2) - 127
    mantissa = 1  # Implicit leading 1 in IEEE 754 format

    for i in range(len(mantissa_bits)):
        if mantissa_bits[i] == '1':
            mantissa += 2 ** -(i + 1)

    # Calculate the final floating-point value
    result = (-1) ** sign_bit * mantissa * (2 ** exponent)

    return result

def protect(float_parameter, bit, valor, status):
	#Returns the proposed value to protect float_parameter by

	#Sanity check
	if (float_parameter != valor):
		raise("ERROR")
	else:
		binary_representation = float_to_bin(float_parameter)
		sign = binary_representation[0]
		old_exponent = binary_representation[1:9]

		if status == "Empty":
			#Substract one from the exponent and fill the mantissa with '1's
			new_exponent = '0' + bin((int(old_exponent, 2) - 1))[2:]
			mantissa_nueva = '1' * 23

		elif status == "Full":
			#Add one to the exponent and fill the mantissa with '0's
			new_exponent = '0' + bin((int(old_exponent, 2) + 1))[2:]
			mantissa_nueva = '0' * 23
		else:
			raise("ERROR")

	return binary_to_float(sign + new_exponent + mantissa_nueva)

def check_exponent_bits_completiveness(binary_representation):
	# Calculate if the exponent is 1-bit far or 2-bit far from completiveness (the eight bits being '1')
	# The function returns a tuple where the first element is the operation that can be performed on the exponent
	# ('Substract', 'Both', 'None') and the second element is the position where bit value is '0' (0 for the MSB of the
	# exponent, 7 for the LSB of the exponent) only if we are interested on it

	exponent_bits = binary_representation[1:9]

    # Check if the first bit of the exponent is 0
	if exponent_bits[0] == '0':
    	# Check if the rest of the exponent bits are all '1' except one
		# Only substraction is allowed (0111 1111)
		if exponent_bits[1:].count('1') == 7:
			return 'Restar', 0
		elif exponent_bits[1:].count('1') == 6:
			# Not interested in 0111 1110
			if exponent_bits[7] == '0':
				return None, None
			# Only substraction is allowed (0111 1101)
			elif exponent_bits[6] == '0':
				return 'Restar', 6
			# Rest of valid cases
			else:
				return 'Ambos', (exponent_bits[1:].find('0') + 1)
		else:
			return None, None
	return None, None

def check_mantissa_bits_status(binary_representation, upp_thr, low_thr):
    # Calculate if the mantissa value is higher than upp_thr or lower than low_thr
    # thresholds (it is never smaller than 1 by definition)
    # If it is higher, it is considered to be "full", so return values are:
    # 	"Full", mantissa_value
    # If it is smaller, it is considered to be "empty", so return values are:
    #	"Empty", mantissa_value
    # If it is neither higher nor smaller, the return values are:
    #	False, None

	mantissa_bits = binary_representation[9:32]
	mantissa_value = 1

	for i in range(len(mantissa_bits)):
		mantissa_value += int(mantissa_bits[i]) * 2**(-(i+1))

	if mantissa_value >= upp_thr:
		return "Full", mantissa_value
	elif mantissa_value <= low_thr:
		return "Empty", mantissa_value
	else:
		return False, None

def print_valuable_information(float_parameter, train_parameter_binary, pos, mantissa_value, status):
	print("The parameter has a value of: ", float_parameter)
	print("Its exponent is: ", train_parameter_binary[1:9])
	print("The exponent has a '0' in position (starting from the left): ", pos)
	print("The old mantissa is: ", mantissa_value)
	print("The mantissa is said to be: ", status)
	print(" - - - - - - - - - - - - - - - - - - - - - - - - -")
	return

class actions():
	def __init__(
		self, model, confFile, infoArray=None, verbose = 0, log_level="ERROR", **kwargs
		):

		# Logging setup
		logging.basicConfig()
		logging.getLogger().setLevel(log_level)
		logging.debug("Logging level set to {0}".format(log_level))

		# Retrieve config params
		analysisConf = config.config(confFile)
		self.Model = model # No more passing or using a session variable in TF v2

		# Call the corresponding analysis function
		analysisFunc = getattr(self, analysisConf["Action"])
		analysisFunc(model, analysisConf, infoArray, verbose, **kwargs)

	def completiveness_analysis(self, model, analysisConf, infoArray = None, verbose = 0, **kwargs):
		num_trainable_variables = len(model.trainable_variables)
		contBias = 0
		contPeso = 0
		info = []

		for layernum in range(num_trainable_variables):
			v = model.trainable_variables[layernum]
			train_variables_numpy = v.numpy()
			upp_thr = analysisConf['Upp_thr']
			low_thr = analysisConf['Low_thr']

			if len(v.shape) == 1:
				for i in range(v.shape[0]):
					float_parameter = train_variables_numpy[i]
					train_parameter_binary = float_to_bin(float_parameter)
					completiveness, pos = check_exponent_bits_completiveness(train_parameter_binary)

					if completiveness == None:
						None
					elif completiveness == 'Ambos':
						status, mantissa_value = check_mantissa_bits_status(train_parameter_binary, upp_thr, low_thr)
						if status == "Empty" or status == "Full":
							contBias += 1
							if verbose > 1:
								print_valuable_information(float_parameter, train_parameter_binary, pos, mantissa_value, status)
							info.append([layernum, i, None, None, None, pos, float_parameter, status])
					elif completiveness == 'Restar':
						status, mantissa_value = check_mantissa_bits_status(train_parameter_binary, upp_thr, low_thr)
						if status == "Empty":
							contBias += 1
							if verbose > 1:
								print_valuable_information(float_parameter, train_parameter_binary, pos, mantissa_value, status)
							info.append([layernum, i, None, None, None, pos, float_parameter, status])
					else:
						raise

			else:
				for i in range(v.shape[0]):
					for j in range(v.shape[1]):
						for k in range(v.shape[2]):
							for l in range(v.shape[3]):
								float_parameter = train_variables_numpy[i, j, k, l]
								train_parameter_binary = float_to_bin(float_parameter)
								completiveness, pos = check_exponent_bits_completiveness(train_parameter_binary)

								if completiveness == None:
									None
								elif completiveness == 'Ambos':
									status, mantissa_value = check_mantissa_bits_status(train_parameter_binary, upp_thr, low_thr)
									if status == "Empty" or status == "Full":
										contPeso += 1
										if verbose > 1:
											print_valuable_information(float_parameter, train_parameter_binary, pos, mantissa_value, status)
										info.append([layernum, i, j, k, l, pos, float_parameter, status])
								elif completiveness == 'Restar':
									status, mantissa_value = check_mantissa_bits_status(train_parameter_binary, upp_thr, low_thr)
									if status == "Empty":
										contPeso += 1
										if verbose > 1:
											print_valuable_information(float_parameter, train_parameter_binary, pos, mantissa_value, status)
										info.append([layernum, i, j, k, l, pos, float_parameter, status])
								else:
									raise
		if verbose > 0:
			print("Number of bias that are going to be protected:", contBias)
			print("Number of weights that are going to be protected:", contPeso)

		print("Analysis info has been saved to:", infoArray)
		np.save(infoArray, info)

	def protection(self, model, analysisConf=None, infoArray=None,  verbose = 0, **kwargs):

		info = np.load(infoArray, allow_pickle=True)
		for i, information in enumerate(info):
			layernum = information[0]
			v = model.trainable_variables[layernum]
			train_variables_numpy = v.numpy()

			ind0 = information[1]
			ind1 = information[2]
			ind2 = information[3]
			ind3 = information[4]
			bit = information[5]
			valor = information[6]
			status = information[7]

			if (ind1 != None) and (ind2 != None) and (ind3 != None):
				float_parameter = train_variables_numpy[ind0, ind1, ind2, ind3]
				if verbose > 0:
					print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -:")
					print("The unprotected parameter is:", float_parameter)
					protected_parameter = protect(float_parameter, bit, valor, status)
					print("The protected parameter is:", protected_parameter)
					train_variables_numpy[ind0, ind1, ind2, ind3] = protected_parameter
				else:
					train_variables_numpy[ind0, ind1, ind2, ind3] = protect(float_parameter, bit, valor, status)
			else:
				float_parameter = train_variables_numpy[ind0]
				if verbose > 0:
					print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -:")
					print("The unprotected parameter is:", float_parameter)
					protected_parameter = protect(float_parameter, bit, valor, status)
					print("The protected parameter is:", protected_parameter)
					train_variables_numpy[ind0] = protected_parameter
				else:
					train_variables_numpy[ind0] = protect(float_parameter, bit, valor, status)

			v.assign(train_variables_numpy)