
import lxml.etree as etree
from mgi.models import Template
from cStringIO import StringIO
from io import BytesIO

from utils.XMLValidation.xml_schema import validate_xml_data

SCHEMA_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
LXML_SCHEMA_NAMESPACE = "{" + SCHEMA_NAMESPACE + "}"


################################################################################
# 
# Function Name: checkValidForMDCS(xmlTree, type)
# Inputs:        request - 
#                xmlTree - 
#                type - 
# Outputs:       errors
# Exceptions:    None
# Description:   Check that the format of the the schema is supported by the current version of the MDCS
# 
################################################################################
def getValidityErrorsForMDCS(xmlTree, type):
    errors = []
    
    # General Tests

    # only support unqualified elements/attributes
    # root = xmlTree.getroot()
    # if 'elementFormDefault' in root.attrib:
    #     if root.attrib['elementFormDefault'] == 'qualified':
    #         errors.append('Only templates with elementFormDefault set to unqualified are accepted.')
    # if 'attributeFormDefault' in root.attrib:
    #     if root.attrib['attributeFormDefault'] == 'qualified':
    #         errors.append('Only templates with attributeFormDefault set to unqualified are accepted.')

    # get the imports
    imports = xmlTree.findall("{}import".format(LXML_SCHEMA_NAMESPACE))
    # get the includes
    includes = xmlTree.findall("{}include".format(LXML_SCHEMA_NAMESPACE))
    # get the elements
    elements = xmlTree.findall("{}element".format(LXML_SCHEMA_NAMESPACE))
    
    if len(imports) != 0 or len(includes) != 0:
        for el_import in imports:
            if 'schemaLocation' not in el_import.attrib:
                errors.append("The attribute schemaLocation of import is required but missing.")
            elif ' ' in el_import.attrib['schemaLocation']:
                errors.append("The use of namespace in import elements is not supported.")
        for el_include in includes:
            if 'schemaLocation' not in el_include.attrib:
                errors.append("The attribute schemaLocation of include is required but missing.")
            elif ' ' in el_include.attrib['schemaLocation']:
                errors.append("The use of namespace in include elements is not supported.")

    # Templates Tests

    if type == "Template":
        # Tests for templates
        if len(elements) < 1 :
            errors.append("Only templates with at least one root element are supported.")

    # Types Tests
    
    elif type == "Type":        
        elements = xmlTree.findall("*")
        if len(elements) > 0:
            # only simpleType, complexType or include
            for element in elements:
                if 'complexType' not in element.tag and 'simpleType' not in element.tag and 'include' not in element.tag:
                    errors.append("A type should be a valid XML schema containing only one type definition (Allowed tags are: simpleType or complexType and include).")
                    break
            # only one type
            for element in elements:
                cptType = 0
                if 'complexType' in element.tag or 'simpleType' in element.tag:
                    cptType += 1
                    if cptType > 1:
                        errors.append("A type should be a valid XML schema containing only one type definition (only one simpleType or complexType).")
                        break
        else:
            errors.append("A type should be a valid XML schema containing only one type definition (only one simpleType or complexType).")

    return errors


################################################################################
#
# Function Name: validateXMLDocument(templateID, xmlString)
# Inputs:        request - 
#                templateID - 
#                xmlString - 
# Outputs:       
# Exceptions:    None
# Description:   Check that the XML document is validated by the template
#                
#
################################################################################
def validateXMLDocument(xml_string, xsd_string):

    xsd_tree = etree.parse(StringIO(xsd_string.encode('utf-8')))
    xml_tree = etree.parse(StringIO(xml_string.encode('utf-8')))

    errors = validate_xml_data(xsd_tree, xml_tree)
    if errors is not None:
        raise Exception(errors)
    

################################################################################
#
# Function Name: manageNamespace(templateID, xmlString)
# Inputs:        request - 
#                templateID - 
#                xmlString - 
# Outputs:       
# Exceptions:    None
# Description:   - manage global targetNamespace
#                
#
################################################################################
def manage_namespaces(xml_string, xsd_string):
    # build the XML tree from the string
    xml_tree = etree.parse(StringIO(xml_string.encode('utf-8')))
    # get the root of the XML document
    xml_root = xml_tree.getroot()
    xml_root = clean_namespaces(xml_root)
    xml_string = etree.tostring(xml_root)

    return xml_string


def clean_namespaces(element, namespace=None):
    """
    Clean redundant namespace declarations: an element doesn't need to declare a namespace if it is the same as its
    parent.
    The function goes recursively down the XML tree, and removes namespace declarations from elements where they are not
    necessary.
    Look for None in the map of namespaces, because the data are created without a namespace prefix.
    :param namespace:
    :param element:
    :return:
    """
    # copy the current element
    element_text = element.text
    new_element = etree.Element(element.tag, element.attrib, nsmap=element.nsmap)
    new_element.text = element_text
    # browse all the children
    for child in list(element):
        # namespace = None, the parent didn't have a namespace
        if namespace is None:
            # the parent element has a xmlns attribute
            if len(element.nsmap) == 1 and None in element.nsmap.keys():
                # the child element has a xmlns attribute
                if len(child.nsmap) == 1 and None in child.nsmap.keys():
                    # the parent and the child are in the same namespace
                    if child.nsmap[None] == element.nsmap[None]:
                        # remove child namespaces
                        nsmap = child.nsmap
                        del nsmap[None]
                        # create a new element to replace the previous one (can't replace directly the nsmap using lxml)
                        new_child_text = child.text
                        new_child = etree.Element(child.tag, child.attrib, nsmap=nsmap)
                        new_child.text = new_child_text
                        # add the child back to the element
                        new_element.append(clean_namespaces(child, element.nsmap[None]))
                    else:
                        new_element.append(clean_namespaces(child))
            else:
                new_element.append(clean_namespaces(child))
        # a namespace has been passed from a parent
        else:
            # the parent and the child are in the same namespace
            if len(child.nsmap) == 1 and None in child.nsmap.keys():
                if child.nsmap[None] == namespace:
                    # remove prefix from namespaces
                    nsmap = child.nsmap
                    del nsmap[None]
                    # create a new element to replace the previous one (can't replace directly the nsmap using lxml)
                    new_child_text = child.text
                    new_child = etree.Element(child.tag, child.attrib, nsmap=nsmap)
                    new_child.text = new_child_text
                    new_element.append(clean_namespaces(child, element.nsmap[None]))
                else:
                    new_element.append(clean_namespaces(child))
            else:
                new_element.append(clean_namespaces(child))
    return new_element


################################################################################
#
# Function Name: getXSDTypes(prefix)
# Inputs:        request - 
#                prefix - Namespace prefix 
# Outputs:       
# Exceptions:    None
# Description:   Returns the list of all supported XSD types
#
################################################################################
def getXSDTypes(prefix):
    # FIXME Some datatypes are missing (https://www.w3.org/TR/xmlschema-2/#built-in-datatypes)
    return ["{0}:string".format(prefix), 
            "{0}:normalizedString".format(prefix),
            "{0}:token".format(prefix),
            "{0}:date".format(prefix),
            "{0}:dateTime".format(prefix),
            "{0}:duration".format(prefix),
            "{0}:gDay".format(prefix),
            "{0}:gMonth".format(prefix),
            "{0}:gMonthDay".format(prefix),
            "{0}:gYear".format(prefix),
            "{0}:gYearMonth".format(prefix),
            "{0}:gYearMonth".format(prefix),
            "{0}:time".format(prefix), 
            "{0}:byte".format(prefix),
            "{0}:decimal".format(prefix),
            "{0}:int".format(prefix),
            "{0}:integer".format(prefix),
            "{0}:long".format(prefix),
            "{0}:negativeInteger".format(prefix),
            "{0}:nonNegativeInteger".format(prefix),
            "{0}:nonPositiveInteger".format(prefix),
            "{0}:positiveInteger".format(prefix), 
            "{0}:short".format(prefix), 
            "{0}:unsignedLong".format(prefix), 
            "{0}:unsignedInt".format(prefix), 
            "{0}:unsignedShort".format(prefix), 
            "{0}:unsignedByte".format(prefix), 
            "{0}:anyURI".format(prefix), 
            "{0}:base64Binary".format(prefix), 
            "{0}:boolean".format(prefix), 
            "{0}:double".format(prefix),  
            "{0}:float".format(prefix),
            "{0}:hexBinary".format(prefix),
            "{0}:QName".format(prefix),
            "{0}:anyType".format(prefix)]
    
    
################################################################################
# 
# Class Name: ChoiceInfo
#
# Description: Store information about a choice being rendered
#
################################################################################
class ChoiceInfo:
    "Class that stores information about a choice being rendered"
        
    def __init__(self, chooseIDStr, counter):
        self.chooseIDStr = chooseIDStr
        self.counter = counter        
        
        
################################################################################
# 
# Function Name: get_namespaces(file)
# Inputs:        file -
# Outputs:       namespaces
# Exceptions:    None
# Description:   Get the namespaces used in the document
#
################################################################################
def get_namespaces(file):
    "Reads and returns the namespaces in the schema tag"
    events = "start", "start-ns"
    ns = {'xml':'http://www.w3.org/XML/1998/namespace'}
    for event, elem in etree.iterparse(file, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                raise Exception("Duplicate prefix with different URI found.")
            # if len(elem[0]) > 0 and len(elem[1]) > 0:
            ns[elem[0]] = "%s" % elem[1]
        elif event == "start":
            break
    return ns


def get_default_prefix(namespaces):
    default_prefix = ''
    for prefix, url in namespaces.items():
        if url == SCHEMA_NAMESPACE:
            default_prefix = prefix

    return default_prefix


def get_target_namespace_prefix(namespaces, xsd_tree):
    root_attributes = xsd_tree.getroot().attrib
    target_namespace = root_attributes['targetNamespace'] if 'targetNamespace' in root_attributes else None
    target_namespace_prefix = ''
    if target_namespace is not None:
        for prefix, url in namespaces.items():
            if url == target_namespace:
                target_namespace_prefix = prefix
        # no target prefix found
        # TODO: check local conflict
        # if target_namespace_prefix == '':
        #     target_namespace_prefix = 'local'
        #     namespaces[target_namespace_prefix] = target_namespace

    return target_namespace_prefix

def get_target_namespace(namespaces, xsd_tree):
    root_attributes = xsd_tree.getroot().attrib
    target_namespace = root_attributes['targetNamespace'] if 'targetNamespace' in root_attributes else None
    target_namespace_prefix = ''
    if target_namespace is not None:
        for prefix, url in namespaces.items():
            if url == target_namespace:
                target_namespace_prefix = prefix
        # no target prefix found
        # TODO: check local conflict
        # if target_namespace_prefix == '':
        #      target_namespace_prefix = 'local'
        #      namespaces[target_namespace_prefix] = target_namespace

    return target_namespace, target_namespace_prefix

################################################################################
# 
# Function Name: getAppInfo(element, namespace)
# Inputs:        element -
#                namespace - 
# Outputs:       app info
# Exceptions:    None
# Description:   Get app info if present
#
################################################################################
def getAppInfo(element):
    app_info = {}
    
    app_info_elements = element.findall("./{0}annotation/{0}appinfo".format(LXML_SCHEMA_NAMESPACE))
    for app_info_element in app_info_elements:
        for app_info_child in app_info_element.getchildren():
            if app_info_child.tag in ['label', 'placeholder', 'tooltip', 'use']:
                app_info[app_info_child.tag] = app_info_child.text
    
    return app_info
