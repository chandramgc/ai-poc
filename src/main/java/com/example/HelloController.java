package com.example;
import org.springframework.web.bind.annotation.*;
@RestController
public class HelloController {
    @GetMapping("/")        public String hello()  { return "Hello, Spring Boot!"; }
    @GetMapping("/api/status") public String status() { return "running"; }
}
