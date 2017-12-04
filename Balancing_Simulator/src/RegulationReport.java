public class RegulationReport {


    public Integer getUuid() {
        return uuid;
    }


    public Integer getPricePoint() {
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
    private Integer pricePoint;


    public RegulationReport(Integer uuid, Double consRegulationAmount, Double ProdRegulationAmount, Integer pricePoint) {
        this.uuid = uuid;
        this.consRegulationAmount = consRegulationAmount;
        this.ProdRegulationAmount = ProdRegulationAmount;
        this.pricePoint = pricePoint;
    }
}
