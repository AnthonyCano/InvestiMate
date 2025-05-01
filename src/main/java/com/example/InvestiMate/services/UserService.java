package com.example.InvestiMate.services;
// Sits between the controller and the repository
// Makes the calls to the db

import com.example.InvestiMate.model.User;
import com.example.InvestiMate.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service // Marks class as bean manged by Spring
public class UserService {

    @Autowired
    private UserRepository userRepository;

}
