// src/main/java/com/example/InvestiMate/config/SecurityConfig.java
package com.example.InvestiMate.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

import com.example.InvestiMate.services.UserService;

@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    private final UserService userService;
    private final PasswordEncoder passwordEncoder;
    
    public SecurityConfig(UserService userService, PasswordEncoder passwordEncoder) {
        this.userService = userService;
        this.passwordEncoder = passwordEncoder;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
          // disable CSRF so curl POST works without a CSRF token
          .csrf(csrf -> csrf.disable())

          // configure URL authorization
          .authorizeHttpRequests(auth -> auth
            // allow signup without auth
            .requestMatchers(HttpMethod.POST, "/api/users").permitAll()
            // all other requests require an authenticated user
            .anyRequest().authenticated()
          )

          // use HTTP Basic (you can swap to formLogin() or JWT later)
          .httpBasic(Customizer.withDefaults());

        return http.build();
    }

    @Bean
    public AuthenticationManager authenticationManager(HttpSecurity http) throws Exception {
        AuthenticationManagerBuilder auth = 
            http.getSharedObject(AuthenticationManagerBuilder.class);

        auth
          // wire in your UserService which implements UserDetailsService
          .userDetailsService(userService)
          // and encode passwords with BCrypt
          .passwordEncoder(passwordEncoder);

        return auth.build();
    }
}
