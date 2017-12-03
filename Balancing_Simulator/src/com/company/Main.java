package com.company;


public class Main {

    public static void main(String[] args) {
	    System.out.println("hello Balancing Simulator");
        SortedUberArray consume = new SortedUberArray();
        consume.addCapacity(0,0,3.0);
        consume.addCapacity(1,0,0.0);
        consume.addCapacity(2,0,2.0);
        System.out.println(consume.getLowestCapacity());
        consume.Sort();
        System.out.println(consume.getLowestCapacity());
    }
}
