package com.chernousov.diploma.auth.service;

import com.chernousov.diploma.auth.domain.UserAccount;
import com.chernousov.diploma.auth.domain.UserRole;
import com.chernousov.diploma.auth.dto.AuthResponse;
import com.chernousov.diploma.auth.dto.LoginRequest;
import com.chernousov.diploma.auth.dto.RegisterRequest;
import com.chernousov.diploma.auth.dto.UserProfileResponse;
import com.chernousov.diploma.auth.exception.InvalidCredentialsException;
import com.chernousov.diploma.auth.exception.InvalidTokenException;
import com.chernousov.diploma.auth.exception.UserAlreadyExistsException;
import com.chernousov.diploma.auth.repository.UserAccountRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AuthService {

    private final UserAccountRepository userAccountRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        String username = request.username().trim();
        String email = request.email().trim().toLowerCase();

        userAccountRepository.findByUsername(username)
                .ifPresent(found -> {
                    throw new UserAlreadyExistsException("Username is already taken");
                });
        userAccountRepository.findByEmail(email)
                .ifPresent(found -> {
                    throw new UserAlreadyExistsException("Email is already taken");
                });

        UserAccount created = userAccountRepository.save(UserAccount.builder()
                .username(username)
                .email(email)
                .passwordHash(passwordEncoder.encode(request.password()))
                .role(UserRole.USER)
                .build());

        return buildAuthResponse(created);
    }

    public AuthResponse login(LoginRequest request) {
        UserAccount user = userAccountRepository.findByUsername(request.username().trim())
                .orElseThrow(InvalidCredentialsException::new);

        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) {
            throw new InvalidCredentialsException();
        }

        return buildAuthResponse(user);
    }

    public UserProfileResponse me(String authorizationHeader) {
        String token = extractBearerToken(authorizationHeader);
        String username = jwtService.extractUsername(token);
        UserAccount user = userAccountRepository.findByUsername(username)
                .orElseThrow(() -> new InvalidTokenException("Token subject user does not exist"));
        return toProfile(user);
    }

    private AuthResponse buildAuthResponse(UserAccount user) {
        String token = jwtService.generateToken(user);
        return new AuthResponse(
                token,
                "Bearer",
                jwtService.extractExpiration(token),
                toProfile(user)
        );
    }

    private UserProfileResponse toProfile(UserAccount user) {
        return new UserProfileResponse(
                user.getId(),
                user.getUsername(),
                user.getEmail(),
                user.getRole().name()
        );
    }

    private String extractBearerToken(String authorizationHeader) {
        if (authorizationHeader == null || authorizationHeader.isBlank()) {
            throw new InvalidTokenException("Missing Authorization header");
        }
        if (!authorizationHeader.startsWith("Bearer ")) {
            throw new InvalidTokenException("Authorization header must be Bearer token");
        }

        String token = authorizationHeader.substring("Bearer ".length()).trim();
        if (token.isEmpty()) {
            throw new InvalidTokenException("JWT token is empty");
        }
        return token;
    }
}
