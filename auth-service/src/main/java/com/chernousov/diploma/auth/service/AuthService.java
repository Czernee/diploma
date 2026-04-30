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

import java.util.Locale;
import java.util.regex.Pattern;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AuthService {

    private static final Pattern USERNAME_PATTERN = Pattern.compile("^[A-Za-z0-9._-]{3,120}$");
    private static final Pattern EMAIL_PATTERN = Pattern.compile("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,63}$");
    private static final Pattern STRONG_PASSWORD_PATTERN =
            Pattern.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^\\w\\s])(?!.*\\s).{8,120}$");

    private final UserAccountRepository userAccountRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        String username = normalizeUsername(request.username());
        String email = normalizeEmail(request.email());
        String password = validateRegistrationPassword(request.password());

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
                .passwordHash(passwordEncoder.encode(password))
                .role(UserRole.USER)
                .build());

        return buildAuthResponse(created);
    }

    public AuthResponse login(LoginRequest request) {
        String username = normalizeUsername(request.username());
        String password = validateLoginPassword(request.password());

        UserAccount user = userAccountRepository.findByUsername(username)
                .orElseThrow(InvalidCredentialsException::new);

        if (!passwordEncoder.matches(password, user.getPasswordHash())) {
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

    private String normalizeUsername(String rawUsername) {
        if (rawUsername == null) {
            throw new IllegalArgumentException("Username is required");
        }

        String username = rawUsername.trim();
        if (!rawUsername.equals(username)) {
            throw new IllegalArgumentException("Username must not contain leading or trailing spaces");
        }
        if (!USERNAME_PATTERN.matcher(username).matches()) {
            throw new IllegalArgumentException("Username must be 3-120 chars and contain only letters, digits, dot, underscore and dash");
        }
        return username;
    }

    private String normalizeEmail(String rawEmail) {
        if (rawEmail == null) {
            throw new IllegalArgumentException("Email is required");
        }

        String trimmed = rawEmail.trim();
        if (!rawEmail.equals(trimmed)) {
            throw new IllegalArgumentException("Email must not contain leading or trailing spaces");
        }

        String normalized = trimmed.toLowerCase(Locale.ROOT);
        if (!EMAIL_PATTERN.matcher(normalized).matches()) {
            throw new IllegalArgumentException("Email format is invalid");
        }
        return normalized;
    }

    private String validateRegistrationPassword(String rawPassword) {
        String password = validateLoginPassword(rawPassword);
        if (!STRONG_PASSWORD_PATTERN.matcher(password).matches()) {
            throw new IllegalArgumentException(
                    "Password must include uppercase, lowercase, digit and special character, and must not contain spaces"
            );
        }
        return password;
    }

    private String validateLoginPassword(String rawPassword) {
        if (rawPassword == null || rawPassword.isBlank()) {
            throw new IllegalArgumentException("Password is required");
        }
        if (rawPassword.length() < 8 || rawPassword.length() > 120) {
            throw new IllegalArgumentException("Password must be between 8 and 120 characters");
        }
        return rawPassword;
    }
}
