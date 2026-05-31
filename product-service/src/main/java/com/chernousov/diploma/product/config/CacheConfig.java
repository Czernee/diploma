package com.chernousov.diploma.product.config;

import org.springframework.cache.CacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.serializer.RedisSerializationContext;
import org.springframework.data.redis.serializer.RedisSerializer;

import java.time.Duration;
import java.util.Map;

@Configuration
public class CacheConfig {

    @Bean
    public RedisCacheConfiguration redisCacheConfiguration() {
        return RedisCacheConfiguration.defaultCacheConfig()
                .disableCachingNullValues()
                .serializeValuesWith(
                        RedisSerializationContext.SerializationPair.fromSerializer(
                                RedisSerializer.json()
                        )
                );
    }

    @Bean
    public CacheManager cacheManager(
            RedisConnectionFactory redisConnectionFactory,
            RedisCacheConfiguration redisCacheConfiguration
    ) {
        Map<String, RedisCacheConfiguration> caches = Map.of(
                "products:search", redisCacheConfiguration.entryTtl(Duration.ofMinutes(3)),
                "products:by-id", redisCacheConfiguration.entryTtl(Duration.ofMinutes(10)),
                "products:categories", redisCacheConfiguration.entryTtl(Duration.ofMinutes(30)),
                "products:configurator", redisCacheConfiguration.entryTtl(Duration.ofMinutes(5))
        );

        return RedisCacheManager.builder(redisConnectionFactory)
                .cacheDefaults(redisCacheConfiguration.entryTtl(Duration.ofMinutes(5)))
                .withInitialCacheConfigurations(caches)
                .transactionAware()
                .build();
    }
}
