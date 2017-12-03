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
        Integer currentCheapestCons = Integer.MAX_VALUE;;
        Integer currentCheapestProd = Integer.MAX_VALUE;;
        Double currentCapacity = 0.0;
        Double capacityPerClient;

        Double smallestCapacity = null;


        if(preImbalance<0){ //Shortage detected
            //Determine the cheapest solution for either
            for (ClientReport currentReport:CR) { //For every client report, go find the smallest
                for (HashMap.Entry<Integer, Double> currentFlexibility: currentReport.getConsFlexibility().entrySet()){
                    //shortage means we want decrease consumption, only count negative prices
                    //And not more than we're willing to spent per kwh regulated
                    if(currentFlexibility.getKey()<0 && currentFlexibility.getKey() >= -pricePoint ){
                        if((-currentFlexibility.getKey()< currentCheapestCons)) {
                            currentCheapestCons = -currentFlexibility.getKey();
                        }
                    }
                }
                for (HashMap.Entry<Integer, Double> currentFlexibility: currentReport.getProdFlexibility().entrySet()){
                    //Shortage means increasing prod, only count keys for positive values
                    //And not more than we're willing to spent per kwh regulated
                    if(currentFlexibility.getKey()>0 && currentFlexibility.getKey() <= pricePoint ){
                        if((currentFlexibility.getKey()< currentCheapestProd)) {
                            currentCheapestProd = currentFlexibility.getKey();
                        }
                    }
                }
            }

            smallestCapacity = Double.MAX_VALUE;

            //If producing is cheaper (or the same price) first produce
            if(currentCheapestProd <= currentCheapestCons){
                int clientsThisRound=0;
                //Get total capacity for cheapest option
                for (ClientReport currentReport:CR) {
                    if(currentReport.getProdFlexibility().containsKey(currentCheapestProd)){
                        clientsThisRound++;
                        currentCapacity += currentReport.getProdFlexibility().get(currentCheapestProd);
                        if (currentReport.getProdFlexibility().get(currentCheapestProd)< smallestCapacity){
                            smallestCapacity =  currentReport.getProdFlexibility().get(currentCheapestProd);
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

                //Now we know how much the biggest order that everybody can execute. Time to execute it
                for (ClientReport currentReport:CR) {
                    if(currentReport.getProdFlexibility().containsKey(currentCheapestProd)){
                        if(currentReport.getProdFlexibility().get(currentCheapestProd)<= capacityPerClient){
                            //There is no energy remainig at this price, so it can be removed.
                            currentReport.getProdFlexibility().remove(currentCheapestProd);
                        } else{
                            //There some energy left over at this flexibility, update the entry for the remaining value
                            currentReport.getProdFlexibility().put(currentCheapestProd,   currentReport.getProdFlexibility().get(currentCheapestProd) - capacityPerClient);
                        }
                        if(RR.containsKey(currentReport.getUuid())){
                            RegulationReport tempRR;
                            tempRR = RR.get(currentReport.getUuid());
                            if (capacityPerClient)
                                RR.put(tempRR.getUuid(), (tempRR.getProdRegulationAmount() + capacityPerClient));
                        }
                    }
                }
            }





















        }
    }

}
