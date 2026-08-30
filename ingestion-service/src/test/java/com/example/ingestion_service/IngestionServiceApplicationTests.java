//package com.example.ingestion_service;
//
//import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
//import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
//import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
//
//import org.junit.jupiter.api.Test;
//import org.springframework.beans.factory.annotation.Autowired;
//import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
//import org.springframework.boot.test.context.SpringBootTest;
//import org.springframework.http.MediaType;
//import org.springframework.test.web.servlet.MockMvc;
//
//@SpringBootTest
//@AutoConfigureMockMvc
//class IngestionServiceApplicationTests {
//
//	@Autowired
//	private MockMvc mockMvc;
//
//	@Test
//	void shouldRejectInboundWhenStatusIsNull() throws Exception {
//		String request = "{\"customerId\":123,\"eventId\":\"evt-123\",\"amound\":20,\"trx\":\"C\",\"isAPR\":true,\"status\":null}";
//
//		mockMvc.perform(post("/inbound")
//				.contentType(MediaType.APPLICATION_JSON)
//				.content(request))
//				.andExpect(status().isBadRequest());
//	}
//
//	@Test
//	void shouldProcessInboundAndCallOutbound() throws Exception {
//		String request = "{\"customerId\":123,\"eventId\":\"evt-123\",\"amound\":20,\"trx\":\"C\",\"isAPR\":true,\"status\":\"FAILED\"}";
//
//		mockMvc.perform(post("/inbound")
//				.contentType(MediaType.APPLICATION_JSON)
//				.content(request))
//				.andExpect(status().isOk())
//				.andExpect(content().string("success"));
//	}
//
//	@Test
//	void shouldIgnoreRequestWhenIsAprIsFalse() throws Exception {
//		String request = "{\"customerId\":123,\"eventId\":\"evt-123\",\"amound\":20,\"trx\":\"C\",\"isAPR\":false,\"status\":\"FAILED\"}";
//
//		mockMvc.perform(post("/inbound")
//				.contentType(MediaType.APPLICATION_JSON)
//				.content(request))
//				.andExpect(status().isOk())
//				.andExpect(content().string("filtered"));
//	}
//
//	@Test
//	void shouldReturnSuccessFromOutbound() throws Exception {
//		mockMvc.perform(post("/outbound")
//				.contentType(MediaType.APPLICATION_JSON)
//				.content("{\"customerId\":123,\"eventId\":\"evt-123\",\"amound\":20,\"trx\":\"C\"}"))
//				.andExpect(status().isOk())
//				.andExpect(content().string("success"));
//	}
//}
