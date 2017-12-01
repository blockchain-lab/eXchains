import java.util.HashMap;
import java.util.Map;


public class Transaction {
    public enum MessageType {
        CLIENTREPORT
    }

    private Integer uuid;
    private Double production;
    private Double consumption;
    private HashMap<String, Double> predictedCons;
    private HashMap<String, Double> predictedProd;
    private HashMap<Double, Double> offeredFlexibility;
    private MessageType messageType;

    public Transaction(MessageType messageType, Integer uuid, Double production, Double consumption, HashMap<String, Double> predictedCons, HashMap<String, Double> predictedProd, HashMap<Double, Double> offeredFlexibility) {
        this.messageType = messageType;
        this.uuid = uuid;
        this.production = production;
        this.consumption = consumption;
        this.predictedCons = predictedCons;
        this.predictedProd = predictedProd;
        this.offeredFlexibility = offeredFlexibility;
    }


    public MessageType getMessageType() {
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

}
