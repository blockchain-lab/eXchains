import java.util.HashMap;
import java.util.Map;


public class Message {
    public enum Type {
        CLIENTREPORT
    }

    private Type messageType;

    public Type getMessageType() {
        return messageType;
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

    public HashMap<Double, Double> getOfferedFlexibility() {
        return offeredFlexibility;
    }

    public HashMap<String, Object> Data;

    private Integer uuid;
    private Double production;
    private Double consumption;
    private HashMap<String, Double> predictedCons;
    private HashMap<String, Double> predictedProd;
    private HashMap<Double, Double> offeredFlexibility;

    public Message(Type messageType, HashMap<String, Map> Data){
        Data= new HashMap<>(Data);
    }

    public Message(Type messageType, Integer uuid, Double production, Double consumption, HashMap<String, Double> predictedCons, HashMap<String, Double> predictedProd, HashMap<Double, Double> offeredFlexibility) {
        messageType = messageType;
        uuid = uuid;
        production = production;
        consumption = consumption;
        predictedCons = predictedCons;
        predictedProd = predictedProd;
        offeredFlexibility = offeredFlexibility;
    }


}
