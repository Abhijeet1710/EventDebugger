package com.example.ingestion_service;

public class EventRequest {

    private Long customerId;
    private String eventId;
    private Double amound;
    private String trx;
    private Boolean isAPR;
    private String status;

    public Long getCustomerId() {
        return customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public String getEventId() {
        return eventId;
    }

    public void setEventId(String eventId) {
        this.eventId = eventId;
    }

    public Double getAmound() {
        return amound;
    }

    public void setAmound(Double amound) {
        this.amound = amound;
    }

    public String getTrx() {
        return trx;
    }

    public void setTrx(String trx) {
        this.trx = trx;
    }

    public Boolean getIsAPR() {
        return isAPR;
    }

    public void setIsAPR(Boolean isAPR) {
        this.isAPR = isAPR;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}