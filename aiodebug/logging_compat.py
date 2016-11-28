try:
	from logwood import get_logger
except ImportError:
	import logging
	get_logger = logging.getLogger
