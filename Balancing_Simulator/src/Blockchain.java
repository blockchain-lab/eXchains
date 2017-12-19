import org.graphstream.graph.Edge;
import org.graphstream.graph.Node;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.LinkedBlockingQueue;

public class Blockchain extends Thread {

    //BlockingQueue<ClientReport> queue = new LinkedBlockingQueue<>();
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


    }

    public void run() {
        System.out.println("Blockchain " + ID + " started");
    }

//    public void sendClientReport(ClientReport transaction){
//        synchronized (ClientReports){
//            ClientReports.add(transaction);
//        }
//
//        //if all messages from clients are recieved
//        if(ClientReports.size() == numberOfChilds){
//
//            // each loop we send:
//            Double production = 0.0;
//            Double consumption = 0.0;
//            HashMap<String, Double> predictedCons = new HashMap<>();
//            HashMap<String, Double> predictedProd = new HashMap<>();
//            HashMap<Integer, Double> consFlexibility = new HashMap<>();
//            HashMap<Integer, Double> prodFlexibility = new HashMap<>();
//            Double preProduction = 0.0;
//            Double preConsumption = 0.0;
//
//
//            for (ClientReport report:ClientReports) {
//                preConsumption += report.getPredictedCons().get("t1");
//                preProduction += report.getPredictedProd().get("t1");
//
//                consFlexibility = sumOfferdFlex(consFlexibility, report.getConsFlexibility());
//                prodFlexibility = sumOfferdFlex(prodFlexibility, report.getProdFlexibility());
//
//                consumption += report.getConsumption();
//                production += report.getProduction();
//            }
//
//            predictedCons.put("t1", preConsumption);
//            predictedProd.put("t1", preProduction);
//
//            ClientReport transactionOut = new ClientReport(ID, production, consumption, predictedCons, predictedProd, consFlexibility, prodFlexibility);
//
//
//            // if first level above clients
//            if(Level == 0){
//
//
//            // if second and final level above clients
//            }else if (Level == 1){
//
//                algorithm.initialize(ClientReports);
//                ClientReports = new LinkedList<>();
//
//                HashMap<Integer, RegulationReport> regulationReports = algorithm.Balance();
//
//                //send Regulation reports down
//                for (HashMap.Entry<Integer, RegulationReport> entry: regulationReports.entrySet()) {
//                    ((Blockchain) clients.get(entry.getKey())).sendRegulationReport(entry.getValue());
//                }
//
//                // update view
//
//            }
//
//        }
//
//    }

    public void sendRegulationReport(RegulationReport report){

        algorithm.initialize(ClientReports);
        ClientReports = new LinkedList<>();

        HashMap<Integer, RegulationReport> regulationReports = new HashMap<>(algorithm.Balance(report.getPricePoint()));

        //System.out.println("Blockchain " + ID + " clients " + clients + " regulationReports " + regulationReports);

        for (HashMap.Entry<Integer, RegulationReport> entry: regulationReports.entrySet()) {
            ((Household_Client) clients.get(entry.getKey())).sendRegulationReport(entry.getValue());
        }

        //TODO verdeel energie onder clients

    }

    public void connect(int id, Object client){
        numberOfChilds++;
        clients.put(id, client);
    }

//    private void sync(){
//        try {
//            Main.gate.await();
//        } catch (InterruptedException e1) {
//            e1.printStackTrace();
//        } catch (BrokenBarrierException e1) {
//            e1.printStackTrace();
//        }
//    }

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
