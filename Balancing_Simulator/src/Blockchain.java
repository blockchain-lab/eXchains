import org.graphstream.graph.Edge;
import org.graphstream.graph.Node;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.LinkedBlockingQueue;

public class Blockchain extends Thread {

    BlockingQueue<ClientReport> queue = new LinkedBlockingQueue<>();
    int ID;
    int numberOfChilds = 0;
    Edge e = null;
    Node n = null;
    Blockchain Parent;
    int Level = 0;
    HashMap<Integer, Object> clients = new HashMap<>();

    LinkedList<ClientReport> ClientReports = new LinkedList<>();

    LaurenSophieAPXAlgorithm algorithm;

    public Blockchain(int id, int level, int ParentID, Blockchain parent){
        ID = id;
        Parent = parent;
        Level = level;
        algorithm = new LaurenSophieAPXAlgorithm(id);

        synchronized (Main.graph) {
            n = Main.graph.addNode("B" + ID);
            if(level == 0){

                parent.connect(id, this);

                double x = (1000/Main.NumberOfCusters)*(ID)+(850/Main.NumberOfCusters)/2;

                n.setAttribute("xy",  x, 200);
                n.addAttribute("ui.label", "0/0 Kwh");
                n.addAttribute("ui.class", "B");

                Node BlockchainNode = Main.graph.getNode("B" + ParentID);
                e = Main.graph.addEdge("BE" + ID, n, BlockchainNode);

            }else if(level == 1){
                n.setAttribute("xy", 475, 350);
                n.addAttribute("ui.label", "0/0 Kwh");
                n.addAttribute("ui.class", "B");
            }
        }
    }

    public void run() {
        System.out.println("Blockchain " + ID + " started");

        ClientReport transaction;

        // each loop we send:
        Double production = 0.0;
        Double consumption = 0.0;
        HashMap<String, Double> predictedCons = new HashMap<>();
        HashMap<String, Double> predictedProd = new HashMap<>();
        HashMap<Integer, Double> consFlexibility = new HashMap<>();
        HashMap<Integer, Double> prodFlexibility = new HashMap<>();

        // Main loop
        while(true){

            // sync up all threads
            //sync();

            consFlexibility = new HashMap<>();
            prodFlexibility = new HashMap<>();

            if(Level == 0){

                // wait for all transactions
                while(queue.size() != numberOfChilds){
                    delay(100);
                }

                // "predict" data from coming time block
                Double preProduction = 0.0;
                Double preConsumption = 0.0;
                while((transaction = queue.poll()) != null) {
                    preConsumption += transaction.getPredictedCons().get("t1");
                    preProduction += transaction.getPredictedProd().get("t1");

                    consFlexibility = sumOfferdFlex(consFlexibility, transaction.getConsFlexibility());
                    prodFlexibility = sumOfferdFlex(prodFlexibility, transaction.getProdFlexibility());

                    consumption += transaction.getConsumption();
                    production += transaction.getProduction();

                }
                predictedCons.put("t1", preConsumption);
                predictedProd.put("t1", preProduction);

                System.out.println("Level 0: preProduction" + preProduction);

                // build transaction out
                ClientReport transactionOut = new ClientReport(ID, production, consumption, predictedCons, predictedProd, consFlexibility, prodFlexibility);

                // set production and consumption for next report
                consumption = preConsumption;
                production = preProduction;


                synchronized (Main.graph) {
                    e.addAttribute("ui.class", "active");
                    e.addAttribute("ui.label",  ((int)(consumption/5)) + "W / " + ((int)(production/5)) + "W");
                    n.addAttribute("ui.label",  ((int)(consumption/5)) + " / " + ((int)(production/5)) + " W");
                }
                delay(1000);

                // send transaction to
                Parent.sendClientReport(transactionOut);

                delay(500);
                synchronized (Main.graph) {
                    e.addAttribute("ui.class", "off");
                }



            }else if(Level == 1){
                // wait for all transactions
                while(queue.size() != numberOfChilds){
                    delay(100);
                }

                LinkedList<ClientReport> CR = new LinkedList<>();

                // "predict" data from coming time block
                Double preProduction = 0.0;
                Double preConsumption = 0.0;

                consumption = 0.0;
                production = 0.0;

                while((transaction = queue.poll()) != null) {
                    preConsumption += transaction.getPredictedCons().get("t1");
                    preProduction += transaction.getPredictedProd().get("t1");

                    consFlexibility = sumOfferdFlex(consFlexibility, transaction.getConsFlexibility());
                    prodFlexibility = sumOfferdFlex(prodFlexibility, transaction.getProdFlexibility());

                    consumption += transaction.getConsumption();
                    production += transaction.getProduction();

                    CR.add(transaction);
                }


                predictedCons.put("t1", preConsumption);
                predictedProd.put("t1", preProduction);


                System.out.println("predicted consumtion: " + preConsumption + " predicted production: " + preProduction);
                System.out.println("adjusted consumtion: " + consumption + " adjusted production: " + production);


                algorithm.initialize(CR);
                HashMap<Integer, RegulationReport> regulationReports = algorithm.Balance();

                for (HashMap.Entry<Integer, RegulationReport> entry: regulationReports.entrySet()) {
                    ((Blockchain) clients.get(entry.getKey())).sendRegulationReport(entry.getValue());
                }

                // build transaction out
                ClientReport transactionOut = new ClientReport(ID, production, consumption, predictedCons, predictedProd, consFlexibility, prodFlexibility);

                // set production and consumption for next report
                consumption = preConsumption;
                production = preProduction;

                synchronized (Main.graph) {
                    n.addAttribute("ui.label",  ((int)(consumption/5)) + " / " + ((int)(production/5)) + " W");
                }
            }
        }
    }

    public void sendClientReport(ClientReport transaction){
        queue.add(transaction);
        ClientReports.add(transaction);
    }

    public void sendRegulationReport(RegulationReport report){
        //System.out.println("Blockchain " + ID + "recived regulationReport");

        algorithm.initialize(ClientReports);

        HashMap<Integer, RegulationReport> regulationReports = algorithm.Balance(report.getPricePoint());

        for (HashMap.Entry<Integer, RegulationReport> entry: regulationReports.entrySet()) {
            ((Household_Client) clients.get(entry.getKey())).sendRegulationReport(entry.getValue());
        }

        //TODO verdeel energie onder clients
    }

    public void connect(int id, Object client){
        numberOfChilds++;
        clients.put(id, client);
    }

    private void sync(){
        try {
            Main.gate.await();
        } catch (InterruptedException e1) {
            e1.printStackTrace();
        } catch (BrokenBarrierException e1) {
            e1.printStackTrace();
        }
    }

    public HashMap<Integer, Double> sumOfferdFlex(HashMap<Integer, Double> List1, HashMap<Integer, Double> List2){
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

    private void delay(int millis){
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }



}
