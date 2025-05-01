package com.example.InvestiMate.controller;

// The REST controller for our user
import com.example.InvestiMate.model.User;
import com.example.InvestiMate.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired; // Tells Spring to auto-inject the required dependency (UserRepository) via dependency injection
import org.springframework.web.bind.annotation.*; // Provides the REST-specific annotations (@RestController, @RequestMapping, etc.)

import java.util.List;
import java.util.Optional;

@RestController // Tells spring it will handle https requests
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserRepository userRepository;

    // Get all users
    @GetMapping
    public List<User> getAllUsers(){
        return userRepository.findAll();
    }

    // Get user by ID
    @GetMapping
    public Optional<User> getUserById(@PathVariable Long id){
        return userRepository.findById(id);
    }

    // Create a new user
    @PostMapping
    public User createUser(@RequestBody User user){
        return userRepository.save(user);
    }

    // Update the existing user
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User updatedUser) {
        return userRepository.findById(id).map(user -> {
            user.setName(updatedUser.getName());
            user.setEmail(updatedUser.getEmail());
            user.setPassword(updatedUser.getPassword());
            return userRepository.save(user);
        }).orElseThrow(() -> new RuntimeException("User not found with id " + id));
    }

    // Delete a user
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
        userRepository.deleteById(id);
    }
}

