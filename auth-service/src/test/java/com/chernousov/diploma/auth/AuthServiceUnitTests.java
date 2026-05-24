package com.chernousov.diploma.auth;

import com.chernousov.diploma.auth.domain.UserAccount;
import com.chernousov.diploma.auth.domain.UserRole;
import com.chernousov.diploma.auth.dto.LoginRequest;
import com.chernousov.diploma.auth.dto.RegisterRequest;
import com.chernousov.diploma.auth.exception.InvalidTokenException;
import com.chernousov.diploma.auth.exception.InvalidCredentialsException;
import com.chernousov.diploma.auth.repository.UserAccountRepository;
import com.chernousov.diploma.auth.service.AuthService;
import com.chernousov.diploma.auth.service.JwtService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.Instant;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AuthServiceUnitTests {

    @Mock
    private UserAccountRepository userAccountRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtService jwtService;

    @InjectMocks
    private AuthService authService;

    @Test
    void registerNormalizesEmailAndPersistsEncodedPassword() {
        when(userAccountRepository.findByUsername("alice")).thenReturn(Optional.empty());
        when(userAccountRepository.findByEmail("alice@example.com")).thenReturn(Optional.empty());
        when(passwordEncoder.encode("Password123!")).thenReturn("encoded-password");
        when(userAccountRepository.save(any(UserAccount.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(jwtService.generateToken(any(UserAccount.class))).thenReturn("token");
        when(jwtService.extractExpiration("token")).thenReturn(Instant.parse("2030-01-01T00:00:00Z"));

        var response = authService.register(new RegisterRequest("alice", "Alice@Example.COM", "Password123!"));

        ArgumentCaptor<UserAccount> savedUserCaptor = ArgumentCaptor.forClass(UserAccount.class);
        verify(userAccountRepository).save(savedUserCaptor.capture());
        UserAccount savedUser = savedUserCaptor.getValue();

        assertThat(savedUser.getEmail()).isEqualTo("alice@example.com");
        assertThat(savedUser.getPasswordHash()).isEqualTo("encoded-password");
        assertThat(savedUser.getRole()).isEqualTo(UserRole.USER);
        assertThat(response.user().email()).isEqualTo("alice@example.com");
        assertThat(response.token()).isEqualTo("token");
    }

    @Test
    void loginRejectsBlankPasswordBeforeRepositoryLookup() {
        assertThatThrownBy(() -> authService.login(new LoginRequest("alice", "   ")))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Password is required");

        verifyNoInteractions(userAccountRepository);
    }

    @Test
    void meRejectsMissingAuthorizationHeader() {
        assertThatThrownBy(() -> authService.me(null))
                .isInstanceOf(InvalidTokenException.class)
                .hasMessageContaining("Missing Authorization header");
    }

    @Test
    void meRejectsNonBearerAuthorizationHeader() {
        assertThatThrownBy(() -> authService.me("Basic abc123"))
                .isInstanceOf(InvalidTokenException.class)
                .hasMessageContaining("Authorization header must be Bearer token");
    }

    @Test
    void loginFailsForUnknownUser() {
        when(userAccountRepository.findByUsername("unknown-user")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> authService.login(new LoginRequest("unknown-user", "Password123!")))
                .isInstanceOf(InvalidCredentialsException.class);
    }
}
