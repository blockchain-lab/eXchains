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

        //Probably split up to new function from here
        Double currentLowestPrice = null;
        Double currentCapacity = 0.0;
        Double capacityPerClient;

        Double smallestCapacity = null;


        if(preImbalance<0){ //Shortage detected
            for (ClientReport currentReport:CR) { //For every client report, go find the smallest
                for (HashMap.Entry<Double, Double> currentFlexibility: currentReport.getOfferedFlexibility().entrySet()){
                    //check all the negative entries (shortage means we want decrease consumption & decrease production)
                    //And not more than we're willing to spent per kwh regulated
                    if(currentFlexibility.getKey()<0 && currentFlexibility.getKey() <=pricePoint ){
                        if((currentLowestPrice==null) || (currentFlexibility.getKey()<currentLowestPrice)) {
                            currentLowestPrice = currentFlexibility.getKey();
                        }
                    }
                }
            }
            //Find all the clients that can offer flexibility for the lowest price and their total capacity.
            int clientsThisRound=0;
            for (ClientReport currentReport:CR) { //For every client report, go find the smallest
                if(currentReport.getOfferedFlexibility().containsKey(currentLowestPrice)){
                    clientsThisRound++;
                    currentCapacity += currentReport.getOfferedFlexibility().get(currentLowestPrice);
                    if (smallestCapacity==null || currentReport.getOfferedFlexibility().get(currentLowestPrice)< smallestCapacity){
                        smallestCapacity =  currentReport.getOfferedFlexibility().get(currentLowestPrice);
                    }
                }
            }
            //Only utilize the capacity we actually need
            if(currentCapacity>postImbalance){
                currentCapacity=postImbalance;
            }
            //Now spreadout the energy equally if multiple clients offer the same price
            capacityPerClient = currentCapacity/clientsThisRound;
            //But clients can only offer so much energy per time
            if(capacityPerClient>smallestCapacity){
                capacityPerClient=smallestCapacity;
            }

            for (ClientReport currentReport:CR) { //For every client report, go find the smallest
                if(currentReport.getOfferedFlexibility().containsKey(currentLowestPrice)){
                    if(currentReport.getOfferedFlexibility().get(currentLowestPrice)<= capacityPerClient){
                        //There is no energy remainig at this price, so it can be removed.
                        currentReport.getOfferedFlexibility().remove(currentLowestPrice);
                    } else{
                        //There some energy left over at this flexibility, update the entry for the remaining value
                        currentReport.getOfferedFlexibility().put(currentLowestPrice,   currentReport.getOfferedFlexibility().get(currentLowestPrice) - capacityPerClient);
                    }
                }
            }





        }
    }

}
