from pathlib import Path

__project_root__ = Path(__file__).parent.parent
__project_name__ = __project_root__.name

from EasyLoggerAJM.errs import InvalidEmailMsgType
from EasyLoggerAJM.custom_loggers import _EasyLoggerCustomLogger
from EasyLoggerAJM.handlers import _BaseCustomEmailHandler, OutlookEmailHandler, StreamHandlerIgnoreExecInfo
from EasyLoggerAJM.formatters import ColorizedFormatter, NO_COLORIZER
from EasyLoggerAJM.filters import ConsoleOneTimeFilter
from EasyLoggerAJM.easy_logger import EasyLogger

__all__ = ['_EasyLoggerCustomLogger', 'InvalidEmailMsgType',
           'OutlookEmailHandler', 'StreamHandlerIgnoreExecInfo',
           'ColorizedFormatter', 'ConsoleOneTimeFilter', 'EasyLogger', 'NO_COLORIZER',
           '__project_name__', '__project_root__']
