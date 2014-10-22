################################################################################
#
# File Name: views.py
# Application: api
# Purpose:   
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

# REST Framework
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
# Models
from mgi.models import SavedQuery, Jsondata, Template, TemplateVersion, Ontology, OntologyVersion, Instance
from django.contrib.auth.models import User
# Serializers
from api.serializers import savedQuerySerializer, jsonDataSerializer, querySerializer, sparqlQuerySerializer, sparqlResultsSerializer, schemaSerializer, templateSerializer, ontologySerializer, resOntologySerializer, TemplateVersionSerializer, OntologyVersionSerializer, instanceSerializer, resInstanceSerializer, UserSerializer, insertUserSerializer, resSavedQuerySerializer, updateUserSerializer

from explore import sparqlPublisher
from curate import rdfPublisher
from lxml import etree
from django.conf import settings
import os
from mongoengine import *
from pymongo import Connection
from bson.objectid import ObjectId
import re
import requests
from django.db.models import Q
import operator
import json
import hashlib
from collections import OrderedDict

projectURI = "http://www.example.com/"

# @api_view(['GET','POST'])
# def savedQuery_list(request): 
#     if request.method == 'GET':
#         savedQueries = SavedQuery.objects
#         serializer = savedQuerySerializer(savedQueries)
#         return Response(serializer.data, status=status.HTTP_200_OK)
# 
#     elif request.method == 'POST':        
#         serializer = savedQuerySerializer(data=request.DATA)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     
# @api_view(['GET', 'PUT', 'DELETE'])
# def savedQuery_detail(request, pk):
#     """
#     Retrieve, update or delete a saved query instance.
#     """              
#     try:
#         savedQuery = SavedQuery.objects.get(pk=pk)
#     except:
#         content = {'message':'No saved query with the given id.'}
#         return Response(content, status=status.HTTP_404_NOT_FOUND)
# 
#     if request.method == 'GET':
#         serializer = savedQuerySerializer(savedQuery)
#         return Response(serializer.data, status=status.HTTP_200_OK)
# 
#     elif request.method == 'PUT':
#         serializer = savedQuerySerializer(savedQuery, data=request.DATA)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# 
#     elif request.method == 'DELETE':
#         savedQuery.delete()
#         content = {'message':'The query was deleted with success.'}
#         return Response(content, status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET','POST'])
# def jsonData_list(request):
#     if request.method == 'GET':
#         jsonData = Jsondata.objects()
#         serializer = jsonDataSerializer(jsonData)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#  
#     elif request.method == 'POST':        
#         serializer = jsonDataSerializer(data=request.DATA)
#         if serializer.is_valid():
#             jsondata = Jsondata(schemaID = request.DATA['schema'], json = request.DATA['content'], title = request.DATA['title'])
#             jsondata.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# 
# 
# @api_view(['GET', 'PUT', 'DELETE'])
# def jsonData_detail(request, pk):
#     """
#     Retrieve, update or delete a saved query instance.
#     """              
#     jsonData = Jsondata.get(pk)
#     if jsonData is None:
#         content = {'message':'No data with the given id.'}
#         return Response(content, status=status.HTTP_404_NOT_FOUND)
# 
#     if request.method == 'GET':
#         serializer = jsonDataSerializer(jsonData)
#         return Response(serializer.data, status=status.HTTP_200_OK)
# 
#     elif request.method == 'PUT':
#         serializer = jsonDataSerializer(jsonData, data=request.DATA)
#         if serializer.is_valid():
#             Jsondata.update(pk, request.DATA)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# 
#     elif request.method == 'DELETE':
#         Jsondata.delete(pk)
#         content = {'message':'Data deleted with success.'}
#         return Response(content, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def select_all_savedqueries(request):
    """
    GET http://localhost/api/saved_queries/select/all
    """
    queries = SavedQuery.objects()
    serializer = savedQuerySerializer(queries)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def select_savedquery(request):
    """
    GET http://localhost/api/saved_queries/select
    id: string (ObjectId)
    user: string 
    template: string
    query: string
    displayedQuery: string
    """
    id = request.QUERY_PARAMS.get('id', None)
    user = request.QUERY_PARAMS.get('user', None)
    template = request.QUERY_PARAMS.get('template', None)
    dbquery = request.QUERY_PARAMS.get('query', None)
    displayedQuery = request.QUERY_PARAMS.get('displayedQuery', None)
    
    try:        
        # create a connection                                                                                                                                                                                                 
        connection = Connection()
        # connect to the db 'mgi'
        db = connection['mgi']
        # get the xmldata collection
        savedQueries = db['saved_query']
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if user is not None:
            if user[0] == '/' and user[-1] == '/':
                query['user'] = re.compile(user[1:-1])
            else:
                query['user'] = user            
        if template is not None:
            if template[0] == '/' and template[-1] == '/':
                query['template'] = re.compile(template[1:-1])
            else:
                query['template'] = template
        if dbquery is not None:
            if dbquery[0] == '/' and dbquery[-1] == '/':
                query['query'] = re.compile(dbquery[1:-1])
            else:
                query['query'] = dbquery
        if displayedQuery is not None:
            if displayedQuery[0] == '/' and displayedQuery[-1] == '/':
                query['displayedQuery'] = re.compile(displayedQuery[1:-1])
            else:
                query['displayedQuery'] = displayedQuery
        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            cursor = savedQueries.find(query)
            listSavedQueries = []
            for resultSavedQuery in cursor:
                resultSavedQuery['id'] = resultSavedQuery['_id']
                del resultSavedQuery['_id']
                listSavedQueries.append(resultSavedQuery)
            serializer = resSavedQuerySerializer(listSavedQueries)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        content = {'message':'No saved query found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def add_savedquery(request):
    """
    POST http://localhost/api/saved_queries/add
    POST data user="user", template="template" query="query", displayedQuery="displayedQuery"
    """    
    serializer = resSavedQuerySerializer(data=request.DATA)
    if serializer.is_valid():
        errors = ""
        try:
            json_object = json.loads(request.DATA["query"])
        except ValueError:
            errors += "Invalid query."
        try:
            template = Template.objects.get(pk=request.DATA["template"])
        except Exception:
            errors += "Unknown template."
        try:
            user = User.objects.get(pk=request.DATA["user"])
        except Exception:
            errors += "Unknown user."
        
        if errors != "":
            content = {'message':errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            SavedQuery(user=request.DATA["user"],template=request.DATA["template"],query=request.DATA["query"],displayedQuery=request.DATA["displayedQuery"]).save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception, e:
            content = {'message':e.message}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def delete_savedquery(request):
    """
    GET http://localhost/api/saved_queries/delete?id=id
    URL parameters: 
    id: string 
    """
    id = request.QUERY_PARAMS.get('id', None)
    if id is not None:
        try:
            query = SavedQuery.objects.get(pk=id)
            query.delete()
            content = {'message':"Query deleted with success."}
            return Response(content, status=status.HTTP_200_OK)
        except:
            content = {'message':"No query found with the given id."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':"No id provided."}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def explore(request):
    """
    GET http://localhost/api/explore/select/all
    """
    jsonData = Jsondata.objects()
    serializer = jsonDataSerializer(jsonData)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def explore_detail(request):
    """
    GET http://localhost/api/explore/select
    id: string (ObjectId)
    schema: string (ObjectId)
    title: string
    """        
    id = request.QUERY_PARAMS.get('id', None)
    schema = request.QUERY_PARAMS.get('schema', None)
    title = request.QUERY_PARAMS.get('title', None)
    
    try:        
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if schema is not None:
            if schema[0] == '/' and schema[-1] == '/':
                query['schema'] = re.compile(schema[1:-1])
            else:
                query['schema'] = schema
        if title is not None:
            if title[0] == '/' and title[-1] == '/':
                query['title'] = re.compile(title[1:-1])
            else:
                query['title'] = title
        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            jsonData = Jsondata.executeQueryFullResult(query)
            serializer = jsonDataSerializer(jsonData)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        content = {'message':'No data found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def explore_delete(request):
    """
    GET http://localhost/api/explore/delete
    id: string (ObjectId)
    """        
    id = request.QUERY_PARAMS.get('id', None)
    
    try:        
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if len(query.keys()) == 0:
            content = {'message':'No id given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            Jsondata.delete(id)
            content = {'message':'Data deleted with success.'}
            return Response(content, status=status.HTTP_204_NO_CONTENT)
    except:
        content = {'message':'No data found with the given id.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

def manageRegexInAPI(query):
    for key, value in query.iteritems():
        if key == "$and" or key == "$or":
            for subValue in value:
                manageRegexInAPI(subValue)
        elif isinstance(value, str):
            if (len(value) > 2 and value[0] == "/" and value[-1] == "/"):
                query[key] = re.compile(value[1:-1])
        elif isinstance(value, dict):
            manageRegexInAPI(value)

@api_view(['POST'])
def query_by_example(request):
    """
    POST http://localhost/api/explore/query-by-example
    POST data query="{'element':'value'}" repositories="Local,Server1,Server2"
    """
    qSerializer = querySerializer(data=request.DATA)
    if qSerializer.is_valid():
        if 'repositories' in request.DATA:
            instanceResults = []
            repositories = request.DATA['repositories'].split(",")
            if len(repositories) == 0:
                content = {'message':'Repositories keyword found but the list is empty.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                instances = []
                local = False
                for repository in repositories:
                    if repository == "Local":
                        local = True
                    else:
                        try:
                            instance = Instance.objects.get(name=repository)
                            instances.append(instance)
                        except:
                            content = {'message':'Unknown repository.'}
                            return Response(content, status=status.HTTP_400_BAD_REQUEST)
                if local:
                    try:
                        query = eval(request.DATA['query'])
                        manageRegexInAPI(query)
                        instanceResults = instanceResults + Jsondata.executeQueryFullResult(query)                        
                    except:
                        content = {'message':'Bad query: use the following format {\'element\':\'value\'}'}
                        return Response(content, status=status.HTTP_400_BAD_REQUEST)
                for instance in instances:
                    url = instance.protocol + "://" + instance.address + ":" + str(instance.port) + "/api/explore/query-by-example"   
                    query = request.DATA['query']              
                    data = {"query":query}
                    r = requests.post(url, data, auth=(instance.user, instance.password))   
                    result = r.text
                    instanceResults = instanceResults + json.loads(result,object_pairs_hook=OrderedDict)
                    
                jsonSerializer = jsonDataSerializer(instanceResults)        
                return Response(jsonSerializer.data, status=status.HTTP_200_OK)
        else:
            try:
                query = eval(request.DATA['query'])
                manageRegexInAPI(query)
                results = Jsondata.executeQueryFullResult(query)
                jsonSerializer = jsonDataSerializer(results)        
                return Response(jsonSerializer.data, status=status.HTTP_200_OK)
            except:
                content = {'message':'Bad query: use the following format {\'element\':\'value\'}'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(qSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def sparql_query(request):
    """
    POST http://localhost/api/explore/sparql-query
    POST data query="SELECT * WHERE {?s ?p ?o}" format="xml" repositories="Local,Server1,Server2"
    """
    sqSerializer = sparqlQuerySerializer(data=request.DATA)
    if sqSerializer.is_valid():
        if 'format' in request.DATA:
            format = request.DATA['format']
            if (format.upper() == "TEXT"):
                query = '0' + request.DATA['query']
            elif (format.upper() == "XML"):
                query = '1' + request.DATA['query']
            elif (format.upper() == "CSV"):
                query = '2' + request.DATA['query']
            elif (format.upper() == "TSV"):
                query = '3' + request.DATA['query']
            elif (format.upper() == "JSON"):
                query = '4' + request.DATA['query']
            else:
                content = {'message':'Accepted formats: text, xml, csv, tsv, json'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            query = '0' + request.DATA['query']
        
        if 'repositories' in request.DATA:
            instanceResults = []
            repositories = request.DATA['repositories'].split(",")
            if len(repositories) == 0:
                content = {'message':'Repositories keyword found but the list is empty.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            else:
                instances = []
                local = False
                for repository in repositories:
                    if repository == "Local":
                        local = True
                    else:
                        try:
                            instance = Instance.objects.get(name=repository)
                            instances.append(instance)
                        except:
                            content = {'message':'Unknown repository.'}
                            return Response(content, status=status.HTTP_400_BAD_REQUEST)
                if local:
                    instanceResults.append(sparqlPublisher.sendSPARQL(query)) 
                for instance in instances:
                    url = instance.protocol + "://" + instance.address + ":" + str(instance.port) + "/api/explore/sparql-query"
                    if 'format' in request.DATA:
                        data = {"query": request.DATA['query'], "format":request.DATA['format']}
                    else:
                        data = {"query": request.DATA['query']}
                    r = requests.post(url, data, auth=(instance.user, instance.password))        
                    instanceResultsDict = eval(r.text)
                    instanceResults.append(instanceResultsDict['content'])
                    
                results = dict()
                results['content'] = instanceResults
                
                srSerializer = sparqlResultsSerializer(results)
                return Response(srSerializer.data, status=status.HTTP_200_OK)
        else:
            results = dict()  
            results['content'] = sparqlPublisher.sendSPARQL(query) 
            
            srSerializer = sparqlResultsSerializer(results)
            return Response(srSerializer.data, status=status.HTTP_200_OK)
    return Response(sqSerializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def curate(request):
    """
    POST http://localhost/api/curate
    POST data title="title", schema="schemaID", content="<root>...</root>"
    """        
    serializer = jsonDataSerializer(data=request.DATA)
    if serializer.is_valid():
        try:
            schema = Template.objects.get(pk=ObjectId(request.DATA['schema']))
            templateVersion = TemplateVersion.objects.get(pk=ObjectId(schema.templateVersion))
            if str(schema.id) in templateVersion.deletedVersions:
                content = {'message: The provided template is currently deleted.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except:
            content = {'message: No template found with the given id.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        xmlStr = request.DATA['content']
        try:
            try:
                xmlTree = etree.fromstring(xmlStr)
            except Exception, e:
                content = {'message: Unable to read the XML data: '+ e.message}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            #TODO: XML validation
#             xmlSchemaTree = etree.fromstring(schema.content)
#             xmlSchema = etree.XMLSchema(xmlSchemaTree)
#             try:
#                 xmlSchema.assertValid(xmlTree)
#             except Exception, e:
#                 content = {'message':e.message}
#                 return Response(content, status=status.HTTP_400_BAD_REQUEST)
            jsondata = Jsondata(schemaID = request.DATA['schema'], xml = xmlStr, title = request.DATA['title'])
            docID = jsondata.save()            

            #xsltPath = './xml2rdf3.xsl' #path to xslt on my machine
            #xsltFile = open(os.path.join(PROJECT_ROOT,'xml2rdf3.xsl'))
            xsltPath = os.path.join(settings.SITE_ROOT, 'static/resources/xsl/xml2rdf3.xsl')
            xslt = etree.parse(xsltPath)
            root = xslt.getroot()
            namespace = root.nsmap['xsl']
            URIparam = root.find("{" + namespace +"}param[@name='BaseURI']") #find BaseURI tag to insert the project URI
            URIparam.text = projectURI + str(docID)
        
            # SPARQL : transform the XML into RDF/XML
            transform = etree.XSLT(xslt)
            # add a namespace to the XML string, transformation didn't work well using XML DOM
            template = Template.objects.get(pk=templateID)
            xmlStr = xmlStr.replace('>',' xmlns="' + projectURI + template.hash + '">', 1) #TODO: OR schema name...                
            # domXML.attrib['xmlns'] = projectURI + schemaID #didn't work well
            domXML = etree.fromstring(xmlStr)
            domRDF = transform(domXML)
        
            # SPARQL : get the rdf string
            rdfStr = etree.tostring(domRDF)
        
            print "rdf string: " + rdfStr
        
            # SPARQL : send the rdf to the triplestore
            rdfPublisher.sendRDF(rdfStr)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            content = {'message: Unable to insert data.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_schema(request):
    """
    POST http://localhost/api/templates/add
    POST data title="title", filename="filename", content="<xsd:schema>...</xsd:schema>" templateVersion="id"
    """
    sSerializer = schemaSerializer(data=request.DATA)
    if sSerializer.is_valid():
        # a template version is provided: if it exists, add the schema as a new version and manage the version numbers
        if "templateVersion" in request.DATA:
            try:
                templateVersions = TemplateVersion.objects.get(pk=request.DATA['templateVersion'])
                if templateVersions.isDeleted == True:
                    content = {'message':'This template version belongs to a deleted template. You are not allowed to delete it.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                templateVersions.nbVersions = templateVersions.nbVersions + 1
                hash = hashlib.sha1(request.DATA['content'])
                hex_dig = hash.hexdigest()
                newTemplate = Template(title=request.DATA['title'], filename=request.DATA['filename'], content=request.DATA['content'], templateVersion=request.DATA['templateVersion'], version=templateVersions.nbVersions, hash=hex_dig).save()
                templateVersions.versions.append(str(newTemplate.id))                
                templateVersions.save()
            except:
                content = {'message':'No template version found with the given id.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            templateVersion = TemplateVersion(nbVersions=1, isDeleted=False).save()
            hash = hashlib.sha1(request.DATA['content'])
            hex_dig = hash.hexdigest()
            newTemplate = Template(title=request.DATA['title'], filename=request.DATA['filename'], content=request.DATA['content'], version=1, templateVersion=str(templateVersion.id), hash=hex_dig).save()
            templateVersion.versions = [str(newTemplate.id)]
            templateVersion.current=str(newTemplate.id)
            templateVersion.save()
            newTemplate.save()
        return Response(sSerializer.data, status=status.HTTP_201_CREATED)
    return Response(sSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def select_schema(request):
    """
    GET http://localhost/api/templates/select?param1=value1&param2=value2
    URL parameters: 
    id: string (ObjectId)
    filename: string
    content: string
    title: string
    version: integer
    templateVersion: string (ObjectId)
    hash: string
    For string fields, you can use regular expressions: /exp/
    """
    id = request.QUERY_PARAMS.get('id', None)
    filename = request.QUERY_PARAMS.get('filename', None)
    content = request.QUERY_PARAMS.get('content', None)
    title = request.QUERY_PARAMS.get('title', None)
    version = request.QUERY_PARAMS.get('version', None)
    templateVersion = request.QUERY_PARAMS.get('templateVersion', None)
    hash = request.QUERY_PARAMS.get('hash', None)
    
    try:        
        # create a connection                                                                                                                                                                                                 
        connection = Connection()
        # connect to the db 'mgi'
        db = connection['mgi']
        # get the xmldata collection
        template = db['template']
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if filename is not None:
            if filename[0] == '/' and filename[-1] == '/':
                query['filename'] = re.compile(filename[1:-1])
            else:
                query['filename'] = filename            
        if content is not None:
            if content[0] == '/' and content[-1] == '/':
                query['content'] = re.compile(content[1:-1])
            else:
                query['content'] = content
        if title is not None:
            if title[0] == '/' and title[-1] == '/':
                query['title'] = re.compile(title[1:-1])
            else:
                query['title'] = title
        if version is not None:
            query['version'] = version
        if templateVersion is not None:
            if templateVersion[0] == '/' and templateVersion[-1] == '/':
                query['templateVersion'] = re.compile(templateVersion[1:-1])
            else:
                query['templateVersion'] = templateVersion
        if hash is not None:
            if hash[0] == '/' and hash[-1] == '/':
                query['hash'] = re.compile(hash[1:-1])
            else:
                query['hash'] = hash
        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            cursor = template.find(query)
            templates = []
            for resultTemplate in cursor:
                resultTemplate['id'] = resultTemplate['_id']
                del resultTemplate['_id']
                templates.append(resultTemplate)
            serializer = templateSerializer(templates)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        content = {'message':'No template found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def select_all_schemas(request):
    """
    GET http://localhost/api/templates/select/all
    """
    templates = Template.objects
    serializer = templateSerializer(templates)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def select_all_schemas_versions(request):
    """
    GET http://localhost/api/schemas/versions/select/all
    """
    templateVersions = TemplateVersion.objects
    serializer = TemplateVersionSerializer(templateVersions)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def current_template_version(request):
    """
    GET http://localhost/api/templates/versions/current?id=IdToBeCurrent
    """
    id = request.QUERY_PARAMS.get('id', None)
    if id is not None:   
        try:
            template = Template.objects.get(pk=id)        
        except:
            content = {'message':'No template found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No template id provided to be current.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    templateVersion = TemplateVersion.objects.get(pk=template.templateVersion)
    if templateVersion.isDeleted == True:
        content = {'message':'This template version belongs to a deleted template. You are not allowed to restore it. Please restore the template first (id:'+ str(templateVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if templateVersion.current == id:
        content = {'message':'The selected template is already the current template.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if id in templateVersion.deletedVersions:
        content = {'message':'The selected template is deleted. Please restore it first to make it current.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    templateVersion.current = id
    templateVersion.save()
    content = {'message':'Current template set with success.'}
    return Response(content, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def delete_schema(request):
    """
    GET http://localhost/api/templates/delete?id=IDtodelete&next=IDnextCurrent
    GET http://localhost/api/templates/delete?templateVersion=IDtodelete
    URL parameters: 
    id: string (ObjectId)
    next: string (ObjectId)
    templateVersion: string (ObjectId)
    """
    id = request.QUERY_PARAMS.get('id', None)
    next = request.QUERY_PARAMS.get('next', None)
    versionID = request.QUERY_PARAMS.get('templateVersion', None)  
    
    if versionID is not None:
        if id is not None or next is not None:
            content = {'message':'Wrong parameters combination.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                templateVersion = TemplateVersion.objects.get(pk=versionID)
                if templateVersion.isDeleted == False:
                    templateVersion.deletedVersions.append(templateVersion.current)
                    templateVersion.isDeleted = True
                    templateVersion.save()
                    content = {'message':'Template version deleted with success.'}
                    return Response(content, status=status.HTTP_200_OK)
                else:
                    content = {'message':'Template version already deleted.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except:
                content = {'message':'No template version found with the given id.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)
    
    if id is not None:   
        try:
            template = Template.objects.get(pk=id)        
        except:
            content = {'message':'No template found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No template id provided to delete.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if next is not None:
        try:
            nextCurrent = Template.objects.get(pk=next)
            if nextCurrent.templateVersion != template.templateVersion:
                content = {'message':'The specified next current template is not a version of the current template.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except:
            content = {'message':'No template found with the given id to be the next current.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        
    templateVersion = TemplateVersion.objects.get(pk=template.templateVersion)
    if templateVersion.isDeleted == True:
        content = {'message':'This template version belongs to a deleted template. You are not allowed to restore it. Please restore the template first (id:'+ str(templateVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if templateVersion.current == str(template.id) and next is None:
        content = {'message':'The selected template is the current. It can\'t be deleted. If you still want to delete this template, please provide the id of the next current template using \'next\' parameter'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif templateVersion.current == str(template.id) and next is not None and str(template.id) == str(nextCurrent.id):
        content = {'message':'Template id to delete and next id are the same.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif templateVersion.current != str(template.id) and next is not None:
        content = {'message':'You should only provide the next parameter when you want to delete a current version of a template.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif templateVersion.current == str(template.id) and next is not None:
        if next in templateVersion.deletedVersions:
            content = {'message':'The template is deleted, it can\'t become current.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        templateVersion.deletedVersions.append(str(template.id)) 
        templateVersion.current = str(nextCurrent.id)
        templateVersion.save()
        content = {'message':'Current template deleted with success. A new version is current.'}
        return Response(content, status=status.HTTP_204_NO_CONTENT)
    else:
#             del templateVersion.versions[templateVersion.versions.index(str(template.id))]
#             template.delete()
        if str(template.id) in templateVersion.deletedVersions:
            content = {'message':'This template is already deleted.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        templateVersion.deletedVersions.append(str(template.id)) 
        templateVersion.save()
        content = {'message':'Template deleted with success.'}
        return Response(content, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def restore_schema(request):
    """
    GET http://localhost/api/templates/restore?id=IDtorestore
    GET http://localhost/api/templates/delete?templateVersion=IDtorestore
    URL parameters: 
    id: string (ObjectId)
    templateVersion: string (ObjectId)
    """
    id = request.QUERY_PARAMS.get('id', None)    
    versionID = request.QUERY_PARAMS.get('templateVersion', None)
    
    if versionID is not None:
        if id is not None:
            content = {'message':'Wrong parameters combination.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                templateVersion = TemplateVersion.objects.get(pk=versionID)
                if templateVersion.isDeleted == False:
                    content = {'message':'Template version not deleted. No need to be restored.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                else:
                    templateVersion.isDeleted = False
                    del templateVersion.deletedVersions[templateVersion.deletedVersions.index(templateVersion.current)]
                    templateVersion.save()
                    content = {'message':'Template restored with success.'}
                    return Response(content, status=status.HTTP_200_OK)
            except:
                content = {'message':'No template version found with the given id.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)
        
    if id is not None:   
        try:
            template = Template.objects.get(pk=id)        
        except:
            content = {'message':'No template found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No template id provided to restore.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    templateVersion = TemplateVersion.objects.get(pk=template.templateVersion)
    if templateVersion.isDeleted == True:
        content = {'message':'This template version belongs to a deleted template. You are not allowed to restore it. Please restore the template first (id:'+ str(templateVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if id in templateVersion.deletedVersions:
        del templateVersion.deletedVersions[templateVersion.deletedVersions.index(id)]
        templateVersion.save()
        content = {'message':'Template version restored with success.'}
        return Response(content, status=status.HTTP_200_OK)
    else:
        content = {'message':'Template version not deleted. No need to be restored.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_ontology(request):
    """
    POST http://localhost/api/types/add
    POST data title="title", filename="filename", content="..." ontologyVersion="id"
    """
    oSerializer = ontologySerializer(data=request.DATA)
    if oSerializer.is_valid():
        # an ontology version is provided: if it exists, add the ontology as a new version and manage the version numbers
        if "ontologyVersion" in request.DATA:
            try:
                ontologyVersions = OntologyVersion.objects.get(pk=request.DATA['ontologyVersion'])
                if ontologyVersions.isDeleted == True:
                    content = {'message':'This ontology version belongs to a deleted ontology. You are not allowed to delete it.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                ontologyVersions.nbVersions = ontologyVersions.nbVersions + 1
                newOntology = Ontology(title=request.DATA['title'], filename=request.DATA['filename'], content=request.DATA['content'], ontologyVersion=request.DATA['ontologyVersion'], version=ontologyVersions.nbVersions).save()
                ontologyVersions.versions.append(str(newOntology.id))                
                ontologyVersions.save()
            except:
                content = {'message':'No ontology version found with the given id.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            ontologyVersion = OntologyVersion(nbVersions=1, isDeleted=False).save()
            newOntology = Ontology(title=request.DATA['title'], filename=request.DATA['filename'], content=request.DATA['content'], version=1, ontologyVersion=str(ontologyVersion.id)).save()
            ontologyVersion.versions = [str(newOntology.id)]
            ontologyVersion.current=str(newOntology.id)
            ontologyVersion.save()
            newOntology.save()
        return Response(oSerializer.data, status=status.HTTP_201_CREATED)
    return Response(oSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def select_ontology(request):
    """
    GET http://localhost/api/types/select?param1=value1&param2=value2
    URL parameters: 
    id: string (ObjectId)
    filename: string
    content: string
    title: string
    version: integer
    ontologyVersion: string (ObjectId)
    For string fields, you can use regular expressions: /exp/
    """
    id = request.QUERY_PARAMS.get('id', None)
    filename = request.QUERY_PARAMS.get('filename', None)
    content = request.QUERY_PARAMS.get('content', None)
    title = request.QUERY_PARAMS.get('title', None)
    version = request.QUERY_PARAMS.get('version', None)
    ontologyVersion = request.QUERY_PARAMS.get('ontologyVersion', None)
    
    try:        
        # create a connection                                                                                                                                                                                                 
        connection = Connection()
        # connect to the db 'mgi'
        db = connection['mgi']
        # get the xmldata collection
        ontology = db['ontology']
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if filename is not None:
            if filename[0] == '/' and filename[-1] == '/':
                query['filename'] = re.compile(filename[1:-1])
            else:
                query['filename'] = filename            
        if content is not None:
            if content[0] == '/' and content[-1] == '/':
                query['content'] = re.compile(content[1:-1])
            else:
                query['content'] = content
        if title is not None:
            if title[0] == '/' and title[-1] == '/':
                query['title'] = re.compile(title[1:-1])
            else:
                query['title'] = title
        if version is not None:
            query['version'] = version
        if ontologyVersion is not None:
            if ontologyVersion[0] == '/' and ontologyVersion[-1] == '/':
                query['ontologyVersion'] = re.compile(ontologyVersion[1:-1])
            else:
                query['ontologyVersion'] = ontologyVersion
        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            cursor = ontology.find(query)
            ontologies = []
            for resultOntology in cursor:
                resultOntology['id'] = resultOntology['_id']
                del resultOntology['_id']
                ontologies.append(resultOntology)
            serializer = resOntologySerializer(ontologies)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        content = {'message':'No ontology found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def select_all_ontologies(request):
    """
    GET http://localhost/api/types/select/all
    """
    ontologies = Ontology.objects
    serializer = resOntologySerializer(ontologies)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def select_all_ontologies_versions(request):
    """
    GET http://localhost/api/types/versions/select/all
    """
    ontologyVersions = OntologyVersion.objects
    serializer = OntologyVersionSerializer(ontologyVersions)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def current_ontology_version(request):
    """
    GET http://localhost/api/types/versions/current?id=IdToBeCurrent
    """
    id = request.QUERY_PARAMS.get('id', None)
    if id is not None:   
        try:
            ontology = Ontology.objects.get(pk=id)        
        except:
            content = {'message':'No ontology found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No ontology id provided to be current.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    ontologyVersion = OntologyVersion.objects.get(pk=ontology.ontologyVersion)
    if ontologyVersion.isDeleted == True:
        content = {'message':'This ontology version belongs to a deleted ontology. You are not allowed to restore it. Please restore the ontology first (id:'+ str(ontologyVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if ontologyVersion.current == id:
        content = {'message':'The selected ontology is already the current ontology.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if id in ontologyVersion.deletedVersions:
        content = {'message':'The selected ontology is deleted. Please restore it first to make it current.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    ontologyVersion.current = id
    ontologyVersion.save()
    content = {'message':'Current ontology set with success.'}
    return Response(content, status=status.HTTP_200_OK)

@api_view(['GET'])
def delete_ontology(request):
    """
    GET http://localhost/api/types/delete?id=IDtodelete&next=IDnextCurrent
    GET http://localhost/api/types/delete?ontologyVersion=IDtodelete
    URL parameters: 
    id: string (ObjectId)
    next: string (ObjectId)
    ontologyVersion: string (ObjectId)
    """
    id = request.QUERY_PARAMS.get('id', None)
    next = request.QUERY_PARAMS.get('next', None)  
    versionID = request.QUERY_PARAMS.get('ontologyVersion', None)  
    
    if versionID is not None:
        if id is not None or next is not None:
            content = {'message':'Wrong parameters combination.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                ontologyVersion = OntologyVersion.objects.get(pk=versionID)
                if ontologyVersion.isDeleted == False:
                    ontologyVersion.deletedVersions.append(ontologyVersion.current)
                    ontologyVersion.isDeleted = True
                    ontologyVersion.save()
                    content = {'message':'Ontology version deleted with success.'}
                    return Response(content, status=status.HTTP_200_OK)
                else:
                    content = {'message':'Ontology version already deleted.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
            except:
                content = {'message':'No ontology version found with the given id.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)
            
    if id is not None:   
        try:
            ontology = Ontology.objects.get(pk=id)        
        except:
            content = {'message':'No ontology found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No ontology id provided to delete.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    if next is not None:
        try:
            nextCurrent = Ontology.objects.get(pk=next)
            if nextCurrent.ontologyVersion != ontology.ontologyVersion:
                content = {'message':'The specified next current ontology is not a version of the current ontology.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except:
            content = {'message':'No ontology found with the given id to be the next current.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        
    ontologyVersion = OntologyVersion.objects.get(pk=ontology.ontologyVersion)
    if ontologyVersion.isDeleted == True:
        content = {'message':'This ontology version belongs to a deleted ontology. You are not allowed to delete it. please restore the ontology first (id='+ str(ontologyVersion.id) +')'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if ontologyVersion.current == str(ontology.id) and next is None:
        content = {'message':'The selected ontology is the current. It can\'t be deleted. If you still want to delete this ontology, please provide the id of the next current ontology using \'next\' parameter'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif ontologyVersion.current == str(ontology.id) and next is not None and str(ontology.id) == str(nextCurrent.id):
        content = {'message':'Ontology id to delete and next id are the same.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif ontologyVersion.current != str(ontology.id) and next is not None:
        content = {'message':'You should only provide the next parameter when you want to delete a current version of a ontology.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif ontologyVersion.current == str(ontology.id) and next is not None:
        if next in ontologyVersion.deletedVersions:
            content = {'message':'The ontology is deleted, it can\'t become current.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        ontologyVersion.deletedVersions.append(str(ontology.id)) 
        ontologyVersion.current = str(nextCurrent.id)
        ontologyVersion.save()
        content = {'message':'Current ontology deleted with success. A new version is current.'}
        return Response(content, status=status.HTTP_204_NO_CONTENT)
    else:
        if str(ontology.id) in ontologyVersion.deletedVersions:
            content = {'message':'This ontology is already deleted.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        ontologyVersion.deletedVersions.append(str(ontology.id)) 
        ontologyVersion.save()
        content = {'message':'Ontology deleted with success.'}
        return Response(content, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def restore_ontology(request):
    """
    GET http://localhost/api/types/restore?id=IDtorestore
    GET http://localhost/api/types/delete?ontologyVersion=IDtorestore
    URL parameters: 
    id: string (ObjectId)
    ontologyVersion: string (ObjectId)
    """
    id = request.QUERY_PARAMS.get('id', None)    
    versionID = request.QUERY_PARAMS.get('ontologyVersion', None)
    
    if versionID is not None:
        if id is not None:
            content = {'message':'Wrong parameters combination.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                ontologyVersion = OntologyVersion.objects.get(pk=versionID)
                if ontologyVersion.isDeleted == False:
                    content = {'message':'Ontology version not deleted. No need to be restored.'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                else:
                    ontologyVersion.isDeleted = False
                    del ontologyVersion.deletedVersions[ontologyVersion.deletedVersions.index(ontologyVersion.current)]
                    ontologyVersion.save()
                    content = {'message':'Ontology restored with success.'}
                    return Response(content, status=status.HTTP_200_OK)
            except:
                content = {'message':'No ontology version found with the given id.'}
                return Response(content, status=status.HTTP_404_NOT_FOUND)
        
    if id is not None:   
        try:
            ontology = Ontology.objects.get(pk=id)        
        except:
            content = {'message':'No ontology found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No ontology id provided to restore.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    ontologyVersion = OntologyVersion.objects.get(pk=ontology.ontologyVersion)
    if ontologyVersion.isDeleted == True:
        content = {'message':'This ontology version belongs to a deleted ontology. You are not allowed to restore it. Please restore the ontology first (id:'+ str(ontologyVersion.id) +').'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if id in ontologyVersion.deletedVersions:
        del ontologyVersion.deletedVersions[ontologyVersion.deletedVersions.index(id)]
        ontologyVersion.save()
        content = {'message':'Ontology version restored with success.'}
        return Response(content, status=status.HTTP_200_OK)
    else:
        content = {'message':'Ontology version not deleted. No need to be restored.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def select_all_repositories(request):
    """
    GET http://localhost/api/repositories/select/all
    """
    instances = Instance.objects
    serializer = instanceSerializer(instances)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def select_repository(request):
    """
    GET http://localhost/api/repositories/select?param1=value1&param2=value2
    URL parameters: 
    id: string (ObjectId)
    name: string
    protocol: string
    address: string
    port: integer
    user: string
    status: string
    For string fields, you can use regular expressions: /exp/
    """
    id = request.QUERY_PARAMS.get('id', None)
    name = request.QUERY_PARAMS.get('filename', None)
    protocol = request.QUERY_PARAMS.get('protocol', None)
    address = request.QUERY_PARAMS.get('address', None)
    port = request.QUERY_PARAMS.get('port', None)
    user = request.QUERY_PARAMS.get('user', None)
    inst_status = request.QUERY_PARAMS.get('status', None)
    
    try:        
        # create a connection                                                                                                                                                                                                 
        connection = Connection()
        # connect to the db 'mgi'
        db = connection['mgi']
        # get the xmldata collection
        instance = db['instance']
        query = dict()
        if id is not None:            
            query['_id'] = ObjectId(id)            
        if name is not None:
            if name[0] == '/' and name[-1] == '/':
                query['name'] = re.compile(name[1:-1])
            else:
                query['name'] = name            
        if protocol is not None:
            if protocol[0] == '/' and protocol[-1] == '/':
                query['protocol'] = re.compile(protocol[1:-1])
            else:
                query['protocol'] = protocol
        if address is not None:
            if address[0] == '/' and address[-1] == '/':
                query['address'] = re.compile(address[1:-1])
            else:
                query['address'] = address
        if port is not None:
            query['port'] = port
        if user is not None:
            if user[0] == '/' and user[-1] == '/':
                query['user'] = re.compile(user[1:-1])
            else:
                query['user'] = user
        if inst_status is not None:
            if inst_status[0] == '/' and inst_status[-1] == '/':
                query['status'] = re.compile(inst_status[1:-1])
            else:
                query['status'] = inst_status
        if len(query.keys()) == 0:
            content = {'message':'No parameters given.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            cursor = instance.find(query)
            instances = []
            for resultInstance in cursor:
                resultInstance['id'] = resultInstance['_id']
                del resultInstance['_id']
                instances.append(resultInstance)
            serializer = resInstanceSerializer(instances)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        content = {'message':'No template found with the given parameters.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def add_repository(request):
    """
    POST http://localhost/api/repositories/add
    POST data name="name", protocol="protocol", address="address", port=port, user="user", password="password"
    """
    iSerializer = instanceSerializer(data=request.DATA)
    if iSerializer.is_valid():
        errors = ""
        # test if the protocol is HTTP or HTTPS
        if request.DATA['protocol'].upper() not in ['HTTP','HTTPS']:
            errors += 'Allowed protocol are HTTP and HTTPS.'
        # test if the name is "Local"
        if (request.DATA['name'] == ""):
            errors += "The name cannot be empty."
        elif (request.DATA['name'] == "Local"):
            errors += 'By default, the instance named Local is the instance currently running.'
        else:
            # test if an instance with the same name exists
            instance = Instance.objects(name=request.DATA['name'])
            if len(instance) != 0:
                errors += "An instance with the same name already exists."
        regex = re.compile("^[0-9]{1,5}$")
        if not regex.match(str(request.DATA['port'])):
            errors += "The port number is not valid."
        regex = re.compile("^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if not regex.match(request.DATA['address']):
            errors += "The address is not valid."
        # test if new instance is not the same as the local instance
        if request.DATA['address'] == request.META['REMOTE_ADDR'] and str(request.DATA['port']) == request.META['SERVER_PORT']:
            errors += "The address and port you entered refer to the instance currently running."
        else:
            # test if an instance with the same address/port exists
            instance = Instance.objects(address=request.DATA['address'], port=request.DATA['port'])
            if len(instance) != 0:
                errors += "An instance with the address/port already exists."
        
        if errors != "":
            content = {'message': errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        inst_status = "Unreachable"
        try:
            url = request.DATA['protocol'] + "://" + request.DATA['address'] + ":" + request.DATA['port'] + "/api/ping"
            r = requests.get(url, auth=(request.DATA['user'], request.DATA['password']))
            if r.status_code == 200:
                inst_status = "Reachable"
        except Exception, e:
            pass
        Instance(name=request.DATA['name'], protocol=request.DATA['protocol'], address=request.DATA['address'], port=request.DATA['port'], user=request.DATA['user'], password=request.DATA['password'], status=inst_status).save()
        return Response(iSerializer.data, status=status.HTTP_201_CREATED)
    return Response(iSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def delete_repository(request):
    """
    GET http://localhost/api/repositories/delete?id=IDtodelete
    """
    id = request.QUERY_PARAMS.get('id', None)
    
    if id is not None:   
        try:
            instance = Instance.objects.get(pk=id)        
        except:
            content = {'message':'No instance found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No instance id provided to restore.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    instance.delete()
    content = {'message':'Instance deleted with success.'}
    return Response(content, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_repository(request):  
    """
    PUT http://localhost/api/repositories/update?id=IDtoUpdate
    PUT data name="name", protocol="protocol", address="address", port=port, user="user", password="password"
    """    
    id = request.QUERY_PARAMS.get('id', None)        
    
    if id is not None:   
        try:
            instance = Instance.objects.get(pk=id)        
        except:
            content = {'message':'No instance found with the given id.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No instance id provided to restore.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    serializer = instanceSerializer(instance, data=request.DATA)
    if serializer.is_valid():
        errors = ""
        # test if the protocol is HTTP or HTTPS
        if request.DATA['protocol'].upper() not in ['HTTP','HTTPS']:
            errors += 'Allowed protocol are HTTP and HTTPS.'
        # test if the name is "Local"
        if (request.DATA['name'] == ""):
            errors += "The name cannot be empty."
        elif (request.DATA['name'] == "Local"):
            errors += 'By default, the instance named Local is the instance currently running.'
        else:
            # test if an instance with the same name exists
            instances = Instance.objects(name=request.DATA['name'])
            if len(instances) != 0:
                errors += "An instance with the same name already exists."
        regex = re.compile("^[0-9]{1,5}$")
        if not regex.match(str(request.DATA['port'])):
            errors += "The port number is not valid."
        regex = re.compile("^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if not regex.match(request.DATA['address']):
            errors += "The address is not valid."
        # test if new instance is not the same as the local instance
        if request.DATA['address'] == request.META['REMOTE_ADDR'] and str(request.DATA['port']) == request.META['SERVER_PORT']:
            errors += "The address and port you entered refer to the instance currently running."
        else:
            # test if an instance with the same address/port exists
            instances = Instance.objects(address=request.DATA['address'], port=request.DATA['port'])
            if len(instances) != 0:
                errors += "An instance with the address/port already exists."
        
        if errors != "":
            content = {'message': errors}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        
        inst_status = "Unreachable"
        try:
            url = request.DATA['protocol'] + "://" + request.DATA['address'] + ":" + request.DATA['port'] + "/api/ping"
            r = requests.get(url, auth=(request.DATA['user'], request.DATA['password']))
            if r.status_code == 200:
                inst_status = "Reachable"
        except Exception, e:
            pass
        instance.name=request.DATA['name']
        instance.protocol=request.DATA['protocol']
        instance.address=request.DATA['address']
        instance.port=request.DATA['port']
        instance.user=request.DATA['user']
        instance.password=request.DATA['password']
        instance.status=inst_status
        instance.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def select_all_users(request):
    """
    GET http://localhost/api/users/select/all
    """
    users = User.objects.all()
    serializer = UserSerializer(users)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def select_user(request):
    """
    GET http://localhost/api/users/select?param1=value1&param2=value2
    URL parameters: 
    username: string
    first_name: string
    last_name: string
    email: string    
    For string fields, you can use regular expressions: /exp/
    """    
    username = request.QUERY_PARAMS.get('username', None)
    first_name = request.QUERY_PARAMS.get('first_name', None)
    last_name = request.QUERY_PARAMS.get('last_name', None)
    email = request.QUERY_PARAMS.get('email', None)
            
    predicates = []
    if username is not None:
        if username[0] == '/' and username[-1] == '/':
            predicates.append(['username__regex',username[1:-1]])
        else:
            predicates.append(['username',username])
    if first_name is not None:
        if first_name[0] == '/' and first_name[-1] == '/':
            predicates.append(['first_name__regex',first_name[1:-1]])
        else:
            predicates.append(['first_name',first_name])
    if last_name is not None:
        if last_name[0] == '/' and last_name[-1] == '/':
            predicates.append(['last_name__regex',last_name[1:-1]])
        else:
            predicates.append(['last_name',last_name])
    if email is not None:
        if email[0] == '/' and email[-1] == '/':
            predicates.append(['email__regex',email[1:-1]])
        else:
            predicates.append(['email',email])
    
    q_list = [Q(x) for x in predicates]
    if len(q_list) != 0:
        try:
            users = User.objects.get(reduce(operator.and_, q_list))
        except:
            users = []
    else:
        users = []
    serializer = UserSerializer(users)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_user(request):
    """
    POST http://localhost/api/users/add
    POST data username="username", password="password" first_name="first_name", last_name="last_name", port=port, email="email"
    """    
    serializer = insertUserSerializer(data=request.DATA)
    if serializer.is_valid():
        username = request.DATA['username']
        password = request.DATA['password']
        if 'first_name' in request.DATA:
            first_name = request.DATA['first_name']
        else:
            first_name = ""
        if 'last_name' in request.DATA:
            last_name = request.DATA['last_name']
        else:
            last_name = ""
        if 'email' in request.DATA:
            email = request.DATA['email']
        else:
            email = ""
        try:
            user = User.objects.create_user(username=username,password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception, e:
            content = {'message':e.message}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def delete_user(request):
    """
    GET http://localhost/api/users/delete?username=username
    URL parameters: 
    username: string
    """
    username = request.QUERY_PARAMS.get('username', None)
    if username is not None:
        try:
            user = User.objects.get(username=username)
            user.delete()
            content = {'message':"User deleted with success."}
            return Response(content, status=status.HTTP_200_OK)
        except:
            content = {'message':"The given username does not exist."}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':"No username provided."}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['PUT'])
def update_user(request):
    """
    PUT http://localhost/api/users/update?username=userToUpdate
    PUT data first_name="first_name", last_name="last_name", port=port, email="email"
    """    
    username = request.QUERY_PARAMS.get('username', None)        
        
    if id is not None:   
        try:
            user = User.objects.get(username=username)        
        except:
            content = {'message':'No user found with the given username.'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    else:
        content = {'message':'No username provided to restore.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    serializer = updateUserSerializer(data=request.DATA)
    if serializer.is_valid():    
        try:
            if 'first_name' in request.DATA:
                user.first_name = request.DATA['first_name']
            if 'last_name' in request.DATA:
                user.last_name = request.DATA['last_name']
            if 'email' in request.DATA:
                user.email = request.DATA['email']
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception, e:
            content = {'message':e.message}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def docs(request):
    content={'message':'Invalid command','docs':'http://'+str(request.get_host())+'/docs/api'}
    return Response(content, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def ping(request):
    content={'message':'Endpoint reached'}
    return Response(content, status=status.HTTP_200_OK)
