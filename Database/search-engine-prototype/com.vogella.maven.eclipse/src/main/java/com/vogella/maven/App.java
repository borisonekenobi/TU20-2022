package com.vogella.maven;

import com.mongodb.*;
import com.mongodb.client.MongoClients;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Filters;

import com.mongodb.client.model.UpdateOptions;
import com.mongodb.client.result.*;
import org.bson.Document;
import org.bson.types.ObjectId;

import java.util.List;
import java.util.Scanner;
import java.util.regex.Pattern;
import java.util.Arrays;
import java.util.ArrayList;

import org.bson.Document;
import org.bson.conversions.Bson;

import static com.mongodb.client.model.Filters.*;
import static com.mongodb.client.model.Updates.*;
import com.mongodb.client.model.Projections;
import com.mongodb.client.model.Sorts;

public class App {
    public static void main(String[] args) {
    	Scanner input = new Scanner(System.in);
    	
    	String search = "";
    	while (true) {
	    	System.out.print("Enter Search Query: ");
	    	search = input.nextLine();

	    	if (search.equals("")) {
	    		break;
	    	}
	    	
	    	MongoClient client = MongoClients.create("mongodb://collectionreader:secretpass@vasilevk.tplinkdns.com/plants");
	    	MongoDatabase database = client.getDatabase("plants");
	    	MongoCollection<Document> plants = database.getCollection("plants");
	    	
	    	Bson projectionFields = Projections.fields(
	    			Projections.include("name", "latin_name", "group"),
	    			Projections.excludeId());
	    	
	    	Document regQuery = new Document();
	    	regQuery.append("$regex", "(?)" + Pattern.quote(search));
	    	regQuery.append("$options", "i");
	
	    	Document findQuery = new Document();
	    	findQuery.append("name", regQuery);
	    	//findQuery.append("flowers.color", "White");
	    	
	    	MongoCursor<Document> cursor = plants.find(findQuery)
	    			.projection(projectionFields)
	    			.sort(Sorts.ascending("Name"))
	    			.iterator();
	    	
	    	try {
	    		while (cursor.hasNext()) {
	    			System.out.println(cursor.next().toJson());
	    		}
	    	} finally {
	    		cursor.close();
	    	}
    	}
    	
    	input.close();
    	System.out.println("Exiting search");
    }
}
