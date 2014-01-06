# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""
This file defines ImageSensor, an extensible sensor for images.
"""

import os
import sys

from PyRegion import PyRegion
import numpy


class RecorderRegion(PyRegion):

  """ Region that takes arbitrary inputs and writes them to a file.
  """


  def __init__(self, path, **kw):
    self._attemptedCategorizations = 0
    self._stepIndex = 0
    self.outFilePath = path
    self._outFile = None
    self.successRecord = []
    self.successCount = 0

  def compute(self, inputs, outputs=None):
    """
    Generate the next sensor output and send it out.

    This method is called by the runtime engine.
    """
    vectorizedInputs = self._vectorizeInputs(inputs)

    categorizationSuccess = self._determineSuccess(vectorizedInputs)
    if categorizationSuccess is not None:
      vectorizedInputs["categorizationSuccess"] = categorizationSuccess
      self.successCount += categorizationSuccess

    self._record(vectorizedInputs)
    self._stepIndex += 1

  def _record(inputs):
    """ write the inputs dictionary to the output file """
    if self._outFile is None:
      self._outFile = open(self.outFilePath, 'w')

    self._outFile.write("%sStep %i%s" % (os.linesep, self._stepIndex, os.linesep))
    for key, val in inputs.iteritems():
      string = "   %s: %s" % (str(key), str(val))
      self._outFile.write(string)

    if "categorizationSuccess" in inputs:
      successRate = self.successCount / float(len(self.successRecord))
      self._outFile.write()

    self._outFile.flush()

  def _determineSuccess(self, inputs):
    if "categoryTruth" not in inputs:
      return None
    elif "categoryGuess" not in inputs:
      return None
    elif inputs["categoryGuess"] == inputs["categoryTruth"]:
      success = 1
    else:
      success = 0
    self.successRecord.append(success)
    return success

  def _vectorizeInputs(self, inputs):
    """ Converts a dict of inputs into a dict of numpy matrices """
    vectorized = {}
    for key, val in inputs.iteritems():
      print type(val)
      # childInputs = [x.wvector(0) for x in val]
      # vectorized[key] = numpy.concatenate([x.array() for x in childInputs])
    raise Exception("derp")
    return vectorized

  def getParameter(self, parameterName, index=-1):
    """Get the value of a RecorderRegion parameter."""
    if hasattr(self, parameterName):
      return getattr(self, parameterName, parameterValue)
    # elif parameterName == 'mySpecialCase':
    #   pass
    else:
      raise Exception("%s is not a valid parameter of the RecorderRegion" % parameterName)

  def setParameter(self, parameterName, index, parameterValue):
    """Set the value of a RecorderRegion parameter."""
    if hasattr(self, parameterName):
      setattr(self, parameterName, parameterValue)
    # elif parameterName == 'mySpecialCase':
    #   pass
    else:
      raise Exception("%s is not a valid parameter of the RecorderRegion" % parameterName)
 
  #---------------------------------------------------------------------------------
  def initialize(self, dims, splitterMaps):
    pass

  #---------------------------------------------------------------------------------
  def getOutputElementCount(self, name):
    raise Exception("RecorderRegion has no outputs.")

  @classmethod
  def getSpec(cls):
    """Return the Spec for this Region."""

    spec = dict(
      description=RecorderRegion.__doc__,
      singleNodeOnly=True,
      inputs = dict(
        mainDataIn = dict(
          dataType="Real32",
          description="""Accepts arbitrary input to store""",
          regionLevel=True,
          count=0,
          required=False,
          isDefaultInput=True,
          requireSplitterMap=False
        ),
        categoryTruth = dict(
          dataType="Real32",
          description="""The current intended category. Used to compute success rates
                         of match between this and categoryGuess. """,
          regionLevel=True,
          count=0,
          required=False,
          isDefaultInput=False,
          requireSplitterMap=False
        ),
        categoryGuess = dict(
          dataType="Real32",
          description="""The current estimated category. Used to compute success rates
                         of match between this and categoryTruth.""",
          regionLevel=True,
          count=0,
          required=False,
          isDefaultInput=True,
          requireSplitterMap=False
        )
      ),
      outputs = {},
      parameters = dict(
        path=dict(
          dataType="Byte",
          constraints="string",
          count=0,
          accessMode="Create",
          defaultValue = "NetworkResults.txt",
          description="""The path to the file where we'll be writing"""),
      ),
      commands={}
    )
    return spec