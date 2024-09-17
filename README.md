# EasyLoggerAJM

EasyLoggerAJM is a Python logging library designed to facilitate flexible and efficient logging for your applications. It offers a streamlined interface for configuring and using loggers, with features to handle warning messages uniquely and options for granular logging.

## Features

- **Console Warning Stream Handler**: Logs warning messages to the console with a filter to ensure each warning is shown only once.
- **Configurable Log Levels**: Easy configuration of log levels through a dictionary.
- **Daily Log Specification**: Option to split logs by day instead of by run.
- **Hourly Log Specification**: Option to split logs by hour.
- **Enhanced Error Handling**: Improved handling for invalid `log_level_to_stream` values.
- **Comprehensive Unit Tests**: Ensures robustness and correctness of the logging functionalities.

## Installation

You can install EasyLoggerAJM via pip:

```sh
pip install EasyLoggerAJM
```

## Usage

### Basic Usage

```python
from EasyLoggerAJM import EasyLogger

# Create a logger instance
EL = EasyLogger(log_level_to_stream='warning')
logger = EL.logger
# Log messages
logger.warning("This is a warning message")
logger.info("This is an info message")
```

### Configuring Log Levels to Stream

```python
log_levels = {
    'debug': 'DEBUG',
    'info': 'INFO',
    'warning': 'WARNING',
    'error': 'ERROR',
    'critical': 'CRITICAL'
}

from EasyLoggerAJM import EasyLogger

logger = EasyLogger(log_level_to_stream=log_levels['warning'])
```

## Development

To contribute to the project, follow these steps:

1. Clone the repository:

    ```sh
    git clone https://github.com/amcsparron2793/EasyLoggerAJM.git
    ```

2. Navigate to the project directory:

    ```sh
    cd EasyLoggerAJM
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Recent Changes

### Version 1.2

- **Refactor Log Specifications and Timestamps Handling**: Introduced a comprehensive `LOG_SPECS` dictionary and updated the `inner_log_fstructure` method, simplifying the format checking logic within getter definitions.
- **Hourly Log Specification**: Added the ability to split logs by hour.
- **Refactor Log Spec Format Handling**: Introduced predefined constants for better readability and maintainability.
- **Logger Levels Normalization**: Revised the normalization of logger levels, converting string levels to integer values.
- **Property for File Logger Levels**: Introduced a property for `file_logger_levels` to allow setting levels dynamically via kwargs.

### Version 1.1

- **Refactor Log Level Handling**: Simplified setting of `log_level_to_stream` using a dictionary lookup.
- **Add Console Warning Stream Handler**: Introduced `ConsoleOneTimeFilter` to filter repeated warning messages.

### Version 1.0

- **Add Timestamp Kwarg**: Introduced a kwarg attribute to the `__init__` method for custom timestamp formatting.
- **Documentation Improvements**: Enhanced docstrings and added detailed unit tests.

### Version 0.5

- **Refactor EasyLogger**: Improved configuration handling and added comprehensive unit tests.

For a detailed list of changes, check the [commit history](https://github.com/amcsparron2793/EasyLoggerAJM/commits/main).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for more information.

## Author

Developed by Andrew McSparron. For queries, contact [amcsparron@albanyny.gov](mailto:amcsparron@albanyny.gov).