import logging



def init_logging():
    # Configure basic logging settings
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",  # Customize date format as needed
        level=logging.DEBUG, # Set desired logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    )

    logging.info("logging initialized")

# end
