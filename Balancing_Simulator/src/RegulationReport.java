public class RegulationReport {


    public Integer getUuid() {
        return uuid;
    }


    public Double getPricePoint() {
        return pricePoint;
    }


    private Integer uuid;

    public Double getConsRegulationAmount() {
        return consRegulationAmount;
    }

    public Double getProdRegulationAmount() {
        return ProdRegulationAmount;
    }

    private Double consRegulationAmount;
    private Double ProdRegulationAmount;
    private Double pricePoint;


    public RegulationReport(Integer receipient, Integer uuid, Double upRegulationAmount, Double consRegulationAmount, Double pricePoint, Double ProdRegulationAmount, Double clusterProduction) {
        this.uuid = uuid;
        this.consRegulationAmount = consRegulationAmount;
        this.ProdRegulationAmount = ProdRegulationAmount;
        this.pricePoint = pricePoint;
    }
}
