import java.util.HashMap;
import java.util.Map;


public class ClientReport {
    public Integer getUuid() {
        return uuid;
    }

    public Double getProduction() {
        return production;
    }

    public Double getConsumption() {
        return consumption;
    }

    public HashMap<String, Double> getPredictedCons() {
        return predictedCons;
    }

    public HashMap<String, Double> getPredictedProd() {
        return predictedProd;
    }

    public HashMap<Double, Double> getOfferedFlexibility() {
        return offeredFlexibility;
    }



    private Integer receipient;
    private Integer uuid;
    //Variables for CLIENTREPORT Messages
    private Double production;
    private Double consumption;
    private HashMap<String, Double> predictedCons;
    private HashMap<String, Double> predictedProd;
    private HashMap<Double, Double> offeredFlexibility;



    public ClientReport(Integer uuid, Double production, Double consumption, HashMap<String, Double> predictedCons, HashMap<String, Double> predictedProd, HashMap<Double, Double> offeredFlexibility) {
        uuid = uuid;
        production = production;
        consumption = consumption;
        predictedCons = predictedCons;
        predictedProd = predictedProd;
        offeredFlexibility = offeredFlexibility;
    }
}
