import com.company.SortedUberArray;

import java.util.HashMap;
import java.util.LinkedList;

public class LaurenSophieAPXAlgorithm {
    // Version 0.1
    // This version only regulates once per upcoming time slot. For now it will not do any balancing in the current timeslot

    private Integer myID;
    private LinkedList<ClientReport> CR;
    private HashMap<Integer, RegulationReport> RR;

    public LaurenSophieAPXAlgorithm(Integer uuid, LinkedList<ClientReport> CR) {
        this.myID = uuid;
        this.CR = new LinkedList<ClientReport>(CR);
    }

    private Double preImbalance(){
        Double result = 0.0;
        for (ClientReport temp:CR) {
            result += temp.getPredictedCons().get("t1") - temp.getPredictedProd().get("t1");
        }
        return result;
    }

    private Double PricePoint(Double imbalance){
        //todo: crate a function that generates a regulation pricepoint based on the imbalance

        return 1234.3;
    }

    public void Balance(){
        Double preImbalance = preImbalance();
        Double postImbalance = preImbalance;
        Double pricePoint = PricePoint(preImbalance);

        SortedUberArray consumptionArray = new SortedUberArray();
        SortedUberArray productionnArray = new SortedUberArray();

        //Select only the flexibility that meets the criteria (up or down, and below the max)
        if(preImbalance<0){ //Shortage detected
            for (ClientReport currentReport:CR) {
                for (HashMap.Entry<Integer, Double> currentFlexibility: currentReport.getConsFlexibility().entrySet()){
                    if(currentFlexibility.getKey()<0 && currentFlexibility.getKey() >= -pricePoint){
                        consumptionArray.addCapacity(currentReport.getUuid(),-currentFlexibility.getKey(),currentFlexibility.getValue());
                    }
                }
                for (HashMap.Entry<Integer, Double> currentFlexibility: currentReport.getProdFlexibility().entrySet()){
                    if(currentFlexibility.getKey()>0 && currentFlexibility.getKey() <= pricePoint){
                        productionnArray.addCapacity(currentReport.getUuid(),currentFlexibility.getKey(),currentFlexibility.getValue());
                    }
                }
            }
        }else{
            for (ClientReport currentReport:CR) {
                for (HashMap.Entry<Integer, Double> currentFlexibility: currentReport.getConsFlexibility().entrySet()){
                    if(currentFlexibility.getKey()>0 && currentFlexibility.getKey() >= pricePoint){
                        consumptionArray.addCapacity(currentReport.getUuid(),currentFlexibility.getKey(),currentFlexibility.getValue());
                    }
                }
                for (HashMap.Entry<Integer, Double> currentFlexibility: currentReport.getProdFlexibility().entrySet()){
                    if(currentFlexibility.getKey()<0 && currentFlexibility.getKey() >=-pricePoint){
                        productionnArray.addCapacity(currentReport.getUuid(),-currentFlexibility.getKey(),currentFlexibility.getValue());
                    }
                }
            }
        }
        consumptionArray.Sort();
        productionnArray.Sort();
    }

}
