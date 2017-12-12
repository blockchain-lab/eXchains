import com.opencsv.CSVReader;
import org.graphstream.graph.Edge;
import org.graphstream.graph.Node;

import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Random;
import java.util.concurrent.BrokenBarrierException;

public class Household_Client extends Thread{

    int ID;
    Blockchain blockchain;
    Edge e;
    Node n;

    double consRegulationAmount = 0;
    double prodRegulationAmount = 0;



    public void run() {
        System.out.println("Household " + ID + " started");

        CSVReader csvReader;

        try {
            //open data file
            Reader reader = Files.newBufferedReader(Paths.get("SimulationData.csv"));
            csvReader = new CSVReader(reader, ';');

            //read first line with header data
            csvReader.readNext();

            //to make simulation more interesting let each client thread start on differnt day from data
            Random rn = new Random();
            int rand = rn.nextInt(41);
            for (int i = 0; i < rand*1440; i++) {
                csvReader.readNext();
            }

            //TODO andere start tijd
            // start on 11:00
//            for (int i = 0; i < 60*11; i++) {
//                csvReader.readNext();
//            }

            // each loop we send:
            Double production = 0.0;
            Double consumption = 0.0;
            HashMap<String, Double> predictedCons = new HashMap<>();
            HashMap<String, Double> predictedProd = new HashMap<>();
            HashMap<Integer, Double> consFlexibility = new HashMap<>();
            HashMap<Integer, Double> prodFlexibility = new HashMap<>();

            // Main loop
            while(true){

                consFlexibility = new HashMap<>();
                prodFlexibility = new HashMap<>();

                // sync up all houses
                sync();
                rn = new Random();
                rand = rn.nextInt(500);
                delay(rand);



                // Reading Records One by One in a String array
                String[] nextRecord;

                // "predict" data from coming time block
                Double preProduction = 0.0;
                Double preConsumption = 0.0;
                for (int i = 0; i < Main.TimeSlotMin; i++) {
                    //A single entry is in watt power for that minute.
                    //divide by 60 becomes wh and wh can be summed
                    if((nextRecord = csvReader.readNext()) != null){
                        preConsumption += Double.parseDouble(nextRecord[3].replace(',', '.'))/60;
                        preProduction += Double.parseDouble(nextRecord[4].replace(',', '.'))/60;
                    }else{
                        System.err.println("Household " + ID + " reached EOF!");
                        break;
                    }
                }
                predictedCons.put("t1", preConsumption);
                predictedProd.put("t1", preProduction);

                //System.out.println("Household " + ID + " preConsumption: " + preConsumption + ", preProduction: " + preProduction);

                //TODO put something in offeredFlexibility

                int P1P = rn.nextInt(900)+100;    // 100 - 1000
                int P1N = -1*rn.nextInt(900)+100;    // 100 - 1000
                Double W1 = ((double)rn.nextInt(10));            // 0 - 10


                int P2P = rn.nextInt(4500)+500;    //  500 - 50000
                int P2N = -1*rn.nextInt(4500)+500;    //  500 - 50000
                Double W2 = ((double)rn.nextInt(133));          // 0 - 133

                int P3P = rn.nextInt(4000)+4000;   //  40000 - 80000
                int P3N = -1*rn.nextInt(4000)+4000;   //  40000 - 80000
                Double W3 = ((double)rn.nextInt(50));            // 0 - 50


                prodFlexibility.put(P1P, W1);
                consFlexibility.put(P1N, W1);

                prodFlexibility.put(P2P, W2);
                consFlexibility.put(P2N, W2);

                prodFlexibility.put(P3P, W2);
                consFlexibility.put(P3N, W2);

                //System.out.println("HouseHold " + ID + " adjusted consumption: " + consRegulationAmount + " adjusted production: " + prodRegulationAmount);
                consumption += consRegulationAmount;
                production += prodRegulationAmount;

                // build Client report
                ClientReport report = new ClientReport( ID, production, consumption, predictedCons, predictedProd, consFlexibility, prodFlexibility);

                // set production and consumption for next report
                consumption = preConsumption;
                production = preProduction;


                delay(1000*Main.simSpeed);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void sendRegulationReport(RegulationReport report){
        //System.out.println("HouseHold " + ID + "recived regulationReport");

        consRegulationAmount = report.getConsRegulationAmount();
        prodRegulationAmount = report.getProdRegulationAmount();

        //TODO verdeel energie onder clients
    }

    private void sync(){

    }

    private void delay(int millis){
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

}
