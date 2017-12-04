import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class SortedUberArray {
    private List<Prices> prices;

    public SortedUberArray() {
        prices = new ArrayList<>();
    }

    public void addCapacity(Integer uuid, Integer centiCent, Double capacity){
        Capacity tempCapacity = new Capacity(capacity, uuid);
        Prices tempPrices = new Prices(centiCent, tempCapacity);
        if(!prices.contains(tempPrices)){
            prices.add(tempPrices);
        } else{
            prices.get(prices.indexOf(tempPrices)).addCapacity(tempCapacity);
        }
    }

    public boolean isEmpty(){
        return (!prices.isEmpty() && !prices.get(0).capacityList.isEmpty());
    }

    public Integer getLowestPrice(){
        return prices.get(0).getPrice();
    }

    public Integer getNumberOfCheapestClients(){
        return prices.get(0).capacityList.size();
    }

    public Double getLowestCapacity(){
        return prices.get(0).getLowestCapacity();
    }

    public List<Integer> deployCapacity(Double capacity){
        List<Integer> uuidList = prices.get(0).deployCapacity(capacity);
        //If whe created an empty price entry, remove it
        if(prices.get(0).capacityList.isEmpty()){
            prices.remove(0);
        }
        //perform a sort just in case, (Don't know for sure if everything shift nicely when removing the head of list)
        this.Sort();
        return uuidList;
    }



    public void Sort(){
        this.prices.sort(Prices::compareTo);

        for (Prices temp: prices) {
            //temp.capacityList.sort(Capacity::compareTo);
            temp.Sort();
        }
    }
    class Capacity implements Comparable<Capacity>, Comparator<Capacity> {
        public Capacity(Double capacity, int uuid) {
            this.capacity = capacity;
            this.uuid = uuid;
        }

        public Double getCapacity() {
            return capacity;
        }

        private void deployCapacity(Double capacity){
            this.capacity -= capacity;
        }

        public int getUuid() {
            return uuid;
        }

        private Double capacity;
        private Integer uuid;

        // Overriding the compareTo method
        public int compareTo(Capacity c) {
            return (this.capacity).compareTo(c.capacity);
        }

        // Overriding the compare method to sort the age
        public int compare(Capacity c, Capacity c1) {
            return Double.compare(c.getCapacity(), c1.getCapacity());
        }
    }


    class Prices implements Comparable<Prices>, Comparator<Prices>{
        public Prices(int price, Capacity capacity) {
            capacityList = new ArrayList<>();
            this.price = price;
            this.capacityList.add(capacity);
        }

        public int getPrice() {
            return price;
        }

        public Boolean addCapacity(Capacity capacity){
            return this.capacityList.add(capacity);
        }

        private List<Integer> deployCapacity(Double capacity){
            List<Integer> uuidList = new ArrayList<>();
            for (Capacity tempcapacity: capacityList){
                //If this is the last capacity, delete the entry, else adjust
                if (tempcapacity.capacity<=capacity){
                    capacityList.remove(tempcapacity);
                }else{
                    tempcapacity.deployCapacity(capacity);
                }
                uuidList.add(tempcapacity.getUuid());
            }
            return uuidList;
        }

        private Integer price;                      //in centicents
        private List<Capacity> capacityList;

        void Sort(){
            capacityList.sort(Capacity::compareTo);
        }

        Double getLowestCapacity(){
            return capacityList.get(0).capacity;
        }

        // Overriding the compareTo method
        public int compareTo(Prices p) {
            return (this.price).compareTo(p.price);
        }

        // Overriding the compare method to sort the age
        public int compare(Prices p, Prices p1) {
            return p.getPrice() - p1.getPrice();
        }

        // Overiding the equals method for using contains
        @Override
        public boolean equals(Object newPrice){
            if (newPrice == null) return false;
            if (newPrice == this) return true;
            if (!(newPrice instanceof Prices))return false;
            Prices otherMyClass = (Prices)newPrice;
            return this.price.equals(otherMyClass.getPrice());
        }
    }
}
