## 
## Copyright (C) 2016-2017 by  Yuan Lufeng
## See license.txt for full license and copyright notice.
## 
## Authors: Yuan Lufeng 
## 
## time_process_stack.py
## 
##  Created on: Nov 5th, 2016
##      Author: Yuan Lufeng 
## 
## \brief Handle the frame using ProcessStack in current timepoint
##
##

import _process_stack as _ps 

def TimepointProcessStack(session):
	parameter = session.split(" ")
	parameterNum = int(parameter[0])
	configFilename = parameter[1]
	frame = int(parameter[2])
	error = _ps.ProcessStack_py(parameterNum, configFilename, frame)
	return error
