import os
import unittest
import sys, slicer, numpy, math, vtk
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

#
# GeodesicPathSlicer
#

class GeodesicPathSlicer(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "GeodesicPathSlicer" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Informatics"]
    self.parent.dependencies = []
    self.parent.contributors = ["Frederic Briend (UNICAEN), Andras Lasso (Queen's)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This module calculates geodesic path in 3D structure.
    """
    self.parent.acknowledgementText = """
    This work was supported by CHU Caen.
""" # replace with organization, grant and thanks.

#
# GeodesicPathSlicerWidget
#

class GeodesicPathSlicerWidget(ScriptedLoadableModuleWidget):

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # Fiducial selector (vtkMRMLMarkupsFiducialNode)
    #	
    self.SourceSelector = slicer.qMRMLNodeComboBox()
    self.SourceSelector.nodeTypes = ( ("vtkMRMLMarkupsFiducialNode"), "" )
    self.SourceSelector.addEnabled = True
    self.SourceSelector.removeEnabled = False
    self.SourceSelector.noneEnabled = True
    self.SourceSelector.showHidden = False
    self.SourceSelector.renameEnabled = True
    self.SourceSelector.showChildNodeTypes = False
    self.SourceSelector.setMRMLScene( slicer.mrmlScene )
    self.SourceSelector.setToolTip( "Pick up a Markups node listing fiducials." )
	parametersFormLayout.addRow("Source points: ", self.SourceSelector)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply geodesic path")
    self.applyButton.toolTip = "Run the algorithm Dijkstra."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # Add vertical spacer
    self.layout.addStretch(1)
	
	#
    # Curve Length area
    #
    lengthCollapsibleButton = ctk.ctkCollapsibleButton()
    lengthCollapsibleButton.text = "Length"
    self.layout.addWidget(lengthCollapsibleButton)
    lengthFormLayout = qt.QFormLayout(lengthCollapsibleButton)
    lengthCollapsibleButton.collapsed = True

    #-- Curve length
    self.lengthLineEdit = qt.QLineEdit()
    self.lengthLineEdit.text = '--'
    self.lengthLineEdit.readOnly = True
    self.lengthLineEdit.frame = True
    self.lengthLineEdit.styleSheet = "QLineEdit { background:transparent; }"
self.lengthLineEdit.cursor = qt.QCursor(qt.Qt.IBeamCursor)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = GeodesicPathSlicerLogic()

    inputVolume = self.inputSelector.currentNode()
    
    if not (inputVolume and fiducial):
      qt.QMessageBox.critical(slicer.util.mainWindow(), 'GeodesicPath', 'Input and two ficuial points are required for GeodesicPath')
      return

    print("Run the algorithm")
    logic.run(inputVolume, fiducial)

	
	
	#####here begin the program
	
	
##Adding fiducials via mouse clicks
##Access to Fiducial Properties (to determinate the start and the end point of the geodesic path)
fidList = slicer.util.getNode('F')
numFids = fidList.GetNumberOfFiducials()
list=[]
for i in range(numFids):
  ras = [0,0,0]
  fidList.GetNthFiducialPosition(i,ras)
  print i,": RAS =",ras
  list.append(ras)

#locator
model #the input volume
pd = model.GetModelDisplayNode()
pd1=pd.GetOutputPolyData()
pd1.GetNumberOfPoints()
loc = vtk.vtkPointLocator()
loc.SetDataSet(pd1)
loc.BuildLocator()
closestPointId = loc.FindClosestPoint(list[0]) #fiducial 1
closestPointId1 = loc.FindClosestPoint(list[1]) #fiducial 2

print 'length= ', (dist/10)+ ' cm')

# GeodesicPathSlicerLogic
#

class GeodesicPathSlicerLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def run(self,inputVolume,outputVolume):
    """
    Run the actual algorithm
    """

    self.delayDisplay('Running the aglorithm')

	##get the distance of the geodesic path 
	appendFilter = vtk.vtkAppendFilter()
	appendFilter.MergePointsOn()
	points = vtk.vtkPoints()
	vIds = [closestPointId,closestPointId1]
	p0 = [0,0,0]
	p1 = [0,0,0]
	dist = 0.0
	for n in range(len(vIds)-1):
		v0 = vIds[n]
		v1 = vIds[n+1]
		
		#create geodesic path: vtkDijkstraGraphGeodesicPath
		dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
		dijkstra.SetInputConnection(pd.GetOutputPolyDataConnection())
		dijkstra.SetStartVertex(v0)
		dijkstra.SetEndVertex(v1)
		dijkstra.Update()
					
		pts = dijkstra.GetOutput().GetPoints()
		end = n<len(vIds)-2 and 0 or -1
		for ptId in range(pts.GetNumberOfPoints()-1, end, -1):
			pts.GetPoint(ptId, p0)
			points.InsertNextPoint(p0)		
		
		for ptId in range(pts.GetNumberOfPoints()-1):
			pts.GetPoint(ptId, p0)
			pts.GetPoint(ptId+1, p1)
			dist += math.sqrt(vtk.vtkMath.Distance2BetweenPoints(p0, p1))
			
		appendFilter.AddInputConnection(dijkstra.GetOutputPort())

    return True