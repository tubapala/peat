#! /bin/env python
#
# Protein Engineering Analysis Tool Structure Analysis (PEATSA)
# Copyright (C) 2010 Michael Johnston & Jens Erik Nielsen
#
# Author: Michael Johnston
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Email: Jens.Nielsen_at_gmail.com
# Normal mail:
# Jens Nielsen
# SBBS, Conway Institute
# University College Dublin
# Dublin 4, Ireland
#
#
#  ColumnStat.py
#  ProteinDesignTool
#
#  Created by Michael Johnston on 18/06/2010.
#  Copyright (c) 2010 UCD. All rights reserved.
#
import PEATSA.Core as Core
import optparse
import numpy, math, sys
import scipy.stats.stats as stats
import scipy.stats.distributions as distributions
import scipy.stats

def normalityTests(array):

	#Histogram
	#print scipy.stats.describe(array)

	histogram, xedges = numpy.histogram(array, 100, new=True)
	histogram = Core.Matrix.Matrix(rows=zip(list(xedges), list(histogram)))

	mean = numpy.mean(array)
	stdev= numpy.std(array)
	normalised = (array - mean)/stdev	

	#Shapiro-Wilk
	#Compares the expected slope of a Q-Q plot to a least squared fit of the slope
	#If the errors are normal the slope of the Q-Q will be the standard-deviation of the errors
	#In this case we have normalised the data-set to set the deviation to one
	shapiro = scipy.stats.shapiro(normalised)
	dangostino = scipy.stats.normaltest(normalised)

	#Kurtosis and Skew Test
	#print 'Kurtosis-Test %6.2lf %E' % scipy.stats.kurtosistest(normalised)

	#Kolomogrov-Smirnov
	kolomogrov = scipy.stats.kstest(normalised, 'norm')

	#Q-Q
	orderStat = range(1, len(array) + 1)
	length = float(len(array))
	for i in range(len(array)):
		orderStat[i] = orderStat[i]/length
		
	invnormStat = [distributions.norm.ppf(x) for x in orderStat]
	normalised.sort()
	data = zip(invnormStat, normalised)
	qq = Core.Matrix.Matrix(rows=data, headers=['Theoretical', 'Experimental'])

	tup = (shapiro[1], dangostino[1], kolomogrov[1])
	return tup + (histogram, qq)

if __name__ == "__main__":
	
	usage = "usage: %prog [options]"

	parser = optparse.OptionParser(usage=usage, version="% 0.1", description=__doc__)
	parser.add_option("-f", "--file", dest="file",
			  help="A csv file", metavar="FILE")
	parser.add_option("-c", "--columns",
			  dest="columns",
			  help="A comma separated list of the indexes of the columns to calculate statistics for",
			  metavar='start')
	parser.add_option("", "--qq", action="store_true",
			  dest="outputQQ", default=False,
			  help="Output QQ matrix for each column")
	parser.add_option("", "--hist", action="store_true",
			  dest="outputHist", default=False,
			  help="Output histogram for each column")		  

	(options, args) = parser.parse_args()

	if not sys.stdin.isatty():
		csv = sys.stdin.read()
		m = Core.Matrix.matrixFromCSVRepresentation(csv)
	elif options.file is None:
		print 'CSV file must be provided'
		sys.exit(1)
	else:
		m = Core.Matrix.matrixFromCSVFile(options.file)

	if options.columns is None:
		print >>sys.stderr, 'No columns specified - defaulting to all'
		indexes = range(m.numberOfColumns())
	else:			
		indexes = [int(el.strip()) for el in options.columns.split(',')]	

	rows = []
	for columnIndex in indexes:
		
		#Returns length (min, max), mean, variance, skewness, kurtosis
		#col = [float(el) for el in m.column(columnIndex)]
		col = m.column(columnIndex)
		stats = scipy.stats.describe(col)
		row = list(stats[1])
		row.extend(stats[2:4])
		row[3] = math.sqrt(row[3])
		
		#Returns Shapiro Prob, Dangostino Prob
		#Kolomogrov Prob, histogram, qq
		stats = normalityTests(col)
		qq = stats[-1]
		histogram = stats[-2]
		row.extend(stats[:-2])

		name = m.headerForColumn(columnIndex)
		row.insert(0, name)
		rows.append(row)
		
		if options.outputQQ:
			f = open('QQ%s.csv' % name, 'w+')
			f.write(qq.csvRepresentation())
			f.close()

		if options.outputHist:
			f = open('ErrorHist%s.csv' % name, 'w+')
			f.write(histogram.csvRepresentation())
			f.close()

	headers = ['Name', 'Min', 'Max', 'Mean', 'Stdev', 'ShaprioProb', 
			'DAngostinoProb', 'KSProb']
	matrix = Core.Matrix.Matrix(rows=rows, headers=headers)
	print matrix.csvRepresentation(),


