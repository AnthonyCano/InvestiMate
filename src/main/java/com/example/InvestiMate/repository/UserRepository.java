package com.example.InvestiMate.repository;

// These imports are for getting database manipulation and normalization
// for sql databases. Second import gives the repo (database) access to user structure
// Repository handles the db
import org.springframework.data.jpa.repository.JpaRepository;
import com.example.InvestiMate.model.User;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
@Repository
public interface UserRepository extends CrudRepository<User, Long> {
    Optional<User> findByEmail(String email);
    Optional<User> findByVerificationCode(String verificationCode);
}
