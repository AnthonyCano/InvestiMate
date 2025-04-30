package com.example.InvestiMate.repository;

// These imports are for getting database manipulation and normalization
// for sql databases. Second import gives the repo (database) access to user structure

import org.springframework.data.jpa.repository.JpaRepository;
import com.example.InvestiMate.model.User;


public interface UserRepository extends JpaRepository<User, Long>{
}
