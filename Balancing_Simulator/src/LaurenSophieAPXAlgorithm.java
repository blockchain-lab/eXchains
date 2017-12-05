import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

public class LaurenSophieAPXAlgorithm {
    // Version 0.1
    // This version only regulates once per upcoming time slot. For now it will not do any balancing in the current timeslot

    private Integer myID;
    private LinkedList<ClientReport> CR;
    private HashMap<Integer, RegulationReport> RR;
    private Integer pricePoint; //In Centicents
    private SortedUberArray consumptionArray;
    private SortedUberArray productionnArray;

    public LaurenSophieAPXAlgorithm(Integer uuid) {
        this.myID = uuid;
    }

    public void initialize(LinkedList<ClientReport> CR){
        this.CR = new LinkedList<ClientReport>(CR);
        this.RR = new HashMap<Integer, RegulationReport>();
        this.consumptionArray = new SortedUberArray();
        this.productionnArray = new SortedUberArray();
    }

    private Double preImbalance(){
        Double result = 0.0;
        for (ClientReport temp:CR) {
            result += + temp.getPredictedProd().get("t1") - temp.getPredictedCons().get("t1");
        }
        System.out.println("Found a balance of: " + result);
        return result;
    }

    private Integer PricePoint(Double imbalance){
        //todo: crate a function that generates a regulation pricepoint based on the imbalance

        return 100000;
    }

    private void PopulateUberArray(Double imbalance){
        if(imbalance<0){ //Shortage detected
            System.out.println("Shortage detected");
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
            System.out.println("SurPlus detected!");
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

    public HashMap<Integer, RegulationReport> Balance(){
        Double imbalance= preImbalance();
        pricePoint = PricePoint(imbalance);
        PopulateUberArray(imbalance);
        Balancing(imbalance);

        return RR;
    }

    private void Balancing(Double imbalance){
        Double postImbalance = imbalance;
        Double smallestCapacity;
        Integer numberOfClients;
        System.out.println("Let's balance the shit out of this " + imbalance + " watt imbalance");
        if (productionnArray.isEmpty() && consumptionArray.isEmpty()){
            return; //No need to try balancing when there is no available capacity
        }

        if (postImbalance<0) { //If we have a negative surplus (shortage)
            if (productionnArray.getLowestPrice() <= consumptionArray.getLowestPrice()) {
                smallestCapacity = productionnArray.getLowestCapacity();
                numberOfClients = productionnArray.getNumberOfCheapestClients();
                //if smallest capacity is more than enough, readjust smallest capacity.
                if (-postImbalance < smallestCapacity * numberOfClients) {
                    smallestCapacity = (-postImbalance) / numberOfClients;
                }
                //Get a list of all the uuid's that participated in this round
                List<Integer> uuidList = productionnArray.deployCapacity(smallestCapacity);
                for (Integer tempUuid : uuidList) {
                    addRegulationReport(tempUuid, 0.0, smallestCapacity);
                }
            } else {
                smallestCapacity = consumptionArray.getLowestCapacity();
                numberOfClients = consumptionArray.getNumberOfCheapestClients();
                //if smallest capacity is more than enough, readjust smallest capacity.
                if (-postImbalance < smallestCapacity * numberOfClients) {
                    smallestCapacity = (-postImbalance) / numberOfClients;
                }
                List<Integer> uuidList = consumptionArray.deployCapacity(smallestCapacity);
                for (Integer tempUuid : uuidList) {
                    addRegulationReport(tempUuid, -smallestCapacity, 0.0);
                }
            }
            postImbalance +=  (smallestCapacity * numberOfClients);
            if (postImbalance<0) { //this is done because small rounding errors may results a small surplus and we don't want infinit balancing
                Balancing(postImbalance);
            }

        }else{  //If we have a positive surplus
            if (productionnArray.getLowestPrice() <= consumptionArray.getLowestPrice()) {
                smallestCapacity = productionnArray.getLowestCapacity();
                numberOfClients = productionnArray.getNumberOfCheapestClients();
                //if smallest capacity is more than enough, readjust smallest capacity.
                if (postImbalance < smallestCapacity * numberOfClients) {
                    smallestCapacity = postImbalance / numberOfClients;
                }
                //Get a list of all the uuid's that participated in this round
                List<Integer> uuidList = productionnArray.deployCapacity(smallestCapacity);
                for (Integer tempUuid : uuidList) {
                    addRegulationReport(tempUuid, 0.0, -smallestCapacity);
                }
            } else {
                smallestCapacity = consumptionArray.getLowestCapacity();
                numberOfClients = consumptionArray.getNumberOfCheapestClients();
                //if smallest capacity is more than enough, readjust smallest capacity.
                if (postImbalance < smallestCapacity * numberOfClients) {
                    smallestCapacity = postImbalance / numberOfClients;
                }
                List<Integer> uuidList = consumptionArray.deployCapacity(smallestCapacity);
                for (Integer tempUuid : uuidList) {
                    addRegulationReport(tempUuid, smallestCapacity, 0.0);
                }
            }

            postImbalance -=  (smallestCapacity * numberOfClients);
            if (postImbalance>0) { //this is done because small rounding errors may results a small surplus and we don't want infinit balancing
                Balancing(postImbalance);
            }
        }
    }

    void addRegulationReport(Integer uuid, Double consAmount, Double prodAmount){
        RegulationReport temp;
        if(RR.containsKey(uuid)){
            temp = new RegulationReport(uuid, RR.get(uuid).getConsRegulationAmount() + consAmount, RR.get(uuid).getProdRegulationAmount() + prodAmount, pricePoint);
        }else{
            temp = new RegulationReport(uuid,  consAmount, prodAmount, pricePoint);
        }
        RR.put(uuid, temp);
    }

}
