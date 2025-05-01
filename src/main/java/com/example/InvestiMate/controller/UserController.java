package com.example.InvestiMate.controller;

// Controllers handle HTTP requests
// The REST controller for our user
import com.example.InvestiMate.model.User;
import com.example.InvestiMate.services.UserService;
import org.springframework.beans.factory.annotation.Autowired; // Tells Spring to auto-inject the required dependency (UserRepository) via dependency injection
import org.springframework.web.bind.annotation.*; // Provides the REST-specific annotations (@RestController, @RequestMapping, etc.)

import java.util.List;
import java.util.Optional;

@RestController // Tells spring it will handle https requests
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    // Get all users
    @GetMapping
    public List<User> getAllUsers(){
        return userService.getAllUsers();
    }

    // Get user by ID
    @GetMapping("/{id}")
    public Optional<User> getUserById(@PathVariable Long id){
        return userService.getUserById(id);
    }

    // Create a new user
    @PostMapping
    public User createUser(@RequestBody User user){
        return userService.createUser(user);
    }

    // Update the existing user
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User updatedUser) {
        return userService.updateUser(id, updatedUser);
    }

    // Delete a user
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
    }
}

