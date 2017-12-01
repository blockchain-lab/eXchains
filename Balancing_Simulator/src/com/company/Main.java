package com.company;

import com.opencsv.CSVReader;

import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Paths;

public class Main {

    public static void main(String[] args) {
	    System.out.println("hello Balancing Simulator");

        Reader reader = null;
        try {
            reader = Files.newBufferedReader(Paths.get("C:\\Users\\Nelis\\Documents\\Local GITHUB\\DEM\\Balancing_Simulator\\SimulationData.csv"));
            CSVReader csvReader = new CSVReader(reader, ';');

            // Reading Records One by One in a String array
            String[] nextRecord;
            while ((nextRecord = csvReader.readNext()) != null) {
                System.out.println("Simulation.Date : " + nextRecord[0]);
                System.out.println("Simulation.Minute : " + nextRecord[1]);
                System.out.println("Simulation.OutdoorTemperature : " + nextRecord[2]);
                System.out.println("TotalElectricityConsumption : " + nextRecord[3]);
                System.out.println("TotalElectricityProduction : " + nextRecord[4]);
                System.out.println("==========================");

            }

        } catch (IOException e) {
            e.printStackTrace();
        }



    }
}
