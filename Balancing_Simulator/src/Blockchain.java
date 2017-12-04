import org.graphstream.graph.Edge;
import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;

import java.util.HashMap;
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

    LaurenSophieAPXAlgorithm algorithm;

    public Blockchain(int id, int level, int ParentID, Blockchain parent){
        ID = id;
        Parent = parent;
        Level = level;
        algorithm = new LaurenSophieAPXAlgorithm(id);

        synchronized (Main.graph) {
            n = Main.graph.addNode("B" + ID);
            if(level == 0){

                parent.connect();

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
        HashMap<Integer, Double> offeredFlexibility = new HashMap<>();

        // Main loop
        while(true){

            // sync up all threads
            //sync();

            offeredFlexibility = new HashMap<>();

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
                    //offeredFlexibility = algorithm.sumOfferdFlex(offeredFlexibility, transaction.getPredictedCons());
                }
                predictedCons.put("t1", preConsumption);
                predictedProd.put("t1", preProduction);



                // build transaction out
                ClientReport transactionOut = new ClientReport(ID, production, consumption, predictedCons, predictedProd, offeredFlexibility, offeredFlexibility);

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
                Parent.sendTransaction(transactionOut);

                delay(500);
                synchronized (Main.graph) {
                    e.addAttribute("ui.class", "off");
                }






            }else if(Level == 1){
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
                    //offeredFlexibility = algorithm.sumOfferdFlex(offeredFlexibility, transaction.getOfferedFlexibility());
                }
                predictedCons.put("t1", preConsumption);
                predictedProd.put("t1", preProduction);

                System.out.println("offeredFlexibility size: " + offeredFlexibility.size());
                System.out.println("offeredFlexibility: " + offeredFlexibility);

                // build transaction out
                ClientReport transactionOut = new ClientReport(ID, production, consumption, predictedCons, predictedProd, offeredFlexibility, offeredFlexibility);

                // set production and consumption for next report
                consumption = preConsumption;
                production = preProduction;

                synchronized (Main.graph) {
                    n.addAttribute("ui.label",  ((int)(consumption/5)) + " / " + ((int)(production/5)) + " W");
                }
            }
        }
    }

    public void sendTransaction(ClientReport transaction){
        queue.add(transaction);
    }

    public void connect(){
        numberOfChilds++;
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

    private void delay(int millis){
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

}
