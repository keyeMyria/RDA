//###############################################################################
//
// File Name: rdfserver.java
// Application: rdf
// Description: 
//
//
// Author:    Guillaume Sousa
//            guillaume.sousa@nist.gov
// Co-Author: Sharief Youssef
//            sharief.youssef@nist.gov
//
// Sponsor: National Institute of Standards and Technology (NIST)
//
//###############################################################################

import java.io.ByteArrayInputStream;
import java.io.InputStream;

import org.zeromq.ZMQ;

import com.hp.hpl.jena.query.Dataset;
import com.hp.hpl.jena.query.ReadWrite;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.tdb.TDBFactory;


public class rdfserver {
	
    //TODO: be sure it is the same address/port as in the client
    public static String SERVER_ENDPOINT; // = "tcp://127.0.0.1:5555";
	
    // TODO: replace by the real folder name in the project
    public static String TDB_DIRECTORY; // = "C:\Users\GAS2\workspace_prod\MGI_Project\mdcs\data\ts";
	
    //TODO: replace by the same project URI as in insertRDFForJena
    public static String PROJECT_URI; // = "http://www.example.com/";
	
    // rdfserver -server_endpoint "tcp://127.0.0.1:5555" -tdb_directory "C:\Users\GAS2\workspace_prod\MGI_Project\mdcs\data\ts" -project_uri "http://www.example.com/"
    public static void main(String[] args) throws Exception {
	if (args.length < 6) {
	    System.out.println("USAGE: rdfserver -server_endpoint <SERVER_ENDPOINT> -tdb_directory <TDB_DIRECTORY> -project_uri <PROJECT_URI>");
	    return;
	} else {
	    for (int i=0;i<6;i=i+2) {
		if (args[i].equals("-server_endpoint")) {
		    SERVER_ENDPOINT = args[i+1];
		    //System.out.println("server endpoint assigned");
		} else if (args[i].equals("-tdb_directory")) {
		    TDB_DIRECTORY = args[i+1];
		    //System.out.println("tdb assigned");
		} else if (args[i].equals("-project_uri")){
		    PROJECT_URI = args[i+1];
		    //System.out.println("project uri assigned");
		} else {
		    System.out.println("USAGE: rdfserver -server_endpoint <SERVER_ENDPOINT> -tdb_directory <TDB_DIRECTORY> -project_uri <PROJECT_URI>");
		    return;
		}
	    }
	}

	//TODO: be sure it is the same context number as in the client
	ZMQ.Context context = ZMQ.context(7);
	// Socket to talk to clients
	ZMQ.Socket responder = context.socket(ZMQ.REP);		 
	responder.bind(SERVER_ENDPOINT);
	
	// Make a TDB-backed dataset				 
	String directory = TDB_DIRECTORY;
	// TODO: need to create the folders before this command
	Dataset dataset = TDBFactory.createDataset(directory) ;
	
	while (true) {
	    try{ 
		// Wait for next request from the client
		byte[] rdf = responder.recv();
		System.out.println("Received RDF");				 	
	
		// create an empty model
		Model modelRDF = ModelFactory.createDefaultModel();
		// read the RDF/XML string
		InputStream rdfIS = new ByteArrayInputStream(rdf);			 				
		modelRDF.read(rdfIS, PROJECT_URI);
		// begin a writing transaction
		dataset.begin(ReadWrite.WRITE) ;
		// get the model from the triple store
		Model modelTDB = dataset.getDefaultModel() ;
		// get the current size of the triple store
		int datasetSize = modelTDB.getGraph().size();
		// add the triples from the RDF/XML file to the triple store
		modelTDB.add(modelRDF);
		// get the new size of the triple store
		int nbTriplesInserted = modelTDB.getGraph().size() - datasetSize;
		// commit the changes
		dataset.commit();    
		// end the transaction
		dataset.end();
		
		// Send reply back to client
		String reply = String.valueOf(nbTriplesInserted);
		responder.send(reply.getBytes(), 0);
	    }catch (Exception e){
		// Send reply back to client
		String reply = e.getMessage();
		responder.send(reply.getBytes(), 0);
	    } 
	}
    }
}