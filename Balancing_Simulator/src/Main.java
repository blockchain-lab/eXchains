
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

    public static final CyclicBarrier gate = new CyclicBarrier(56);

    public final static Graph graph = new SingleGraph("Balancing Simulator");

    public static void main(String[] args) {

        System.setProperty("org.graphstream.ui.renderer", "org.graphstream.ui.j2dviewer.J2DGraphRenderer");
        graph.addAttribute("ui.quality");
        graph.addAttribute("ui.antialias");
        graph.addAttribute("ui.stylesheet", readFile("src\\ui.stylesheet", Charset.defaultCharset()));
        Viewer view =  graph.display();
        view.disableAutoLayout();


        Blockchain blockchainL1 = new Blockchain(100, 0, null);
        blockchainL1.start();
        blockchains.add(blockchainL1);

        for (int i = 0; i < 5; i++) {
            Blockchain blockchainL0 = new Blockchain(i, 100, blockchainL1);
            blockchainL0.start();
            blockchains.add(blockchainL0);

            for (int j = i*10; j < i*10+10; j++) {
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
