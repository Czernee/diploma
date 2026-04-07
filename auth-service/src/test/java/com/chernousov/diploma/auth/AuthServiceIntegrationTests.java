package com.chernousov.diploma.auth;

import com.chernousov.diploma.auth.dto.LoginRequest;
import com.chernousov.diploma.auth.dto.RegisterRequest;
import com.chernousov.diploma.auth.exception.InvalidCredentialsException;
import com.chernousov.diploma.auth.exception.InvalidTokenException;
import com.chernousov.diploma.auth.exception.UserAlreadyExistsException;
import com.chernousov.diploma.auth.service.AuthService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
class AuthServiceIntegrationTests {

    @Autowired
    private AuthService authService;

    @Test
    void registerLoginAndMeFlowWorks() {
        var register = authService.register(new RegisterRequest(
                "alice",
                "alice@example.com",
                "password123"
        ));
        assertThat(register.token()).isNotBlank();
        assertThat(register.user().username()).isEqualTo("alice");

        var login = authService.login(new LoginRequest("alice", "password123"));
        assertThat(login.token()).isNotBlank();
        assertThat(login.tokenType()).isEqualTo("Bearer");

        var me = authService.me("Bearer " + login.token());
        assertThat(me.username()).isEqualTo("alice");
        assertThat(me.email()).isEqualTo("alice@example.com");
        assertThat(me.role()).isEqualTo("USER");
    }

    @Test
    void duplicateUserRegistrationFails() {
        authService.register(new RegisterRequest("bob", "bob@example.com", "password123"));

        assertThatThrownBy(() -> authService.register(new RegisterRequest("bob", "other@example.com", "password123")))
                .isInstanceOf(UserAlreadyExistsException.class);
        assertThatThrownBy(() -> authService.register(new RegisterRequest("other-bob", "bob@example.com", "password123")))
                .isInstanceOf(UserAlreadyExistsException.class);
    }

    @Test
    void invalidCredentialsFail() {
        authService.register(new RegisterRequest("charlie", "charlie@example.com", "password123"));

        assertThatThrownBy(() -> authService.login(new LoginRequest("charlie", "bad-password")))
                .isInstanceOf(InvalidCredentialsException.class);
    }

    @Test
    void invalidTokenFails() {
        assertThatThrownBy(() -> authService.me("Bearer bad-token"))
                .isInstanceOf(InvalidTokenException.class);
    }
}
