from opencmiss.zinc.context import Context
from opencmiss.zinc.element import Element
from opencmiss.zinc.field import Field
from opencmiss.zinc.fieldmodule import Fieldmodule
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.graphics import Graphics
from opencmiss.zinc.material import Material
import json

class PyZincExport(object):
    '''
    This example demonstrates how to read and export a simple mesh
    '''
    def __init__(self):
        '''Initialise PyZinc Objects'''
        self._context = Context('animation_deforming_heart')
        self._context.getGlyphmodule().defineStandardGlyphs()
        self._default_region = self._context.getDefaultRegion()
        self._logger = self._context.getLogger()
        self._materialModule = self._context.getMaterialmodule()
        self._materialModule.defineStandardMaterials()
        self._materialIterator = self._materialModule.createMaterialiterator()
        '''Export To ZincJS format'''
        #self.exportWebGLJson()
        '''Export graphics into JSON format'''
        numOfMessages = self._logger.getNumberOfMessages()
        for i in range(1, numOfMessages+1):
            print(self._logger.getMessageTextAtIndex(i))
            
    def getNextMaterial(self):
        '''
        Go through the material module to find the next suitable colour
        '''
        material = self._materialIterator.next()
        if material.isValid():
            alpha = material.getAttributeReal(material.ATTRIBUTE_ALPHA) 
            if 1.0 > alpha:
                return self.getNextMaterial()
            else:
                return material
        else:
            self._materialIterator = self._materialModule.createMaterialiterator()
            return self.getNextMaterial()
        
    def exportWebGLJson(self, region):
        '''
        Export graphics into JSON format, one json export represents one
        surface graphics.
        '''
        scene = region.getScene()
        prefix = region.getName()
        if prefix == None:
            prefix = 'root'
        sceneSR = scene.createStreaminformationScene()
        sceneSR.setIOFormat(sceneSR.IO_FORMAT_THREEJS)
        number = sceneSR.getNumberOfResourcesRequired()
        resources = []
        '''Write out each graphics into a json file which can be rendered with ZincJS'''
        for i in range(number):
            resources.append(sceneSR.createStreamresourceMemory())
        scene.write(sceneSR)
        '''Write out each resource into their own file'''
        return [resources[i].getBuffer()[1].decode('utf-8') for i in range(number)]
        
    def createSurfaceGraphics(self, region, group):
        '''
        Create the surface graphics using the finite element field 'coordinates'.
        The tessellations of the surface can be changed to increase/decrease details
        of the mesh.
        '''
        scene = region.getScene()
        fieldmodule = region.getFieldmodule()
        tm = self._context.getTessellationmodule()
        tessellation = tm.createTessellation()
        tessellation.setMinimumDivisions([4,4,1])
        scene.beginChange()
        surface = scene.createGraphicsSurfaces()
        finite_element_field = fieldmodule.findFieldByName('coordinates')
        surface.setCoordinateField(finite_element_field)
        surface.setTessellation(tessellation)
        surface.setSubgroupField(group)
        ''' Setting exterior only should reduce export size without compromising quality '''
        surface.setExterior(True)
        material = self.getNextMaterial()
        surface.setMaterial(material)
        # Let the scene render the scene.
        scene.endChange()
        # createSurfaceGraphics end
        
    def createGlyphGraphics(self, region):
        '''
        Create the glyph graphics using the finite element field 'coordinates'.
        '''
        scene = region.getScene()
        fieldmodule = region.getFieldmodule()
        scene.beginChange()
        glyph = scene.createGraphicsPoints()
        glyph.setFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        finite_element_field = fieldmodule.findFieldByName('data_coordinates')
        glyph.setCoordinateField(finite_element_field)
        pointAttr = glyph.getGraphicspointattributes()
        label_field = fieldmodule.findFieldByName('data_label')
        pointAttr.setLabelField(label_field)
        sphere = self._context.getGlyphmodule().findGlyphByGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        pointAttr.setGlyph(sphere)
        # Let the scene render the scene.
        scene.endChange()
        # createSurfaceGraphics end

        
    def generateGraphics(self, list):
        for item in list:
            region = item[0]
            fm = region.getFieldmodule()
            #datapoints = fm.findNodesetByName("datapoints")
            mesh = fm.findMeshByDimension(3)
            groupList = item[1]
            for group in groupList:
                elementField = group.getFieldElementGroup(mesh)
                meshGroup = elementField.getMeshGroup()
                if meshGroup.getSize() > 0:
                    self.createSurfaceGraphics(region, group)
        #    if datapoints.getSize() > 0:
        #        self.createGlyphGraphics(region)
            
    def readMesh(self, files):
        '''
        Create a stream information then call createStreamresourceFile 
        with the files you want to read into PyZinc
        '''
        print(files)
        sir = self._default_region.createStreaminformationRegion()
        for x in files:
            sir.createStreamresourceFile(x)
            #with open(x, 'r') as content_file:
            #    buffer = content_file.read()
            #    sir.createStreamresourceMemoryBuffer(buffer)
        self._default_region.read(sir)
        
        
    '''Get groups in region'''
    def getGroupList(self, region):
        groups = []
        fieldmodule = region.getFieldmodule()
        fielditer = fieldmodule.createFielditerator()
        field = fielditer.next()
        while field.isValid():
            group = field.castGroup()
            if group.isValid():
                groups.append(group)
            field = fielditer.next()
        return groups

    def getRegionsList(self, region):
        regionList = []
        childRegion = region.getFirstChild()
        if childRegion.isValid():
            childRegions = self.getRegionList(childRegion)
            regionList.extend(childRegions)
        siblingRegion = region.getNextSibling()
        if siblingRegion.isValid():
            siblingRegions = self.getRegionList(siblingRegion)
            regionList.extend(siblingRegions)
        regionList.append(region)
        return regionList
        
    def outputName(self, list):
        for item in list:
            region = item[0]
            groupList = item[1]
            groupName = []
            for group in groupList:
                if group.isValid(): 
                    groupName.append(group.getName())

    def outputModel(self, files, annotations):
        """
        Provided meshtype must exist as a key in the meshes dict in this
        module.
        """
        self.readMesh(files)
        regionList = self.getRegionsList(self._default_region)
        regionGroupList = []
        for region in regionList:
            groups = self.getGroupList(region)
            regionGroupList.append([region, groups])
        self.outputName(regionGroupList)
        self.generateGraphics(regionGroupList)
        response = []
        for item in regionGroupList:
            region = item[0]
            buffers = self.exportWebGLJson(region)
            response = response + buffers
        return response

