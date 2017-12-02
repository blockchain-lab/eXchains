import com.opencsv.CSVReader;
import org.graphstream.graph.Edge;
import org.graphstream.graph.Graph;
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

    public Household_Client(int id, int ParentID, Blockchain parent){
        ID = id;
        this.blockchain = parent;
        parent.connect();

        synchronized (Main.graph) {
            Node n = Main.graph.addNode("H" + ID);
            n.addAttribute("ui.label", "H" + ID);
            n.addAttribute("ui.class", "H");

            int totaalHouseholds = Main.HousesPerCluster * Main.NumberOfCusters;

            double x = (id*90)/totaalHouseholds + (10/(Main.NumberOfCusters-1))*(id/Main.HousesPerCluster);

            n.setAttribute("xy", x , 20);

            Node BlockchainNode = Main.graph.getNode("B" + ParentID);
            e = Main.graph.addEdge("HE" + ID, n, BlockchainNode);
            e.addAttribute("ui.class", "off");
        }
    }

    public void run() {
        System.out.println("Household " + ID + " started");

        CSVReader csvReader;

        try {
            Reader reader = Files.newBufferedReader(Paths.get("SimulationData.csv"));
            csvReader = new CSVReader(reader, ';');

            Random rn = new Random();
            int rand = rn.nextInt(50) + 1;

            for (int i = 0; i < rand; i++) {
                csvReader.readNext();
            }

            while(true){

                try {
                    Main.gate.await();
                } catch (InterruptedException e1) {
                    e1.printStackTrace();
                } catch (BrokenBarrierException e1) {
                    e1.printStackTrace();
                }

                // Reading Records One by One in a String array
                String[] nextRecord;

                if((nextRecord = csvReader.readNext()) != null){
                    Double production = Double.parseDouble(nextRecord[4].replace(',', '.'));
                    Double consumption= Double.parseDouble(nextRecord[3].replace(',', '.'));
                    HashMap<String, Double> predictedCons = null;
                    HashMap<String, Double> predictedProd = null;
                    HashMap<Double, Double> offeredFlexibility = null;

                    Transaction transaction = new Transaction(Transaction.MessageType.CLIENTREPORT, ID, production, consumption, predictedCons, predictedProd, offeredFlexibility);
                    blockchain.sendTransaction(transaction);

                    synchronized (Main.graph){
                        e.addAttribute("ui.class", "active");
                    }
                    delay(800);
                    synchronized (Main.graph){
                        e.addAttribute("ui.class", "off");
                    }
                }
                delay(5000);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void delay(int millis){
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

}
