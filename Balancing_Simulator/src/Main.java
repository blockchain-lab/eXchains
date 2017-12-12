

import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Random;

import com.opencsv.CSVReader;


public class Main {

    private static List<Household_Client> Households = new LinkedList<>();
    private static List<Blockchain> blockchains = new LinkedList<>();

    public static final int HousesPerCluster = 100; //max 100 clusters due to (XYY, where X is cluster id, YY is node id)
    public static final int NumberOfClusters = 2; //

    public static final int TimeSlotMin = 5;

    public static final int simSpeed = 3;// time between each client send in seconds -1.5

    public static void main(String[] args) {
        LaurenSophieAPXAlgorithm rootNode = new LaurenSophieAPXAlgorithm(0); //Highest layer node.
        LinkedList<LaurenSophieAPXAlgorithm> level1 = new LinkedList<LaurenSophieAPXAlgorithm>();
        Reader dataFile;

    //Initialize clusters+house hold en other crap
        try {
            dataFile = Files.newBufferedReader(Paths.get("SimulationData.csv"));
        } catch (IOException e) {
            System.out.println("Error while opening data file");
            return;
        }

        //Create a two dimension array of csv readers, first dimension is clsuter id, second is node id
        LinkedList<LinkedList<CSVReader>> inputData = new LinkedList<LinkedList<CSVReader>>();
        //create a list with client reports, first dimmension is cluster id, second is house id
        LinkedList<LinkedList<ClientReport>> reports = new LinkedList<>();
        //List with the aggregated reports, index is cluster id
        LinkedList<ClientReport> aggregatedReports = new LinkedList<>();

        for (int i = 0; i < NumberOfClusters; i++) {
            level1.add(new LaurenSophieAPXAlgorithm(i + 100));
            inputData.add(new LinkedList<CSVReader>());
            for (int j = 0; j < HousesPerCluster; j++) {

                //inputData.get(i).add(new CSVReader(dataFile, ';'));
                try {
                    inputData.get(i).add(new CSVReader((Files.newBufferedReader(Paths.get("SimulationData.csv"))), ';'));
                } catch (IOException e) {
                    e.printStackTrace();
                }


                try {
                    //Skip header parameters
                    inputData.get(i).get(j).readNext();
                    //Set every cvs reader to start at a random day of the week
                    Random rn = new Random();
                    int rand = rn.nextInt(41);
                    System.out.println("Cluster " + i + " Household " + j + " I'm picking day " + rand);
                    for (int k = 0; k < rand * 1440; k++) {
                        inputData.get(i).get(j).readNext();
                    }
                } catch (IOException e) {
                    System.out.println("Something went wrong during the reding of the data");
                    e.printStackTrace();
                }
            }
        }
        while(true) {

            /*
            Copied straight from niels
            This code will generate the client reports and randomly generated flexibility based on the given input file.
            */
            for (int i = 0; i < NumberOfClusters; i++) {
                //This is a new round so start out with a new linked list for every cluster
                //If the this cluster hasn't been initialized initialize, else clear
                if(reports==null || reports.size()<=i){
                    reports.add(new LinkedList<ClientReport>());
                }else{
                    reports.get(i).clear();
                }


                //System.out.println("Generating client reports for Cluster " + i);
                for (int j = 0; j < HousesPerCluster; j++) {

                    //Consumption and production numbers aren't currently used yet.
                    Double production = 0.0;
                    Double consumption = 0.0;


                    HashMap<String, Double> predictedCons = new HashMap<>();
                    HashMap<String, Double> predictedProd = new HashMap<>();
                    HashMap<Integer, Double> consFlexibility = new HashMap<>();
                    HashMap<Integer, Double> prodFlexibility = new HashMap<>();

                    consFlexibility = new HashMap<>();
                    prodFlexibility = new HashMap<>();

                    // "predict" data from coming time block
                    Double preProduction = 0.0;
                    Double preConsumption = 0.0;

                    Random rn = new Random();
                    int rand = rn.nextInt(500);
                    // Reading Records One by One in a String array
                    String[] nextRecord;

                    for (int k = 0; k < TimeSlotMin; k++) {
                        //A single entry is in watt power for that minute.
                        //divide by 60 becomes wh and wh can be summed
                        try {
                            if ((nextRecord = inputData.get(i).get(j).readNext()) != null) {
                                preConsumption += Double.parseDouble(nextRecord[3].replace(',', '.')) / 60;
                                preProduction += Double.parseDouble(nextRecord[4].replace(',', '.')) / 60;
                            } else {
                                System.err.println("Cluster " + i + " household " + j + " reached EOF!");
                                return;
                                //break;
                            }
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                    predictedCons.put("t1", preConsumption);
                    predictedProd.put("t1", preProduction);

                    //System.out.println("Cluster " + i + " household " + j + " preConsumption: " + preConsumption + ", preProduction: " + preProduction);

                    //Randomly generate the offered flexibility

                    int P1P = rn.nextInt(900) + 100;    // 100 - 1000
                    int P1N = -1 * rn.nextInt(900) + 100;    // 100 - 1000
                    Double W1 = ((double) rn.nextInt(10));            // 0 - 10


                    int P2P = rn.nextInt(4500) + 500;    //  500 - 50000
                    int P2N = -1 * rn.nextInt(4500) + 500;    //  500 - 50000
                    Double W2 = ((double) rn.nextInt(133));          // 0 - 133

                    int P3P = rn.nextInt(4000) + 4000;   //  40000 - 80000
                    int P3N = -1 * rn.nextInt(4000) + 4000;   //  40000 - 80000
                    Double W3 = ((double) rn.nextInt(50));            // 0 - 50


                    prodFlexibility.put(P1P, W1);
                    consFlexibility.put(P1N, W1);

                    prodFlexibility.put(P2P, W2);
                    consFlexibility.put(P2N, W2);

                    prodFlexibility.put(P3P, W2);
                    consFlexibility.put(P3N, W2);


                    // build Client report
                    ClientReport report = new ClientReport(j, production, consumption, predictedCons, predictedProd, consFlexibility, prodFlexibility);
                    reports.get(i).add(report);
                    // End of copy
                }
            }
            //After having generated client reports sum them per clsuter
            aggregatedReports = new LinkedList<>();
            for (int i = 0; i < NumberOfClusters; i++) {
                aggregatedReports.add(SumReports(i,reports.get(i)));
            }
            rootNode.initialize(aggregatedReports);
            rootNode.Balance();

            for (int i = 0; i < NumberOfClusters; i++) {
                //aggregatedReports.add(SumReports(i,reports.get(i)));
                level1.get(i).initialize(reports.get(i));
                level1.get(i).Balance(rootNode.getPricePoint());
            }
            System.out.println("One day done");
        }
    }
    static public HashMap<Integer, Double> sumOfferdFlex(HashMap<Integer, Double> List1, HashMap<Integer, Double> List2){
        HashMap<Integer, Double> L1 = new HashMap<>(List1);

        for (HashMap.Entry<Integer, Double> Entry: List2.entrySet()) {
            if(L1.containsKey(Entry.getKey())){
                L1.put(Entry.getKey(), L1.get(Entry.getKey()) + Entry.getValue());
            }else{
                L1.put(Entry.getKey(), Entry.getValue());
            }
        }
        return L1;
    }

    static public ClientReport SumReports(int clusterId, LinkedList<ClientReport> reportList){
        Double production = 0.0;
        Double consumption = 0.0;
        HashMap<String, Double> predictedCons = new HashMap<>();
        HashMap<String, Double> predictedProd = new HashMap<>();
        HashMap<Integer, Double> consFlexibility = new HashMap<>();
        HashMap<Integer, Double> prodFlexibility = new HashMap<>();
        Double preProduction = 0.0;
        Double preConsumption = 0.0;

        for (ClientReport report:reportList) {
            preConsumption += report.getPredictedCons().get("t1");
            preProduction += report.getPredictedProd().get("t1");

            consFlexibility = sumOfferdFlex(new HashMap<>(consFlexibility), report.getConsFlexibility());
            prodFlexibility = sumOfferdFlex(new HashMap<>(prodFlexibility), report.getProdFlexibility());

            consumption += report.getConsumption();
            production += report.getProduction();
        }

        predictedCons.put("t1", preConsumption);
        predictedProd.put("t1", preProduction);

        return new ClientReport(clusterId, production, consumption, predictedCons, predictedProd, consFlexibility, prodFlexibility);
    }
}

