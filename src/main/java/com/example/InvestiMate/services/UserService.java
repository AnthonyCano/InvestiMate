package com.example.InvestiMate.services;

import com.example.InvestiMate.model.User;
import com.example.InvestiMate.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
public class UserService implements UserDetailsService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Autowired
    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        // Load using the username field (NOT email)
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with username: " + username));
    }
    public List<User> allUsers() {
        List<User> users = new ArrayList<>();
        userRepository.findAll().forEach(users::add);
        return users;
    }

    public User createUser(User user) {
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        user.setEnabled(false); // Disable by default until verification
        return userRepository.save(user);
    }

//    public User updateUser(Long id, User updatedUser) {
//        return userRepository.findById(id).map(user -> {
//            user.setUsername(updatedUser.getUsername());
//            user.setName(updatedUser.getName());
//            user.setEmail(updatedUser.getEmail());
//            if (updatedUser.getPassword() != null && !updatedUser.getPassword().isBlank()) {
//                user.setPassword(passwordEncoder.encode(updatedUser.getPassword()));
//            }
//            return userRepository.save(user);
//        }).orElseThrow(() -> new RuntimeException("User not found"));
//    }


}
