
import org.graphstream.graph.Graph;
import org.graphstream.graph.implementations.SingleGraph;
import org.graphstream.ui.view.Viewer;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.CyclicBarrier;

public class Main {
    //Lauren's variables
    static LaurenSophieAPXAlgorithm myAlgorithms;
    static List<ClientReport> CR;

    //Sophie's variables
    private static List<Household_Client> Households = new LinkedList<>();
    private static List<Blockchain> blockchains = new LinkedList<>();

    public static final int HousesPerCluster = 7;
    public static final int NumberOfCusters = 3;

    public static final int TimeSlotMin = 5;

    public static final int simSpeed = 3;// time between each client send in seconds -1.5

    public static final CyclicBarrier gate = new CyclicBarrier(((HousesPerCluster)*NumberOfCusters));

    public final static Graph graph = new SingleGraph("Balancing Simulator");


    public static void main(String[] args) {
        CR = new LinkedList<>();
        HashMap<Integer, Double> c1ConsFlex = new HashMap<>();
        HashMap<Integer, Double> c1ProdFlex = new HashMap<>();
        HashMap<Integer, Double> c2ConsFlex = new HashMap<>();
        HashMap<Integer, Double> c2ProdFlex = new HashMap<>();

        c1ConsFlex.put(-2,12.0);

        c2ProdFlex.put(2,8.0);


        HashMap<String, Double> c1Cons = new HashMap<>();
        HashMap<String, Double> c1Prod = new HashMap<>();

        HashMap<String, Double> c2Cons = new HashMap<>();
        HashMap<String, Double> c2Prod = new HashMap<>();


        myAlgorithms = new LaurenSophieAPXAlgorithm(12345);
        c1Cons.put("t1",12.0);
        c1Prod.put("t1", 0.0);

        c2Cons.put("t1",0.0);
        c2Prod.put("t1", 0.0);



        CR.add(new ClientReport(0,12.0,0.0, c1Cons,c1Prod,c1ConsFlex,c1ProdFlex));
        CR.add(new ClientReport(1,0.0,0.0, c2Cons,c2Prod,c2ConsFlex,c2ProdFlex));
        myAlgorithms.initialize(new LinkedList<>(CR));
        HashMap<Integer, RegulationReport> results = myAlgorithms.Balance();
        System.out.println(results.get(0).getConsRegulationAmount());
        System.out.println(results.get(1).getProdRegulationAmount());

        //System.out.println(results.get(2).getConsRegulationAmount());
        //results.entrySet()



//        System.setProperty("org.graphstream.ui.renderer", "org.graphstream.ui.j2dviewer.J2DGraphRenderer");
//        graph.addAttribute("ui.quality");
//        graph.addAttribute("ui.antialias");
//        graph.addAttribute("ui.stylesheet", readFile("src\\ui.stylesheet", Charset.defaultCharset()));
//        Viewer view =  graph.display();
//        view.disableAutoLayout();
//
//
//        Blockchain blockchainL1 = new Blockchain(100, 1,-1, null);
//        blockchainL1.start();
//        blockchains.add(blockchainL1);
//
//        for (int i = 0; i < NumberOfCusters; i++) {
//            Blockchain blockchainL0 = new Blockchain(i,0, 100, blockchainL1);
//            blockchainL0.start();
//            blockchains.add(blockchainL0);
//
//            for (int j = i*HousesPerCluster; j < (i+1)*HousesPerCluster; j++) {
//                Household_Client household = new Household_Client(j, i, blockchainL0);
//                household.start();
//                Households.add(household);
//            }
//        }

    }

    static String readFile(String path, Charset encoding) {
        byte[] encoded = new byte[0];
        try {
            encoded = Files.readAllBytes(Paths.get(path));
        } catch (IOException e) {
            e.printStackTrace();
            return "";
        }
        return new String(encoded, encoding);
    }
}
