package com.example.InvestiMate.services;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.SignatureAlgorithm;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cglib.core.Signature;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import java.util.function.Function;

@Service
public class JwtService {

    @Value("${security.jwt.secret-key")
    private String secretKey;

    @Value("${security.jwt.expiration.time")
    private long jwtExpiration;

    public String extractUsername(String token){
        return extractClaim(token, Claims::getSubject);
    }

    // <T> T just means the method will return whatever it needs to!
    public <T> T extractClaim(String Token, Function<Claims,T> claimsResolver){
        final Claims claims = extractAllCalims(token); // Claims: What we are requesting (username, expiration_time)
        return claimsResolver.apply(claims); // Runs the provided appropriate function
    }
    
    // Simple single claim method
    public String generateToken(UserDetails userDetails){
        return generateToken(new HashMap<>(), userDetails);
    }
    
    // Overloaded version that allows for extra claims
    public String generateToken(Map<String, Object> extraClaims, UserDetails userDetails){
        return buildToken(extraClaims,userDetails, jwtExpiration);
    }

    public Long getExpirationTime(){
        return jwtExpiration;
    }
    
    public String buildToken(Map<String, Object> extraClaims, UserDetails userDetails, long expiration){
        // Build the token, Sets the claims, setting the subject(user), 
        // setting the issued time, setting expire time, signs it, and then compacts it.
        return Jwts
            .builder()
            .setClaims(extraClaims)
            .setSubject(userDetails.getUsername())
            .setIssuedAt(new Date(System.currentTimeMillis()))
            .setExpiration(new Date(System.currentTimeMillis() + expiration))
            .signWith(getSignInKey(), SignatureAlgorithm.ES256)
            .compact();
    }

    public boolean isTokenValid(String token, UserDetails userDetails){
        // final just makes sure the username isn't chagned in the function
        final String username = extractUsername(token);
        return (username.equals(userDetails.getUsername()) && !isTokenExpired(token));

    }

    private boolean isToken
}
