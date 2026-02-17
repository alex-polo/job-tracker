class RabbitMQError(Exception):
    """Base class for RabbitMQ-related errors."""


class RabbitMQConnectionError(RabbitMQError):
    """Raised when the connection to RabbitMQ cannot be established."""


class RabbitMQInitializeError(RabbitMQError):
    """Raised when RabbitMQ infrastructure cannot be initialized."""


class RabbitMQPublishError(RabbitMQError):
    """Raised when a message cannot be published to RabbitMQ."""


class RabbitMQConsumeError(RabbitMQError):
    """Raised when consuming messages fails."""


class RabbitMQSerializationError(RabbitMQError):
    """Raised when message serialization/deserialization fails."""


class RabbitMQTimeoutError(RabbitMQError):
    """Raised when a RabbitMQ operation times out."""
