import java.util.HashMap;
import java.util.Map;

//All the prices mention here are displayed in Euro-centicents
public class ClientReport {

    public ClientReport(Integer uuid, Double production, Double consumption, HashMap<String, Double> predictedCons, HashMap<String, Double> predictedProd, HashMap<Integer, Double> consFlexibility, HashMap<Integer, Double> prodFlexibility) {
        this.uuid = uuid;
        this.production = production;
        this.consumption = consumption;
        this.predictedCons = predictedCons;
        this.predictedProd = predictedProd;
        this.consFlexibility = consFlexibility;
        this.prodFlexibility = prodFlexibility;
    }

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

    public HashMap<Integer, Double> getConsFlexibility() {
        return consFlexibility;
    }

    public HashMap<Integer, Double> getProdFlexibility() {
        return prodFlexibility;
    }

    private Integer uuid;
    //Variables for CLIENTREPORT Messages
    private Double production;
    private Double consumption;
    private HashMap<String, Double> predictedCons;
    private HashMap<String, Double> predictedProd;
    private HashMap<Integer, Double> consFlexibility;
    private HashMap<Integer, Double> prodFlexibility;



}
