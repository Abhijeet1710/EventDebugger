package com.example.ingestion_service;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class InboundController {

    private static final Logger log = LogManager.getLogger(InboundController.class);

    @PostMapping("/inbound")
    public ResponseEntity<String> inbound(@RequestBody EventRequest request) {
        log.info("customerId={} eventId={} step=Request received", request.getCustomerId(), request.getEventId());

        validateStatus(request);

        boolean filtered = filterApr(request);
        if (filtered) {
            log.info("customerId={} eventId={} step=filter complete", request.getCustomerId(), request.getEventId());
            return ResponseEntity.ok("filtered");
        }

        EventRequest transformed = transformEvent(request);
        try {
            if(request.getStatus().equals("FAILED")) throw new IllegalArgumentException("Simulated exception for testing");
            String result = outboundCall(transformed);

            return ResponseEntity.ok(result);
        }catch (Exception e) {
            log.error("customerId={} eventId={} step={}", request.getCustomerId(), request.getEventId(), e.getMessage());
        }

        return ResponseEntity.internalServerError().body("Internal Server Error");
    }


    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<String> handleInvalidRequest(IllegalArgumentException exception) {
        return ResponseEntity.badRequest().body(exception.getMessage());
    }

    public void validateStatus(EventRequest request) {
        if (request == null || request.getStatus() == null) {
            log.info("customerId={} eventId={} step=validate complete", "NA", "NA");
            throw new IllegalArgumentException("status cannot be null");
        }
        log.info("customerId={} eventId={} step=validate complete", request.getCustomerId(), request.getEventId());
    }

    public boolean filterApr(EventRequest request) {
        boolean shouldSkip = Boolean.FALSE.equals(request.getIsAPR());
        log.info("customerId={} eventId={} step=filter complete", request.getCustomerId(), request.getEventId());
        return shouldSkip;
    }

    public EventRequest transformEvent(EventRequest request) {
        EventRequest transformed = new EventRequest();
        transformed.setCustomerId(request.getCustomerId());
        transformed.setEventId(request.getEventId());
        transformed.setAmound(request.getAmound());
        transformed.setTrx(request.getTrx());
        log.info("customerId={} eventId={} step=transform complete", request.getCustomerId(), request.getEventId());
        return transformed;
    }

    public String outboundCall(EventRequest transformed) {
        log.info("customerId={} eventId={} step=outbound complete", transformed.getCustomerId(), transformed.getEventId());
        return outbound(transformed).getBody();
    }

    @PostMapping("/outbound")
    public ResponseEntity<String> outbound(@RequestBody EventRequest request) {
//        log.info("customerId={} eventId={} step=outbound receive complete", request.getCustomerId(), request.getEventId());
        return ResponseEntity.ok("success");
    }

}