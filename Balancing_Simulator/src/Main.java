
import org.graphstream.graph.Graph;
import org.graphstream.graph.implementations.SingleGraph;
import org.graphstream.ui.view.Viewer;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.CyclicBarrier;

public class Main {

    private static List<Household_Client> Households = new LinkedList<>();
    private static List<Blockchain> blockchains = new LinkedList<>();

    public static final int HousesPerCluster = 8;
    public static final int NumberOfCusters= 5;

    public static final CyclicBarrier gate = new CyclicBarrier(((HousesPerCluster+1)*NumberOfCusters)+1);

    public final static Graph graph = new SingleGraph("Balancing Simulator");



    public static void main(String[] args) {

        System.setProperty("org.graphstream.ui.renderer", "org.graphstream.ui.j2dviewer.J2DGraphRenderer");
        graph.addAttribute("ui.quality");
        graph.addAttribute("ui.antialias");
        graph.addAttribute("ui.stylesheet", readFile("src\\ui.stylesheet", Charset.defaultCharset()));
        Viewer view =  graph.display();
        view.disableAutoLayout();


        Blockchain blockchainL1 = new Blockchain(100, 1,-1, null);
        blockchainL1.start();
        blockchains.add(blockchainL1);

        for (int i = 0; i < NumberOfCusters; i++) {
            Blockchain blockchainL0 = new Blockchain(i,0, 100, blockchainL1);
            blockchainL0.start();
            blockchains.add(blockchainL0);

            for (int j = i*HousesPerCluster; j < (i+1)*HousesPerCluster; j++) {
                Household_Client household = new Household_Client(j, i, blockchainL0);
                household.start();
                Households.add(household);
            }
        }

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
