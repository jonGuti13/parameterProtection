### Introduction
This repository contains the code which was developed to perform the analysis and protection of the TensorFlow 2 Deep Learning models as described in []. It is written in Python 3 and makes use of the Keras Model APIs to protect weights and biases against bit-flips under certain circumstances.

### Dependencies
The code has been tested with the following packages in the following versions.
1. TensorFlow framework (tested with 2.12.0)

2. Python (tested with 3.8.6)

3. Keras framework (tested with 2.12.0, part of TensorFlow)

4. numpy package (tested with 1.23.5, part of TensorFlow)

Alternatively, you can use the [Dockerfile](parameterProtection/Dockerfile) we provide to build the image with all the necessary dependencies contained on it.

### Installation

Installation just consists of downloading the source code by cloning the repository.

`git clone git@github.com:jonGuti13/parameterProtection.git`

### Usage

#### Step 1: perform the analysis of the model
You can perform the analysis of the model by specifying the path where the model is located, the path to the analysis .yml, the level of protection to be applied
and the level of verbosity as follows:

`python3 analysis.py -m "./models/example.h5" -c "./conf/completivenessAnalysis.yaml" -p 0 -v 0`

#### Step 2: protect the model with a certain protection level
You can perform the analysis of the model by specifying the path where the model is located, the path to the analysis .yml, the path to the analysis .npy, the level of protection to be applied and the level of verbosity as follows:

`python3 protection.py -m "./models/example.h5" -c "./conf/completivenessAnalysis.yaml" -p 0 -i "./conf/completiveness_analysis_u0_l0.npy" -v 0`

The protected model is going to be saved at "./models/example_u0_l0.h5"

#### Rest of the steps:
The rest of the steps consists of verifying if the selected protection level damages the model in absence of faults, performing the fault injection campaign and evaluating how much more robust the model is, but these steps are out of the scope of this repository and can be done, as explained in [], using [TensorFI2](https://github.com/DependableSystemsLab/TensorFI2).

### Resumed theoretical explanation
As described in []() we are only interested in protecting the parameters which are one position away of having the (partial) exponent full in IEEE-754 single floating point representation. Partial exponent is defined as the 7 least significant bits of the exponent when the MSB is '0'. Apart from having the (partial) exponent that way, the mantissa value of the parameters must also fullfil a certain condition. It needs to be above/below a threshold value as specified by the threshold values for the different protection levels.

All in all, we are only interested in the following situations:
- 1-bit far if that bit is the leftmost one	(from \pm 1 to \pm inf or from 1._____ to Nan)
	- 0111 1111 (1) substraction of the exponent is only allowed
    	- Substraction --> 0111 1110 (0.5)
- 2-bit far if one of the bits is the leftmost one (from smaller numbers than 1 to higher numbers than 1, leaving the sign bit apart)
    - 0011 1111 (5.42101086243e-20) both substraction and addition of the exponent are allowed
        - Addition --> 0011 1110 (2.71050543121e-20)
        - Substraction --> 0100 0000 (1.08420217249e-19)
    - 0101 1111 (2.32830643654e-10) both substraction and addition of the exponent are allowed
        - Addition --> 0101 1110 (1.16415321827e-10)
        - Substraction --> 0110 0000 (4.65661287308e-10)
    - 0110 1111 (1.52587890625e-05) both substraction and addition of the exponent are allowed
        - Addition --> 0110 1110 (7.62939453125e-06)
        - Substraction --> 0111 0000 (3.0517578125e-05)
    - 0111 0111 (0.00390625) both substraction and addition of the exponent are allowed
        - Addition --> 0111 0110 (0.001953125)
        - Substraction --> 0111 1000 (0.0078125)
    - 0111 1011 (0.0625) both substraction and addition of the exponent are allowed
        - Addition --> 0111 1010 (0.03125)
        - Substraction --> 0111 1100 (0.125)
    - 0111 1101 (0.25) only substraction of the exponent is allowed
        - Substraction --> 0111 1100 (0.125)
    - 0111 1110 case is not useful for us

### Citing
If you find these repo useful, please consider citing it as [].