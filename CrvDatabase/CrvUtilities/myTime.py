# -*- coding: utf-8 -*-
## File = 'myTime.py"
#
#	A python script to return the time and 
#	date from the computer when called.
#		Written by Merrill Jenkins 2014Dec17
#			Department of Physics
#			University of South Alabama
#			Mobile, AL 36688
#	Used "Core Python Programmaing", Page 49
#	And "Python Essential Reference", Page 405
#
#	To use:
#		import myTime *
#		t = myTime()
#		t.getComputerTime()	# call at instant you want time
#		t.getCalendarDate()	# returns string with calandar date
#		t.getClockTime()	# returns as string with the clock time
#	To test, just run this file (with stand alone test program at the end)
#		python myTime.py
#	Other functions available:
#		getYear()	# returns string with year
#		getMon()	# returns string with month
#		getDay()	# returns string with day
#		getHour()	# returns string with hour
#		getSec()	# returns string with second
#		getDayOfWeek()	# returns string with the day of the week
#		getTimeZone()	# returns string with the time zone
#		getInternationalCalendarDate()	# returns string with calendar date and time zone
#		getInternationalClockTime()	# returns string with time and time zone
#		getTimeForSavedFiles()		# returns string with calandar date and time 
#						# in format to use with file name
#		getInternationalTimeForSavedFiles()	# returns string with calandar date, 
#							# time and time zone in format to us
#							# with file name
#
##  To transmit any changes to the dependent
##  python scripts, complete these steps in the
##  Utilities directory:
##     > rm Utilities.zip
##     > zip -r Utilities.zip *.py
#
#!/bin/env python
from time import *
class myTime:
	def __init__(self):
		# Initialize variables... 
		self.date   = 0; self.year = 0; self.month = 0
		self.day    = 0; self.hour = 0; self.minute = 0
		self.second = 0; self.tmeZone = 0; self.dayOfWeek = 0
		self.calendarDate = 0; 
		self.calendarDateWithDay = 0;
		self.clockTime = 0
		self.clockTime = 0
		self.timeForSavedFiles = 0;
		self.inputTuple = ''
		self.computerTime = ''
#
#		Get the computer time at the instant this method is called
#		This time is decoded into useful strings with the other methods
	def getComputerTime(self):
		# Initialize before each call to the computer clock.
		self.date   = 0; self.year = 0; self.month = 0
		self.day    = 0; self.hour = 0; self.minute = 0
		self.second = 0; self.tmeZone = 0; self.dayOfWeek = 0
		self.calandarDate = 0; self.clockTime = 0
		self.timeForSavedFiles = 0;
		# Load the tuple that has the computer time.
		self.inputTuple = ''
		self.inputTuple = localtime()
		self.computerTime = asctime(self.inputTuple)
	def getDate(self):			# method to get
		self.date = self.computerTime
		return(self.date)
	def getYear(self):
		self.year = self.computerTime[20:24]
		return(self.year)
	def getMonth(self):			# method to get month
		self.month = self.computerTime[4:7]
		return(self.month)
	def getDay(self):			# method to get day
		self.day = self.computerTime[8:10]
#		if int(self.day) < 10:
		if self.computerTime[8:9] == ' ':
			self.day=self.computerTime[9:10]
		return(self.day)
	def getZeroDay(self):			# method to get day
		self.day = '0d2' % self.computerTime[8:10]
#		if int(self.day) < 10:
#		if self.computerTime[8:9] == ' ':
#			self.day=self.computerTime[9:10]
		return(self.day)
	def getHour(self):			# method to get hour
		self.hour = self.computerTime[11:13]
		return(self.hour)
	def getMin(self):			# method to get minutes
		self.minute = self.computerTime[14:16]
		return(self.minute)
	def getSec(self):			# method to get seconds
		self.second = self.computerTime[17:19]
		return(self.second)
	def getTimeZone(self):			# method to get time zone
		self.timeZone = strftime('%Z',self.inputTuple)
		return(self.timeZone)
	def getDayOfWeek(self):			# method to get day of the week
		self.dayOfWeek = self.computerTime[0:3]
		return(self.dayOfWeek)
	def getCalendarDate(self):		# construct the calandar date
		myMonth = self.getMonth()
		myDay  = self.getDay()
		myYear = self.getYear()
		self.calendarDate = myMonth+'/'+myDay+'/'+myYear
		return(self.calendarDate)
	def getCalendarDateWithDay(self):	# construct the calandar date
		myMonth = self.getMonth()
		myDay  = self.getDay()
		myYear = self.getYear()
		myDayOfWeek = self.getDayOfWeek()
		self.calendarDateWithDay = '('+myDayOfWeek+')'+myMonth+'/'+myDay+'/'+myYear
		return(self.calendarDateWithDay)
	def getClockTime(self):			# construct the local wall clock time
		myHour   = self.getHour()
		myMinute = self.getMin()
		mySecond = self.getSec()
		self.clockTime = myHour+':'+myMinute+':'+mySecond
		return(self.clockTime)
	def getInternationalClockTime(self):		# construct the local wall clock time
							# with Time Zone
		myHour   = self.getHour()
		myMinute = self.getMin()
		mySecond = self.getSec()
		myTimeZone = self.getTimeZone()
		myclockTime = myTimeZone+'::'+myHour+':'+myMinute+':'+mySecond
		return(myclockTime)
	def getTimeForSavedFiles(self):		# construct a string to be included in file names
		myMonth  = self.getMonth()
		myDay    = self.getDay()
		myYear   = self.getYear()
		myHour   = self.getHour()
		myMinute = self.getMin()
		mySecond = self.getSec()
		self.timeForSavedFiles = '_'+myYear+myMonth+myDay+'_'+myHour+'_'+myMinute+'_'+mySecond+'_'
		return(self.timeForSavedFiles)
	def getInternationalTimeForSavedFiles(self):	# construct a string to be included 
							# in file names with time zone
		myMonth  = self.getMonth()
		myDay    = self.getDay()
		myYear   = self.getYear()
		myHour   = self.getHour()
		myMinute = self.getMin()
		mySecond = self.getSec()
		myTimeZone = self.getTimeZone()
		myTimeForSavedFiles = '_'+myTimeZone+'_'+myYear+myMonth+myDay+'_'+myHour+'_'+myMinute+'_'+mySecond+'_'
		return(myTimeForSavedFiles)
#
#   Test as stand alone.... This program only runs if this script is run in the command line:
#			python myTime.py
if __name__ == "__main__": 
	whatTimeIsIt = myTime()
	whatTimeIsIt.getComputerTime()
	print 'Date = %s' % whatTimeIsIt.getDate()
	print 'Year = %s' % whatTimeIsIt.getYear()
	print 'Month = %s' % whatTimeIsIt.getMonth()
	print 'Day = %s' % whatTimeIsIt.getDay()
	print 'Hour = %s' % whatTimeIsIt.getHour()
	print 'Minute = %s' % whatTimeIsIt.getMin()
	print 'Second = %s' % whatTimeIsIt.getSec()
	print 'Day of the Week  = %s' % whatTimeIsIt.getDayOfWeek()
	print 'TimeZone = %s' % whatTimeIsIt.getTimeZone()
        print ; print
        print '------------------------- '
	print 'Calendar = %s' % whatTimeIsIt.getCalendarDate()
	print 'Calendar with Day of Week  = %s' % whatTimeIsIt.getCalendarDateWithDay()
	print 'Clock Time = %s' % whatTimeIsIt.getClockTime()
	print 'International Clock Time = %s' % whatTimeIsIt.getInternationalClockTime()
	print 'FileNameFragment = %s' % whatTimeIsIt.getTimeForSavedFiles()
	print 'FileNameFragment (with Time Zone) = %s' % whatTimeIsIt.getInternationalTimeForSavedFiles()
##   Test that clock is updated after each call:
	from time import sleep
	print; print; print ' ============================ '
	for mm in range(1,10):
		whatTimeIsIt.getComputerTime()
		myDate = whatTimeIsIt.getCalendarDateWithDay()
		myTime = whatTimeIsIt.getInternationalClockTime()
		print '%s Clock Time = %s' %(myDate,myTime)
		sleep(1.0)		# ask the script to sleep for one second between iterations
