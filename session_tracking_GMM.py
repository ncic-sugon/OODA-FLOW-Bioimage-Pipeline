## 
## Copyright (C) 2016-2017 by  Yuan Lufeng
## See license.txt for full license and copyright notice.
## 
## Authors: Yuan Lufeng 
## 
## session_tracking_GMM.py
## 
##  Created on: Dec 18th, 2016
##      Author: Yuan Lufeng 
## 
## \brief Handle the frame using TrackingGMM in current session
##
##

import _tracking_GMM as _tGMM 

def SessionTrackingGMM(session):
	parameter = session.split(" ")
	parameterNum = int(parameter[0])
	configFilename = parameter[1]
	begin_frame = int(parameter[2])
	end_frame = int(parameter[3])
	error = _tGMM.TrackingGMM_py(parameterNum, configFilename, begin_frame, end_frame)
	return error
#def TimepointProcessStack(session):
#	parameter = session.split(" ")
#	parameterNum = int(parameter[0])
#	configFilename = parameter[1]
#	frame = int(parameter[2])
#	error = _ps.ProcessStack_py(parameterNum, configFilename, frame)
#	return error
