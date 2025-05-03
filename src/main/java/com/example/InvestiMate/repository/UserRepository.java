package com.example.InvestiMate.repository;

// These imports are for getting database manipulation and normalization
// for sql databases. Second import gives the repo (database) access to user structure
// Repository handles the db
import org.springframework.data.jpa.repository.JpaRepository;
import com.example.InvestiMate.model.User;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long>{
    Optional<User> findByEmail(String email);
}
