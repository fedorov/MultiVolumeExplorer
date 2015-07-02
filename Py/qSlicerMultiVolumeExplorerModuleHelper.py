
from __main__ import vtk, slicer

class qSlicerMultiVolumeExplorerModuleHelper( object ):

  @staticmethod
  def SetBgFgVolumes(bg, fg):
    appLogic = slicer.app.applicationLogic()
    selectionNode = appLogic.GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(bg)
    selectionNode.SetReferenceSecondaryVolumeID(fg)
    appLogic.PropagateVolumeSelection()

  # input: multivolume node, output folder
  # extracts individual frames and saves them in the folder using
  # numbered files
  @staticmethod
  def ExplodeMultiVolume(mvNode, outputPath):
    
    mvNodeFrameCopy = slicer.vtkMRMLScalarVolumeNode()
    mvNodeFrameCopy.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(mvNodeFrameCopy)
    storageNode = mvNodeFrameCopy.CreateDefaultStorageNode()

    nFrames = mvNode.GetNumberOfFrames()
    for f in range(nFrames):
      fileName = "frame_%04d.nrrd" % f
      fullFilePath = os.path.join(outputPath,fileName)
      mvNodeFrameCopy = qSlicerMultiVolumeExplorerModuleHelper.ExtractFrame(mvNode, f, mvNodeFrameCopy)
      storageNode.SetFileName(fullFilePath)
      storageNode.WriteData(mvNodeFrameCopy)
      print('Saved frame '+fullFilePath)

  # input: multivolume node, frame nummber, initialized scalar volume node
  #  to keep the extracted frame
  # returns: scalar volume node with the extracted frame
  @staticmethod
  def ExtractFrame(mvNode, frameNumber, mvNodeFrameCopy):
    mvNodeFrameCopy = slicer.vtkMRMLScalarVolumeNode()
    mvNodeFrameCopy.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(mvNodeFrameCopy)

    mvImage = mvNode.GetImageData()
    extract = vtk.vtkImageExtractComponents()
    if vtk.VTK_MAJOR_VERSION <= 5:
      extract.SetInput(mvImage)
    else:
      extract.SetInputData(mvImage)
    extract.SetComponents(frameNumber)
    extract.Update()

    ras2ijk = vtk.vtkMatrix4x4()
    ijk2ras = vtk.vtkMatrix4x4()
    mvNode.GetRASToIJKMatrix(ras2ijk)
    mvNode.GetIJKToRASMatrix(ijk2ras)
    #print(dir(mvNodeFrameCopy))
    mvNodeFrameCopy.SetRASToIJKMatrix(ras2ijk)
    mvNodeFrameCopy.SetIJKToRASMatrix(ijk2ras)

    mvNodeFrameCopy.SetAndObserveImageData(extract.GetOutput())

    displayNode = mvNodeFrameCopy.GetDisplayNode()

    if displayNode == None:
      displayNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLScalarVolumeDisplayNode')
      displayNode.SetReferenceCount(1)
      displayNode.SetScene(slicer.mrmlScene)
      slicer.mrmlScene.AddNode(displayNode)
      displayNode.SetDefaultColorMap()
      mvNodeFrameCopy.SetAndObserveDisplayNodeID(displayNode.GetID())

    return mvNodeFrameCopy
