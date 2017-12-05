import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.ui.ApplicationFrame;

import java.awt.*;
import java.util.LinkedList;
import java.util.List;

public class XYLineChart_AWT extends ApplicationFrame {

    private LinkedList<Double> unBalancedData = new LinkedList<>();
    private LinkedList<Double> BalancedData = new LinkedList<>();

    String Title;
    String chartitle;



    public XYLineChart_AWT( String applicationTitle, String chartTitle ) {
        super(applicationTitle);

        Title = applicationTitle;
        chartitle = chartTitle;

        JFreeChart xylineChart = ChartFactory.createXYLineChart(
                chartTitle ,
                "Category" ,
                "Score" ,
                createDataset() ,
                PlotOrientation.VERTICAL ,
                true , true , false);

        ChartPanel chartPanel = new ChartPanel( xylineChart );


        chartPanel.setPreferredSize( new java.awt.Dimension( 560 , 367 ) );
        final XYPlot plot = xylineChart.getXYPlot();

        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer( );
        renderer.setSeriesPaint( 0 , Color.RED );
        renderer.setSeriesPaint( 1 , Color.GREEN );
        renderer.setSeriesStroke( 0 , new BasicStroke( 4.0f ) );
        renderer.setSeriesStroke( 1 , new BasicStroke( 3.0f ) );
        plot.setRenderer( renderer );
        setContentPane( chartPanel );
    }

    public void redraw(){

        //chartPanel.repaint();

        JFreeChart xylineChart = ChartFactory.createXYLineChart(
                chartitle ,
                "Category" ,
                "Score" ,
                createDataset() ,
                PlotOrientation.VERTICAL ,
                true , true , false);

        ChartPanel chartPanel = new ChartPanel( xylineChart );

        setContentPane( chartPanel );




    }

    private XYDataset createDataset( ) {
        final XYSeries BalancedSerie = new XYSeries( "Balanced" );
        final XYSeries UnbalancedSerie = new XYSeries( "Unbalanced" );

        int i = 0;
        for (double point: BalancedData) {
            BalancedSerie.add(i++,point);
        }

        i = 0;
        for (double point: unBalancedData) {
            UnbalancedSerie.add(i++,point);
        }

        final XYSeriesCollection dataset = new XYSeriesCollection( );
        dataset.addSeries( BalancedSerie );
        dataset.addSeries( UnbalancedSerie );
        return dataset;
    }

    public void addData(double Balanced, double Unbalanced){
        BalancedData.add(Balanced);
        unBalancedData.add(Unbalanced);
        redraw();
    }

}
