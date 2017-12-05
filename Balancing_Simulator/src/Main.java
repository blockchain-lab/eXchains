
import org.graphstream.graph.Graph;
import org.graphstream.graph.implementations.SingleGraph;
import org.graphstream.ui.view.Viewer;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.ui.RefineryUtilities;

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

    public static final int HousesPerCluster = 7;
    public static final int NumberOfCusters = 3;

    public static final int TimeSlotMin = 5;

    public static final int simSpeed = 3;// time between each client send in seconds -1.5

    public static final CyclicBarrier gate = new CyclicBarrier(((HousesPerCluster)*NumberOfCusters));

    public final static Graph graph = new SingleGraph("Balancing Simulator");



    public static void main(String[] args) {

        //testGraph();

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

    static void testGraph(){
        XYLineChart_AWT chart = new XYLineChart_AWT("Browser Usage Statistics",
                "Which Browser are you using?");
        chart.pack( );
        RefineryUtilities.centerFrameOnScreen( chart );
        chart.setVisible( true );

        chart.addData(1,2);
        delay(1000);

        chart.addData(2,4);
        delay(1000);

        chart.addData(3,6);

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

    static private void delay(int millis){
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
