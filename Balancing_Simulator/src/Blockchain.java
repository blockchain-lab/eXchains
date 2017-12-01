import org.graphstream.graph.Edge;
import org.graphstream.graph.Graph;
import org.graphstream.graph.Node;

import java.util.HashMap;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.LinkedBlockingQueue;

public class Blockchain extends Thread {

    BlockingQueue<Transaction> queue = new LinkedBlockingQueue<Transaction>();
    int ID;
    int numberOfChilds = 0;
    Edge e = null;
    Blockchain Parent;

    public Blockchain(int id, int ParentID, Blockchain parent){
        ID = id;
        Parent = parent;
        synchronized (Main.graph) {
            Node n = Main.graph.addNode("B" + ID);
            if(parent != null){
                n.setAttribute("xy", id*20+9.5, 30);
                n.addAttribute("ui.label", "B" + ID);
            }else{
                n.setAttribute("xy", 50, 40);
                n.addAttribute("ui.label", "B" + ID);
            }

            if(parent != null){
                Node BlockchainNode = Main.graph.getNode("B" + ParentID);
                e = Main.graph.addEdge("BE" + ID, n, BlockchainNode);
            }
        }
    }

    public void run() {
        System.out.println("Blockchain " + ID + " started");

        Transaction transaction;

        while(true){
            try {
                Main.gate.await();
            } catch (InterruptedException e1) {
                e1.printStackTrace();
            } catch (BrokenBarrierException e1) {
                e1.printStackTrace();
            }

            int transCounter = 0;
            Boolean done = false;
            if (e != null) {
                while (!done) {
                    Double production = 0.0;
                    Double consumption = 0.0;

                    while ((transaction = queue.poll()) != null) {
                        transCounter++;
                        //TODO: handle transaction

                        production += transaction.getProduction();
                        consumption += transaction.getConsumption();

                        if (transCounter == numberOfChilds) {
                            delay(1000);

                            //TODO: send transaction

                            HashMap<String, Double> predictedCons = null;
                            HashMap<String, Double> predictedProd = null;
                            HashMap<Double, Double> offeredFlexibility = null;

                            Transaction transactionOut = new Transaction(Transaction.MessageType.CLIENTREPORT, ID, production, consumption, predictedCons, predictedProd, offeredFlexibility);

                            System.out.println("Blockchain " + transactionOut.getUuid() + " Summary Consumption: " + transactionOut.getConsumption() + " Production: " + transactionOut.getProduction());

                            Parent.sendTransaction(transactionOut);

                            synchronized (Main.graph) {
                                e.addAttribute("ui.class", "active");
                            }
                            delay(800);
                            synchronized (Main.graph) {
                                e.addAttribute("ui.class", " ");
                            }
                            done = true;
                        }
                    }
                }
            }
            delay(100);
        }
    }

    public void sendTransaction(Transaction transaction){
        queue.add(transaction);
    }

    public void connect(){
        numberOfChilds++;
    }

    private void delay(int millis){
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

}
