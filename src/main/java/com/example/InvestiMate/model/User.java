package com.example.InvestiMate.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Column;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")

public class User {
    // User ID
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    // Getter function for the ID
    public Long getId() {
        return id;
    }
    // Setter function for set ID
    public void setId(Long id){
        this.id = id;
    }

    // User Name
    private String name;
    public String getName(){
        return name;
    }
    public void setName(String name){
        this.name = name;
    }

    // Email
    @Column(nullable = false, unique = true)
    private String email;
    public String getEmail(){
        return email;
    }
    public void setEmail(String email){
        this.email = email;
    }

    // Password
    private String password;
    public String getPassword(){
        return password;
    }
    public void setPassword(String password){
        this.password = password;
    }

    // Timestamp
    @CreationTimestamp
    private LocalDateTime createdAt;
    public LocalDateTime getCreatedAt(){
        return createdAt;
    }
    public void setCreatedAt(LocalDateTime createdAt){
        this.createdAt = createdAt;
    }
}
