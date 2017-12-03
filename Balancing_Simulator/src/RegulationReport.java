public class RegulationReport {

    private Integer receipient;
    private Integer uuid;

    private Double regulationAmount;
    private Double pricePoint;
    private Double clusterConsumption;
    private Double clusterProduction;

    public RegulationReport(Integer receipient, Integer uuid, Double regulationAmount, Double pricePoint, Double clusterConsumption, Double clusterProduction) {
        this.receipient = receipient;
        this.uuid = uuid;
        this.regulationAmount = regulationAmount;
        this.pricePoint = pricePoint;
        this.clusterConsumption = clusterConsumption;
        this.clusterProduction = clusterProduction;
    }

    public Integer getUuid() {
        return uuid;
    }

    public Double getRegulationAmount() {
        return regulationAmount;
    }

    public Double getPricePoint() {
        return pricePoint;
    }

    public Double getClusterConsumption() {
        return clusterConsumption;
    }

    public Double getClusterProduction() {
        return clusterProduction;
    }

}
